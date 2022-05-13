# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.document import Document

class EmployeeMasterRecord(Document):
	pass

# @frappe.whitelist()
# def leave_tracker(doc,method):
#     employee = frappe.db.get_all("Leave Application",{'employee':doc.employee_id},[''])
#     tracker = frappe.db.sql("""select leave_type,from_date,to_date,ticket_required,from,to from `tabLeave Application` where employee %s """  %(employee), as_dict=1)
#     return tracker

