# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now
from frappe.utils import now, getdate,date_diff,add_days
from datetime import timedelta
class RejoiningForm(Document):

	def on_submit(self):
		application = frappe.get_doc("Leave Application", {"name":self.leave_application,'docstatus':('!=',2)})
		if application:
			re_join_date = getdate(self.re_join)
			if application.to_date > re_join_date:
				frappe.db.sql("""update `tabAttendance` set docstatus = 2 where leave_application = '%s' and docstatus != 2 """%(self.leave_application),as_dict = True)
				frappe.db.sql("""update `tabLeave Application` set status = "Cancelled" where name = '%s' and docstatus != 2 """%(self.leave_application),as_dict = True)
				frappe.db.sql("""update `tabLeave Application` set docstatus = 2 where name = '%s' and docstatus != 2 """%(self.leave_application),as_dict = True)
				frappe.db.sql("""update `tabLeave Application` set workflow_state="Cancelled" where name = '%s' and status = "Cancelled" """%(self.leave_application),as_dict = True)
				frappe.db.sql("""delete from `tabLeave Ledger Entry` where transaction_name = '%s' """%(self.leave_application),as_dict = True)
				frappe.msgprint('Please check the Leave Application')
				doc = frappe.new_doc("Leave Application")
				doc.amended_from = self.leave_application
				doc.employee = self.emp_no
				doc.from_date = self.start
				doc.to_date = add_days(self.re_join,-1)
				doc.postingdate = now()
				doc.leave_type = self.nature_of_leave
				doc.description = application.description
				doc.save(ignore_permissions = True)
				frappe.db.sql("""update `tabLeave Application` set workflow_state = "Approved"  where name = '%s'"""%(doc.name),as_dict = True)
				frappe.db.sql("""update `tabLeave Application` set status = "Approved"  where name = '%s'"""%(doc.name),as_dict = True)
				frappe.db.commit()
				le = frappe.new_doc("Leave Ledger Entry")
				le.employee = doc.employee
				le.leave_type = doc.leave_type
				le.transaction_type = "Leave Application"
				le.transaction_name = doc.name
				le.company=doc.company
				le.leaves = -(doc.total_leave_days)
				le.from_date = doc.from_date
				le.to_date = doc.to_date
				le.submit()
				frappe.db.commit()
				dates = getdays(self)
				for date in dates:
					attendance_doc = frappe.new_doc("Attendance")
					attendance_doc.employee = self.emp_no
					attendance_doc.attendance_date = date
					attendance_doc.status = "On Leave"
					attendance_doc.leave_type = doc.leave_type
					attendance_doc.leave_application = doc.name
					attendance_doc.company = doc.company
					attendance_doc.insert()
					attendance_doc.submit()
					frappe.db.commit()
			# else:


			

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
		# if rejoin:
		# 	frappe.errprint("HII")
		# else:
		# 	frappe.errprint("hi")

		# rejoin = frappe.db.get_value("Rejoining Form" ,{"emp_no" :employee},["re_join"])
		
		# rejoin = frappe.db.sql("""select name,creation,re_join from `tabRejoining Form` where emp_no = '%s' order by `creation` desc limit 1 """ %(self.emp_no),as_dict=True)
		# frappe.errprint(rejoin[0]["re_join"])
		# frappe.db.set_value("Leave Salary", rejoin[0]["name"], "rejoining_date", rejoin[0]["re_join"])

# @frappe.whitelist()		
# def on_submit(self):
# 	if self.workflow_state == "Approved":
# 		from_date = self.start
# 		to_date = self.end
# 		employee = self.emp_no
# 		attendance_documents = frappe.get_all(
# 			'Attendance',
# 			filters={
# 				'employee': employee,
# 				'attendance_date': ['between', [from_date, to_date]],
# 				'workflow_state': 'Approved',
# 				'status': 'On Leave'
# 			},
# 			fields=['name']
# 		)

# 		for document in attendance_documents:
# 			frappe.delete_doc('Attendance', document.name)

# 		return _("Attendance documents deleted successfully.")
	
