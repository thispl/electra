# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MobileTariffChange(Document):
	def on_submit(self):
		emp = frappe.get_doc('Employee',{'employee_number':self.emp_id})
		emp.current_plan = self.proposed_plan
		emp.current_benefits = self.proposed_benefits
		emp.save(ignore_permissions =True)
