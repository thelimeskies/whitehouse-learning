# Copyright (c) 2024, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LMSProgramMember(Document):
	def before_insert(self):
		if frappe.session.user == "Administrator" or {"Moderator", "System Manager"} & set(
			frappe.get_roles()
		):
			return
		frappe.throw(_("Only an administrator can assign a program to a learner."), frappe.PermissionError)
