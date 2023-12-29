# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from itertools import groupby
from operator import itemgetter

class MultiProjectDayPlan(Document):
	def on_submit(self):
		pdp = frappe.new_doc("Projects Timesheet")
		pdp.plan_date = self.plan_date
		pdp.company = self.company
		pdp.multi_project_day_plan = self.name
		for pdpe in self.project_day_plan_employee:
			pdp.append("project_day_plan_employee", {
					"project": pdpe.project,
					"project_name": pdpe.project_name,
					"employee": pdpe.employee,
					"employee_name": pdpe.employee_name,
					"designation": pdpe.designation,
					"from_time":"00:00:00",
					"to_time":"00:00:00",
					"lunch_break":"01:00:00",
					"total_working_hours":"00:00:00",
					"ot":"00:00:00"
				})
		pdp.save(ignore_permissions=True)

@frappe.whitelist()
def get_child_table_data(name):
	project_dict_list = []
	data = "<table border=1px class='table table-bordered'><tr><td style=width:50%><b>Project Name</b></td><td><b>Employee Name</b></td></tr>"
	tape = frappe.db.sql("""select project_name,employee_name from `tabProject Day Plan Child` where parent='%s'  """ %(name), as_dict=True)
	students = sorted(tape,
				  key = itemgetter('project_name'))
	for key, value in groupby(students,key = itemgetter('project_name')):
		for k in value:
			project_dict_list.append(k)
	merged_dict = {}
	for d in project_dict_list:
		if d['project_name'] in merged_dict:
			merged_dict[d['project_name']].append(d['employee_name'])
		else:
			merged_dict[d['project_name']] = [d['employee_name']]
	merged_list = [{'project_name': k, 'employee_name': v} for k, v in merged_dict.items()]		
	for i in merged_list:
		emp_name_len = len(i['employee_name'])
		data += "<tr><td rowspan = '%s' >%s</td><td>%s</td></tr>"%(emp_name_len,i['project_name'],i['employee_name'][0])
		for j in range(1,emp_name_len): 
			data += "<tr><td >%s</td></tr>"%(i['employee_name'][j])
	'</table>'    
	return data

@frappe.whitelist()
def get_driver_table_data(name):
	project_day_plan_driver_count = frappe.db.count("Project Day Plan Driver", filters={"parent": name})

	if project_day_plan_driver_count > 0:
		project_dict_list = []
		data = "<table border=1px class='table table-bordered'><tr><td style=width:50%><b>Project Name</b></td><td><b>Employee Name</b></td></th>"
		tape = frappe.db.sql("""select project_name,employee_name from `tabProject Day Plan Driver` where parent='%s'  """ %(name), as_dict=True)
		students = sorted(tape,
					key = itemgetter('project_name'))
		for key, value in groupby(students,key = itemgetter('project_name')):
			for k in value:
				project_dict_list.append(k)
		merged_dict = {}
		for d in project_dict_list:
			if d['project_name'] in merged_dict:
				merged_dict[d['project_name']].append(d['employee_name'])
			else:
				merged_dict[d['project_name']] = [d['employee_name']]
		merged_list = [{'project_name': k, 'employee_name': v} for k, v in merged_dict.items()]		
		for i in merged_list:
			emp_name_len = len(i['employee_name'])
			data += "<tr><td rowspan = '%s' >%s</td><td>%s</td></tr>"%(emp_name_len,i['project_name'],i['employee_name'][0])
			for j in range(1,emp_name_len): 
				data += "<tr><td >%s</td></tr>"%(i['employee_name'][j])
		'</table>'    
		return data
	