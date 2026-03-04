# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from itertools import groupby
from operator import itemgetter
from electra.utils import get_series

class MultiProjectDayPlan(Document):
	def on_submit(self):
		att_set = frappe.get_single("Attendance Settings")
		if att_set.from_date <= self.plan_date <= att_set.to_date:
			name = frappe.db.get_value('User',frappe.session.user,'full_name')
			self.approved_by_name = name
			pdp = frappe.new_doc("Projects Timesheet")
			pdp.plan_date = self.plan_date
			pdp.company = self.company
			pdp.multi_project_day_plan = self.name
			pdp.naming_series = get_series(self.company,"Projects Timesheet")
			for pdpe in self.project_day_plan_employee:
				pdp.append("project_day_plan_employee", {
						"project": pdpe.project,
						"project_name": pdpe.project_name,
						"sales_order": pdpe.sales_order,
						"employee": pdpe.employee,
						"employee_name": pdpe.employee_name,
						"designation": pdpe.designation,
						"from_time":"08:00:00",
						"to_time":"14:00:00",
						"lunch_break":"01:00:00",
						"total_working_hours":"6",
						"ot":"0"
					})
			pdp.save(ignore_permissions=True)
		else:
			name = frappe.db.get_value('User',frappe.session.user,'full_name')
			self.approved_by_name = name
			pdp = frappe.new_doc("Projects Timesheet")
			pdp.plan_date = self.plan_date
			pdp.company = self.company
			pdp.multi_project_day_plan = self.name
			pdp.naming_series = get_series(self.company,"Projects Timesheet")
			for pdpe in self.project_day_plan_employee:
				pdp.append("project_day_plan_employee", {
						"project": pdpe.project,
						"project_name": pdpe.project_name,
						"sales_order": pdpe.sales_order,
						"employee": pdpe.employee,
						"employee_name": pdpe.employee_name,
						"designation": pdpe.designation,
						"from_time":"08:00:00",
						"to_time":"16:00:00",
						"lunch_break":"01:00:00",
						"total_working_hours":"8",
						"ot":"0"
					})
			pdp.save(ignore_permissions=True)

	def on_cancel(self):
		if frappe.db.exists("Projects Timesheet",{'multi_project_day_plan':self.name,'docstatus':('!=',2)}):
			projects_timesheet = frappe.get_doc("Projects Timesheet",{'multi_project_day_plan':self.name,'docstatus':('!=',2)})
			if projects_timesheet.docstatus==0:
				projects_timesheet.delete()
			elif projects_timesheet.docstatus==1:
				projects_timesheet.cancel()
				# projects_timesheet.delete()

@frappe.whitelist()
def get_child_table_data(name):
	project_dict_list = []
	data = "<table border=1px class='table table-bordered'><tr><td><b>Project</b></td><td style=width:40%><b>Project Name</b></td><td><b>Employee Name</b></td></tr>"
	tape = frappe.db.sql("""SELECT project_name, project, employee, employee_name FROM `tabProject Day Plan Child` WHERE parent='%s'""" % (name), as_dict=True)
	students = sorted(tape, key=itemgetter('project_name'))
	
	for key, value in groupby(students, key=itemgetter('project_name')):
		for k in value:
			project_dict_list.append(k)
	
	merged_dict = {}
	for d in project_dict_list:
		employee_id = f"{d['employee']}:{d['employee_name']}"
		if d['project_name'] in merged_dict:
			merged_dict[d['project_name']].append({'project': d['project'], 'employee_id': employee_id})
		else:
			merged_dict[d['project_name']] = [{'project': d['project'], 'employee_id': employee_id}]
	
	merged_list = [{'project_name': k, 'details': v} for k, v in merged_dict.items()]
	
	for i in merged_list:
		emp_name_len = len(i['details'])
		first_row = i['details'][0]
		data += "<tr><td rowspan=%s>%s</td><td rowspan=%s>%s</td><td>%s</td></tr>" % (emp_name_len, first_row['project'], emp_name_len, i['project_name'], first_row['employee_id'])
		for j in range(1, emp_name_len): 
			data += "<tr><td>%s</td></tr>" % (i['details'][j]['employee_id'])
	data += '</table>'
	return data



@frappe.whitelist()
def get_driver_table_data(name):
	project_day_plan_driver_count = frappe.db.count("Project Day Plan Driver", filters={"parent": name})

	if project_day_plan_driver_count > 0:
		project_dict_list = []
		data = "<table border=1px class='table table-bordered'><tr><td><b>Project</b></td><td style=width:40%><b>Project Name</b></td><td><b>Employee Name</b></td></tr>"
		tape = frappe.db.sql("""select project_name,employee,project,employee_name from `tabProject Day Plan Driver` where parent='%s'  """ %(name), as_dict=True)
		students = sorted(tape, key=itemgetter('project_name'))
		
		for key, value in groupby(students, key=itemgetter('project_name')):
			for k in value:
				project_dict_list.append(k)
		
		merged_dict = {}
		for d in project_dict_list:
			employee_id = f"{d['employee']}:{d['employee_name']}"
			if d['project_name'] in merged_dict:
				merged_dict[d['project_name']].append({'project': d['project'], 'employee_id': employee_id})
			else:
				merged_dict[d['project_name']] = [{'project': d['project'], 'employee_id': employee_id}]
		
		merged_list = [{'project_name': k, 'details': v} for k, v in merged_dict.items()]
		
		for i in merged_list:
			emp_name_len = len(i['details'])
			first_row = i['details'][0]
			data += "<tr><td rowspan=%s>%s</td><td rowspan=%s>%s</td><td>%s</td></tr>" % (emp_name_len, first_row['project'], emp_name_len, i['project_name'], first_row['employee_id'])
			for j in range(1, emp_name_len): 
				data += "<tr><td>%s</td></tr>" % (i['details'][j]['employee_id'])
		data += '</table>'
		return data
	
@frappe.whitelist()
def get_project_details(company):
	project_list = []
	projects = frappe.get_all('Project',filters={'status':'Open', 'company': company},fields=['name','project_name','sales_order'])
	for project in projects:
		docstatus = frappe.db.get_value("Sales Order", project.sales_order, "docstatus")
		if docstatus == 1:
			project_list.append({
				'project': project.name,
				'project_name': project.project_name,
				'sales_order': project.sales_order,
			})
	
	return project_list

def test_check():
    return get_project_details("ENGINEERING DIVISION - ELECTRA")