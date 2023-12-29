# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AdditionalVecation(Document):
	pass

	def on_submit(self):
		frappe.errprint("HI")
		doc = frappe.new_doc("Leave Application")
		doc.employee = self.employee
		doc.from_date = self.from_date
		doc.to_date = self.to_date
		doc.description = self.reason
		doc.leave_type = "Annual Leave"
		doc.i_agree0 = 1
		doc.status = "Approved"
		doc.save(ignore_permissions = True)
		# doc.submit()
		frappe.db.commit()
		frappe.errprint("HI")
		# leave = frappe.db.sql("""update `tabLeave Application` set workflow_state = "Approved" and docstatus = 1  where employee = '%s' and from_date = '%s' and to_date = '%s' """%(self.employee,self.from_date,self.to_date),as_dict = True)
		# leave.save(ignore_permissions = True)
		