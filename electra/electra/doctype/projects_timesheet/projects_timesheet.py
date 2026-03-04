# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt,time_diff_in_hours,to_timedelta
import datetime
from datetime import time
from frappe import _

class ProjectsTimesheet(Document):
	def after_insert(self):
		att_set = frappe.get_single("Attendance Settings")
		if att_set.from_date <= self.plan_date <= att_set.to_date:
			for row in self.project_day_plan_employee:
				row.total_working_hours = "6"
				row.from_time = "08:00:00"
				row.to_time = "14:00:00"
				row.ot = "0"
		else:
			for row in self.project_day_plan_employee:
				row.total_working_hours = "8"
				row.from_time = "08:00:00"
				row.to_time = "16:00:00"
				row.ot = "0"
	def validate(self):
		if self.plan_date:
			for row in self.project_day_plan_employee:
				if row.project:
					project_name = frappe.get_value("Project", row.project, "project_name")
					row.project_name = project_name
				row.worked_date = self.plan_date
		self.validate_working_hours()
	def on_submit(self):
		idx = 0
		for row in self.project_day_plan_employee:
			idx += 1
			if not row.total_working_hours or row.total_working_hours == time(0, 0):
				frappe.throw(f"<b>ROw-{idx}</b>: <b>WH</b> should not be <b>00:00</b>")
			
		# update task qty
		for tl in self.project_day_plan_employee:
			if tl.activity:
				task_id = frappe.get_doc("Task",tl.activity)
				if task_id.qty > 0:
					task_id.pending_qty -= tl.qty
					task_id.completed_qty += tl.qty
					task_id.save(ignore_permissions=True)
					frappe.db.commit()
			
		
		#create timesheet
		self.start_time = frappe.get_value("Day Plan",self.day_plan,"from_time")
		if self.start_time:
			start_time = self.start_time
		else:
			plan_date = datetime.datetime.strptime(str(self.plan_date),"%Y-%m-%d").date()
			start_time = datetime.datetime.combine(plan_date, datetime.time(hour=6))
		amt_1 = 0
		amt_2 = 0
		for tlog in self.project_day_plan_employee:
			query = """
				SELECT DISTINCT ts.name
				FROM `tabTimesheet` ts
				JOIN `tabTimesheet Detail` tsd ON ts.name = tsd.parent
				WHERE '%s' BETWEEN ts.start_date AND ts.end_date
				AND ts.employee = '%s'
				AND tsd.project = '%s'
				AND ts.docstatus = 1
			""" % (self.plan_date, tlog.employee, tlog.project)
			# query = """
			# 	select * from `tabTimesheet` ts where '%s' between ts.start_date and ts.end_date and employee = '%s' and ts.docstatus=1
			# 				""" % (self.plan_date,tlog.employee)
			timesheet_id = frappe.db.sql(query,as_dict=True)
			
			if not timesheet_id:
				ts = frappe.new_doc('Timesheet')
				ts.project = tlog.project
				ts.employee = tlog.employee
				ot = ot_hours = total_working_hours = 0
				# total_working_hours = time_diff_in_hours(tlog.to_time,tlog.from_time)
				if tlog.ot:
					# ot = to_timedelta(tlog.ot).total_seconds()
					# ot_hours = ot / 3600
					ot_hours = float(tlog.ot)
				
				working_hours = float(tlog.total_working_hours)
				end_time = start_time + datetime.timedelta(hours=working_hours)
				per_hour_cost = frappe.db.get_value('Employee',{'name':tlog.employee},'per_hour_cost')
				leave = frappe.db.get_value('Employee',{'name':tlog.employee},'holiday_list')
				holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
				left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(leave,self.plan_date),as_dict=True)
				if holiday:
					amt_1 = flt(per_hour_cost*1.50)
					if working_hours and working_hours > 0:
						
						ts.append("time_logs", {
						"activity_type" : "Regular Work",
						"project":tlog.project,
						"task": tlog.activity,
						"from_time" : start_time,
						"to_time" : end_time,
						"hours": working_hours,
						"is_billable" : 1,
						"costing_rate": amt_1,
						
					})
					if ot_hours and ot_hours > 0:
						overtime = end_time + datetime.timedelta(hours=ot_hours)
						end_of_day = datetime.datetime.combine(overtime.date(), datetime.time(23, 59, 59))
						if overtime > end_of_day:
							overtime = end_of_day
						ts.append("time_logs", {
						"activity_type" : "Overtime",
						"project":tlog.project,
						"task": tlog.activity,
						"from_time" : end_time,
						"to_time" : overtime,
						"hours": ot_hours,
						"is_billable" : 1,
						"costing_rate": amt_1,
						
					})
				else:
					amt_2 = flt(per_hour_cost*1.25)
					if working_hours and working_hours > 0:
						ts.append("time_logs", {
							"activity_type" : "Regular Work",
							"project":tlog.project,
							"task": tlog.activity,
							"from_time" : start_time,
							"to_time" : end_time,
							"hours": working_hours,
							"is_billable" : 1,
							"costing_rate": flt(per_hour_cost),
							
						})
					if ot_hours and ot_hours > 0:
						overtime = end_time + datetime.timedelta(hours=ot_hours)
						end_of_day = datetime.datetime.combine(overtime.date(), datetime.time(23, 59, 59))
						if overtime > end_of_day:
							overtime = end_of_day
						
						ts.append("time_logs", {
						"activity_type" : "Overtime",
						"project":tlog.project,
						"task": tlog.activity,
						"from_time" : end_time,
						"to_time" : overtime,
						"hours": ot_hours,
						"is_billable" : 1,
						"costing_rate":amt_2,
						
					})
				ts.save(ignore_permissions=True)
			   
				# leave = frappe.db.get_value('Employee',{'name':ts.employee},'holiday_list')
				# holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
				# left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(leave,self.plan_date),as_dict=True)
				# if holiday:
				#     ts.total_billable_amount = flt(((per_hour_cost/26)/8) * 1.50)
				# else:
				#     ts.total_billable_amount = flt(((per_hour_cost/26)/8) * 1.25)
				# ts.save(ignore_permissions=True)
				ts.submit()
			else:
				frappe.throw("Timesheets has been already created for this Employee for the same period")
	def on_cancel(self):
		for tlog in self.project_day_plan_employee:
			query = """
				SELECT DISTINCT ts.name
				FROM `tabTimesheet` ts
				JOIN `tabTimesheet Detail` tsd ON ts.name = tsd.parent
				WHERE '%s' BETWEEN ts.start_date AND ts.end_date
				AND ts.employee = '%s'
				AND tsd.project = '%s'
				AND ts.docstatus = 1
			""" % (self.plan_date, tlog.employee, tlog.project)
			timesheet_id = frappe.db.sql(query,as_dict=True)
			if timesheet_id:
				timesheet = frappe.get_doc("Timesheet",timesheet_id)
				timesheet.cancel()
				# timesheet.delete()
	# def validate(self):
	#     #create timesheet
	#     start_time = frappe.get_value("Day Plan",self.day_plan,"from_time")
	#     if start_time:
	#         start_time = start_time
	#     else:
	#         plan_date = datetime.datetime.strptime(str(self.plan_date),"%Y-%m-%d").date()
	#         start_time = datetime.datetime.combine(plan_date, datetime.time(hour=6))
	#     for tlog in self.project_day_plan_employee:
	#         query = """
	#             select * from `tabTimesheet` ts where '%s' between ts.start_date and ts.end_date and employee = '%s'
	#                         """ % (self.plan_date,tlog.employee)
	#         timesheet_id = frappe.db.sql(query,as_dict=True)
			
	#         if not timesheet_id:
	#             ot = ot_hours = total_working_hours = 0
	#             total_working_hours = time_diff_in_hours(tlog.to_time,tlog.from_time)
	#             if tlog.ot:
	#                 ot = to_timedelta(tlog.ot).total_seconds()
	#                 ot_hours = ot / 3600
				
	#             working_hours = total_working_hours - ot_hours
	#             end_time = start_time + datetime.timedelta(hours=working_hours)

	def validate_working_hours(self):
		emp_date_hours = {}

		for row in self.project_day_plan_employee:
			key = (row.employee, row.worked_date)
			emp_date_hours[key] = flt(emp_date_hours.get(key, 0)) + flt(row.total_working_hours or 0)

		for (employee, worked_date), total_hours in emp_date_hours.items():
			if is_restricted_day(worked_date) == "yes":
				if total_hours > 6:
					frappe.throw(
						_("Total working hours cannot exceed 6")
					)
			# else:
			# 	if total_hours > 8:
			# 		frappe.throw(
			# 			_("Total working hours cannot exceed 8")
			# 		)

	
@frappe.whitelist()
def is_restricted_day(date):
	att_set = frappe.get_single("Attendance Settings")
	if att_set.from_date <= date <= att_set.to_date:
		return "yes"
	else:
		return "no"
