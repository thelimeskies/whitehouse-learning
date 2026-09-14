"""Administrator-only course assignment, CSV import, and learning analytics."""

import csv
import io

import frappe
from frappe import _
from frappe.utils import cint, validate_email_address


MAX_IMPORT_ROWS = 500
MAX_IMPORT_BYTES = 100_000


def require_learning_admin():
	if frappe.session.user == "Administrator" or {"Moderator", "System Manager"} & set(
		frappe.get_roles()
	):
		return
	frappe.throw(_("Only learning administrators can perform this action."), frappe.PermissionError)


@frappe.whitelist()
def get_organizations():
	"""Whitehouse-managed client list; no client-side administrative roles."""
	require_learning_admin()
	return frappe.get_all(
		"LMS Organization",
		fields=["name", "organization_name", "status"],
		order_by="organization_name asc",
		limit_page_length=1000,
	)


@frappe.whitelist()
def create_organization(organization_name: str):
	require_learning_admin()
	organization_name = (organization_name or "").strip()
	if not organization_name or len(organization_name) > 140:
		frappe.throw(_("Enter an organization name of 1 to 140 characters."))
	if frappe.db.exists("LMS Organization", organization_name):
		return {"name": organization_name, "created": False}
	doc = frappe.get_doc(
		{"doctype": "LMS Organization", "organization_name": organization_name, "status": "Active"}
	).insert(ignore_permissions=True)
	return {"name": doc.name, "created": True}


@frappe.whitelist()
def invite_learner(email: str, first_name: str, last_name: str = ""):
	"""Create an invited learner, leaving client grouping to course assignments."""
	require_learning_admin()
	email = (email or "").strip().lower()
	first_name = (first_name or "").strip()
	last_name = (last_name or "").strip()
	validate_email_address(email, True)
	if not first_name or len(first_name) > 140 or len(last_name) > 140:
		frappe.throw(_("Enter a first name of 1 to 140 characters."))
	if frappe.db.exists("User", email):
		frappe.throw(_("This user already exists. Find them in Users and assign their training."))

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"last_name": last_name,
			"enabled": 1,
			"user_type": "Website User",
			"send_welcome_email": 1,
			"roles": [{"role": "LMS Student"}],
		}
	).insert(ignore_permissions=True)
	return {"email": user.email, "created": True, "welcome_email_queued": bool(user.flags.email_sent)}


@frappe.whitelist()
def set_organization_status(name: str, status: str):
	"""Pause or resume future assignments without removing existing records."""
	require_learning_admin()
	if status not in {"Active", "Inactive"}:
		frappe.throw(_("Choose Active or Inactive status."))
	organization = frappe.get_doc("LMS Organization", name)
	organization.status = status
	organization.save(ignore_permissions=True)
	return {"name": organization.name, "status": organization.status}


@frappe.whitelist()
def bulk_assign_course(
	course: str, csv_text: str, create_missing: int = 0, dry_run: int = 1,
	organization: str | None = None,
):
	"""Atomically assign a course from a CSV of email,first_name,last_name.

	A dry run validates all rows and reports what would change. No existing user
	profile or role is ever modified. Repeated rows and existing enrollments are
	counted as skips. New users receive the normal Frappe welcome flow.
	"""
	require_learning_admin()
	if not frappe.db.exists("LMS Course", course):
		frappe.throw(_("Course not found."), frappe.DoesNotExistError)
	if organization:
		if not frappe.db.exists("LMS Organization", {"name": organization, "status": "Active"}):
			frappe.throw(_("Select an active client organization."))
	if not isinstance(csv_text, str) or len(csv_text.encode("utf-8")) > MAX_IMPORT_BYTES:
		frappe.throw(_("CSV must be UTF-8 text smaller than 100 KB."))

	reader = csv.DictReader(io.StringIO(csv_text.lstrip("\ufeff")))
	if not reader.fieldnames or "email" not in [name.strip().lower() for name in reader.fieldnames]:
		frappe.throw(_("CSV must include an email column."))
	reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
	rows = list(reader)
	if not rows or len(rows) > MAX_IMPORT_ROWS:
		frappe.throw(_("CSV must contain between 1 and 500 learners."))

	create_missing = bool(cint(create_missing))
	dry_run = bool(cint(dry_run))
	seen = set()
	prepared = []
	errors = []
	for number, row in enumerate(rows, start=2):
		email = (row.get("email") or "").strip().lower()
		if not email:
			errors.append({"row": number, "message": _("Email is required.")})
			continue
		try:
			validate_email_address(email, True)
		except frappe.ValidationError:
			errors.append({"row": number, "message": _("Invalid email address.")})
			continue
		if email in seen:
			continue
		seen.add(email)
		user_exists = bool(frappe.db.exists("User", email))
		if not user_exists and not create_missing:
			errors.append({"row": number, "message": _("Learner does not exist: {0}").format(email)})
			continue
		prepared.append(
			{
				"email": email,
				"first_name": (row.get("first_name") or "").strip() or "Learner",
				"last_name": (row.get("last_name") or "").strip(),
				"new_user": not user_exists,
				"already_assigned": bool(
					frappe.db.exists("LMS Enrollment", {"course": course, "member": email})
				),
				"existing_organization": frappe.db.get_value(
					"LMS Enrollment", {"course": course, "member": email}, "organization"
				),
			}
		)
		if organization and prepared[-1]["already_assigned"] and prepared[-1]["existing_organization"] != organization:
			errors.append({"row": number, "message": _("Learner is already assigned to this course under another organization.")})

	result = {
		"ok": not errors,
		"rows": len(rows),
		"new_users": sum(item["new_user"] for item in prepared),
		"to_assign": sum(not item["already_assigned"] for item in prepared),
		"already_assigned": sum(item["already_assigned"] for item in prepared),
		"errors": errors[:50],
		"applied": False,
	}
	if errors or dry_run:
		return result

	for item in prepared:
		if item["new_user"]:
			frappe.get_doc(
				{
					"doctype": "User",
					"email": item["email"],
					"first_name": item["first_name"],
					"last_name": item["last_name"],
					"enabled": 1,
					"user_type": "Website User",
					"roles": [{"role": "LMS Student"}],
				}
			).insert(ignore_permissions=True)
		if not item["already_assigned"]:
			frappe.get_doc(
				{
					"doctype": "LMS Enrollment", "course": course,
					"member": item["email"], "organization": organization,
				}
			).insert(ignore_permissions=True)
	result["applied"] = True
	return result


@frappe.whitelist()
def get_admin_learning_analytics(course: str | None = None, organization: str | None = None):
	"""Assignment funnel, engagement risk, trend, and per-course outcomes."""
	require_learning_admin()
	if course and not frappe.db.exists("LMS Course", course):
		frappe.throw(_("Course not found."), frappe.DoesNotExistError)
	if organization and not frappe.db.exists("LMS Organization", organization):
		frappe.throw(_("Client organization not found."), frappe.DoesNotExistError)
	conditions = []
	if course:
		conditions.append("e.course = %(course)s")
	if organization:
		conditions.append("e.organization = %(organization)s")
	where = "WHERE " + " AND ".join(conditions) if conditions else ""
	params = {"course": course, "organization": organization}
	summary = frappe.db.sql(
		f"""
		SELECT COUNT(*) AS assignments,
		       COUNT(DISTINCT e.member) AS learners,
		       SUM(CASE WHEN IFNULL(e.progress, 0) = 0 THEN 1 ELSE 0 END) AS not_started,
		       SUM(CASE WHEN e.progress > 0 AND e.progress < 100 THEN 1 ELSE 0 END) AS in_progress,
		       SUM(CASE WHEN e.progress >= 100 THEN 1 ELSE 0 END) AS completed,
		       ROUND(AVG(IFNULL(e.progress, 0)), 1) AS average_progress,
		       SUM(CASE WHEN e.progress < 100
		                AND DATEDIFF(CURRENT_DATE(), DATE(e.modified)) >= 14
		                THEN 1 ELSE 0 END) AS inactive_14_days
		FROM `tabLMS Enrollment` e {where}
		""",
		params,
		as_dict=True,
	)[0]
	courses = frappe.db.sql(
		f"""
		SELECT c.name, c.title, COUNT(*) AS assignments,
		       SUM(CASE WHEN IFNULL(e.progress, 0) = 0 THEN 1 ELSE 0 END) AS not_started,
		       SUM(CASE WHEN e.progress > 0 AND e.progress < 100 THEN 1 ELSE 0 END) AS in_progress,
		       SUM(CASE WHEN e.progress >= 100 THEN 1 ELSE 0 END) AS completed,
		       ROUND(AVG(IFNULL(e.progress, 0)), 1) AS average_progress
		FROM `tabLMS Enrollment` e
		JOIN `tabLMS Course` c ON c.name = e.course
		{where}
		GROUP BY c.name, c.title
		ORDER BY assignments DESC, c.title ASC
		""",
		params,
		as_dict=True,
	)
	trend = frappe.db.sql(
		f"""
		SELECT DATE(e.creation) AS date, COUNT(*) AS assignments
		FROM `tabLMS Enrollment` e
		{where + (' AND' if where else ' WHERE')} e.creation >= DATE_SUB(CURRENT_DATE(), INTERVAL 29 DAY)
		GROUP BY DATE(e.creation)
		ORDER BY date ASC
		""",
		params,
		as_dict=True,
	)
	at_risk = frappe.db.sql(
		f"""
		SELECT e.member, u.full_name, c.title AS course_title,
		       e.course, e.progress, e.modified AS last_activity
		FROM `tabLMS Enrollment` e
		JOIN `tabUser` u ON u.name = e.member
		JOIN `tabLMS Course` c ON c.name = e.course
		{where + (' AND' if where else ' WHERE')} e.progress < 100
		AND DATEDIFF(CURRENT_DATE(), DATE(e.modified)) >= 14
		ORDER BY e.modified ASC
		LIMIT 100
		""",
		params,
		as_dict=True,
	)
	organizations = frappe.db.sql(
		f"""
		SELECT e.organization, COUNT(*) AS assignments,
		       COUNT(DISTINCT e.member) AS learners,
		       SUM(CASE WHEN e.progress >= 100 THEN 1 ELSE 0 END) AS completed,
		       ROUND(AVG(IFNULL(e.progress, 0)), 1) AS average_progress
		FROM `tabLMS Enrollment` e {where + (' AND' if where else ' WHERE')}
		e.organization IS NOT NULL AND e.organization != ''
		GROUP BY e.organization ORDER BY assignments DESC, e.organization ASC
		""",
		params,
		as_dict=True,
	)
	people = frappe.db.sql(
		f"""
		SELECT e.member, u.full_name, e.organization, e.course, c.title AS course_title,
		       IFNULL(e.progress, 0) AS progress, e.current_lesson,
		       e.creation AS assigned_on, e.modified AS last_enrollment_update,
		       (SELECT COUNT(*) FROM `tabLMS Course Progress` cp
		        WHERE cp.member = e.member AND cp.course = e.course AND cp.status = 'Complete')
		        AS lessons_completed,
		       (SELECT ROUND(IFNULL(SUM(CAST(v.watch_time AS DECIMAL(12, 2))), 0) / 60, 1)
		        FROM `tabLMS Video Watch Duration` v
		        WHERE v.member = e.member AND v.course = e.course) AS recorded_video_minutes,
		       (SELECT MAX(q.percentage) FROM `tabLMS Quiz Submission` q
		        WHERE q.member = e.member AND q.course = e.course) AS best_quiz_percent
		FROM `tabLMS Enrollment` e
		JOIN `tabUser` u ON u.name = e.member
		JOIN `tabLMS Course` c ON c.name = e.course
		{where}
		ORDER BY u.full_name ASC, e.creation DESC
		LIMIT 1000
		""",
		params,
		as_dict=True,
	)
	return {
		"summary": summary, "courses": courses, "trend": trend,
		"at_risk": at_risk, "organizations": organizations, "people": people,
	}
