# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from csv import writer
from inspect import getfile
from unicodedata import name
import frappe
from frappe.utils import cstr, add_days, date_diff, getdate
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file, upload
from frappe.model.document import Document
from datetime import datetime,timedelta,date,time
from frappe.utils import cint,today,flt,date_diff,add_days,add_months,date_diff,getdate,formatdate,cint,cstr
from numpy import unicode_
from frappe.utils import  formatdate
class AttendanceTemplate(Document):
	pass

@frappe.whitelist()
def get_template():
	args = frappe.local.form_dict

	if getdate(args.from_date) > getdate(args.to_date):
		frappe.throw(_("To Date should be greater than From Date"))

	w = UnicodeWriter()
	w = add_header(w)
	w = add_data(w, args)

	frappe.response['result'] = cstr(w.getvalue())
	frappe.response['type'] = 'csv'
	frappe.response['doctype'] = "Attendance"

def add_header(w):
	w.writerow(["ID","Employee", "Employee Name", "Attendance Date", "Status", "Company"])
	return w

def add_data(w, args):
	data = get_data(args)
	writedata(w, data)
	return w

@frappe.whitelist()
def get_data(args):
	employees = frappe.db.sql("""select * from `tabAttendance` where attendance_date between '%s' and '%s' and company = '%s' and docstatus = 0 ORDER BY employee,attendance_date ASC """%(args.from_date,args.to_date,args.company),as_dict= True)
	data = []
	for emp in employees:
		format_date = formatdate(emp.attendance_date, "dd-mm-yyyy")
		row = [
			emp.name,
   			emp.employee,
			emp.employee_name,
			format_date,
			"",
			emp.company
			]
		data.append(row)
	return data

@frappe.whitelist()
def writedata(w, data):
	for row in data:
		w.writerow(row)

@frappe.whitelist()    
def enqueue_create_attendance(from_date,to_date,company):
	frappe.enqueue(
		create_attendance, # python function or a module path as string
		queue="long", # one of short, default, long
		timeout=80000, # pass timeout manually
		is_async=True, # if this is True, method is run in worker
		now=False, # if this is True, method is run directly (not in a worker) 
		job_name='Attendance' + '' + company,
		from_date=from_date,
		to_date=to_date,
		company = company
	) 
	return 'OK'

@frappe.whitelist()    
def create_attendance(from_date,to_date,company):
	frappe.errprint("HI")
	dates = get_dates(from_date,to_date)
	for date in dates:
		employee = frappe.db.get_all('Employee',{'status':'Active','date_of_joining':['<=',from_date],'company':company},['*'])
		for emp in employee:
			hh = check_holiday(date,emp.name)
			if not hh:
				if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
					att = frappe.new_doc('Attendance')
					att.employee = emp.name
					att.status = 'Absent'
					att.attendance_date = date
					att.company = emp.company
					att.save(ignore_permissions=True)
					frappe.db.commit() 
					print(date)  

def get_dates(from_date,to_date):
	no_of_days = date_diff(add_days(to_date, 1), from_date)
	dates = [add_days(from_date, i) for i in range(0, no_of_days)]
	return dates

def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	if holiday:
		if holiday[0].weekly_off == 1:
			return "WW"
		else:
			return "HH"


@frappe.whitelist()    
def enqueue_upload(attach):
	frappe.enqueue(
		att_upload, # python function or a module path as string
		queue="long", # one of short, default, long
		timeout=80000, # pass timeout manually
		is_async=True, # if this is True, method is run in worker
		now=False, # if this is True, method is run directly (not in a worker) 
		job_name='Attendance Updation' + '' + attach,
		attach = attach
	) 
	return 'OK'

@frappe.whitelist()    
def att_upload(attach):
	filepath = get_file(attach)
	pps = read_csv_content(filepath[1])
	for pp in pps:
		if pp[0] != 'ID':
			if pp[4] not in ["Present","Absent"]:
				frappe.throw(_("Please check the {0} Attendance Status on {0}").format(pp[1],pp[3]))
	for pp in pps:
		if pp[0] != 'ID':
			att = frappe.get_doc('Attendance',{'name':pp[0]})
			att.status = pp[4]
			att.save(ignore_permissions=True)
			att.submit()
			frappe.db.commit() 
		

# @frappe.whitelist()    
# def att_upload_check(attach):
# 	filepath = get_file(attach)
# 	pps = read_csv_content(filepath[1])
# 	for pp in pps:
# 		if pp[0] != 'ID':
# 			if pp[4] not in ["Present","Absent"]:
# 				return "OK"
				# frappe.throw(_("Please check the {0} Attendance Status on {0}").format(pp[1],pp[3]))
				