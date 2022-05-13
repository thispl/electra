# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe.model.document import Document
from datetime import datetime

class AccidentDeclarationForm(Document):
	@frappe.whitelist()
	def get_day(self):
		date = datetime.strptime(self.date,'%Y-%m-%d').date()
		day = date.strftime('%A')
		return day

@frappe.whitelist()
def accident_declaration_form(due_date):
	data = frappe.db.get_value("Legal Compliance Monitor",{'next_due_date':due_date,'visa_approval_number':None},['name'])
	if data:
		for d in data:
			name = d.name
			if name:
				for i in name:
					return data

@frappe.whitelist()
def test_case(employee,data,id):
	list_data = []
	emp_data = frappe.db.get_value("Shift Assignment",{'employee':employee})
	list_data.append(emp_data)
	l = len(list_data)
	if l>3:
		frappe.throw("This is not approved by the Admin ")

	else:
		frappe.throw("Youre eligible for this ")
		frappe.msgprint("Success")