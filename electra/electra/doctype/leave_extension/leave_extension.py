# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe import _
from frappe.model.document import Document
from frappe.model.document import Document

from frappe.utils import getdate, add_days



class LeaveExtension(Document):
	def get_leave_details_le(employee):
		leave_application = frappe.get_list(
			"Leave Application",
			filters={
				"employee": employee,
				"status": "Approved",
				"leave_type": "Annual Leave"
			},
			fields=["name", "from_date", "to_date"],
			order_by="creation desc",
			limit=1
		)
		if leave_application:
			leave_details = leave_application[0]
			return {
				"leave_application": leave_details.name,
				"from_date": leave_details.from_date,
				"to_date": leave_details.to_date
			}

		else:
			frappe.throw(_("No approved annual leave application found for the employee."))


	# def on_submit(self):
	# 	if self.workflow_state == "Approved":
	# 		from_date = self.extension_from_date
	# 		to_date = self.extension_to_date
	# 		employee = self.employee
	# 		employee_name = self.employee_name
	# 		company = self.company

	# 		current_date = getdate(from_date)
	# 		while current_date <= getdate(to_date):
	# 			new_attendance_doc = frappe.new_doc("Attendance")
	# 			new_attendance_doc.employee = employee
	# 			new_attendance_doc.employee_name = employee_name
	# 			new_attendance_doc.attendance_date = current_date
	# 			new_attendance_doc.company = company
	# 			new_attendance_doc.leave_type = "Annual Leave"
	# 			new_attendance_doc.status = "On Leave"
	# 			new_attendance_doc.flags.ignore_validate = True
	# 			new_attendance_doc.insert(ignore_permissions=True)
	# 			new_attendance_doc.submit()

	# 			current_date = add_days(current_date, 1)


	def on_submit(self):
		from_date = self.extension_from_date
		to_date = self.extension_to_date
		employee = self.employee
		employee_name = self.employee_name
		company = self.company
		current_date = getdate(from_date)
		while current_date <= getdate(to_date):
			if not frappe.db.exists("Attendance",{'attendance_date':current_date,'docstatus':('!=',2)}):
				new_attendance_doc = frappe.new_doc("Attendance")
			else:
				new_attendance_doc = frappe.get_doc("Attendance",{'attendance_date':current_date,'docstatus':('!=',2)})
			new_attendance_doc.employee = employee
			new_attendance_doc.employee_name = employee_name
			new_attendance_doc.attendance_date = current_date
			new_attendance_doc.company = company
			new_attendance_doc.leave_type = "Annual Leave"
			new_attendance_doc.status = "On Leave"
			new_attendance_doc.flags.ignore_validate = True
			new_attendance_doc.insert(ignore_permissions=True)
			new_attendance_doc.submit()
			current_date = add_days(current_date, 1)
		frappe.db.commit()  # Commit the changes after creating all Attendance documents

