import frappe

from lms.lms.admin_learning import (
	bulk_assign_course,
	create_organization,
	get_admin_learning_analytics,
	get_organizations,
)
from lms.lms.test_helpers import BaseTestUtils


class TestAdminAssignedLearning(BaseTestUtils):
	def setUp(self):
		super().setUp()
		suffix = frappe.generate_hash(length=6)
		self.learner = self._create_user(
			f"assignment-{suffix}@example.com", "Test", "Learner", ["LMS Student"]
		)
		self.course = self._create_course(title=f"Assigned Course {suffix}")

	def test_learner_cannot_self_enroll_even_with_ignore_permissions(self):
		frappe.session.user = self.learner.name
		try:
			with self.assertRaises(frappe.PermissionError):
				frappe.get_doc(
					{"doctype": "LMS Enrollment", "course": self.course.name, "member": self.learner.name}
				).insert(ignore_permissions=True)
		finally:
			frappe.session.user = "Administrator"

	def test_bulk_import_previews_then_assigns_once(self):
		csv_text = f"email\n{self.learner.email}\n{self.learner.email}\n"
		preview = bulk_assign_course(self.course.name, csv_text)
		self.assertTrue(preview["ok"])
		self.assertFalse(preview["applied"])
		self.assertEqual(preview["to_assign"], 1)
		self.assertFalse(
			frappe.db.exists(
				"LMS Enrollment", {"course": self.course.name, "member": self.learner.name}
			)
		)
		applied = bulk_assign_course(self.course.name, csv_text, dry_run=0)
		self.assertTrue(applied["applied"])
		enrollment = frappe.db.exists(
			"LMS Enrollment", {"course": self.course.name, "member": self.learner.name}
		)
		self.assertTrue(enrollment)
		self.cleanup_items.append(("LMS Enrollment", enrollment))
		self.assertEqual(bulk_assign_course(self.course.name, csv_text)["already_assigned"], 1)

	def test_learner_cannot_read_admin_analytics_or_bulk_assign(self):
		frappe.session.user = self.learner.name
		try:
			with self.assertRaises(frappe.PermissionError):
				get_admin_learning_analytics()
			with self.assertRaises(frappe.PermissionError):
				bulk_assign_course(self.course.name, f"email\n{self.learner.email}\n")
			with self.assertRaises(frappe.PermissionError):
				get_organizations()
		finally:
			frappe.session.user = "Administrator"

	def test_whitehouse_client_assignment_and_person_analytics(self):
		name = f"Test Training Client {frappe.generate_hash(length=6)}"
		organization = create_organization(name)["name"]
		self.cleanup_items.append(("LMS Organization", organization))
		result = bulk_assign_course(
			self.course.name, f"email\n{self.learner.email}\n", dry_run=0,
			organization=organization,
		)
		self.assertTrue(result["applied"])
		enrollment = frappe.db.exists(
			"LMS Enrollment", {"course": self.course.name, "member": self.learner.name}
		)
		self.cleanup_items.append(("LMS Enrollment", enrollment))
		self.assertEqual(frappe.db.get_value("LMS Enrollment", enrollment, "organization"), organization)
		analytics = get_admin_learning_analytics(organization=organization)
		self.assertEqual(analytics["summary"]["assignments"], 1)
		self.assertEqual(analytics["people"][0]["member"], self.learner.name)
		self.assertEqual(analytics["organizations"][0]["organization"], organization)
		other = create_organization(f"Other Training Client {frappe.generate_hash(length=6)}")["name"]
		self.cleanup_items.append(("LMS Organization", other))
		conflict = bulk_assign_course(
			self.course.name, f"email\n{self.learner.email}\n", organization=other,
		)
		self.assertFalse(conflict["ok"])
