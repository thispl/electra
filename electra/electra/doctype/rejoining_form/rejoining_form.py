# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now
from frappe.utils import now, getdate,date_diff,add_days
from datetime import timedelta
import datetime
class RejoiningForm(Document):

	def on_submit(self):
		re_join_date = frappe.utils.data.getdate(self.re_join)
		leave_end_date = frappe.utils.data.getdate(self.end)
		if leave_end_date > re_join_date and self.nature_of_leave=="Annual Leave":
			if not frappe.db.exists("Leave Revocation", {"rejoining_form": self.name}):
				attendance_doc = frappe.new_doc("Leave Revocation")
				attendance_doc.employee = self.emp_no
				attendance_doc.rejoining_form = self.name
				attendance_doc.total_no_of_not_used_leave = abs(int(self.late_joining_in_days))
				attendance_doc.save(ignore_permissions=True)
				frappe.db.commit()
				le = frappe.new_doc("Leave Ledger Entry")
				le.employee = self.emp_no
				le.leave_type = "Annual Leave"
				le.transaction_type = "Leave Revocation"
				le.transaction_name = attendance_doc.name
				le.company = self.company
				le.leaves = abs(int(self.late_joining_in_days))
				le.from_date = frappe.utils.data.add_days(self.re_join, 1)
				current_year = frappe.utils.data.getdate(datetime.datetime.now()).year
				end_date = frappe.utils.data.getdate(datetime.date(current_year, 12, 31))
				le.to_date = end_date
				le.save(ignore_permissions=True)
				le.submit()
				frappe.db.commit()
		from_date = self.start
		to_date=self.end
		rejoining_date=self.re_join
		if self.nature_of_leave=="Annual Leave" and date_diff(frappe.utils.data.getdate(self.re_join),frappe.utils.data.getdate(self.end))>1:
			if not frappe.db.exists("Leave Extension", {"leave_application": self.leave_application,"docstatus":("!=",2)}):
				leave_ext= frappe.new_doc("Leave Extension")
				leave_ext.employee=self.emp_no
				leave_ext.from_date=from_date
				leave_ext.to_date=to_date
				leave_ext.extension_from_date=add_days(to_date, 1)
				leave_ext.extension_to_date=add_days(rejoining_date, -1)
				leave_ext.leave_application=self.leave_application
				leave_ext.reason=self.custom_reason
				leave_ext.custom_rejoining=self.name
				difference = date_diff(add_days(rejoining_date, -1), add_days(to_date, 1))
				frappe.errprint(difference)
				if difference >= 0:
					leave_ext.total_no_of_days = difference + 1
				leave_ext.save(ignore_permissions=True)
				leave_ext.submit()
				frappe.db.commit()
	
	def on_cancel(self):
		leave_extension = frappe.get_all("Leave Extension",{"leave_application": self.leave_application, "custom_rejoining": self.name},["name"])
		if leave_extension:
			leave_ext_doc = frappe.get_doc("Leave Extension", leave_extension[0].name)
			leave_ext_doc.cancel()
			frappe.db.commit()  

			
		


			

def getdays(self):
	start_date = self.start
	end_date = add_days(self.re_join,-1)
	no_of_days = date_diff(add_days(end_date,1),start_date)
	dates =[add_days(start_date,i) for i in range(0,no_of_days)]
	return dates

@frappe.whitelist()
def rejoining_date(employee,rejoin):
		leave_salary= frappe.db.get_value('Leave Salary', {'employee_number':employee},["name"])
		# frappe.errprint(leave_salary)
		rejoining = frappe.db.sql("""select name,rejoining_date from `tabLeave Salary` where employee_number = '%s' order by `creation` desc limit 1 """ %(employee),as_dict=True)
		for i in rejoining:
			# frappe.errprint(i.rejoining_date)
			# frappe.errprint(rejoin)
			ls = frappe.get_doc("Leave Salary",{'name':i.name})
			frappe.errprint(ls.employee_name)
			ls.rejoining_date = rejoin 
			ls.save(ignore_permissions=True)
			frappe.db.commit()

