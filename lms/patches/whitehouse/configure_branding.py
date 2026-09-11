import frappe

from lms.install import configure_whitehouse_branding


def execute():
	"""Apply Whitehouse Learning branding to sites created before this client fork."""
	configure_whitehouse_branding()
	frappe.clear_cache()
