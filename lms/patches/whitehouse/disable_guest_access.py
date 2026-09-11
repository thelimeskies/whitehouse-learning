import frappe


def execute():
	"""Keep the Whitehouse LMS private unless an administrator opts out later."""
	frappe.db.set_single_value("LMS Settings", "allow_guest_access", 0)
