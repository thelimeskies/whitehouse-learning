import frappe
from frappe.model.document import Document


class LMSOrganization(Document):
	def validate(self):
		self.organization_name = (self.organization_name or "").strip()
		if not self.organization_name:
			frappe.throw("Organization name is required.")
