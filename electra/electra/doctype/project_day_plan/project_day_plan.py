# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date, datetime, timedelta
import time

class ProjectDayPlan(Document):
	def on_submit(self):
		# frappe.errprint("Vankkkam")
		proj_ot = '00:00:00'
		one_hour = '01:00:00'
		for pro in self.project_day_plan_employee:
			if pro.total_working_hours:
				proj_time = datetime.strptime(str(pro.total_working_hours), "%H:%M:%S").time()
				eight_hours = datetime.strptime(str('08:00:00'),'%H:%M:%S').time()
				proj_ot = datetime.strptime(str(pro.ot), "%H:%M:%S").time()
				one_hour = datetime.strptime(str('01:00:00'),'%H:%M:%S').time()
				# frappe.errprint(one_hour)
				# ot = time.strptime(pro.ot, "%H:%M:%S")
				# frappe.errprint(ot.tm_hour)
				in_t = datetime.strptime(str(pro.from_time),'%H:%M:%S').time()
				in_time = datetime.combine(self.plan_date, in_t)
				frappe.errprint(in_time)
				ou_t = datetime.strptime(str(pro.to_time),'%H:%M:%S').time()
				out_time = datetime.combine(self.plan_date, ou_t)
				frappe.errprint(out_time)
				get_att = frappe.db.exists("Attendance",{'employee_name':pro.employee_name,'attendance_date':self.plan_date})
				if not get_att:
					if proj_time >= eight_hours:
						frappe.errprint(get_att)
						att = frappe.new_doc("Attendance")
						att.company = self.company
						att.employee = pro.employee
						att.status = "Present"
						att.attendance_date = self.plan_date
						att.in_time = in_time
						att.out_time = out_time
						att.save(ignore_permissions=True)

			# if pro.ot:
			ot = time.strptime(str(pro.ot),'%H:%M:%S')
			frappe.errprint(ot)
			get_ts = frappe.db.exists("Timesheet",{'employee_name':pro.employee_name,'end_date':self.plan_date,'parent_project':pro.project})
			frappe.errprint(get_ts)
			if not get_ts:
				if proj_ot >= one_hour:
					ts = frappe.new_doc("Timesheet")
					ts.company = self.company
					ts.status = "Draft"
					ts.employee = pro.employee
					ts.start_date = self.plan_date
					ts.end_date = self.plan_date
					ts.parent_project =pro.project
					ts.append("time_logs", {
						"activity_type": "Overtime",
						"hours":ot.tm_hour,
						"billing_hours":ot.tm_hour,
						"project":pro.project,
						"is_billable": 1,
					})
					ts.save(ignore_permissions=True)





				# if tim.tm_hour > 4 and tim.tm_hour < 8:
				# 	frappe.errprint(get_att)
				# 	if not get_att:
				# 		att = frappe.new_doc("Attendance")
				# 		att.company = "ENGINEERING DIVISION - ELECTRA"
				# 		att.employee = pro.employee
				# 		att.status = "Half-"
				# 		att.attendance_date = self.plan_date
				# 		att.in_time = self.plan_date + " " + pro.from_time
				# 		att.out_time = self.plan_date + " " + pro.to_time
				# 		att.save(ignore_permissions=True)


					
					# frappe.errprint(pro.project)
					# frappe.errprint(pro.from_time)
					# frappe.errprint(pro.to_time)
					# frappe.errprint(pro.ot)





			# if pro.total_working_hours >= "08:00:00":
				# frappe.errprint(type(pro.total_working_hours))
				# date_time = datetime.strptime(pro.total_working_hours, "%H:%M:%S")
				# time_obj = time.strptime(date_time, '%H:%M:%S')
				
				# frappe.errprint(time_obj)
				# frappe.errprint(type(time_obj))
