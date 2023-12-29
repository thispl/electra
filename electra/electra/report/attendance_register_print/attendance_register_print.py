# # Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt

# from __future__ import unicode_literals
# from functools import total_ordering
# from itertools import count
# import frappe
# from frappe import permissions
# from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
# from frappe.utils import cstr, add_days, date_diff, getdate, format_date
# from math import floor
# from frappe import msgprint, _
# from calendar import month, monthrange
# from datetime import date, timedelta, datetime,time
# from numpy import true_divide
# import pandas as pd

# status_map = {
# 	'On Duty':'OD',
# 	'Half Day':'HD',
# 	"Absent": "A",
# 	"Holiday": "HH",
# 	"Weekly Off": "WW",
# 	"Present": "P",
# 	"On Leave":"On Leave",
# 	"Work From Home" : "WFH",
# 	"Leave Without Pay" : "LWP",
# 	"Annual Leave" : "AL",
# 	"Emergency Leave" : "EML",
# 	"Marriage Leave" : "MAL",
# 	"Maternity Leave" :'MTL',
# 	"Medical Leave" : 'ML',
# 	"Sick Leave" : "SL",
# 	"Hajj/Umrah" : "HA/U L",
# 	"Hajj Leave" : "HL",
# 	"Casual Leave" : "CL",
# 	"Compensatory Off" : "C-OFF",
# 	"Privilege Leave" : "PL"
# }
# def execute(filters=None):
# 	columns = get_columns(filters)
# 	data = get_data(filters)
# 	return columns, data

# def get_columns(filters):
# 	columns = []
# 	columns += [
# 		_("Employee ID") + ":Data/:140",
# 		_("Employee Name") + ":Data/:200",
# 		# _("Department") + ":Data/:140",
# 		# _("Designation") + ":Data/:140",
# 		# _("DOJ") + ":Date/:100",
# 	]
# 	dates = get_dates(filters.from_date,filters.to_date)
# 	for date in dates:
# 		date = datetime.strptime(date,'%Y-%m-%d')
# 		day = datetime.date(date).strftime('%d')
# 		month = datetime.date(date).strftime('%b')
# 		columns.append(_(day + '/' + month) + ":Data/:65")
# 	columns.append(_("Present") + ":Data/:75")
# 	columns.append(_('Half Day') +':Data/:75')
# 	columns.append(_("Absent") + ":Data/:75")
# 	columns.append(_("On Leave")+ ':Data/:75')
# 	# columns.append(_("LWP")+ ':Data/:75')
# 	# columns.append(_("AL")+ ':Data/:75')
# 	# columns.append(_("EML")+ ':Data/:75')
# 	# columns.append(_("Mar L")+ ':Data/:75')
# 	# columns.append(_("Mat L")+ ':Data/:75')
# 	# columns.append(_("Med L")+ ':Data/:75')
# 	# columns.append(_("SL")+ ':Data/:75')
# 	# columns.append(_("Hajj/Umrah")+ ':Data/:75')
# 	# columns.append(_("Hajj Leave")+ ':Data/:75')
# 	# columns.append(_("CL")+ ':Data/:75')
# 	# columns.append(_("C Off")+ ':Data/:75')
# 	# columns.append(_("P L")+ ':Data/:75')
	

# 	return columns

# def get_data(filters):
# 	data = []
# 	emp_status_map = []
# 	employees = get_employees(filters)
# 	for emp in employees:
# 		frappe.errprint(emp.name)
# 		dates = get_dates(filters.from_date,filters.to_date)
# 		row1 = [emp.name,emp.employee_name]
# 		total_present = 0
# 		total_half_day = 0
# 		total_absent = 0
# 		total_onleave = 0
# 		total_holiday = 0
# 		total_weekoff = 0
# 		total_al = 0
# 		total_mdl = 0
# 		total_haul = 0
# 		total_cl = 0
# 		total_hl = 0
# 		total_eml = 0
# 		total_mal = 0
# 		total_mtl = 0
# 		total_sl = 0
# 		total_cof = 0
# 		total_lwp = 0
# 		total_pl = 0
# 		for date in dates:
# 			att = frappe.db.get_value("Attendance",{'attendance_date':date,'employee':emp.name,'docstatus':1},['status','employee','attendance_date','leave_type']) or ''
# 			if att:
# 				status = status_map.get(att[0], "")
# 				leave = status_map.get(att[3], "")
# 				if status == 'P':
# 					hh = check_holiday(date,emp.name)
# 					if hh :
# 						if hh == 'WW':
# 							row1.append('WW/P')
# 						elif hh == 'HH':
# 							row1.append('HH/P')   
# 					else:  
# 						row1.append(status or "-")
# 						total_present = total_present + 1  
# 				elif status == 'A':
# 					hh = check_holiday(date,emp.name)
# 					if hh:
# 						if hh == 'WW':
# 							row1.append('WW/A')
# 						elif hh == 'HH':
# 							row1.append('HH/A')
# 					else: 
# 						row1.append(status or '-') 
# 						total_absent = total_absent + 1
# 				elif status == 'WFH':
# 					hh = check_holiday(date,emp.name)
# 					if hh:
# 						if hh == 'WW':
# 							row1.append('WW/WFH')
# 						elif hh == 'HH':
# 							row1.append('HH/WFH')
# 					else: 
# 						row1.append(status or '-') 
# 						total_present = total_present + 1 
# 				elif status == 'HD':
# 					hh = check_holiday(date,emp.name)
# 					if hh:
# 						if hh == 'WW':
# 							row1.append('WW/HD')
# 							total_half_day += 1
# 						elif hh == 'HH':
# 							row1.append('HH/HD')
# 							total_half_day += 1
# 					else:
# 						if leave == "LWP":
# 							row1.append( 'HD/' + "V" or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_lwp += 0.5
# 						if leave  == "AL":
# 							row1.append( 'HD/' + "V" or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_al += 0.5
# 						if leave  == "EML":
# 							row1.append( 'HD/' + "V" or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_eml += 0.5
# 						if leave  == "MAL":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_mal += 0.5
# 						if leave  == "MTL":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_mtl += 0.5
# 						if leave  == "ML":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_mdl += 0.5
# 						if leave  == "SL":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_sl += 0.5
# 						if leave  == "HA/U L":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_haul += 0.5
# 						if leave  == "HL":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_hl += 0.5
# 						if leave  == "CL":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_cl += 0.5
# 						if leave  == "C-OFF":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_cof += 0.5
# 						if leave  == "PL":
# 							row1.append( 'HD/' + leave or '-')
# 							total_half_day += 1
# 							total_onleave += 0.5
# 							total_pl += 0.5
# 						else:
# 							row1.append(status or '-') 
# 							total_half_day += 1			
# 				elif status == 'On Leave':
# 					if leave  == "LWP":
# 						row1.append("V" or '-')
# 						total_onleave += 1
# 						total_lwp += 1
# 					if leave  == "AL":
# 						row1.append("V" or '-')
# 						total_onleave += 1
# 						total_al += 1
# 					if leave  == "EML":
# 						row1.append("V" or '-')
# 						total_onleave += 1
# 						total_eml += 1
# 					if leave  == "MAL":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_mal += 1
# 					if leave  == "MTL":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_mtl += 1
# 					if leave  == "ML":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_mdl += 1
# 					if leave  == "SL":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_sl += 1
# 					if leave  == "HA/U L":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_haul += 1
# 					if leave  == "HL":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_hl += 1
# 					if leave  == "CL":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_cl += 1
# 					if leave  == "C-OFF":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_cof += 1
# 					if leave  == "PL":
# 						row1.append(leave or '-')
# 						total_onleave += 1
# 						total_pl += 1
# 			else:
# 				hh = check_holiday(date,emp.name)
# 				if hh :
# 					if hh == 'WW': 
# 						total_weekoff += 1
# 					elif hh == 'HH':
# 						total_holiday += 1
# 					else:
# 						hh = '-'
# 					row1.append(hh)
# 				else:
# 					row1.append('-')
				
# 		row1.extend([
# 			total_present,
# 			total_half_day,
# 			total_absent,
# 			total_onleave,
# 			# total_lwp,
# 			# total_al,
# 			# total_eml,
# 			# total_mal,
# 			# total_mtl,
# 			# total_mdl,
# 			# total_sl,
# 			# total_haul,
# 			# total_hl,
# 			# total_cl,
# 			# total_cof,
# 			# total_pl
# 			])
# 		data.append(row1)
	   
# 	return data

# def get_dates(from_date,to_date):
# 	no_of_days = date_diff(add_days(to_date, 1), from_date)
# 	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
# 	return dates

# def get_employees(filters):
# 	conditions = ''
# 	left_employees = []
# 	if filters.employee:
# 		conditions += "and employee = '%s' " % (filters.employee)
# 	if filters.company:
# 		conditions += "and company = '%s' " % (filters.company)
# 	if filters.department:
# 		conditions+="and department = '%s' "%(filters.department)
# 	employees = frappe.db.sql("""select name, employee_name, department, designation ,date_of_joining,holiday_list,company from `tabEmployee` where status = 'Active' %s ORDER BY name""" % (conditions), as_dict=True)
# 	left_employees = frappe.db.sql("""select name, employee_name, department, designation, date_of_joining,company from `tabEmployee` where status = 'Left' and relieving_date >= '%s' %s ORDER BY name""" %(filters.from_date,conditions),as_dict=True)
# 	employees.extend(left_employees)
# 	return employees

# def check_holiday(date,emp):
# 	holiday_list = frappe.db.get_value('Employee',{'name':emp},'holiday_list')
# 	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
# 	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
# 	doj= frappe.db.get_value("Employee",{'name':emp},"date_of_joining")
# 	status = ''
# 	if holiday :
# 		if doj < holiday[0].holiday_date:
# 			if holiday[0].weekly_off == 1:
# 				status = "WW"     
# 			else:
# 				status = "HH"
# 		else:
# 			status = 'Not Joined'
# 	return status
	




