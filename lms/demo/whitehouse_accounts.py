"""One-time, explicit provisioning for the Whitehouse client demonstration.

Run with ``bench --site <site> execute lms.demo.whitehouse_accounts.create_demo_accounts``.
Never call this from install hooks or application startup.
"""

import secrets

import frappe


DEMO_USERS = (
	("demo.learner.one@whitehouse-learning.kylodo.com", "Demo", "Learner One"),
	("demo.learner.two@whitehouse-learning.kylodo.com", "Demo", "Learner Two"),
)
DEMO_ORGANIZATION = "Demo Training Client"


def create_demo_accounts():
	"""Create only absent learner accounts; return credentials only on creation."""
	if frappe.session.user != "Administrator":
		frappe.throw("Run demo provisioning as the site Administrator.", frappe.PermissionError)

	results = []
	if not frappe.db.exists("LMS Organization", DEMO_ORGANIZATION):
		frappe.get_doc(
			{
				"doctype": "LMS Organization",
				"organization_name": DEMO_ORGANIZATION,
				"status": "Active",
			}
		).insert(ignore_permissions=True)
	for email, first_name, last_name in DEMO_USERS:
		if frappe.db.exists("User", email):
			results.append({"email": email, "status": "already exists"})
			continue

		password = secrets.token_urlsafe(18)
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first_name,
				"last_name": last_name,
				"enabled": 1,
				"user_type": "Website User",
				"send_welcome_email": 0,
				"new_password": password,
				"roles": [{"role": "LMS Student"}],
			}
		)
		user.insert(ignore_permissions=True)
		results.append({"email": email, "password": password, "status": "created"})

	course = frappe.db.get_value("LMS Course", {"published": 1}, "name", order_by="creation asc")
	if course and frappe.db.exists("User", DEMO_USERS[0][0]):
		member = DEMO_USERS[0][0]
		if not frappe.db.exists("LMS Enrollment", {"course": course, "member": member}):
			frappe.get_doc({"doctype": "LMS Enrollment", "course": course, "member": member,
				"organization": DEMO_ORGANIZATION}).insert(
				ignore_permissions=True
			)
		results[0]["assigned_course"] = course
		results[0]["organization"] = DEMO_ORGANIZATION

	frappe.db.commit()
	return results
