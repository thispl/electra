# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
import calendar
import math
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
class AdditionalSalaryTemplate(Document):
    pass

@frappe.whitelist()
@frappe.whitelist()
def get_template():
    args = frappe.local.form_dict
    w = UnicodeWriter()
    w = add_header(w, args)
    w = add_data(w, args)

    frappe.response['result'] = cstr(w.getvalue())
    frappe.response['type'] = 'csv'
    frappe.response['doctype'] = "Additional Salary"

def add_header(w,args):
    w.writerow(["Employee","Employee Name","Payroll Date","NOT Hours","HOT Hours","Previous Month Additionals","Others Additions","Loan Deduction","Other/ Advance Deduction","Previous Month Abs Detection","Mess Advance","Company"])
    return w

def add_data(w, args):
    data = get_data(args)
    writedata(w, data)
    return w

def get_data(args):
    employees = get_active_employees(args)
    data = []
    for employee in employees:
        doj = frappe.db.get_value("Employee",{"name":employee.employee},["date_of_joining"])
        camp_mess_deduction = frappe.db.get_value("Employee",{"name":employee.employee},["camp_mess_deduction"])
        payroll_date = datetime.strptime(args.payroll_date, '%Y-%m-%d').date()
        if doj > payroll_date:
            pd = doj
        else:
            pd = args.payroll_date
        if camp_mess_deduction==1:
            mess="250"
        else:
            mess="0"
        row = [employee.employee,employee.employee_name,pd,"0","0","0","0","0","0","0",mess,args.company]
        data.append(row)
        # doj = frappe.db.get_value("Employee",{"name":employee.employee},["date_of_joining"])
        # camp_mess_deduction = frappe.db.get_value("Employee",{"name":employee.employee},["camp_mess_deduction"])
        # payroll_date = datetime.strptime(args.payroll_date, '%Y-%m-%d').date()
        # if doj > payroll_date:
        # 	pd = doj
        # else:
        # 	pd = args.payroll_date
        # if camp_mess_deduction==1:
        # 	mess="250"
        # else:
        # 	mess="0"
        # # row = [employee.employee,employee.employee_name,pd,"0","0","0","0","0","0","0",mess,args.company]
        # row = [employee.employee,employee.employee_name,pd,"0","0","0","0","0","0","0",mess,args.company]
        # data.append(row)
    return data

@frappe.whitelist()
def writedata(w, data):
    for row in data:
        w.writerow(row)


@frappe.whitelist()
def get_active_employees(args):
    import calendar
    from datetime import datetime

    payroll_date = args.payroll_date
    payroll_date_obj = datetime.strptime(payroll_date, '%Y-%m-%d')

    start_date = payroll_date_obj.replace(day=1)
    last_day_of_month = calendar.monthrange(start_date.year, start_date.month)[1]
    end_date = start_date.replace(day=last_day_of_month)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    company = args.company
    employees = frappe.db.sql(
        """
        SELECT DISTINCT employee, employee_name 
        FROM `tabAttendance` 
        WHERE attendance_date BETWEEN %(start_date)s AND %(end_date)s 
        AND company = %(company)s 
        AND docstatus != 2
        ORDER BY employee ASC
        """,
        {
            'start_date': start_date_str,
            'end_date': end_date_str,
            'company': company
        },
        as_dict=True
    )

    return employees

import frappe
from frappe.utils.file_manager import get_file
from frappe.utils.csvutils import read_csv_content

def get_employee_working_and_payment_days(employee, payroll_date):
	"""Compute total_working_days and payment_days for an employee for the given payroll month,
	replicating the logic from Salary Slip's get_working_days_details."""
	from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
	from hrms.utils.holiday_list import get_holiday_dates_between

	pd = getdate(payroll_date)
	start_date = pd.replace(day=1)
	last_day = calendar.monthrange(start_date.year, start_date.month)[1]
	end_date = start_date.replace(day=last_day)

	payroll_settings = frappe.get_cached_value(
		"Payroll Settings",
		None,
		("payroll_based_on", "include_holidays_in_total_working_days", "daily_wages_fraction_for_half_day"),
		as_dict=1,
	)
	include_holidays = cint(payroll_settings.include_holidays_in_total_working_days)
	daily_wages_fraction_for_half_day = flt(payroll_settings.daily_wages_fraction_for_half_day) or 0.5

	holiday_list = get_holiday_list_for_employee(employee)
	holidays = []
	if holiday_list:
		holidays = get_holiday_dates_between(holiday_list, start_date, end_date)

	working_days = date_diff(end_date, start_date) + 1
	if not include_holidays:
		working_days -= len(holidays)
	total_working_days = working_days

	doj, relieving_date = frappe.db.get_value("Employee", employee, ["date_of_joining", "relieving_date"])

	actual_start = getdate(start_date)
	actual_end = getdate(end_date)
	if doj and getdate(doj) > actual_start:
		actual_start = getdate(doj)
	if relieving_date and getdate(relieving_date) < actual_end:
		actual_end = getdate(relieving_date)

	if actual_start > actual_end:
		return total_working_days, 0

	payment_days = date_diff(actual_end, actual_start) + 1
	if not include_holidays:
		period_holidays = [h for h in holidays if actual_start <= getdate(h) <= actual_end]
		payment_days -= len(period_holidays)

	if payroll_settings.payroll_based_on == "Attendance":
		leave_types = frappe.get_all(
			"Leave Type",
			or_filters={"is_ppl": 1, "is_lwp": 1},
			fields=["name", "is_lwp", "is_ppl", "fraction_of_daily_salary_per_leave", "include_holiday"],
		)
		leave_type_map = {lt.name: lt for lt in leave_types}

		attendance_details = frappe.get_all(
			"Attendance",
			filters={
				"employee": employee,
				"docstatus": 1,
				"status": ["in", ["Absent", "Half Day", "On Leave"]],
				"attendance_date": ["between", [start_date, end_date]],
			},
			fields=["attendance_date", "status", "leave_type"],
		)

		lwp = 0
		absent = 0
		for d in attendance_details:
			if d.status in ("Half Day", "On Leave") and d.leave_type and d.leave_type not in leave_type_map:
				continue

			if not include_holidays and getdate(d.attendance_date) in holidays:
				if d.status == "Absent" or (d.leave_type and d.leave_type in leave_type_map and not leave_type_map[d.leave_type]["include_holiday"]):
					continue

			if d.status == "Half Day":
				equivalent_lwp = 1 - daily_wages_fraction_for_half_day
				if d.leave_type in leave_type_map and leave_type_map[d.leave_type]["is_ppl"]:
					fraction = leave_type_map[d.leave_type].get("fraction_of_daily_salary_per_leave")
					equivalent_lwp *= (fraction if fraction else 1)
				lwp += equivalent_lwp
			elif d.status == "On Leave" and d.leave_type and d.leave_type in leave_type_map:
				equivalent_lwp = 1
				if leave_type_map[d.leave_type]["is_ppl"]:
					fraction = leave_type_map[d.leave_type].get("fraction_of_daily_salary_per_leave")
					equivalent_lwp *= (fraction if fraction else 1)
				lwp += equivalent_lwp
			elif d.status == "Absent":
				absent += 1

		current_year = datetime.now().year
		leave_apps = frappe.get_all(
			"Leave Application",
			filters={
				"employee": employee,
				"leave_type": "Medical Leave",
				"from_date": [">=", f"{current_year}-01-01"],
				"to_date": ["<=", f"{current_year}-12-31"],
				"docstatus": 1,
			},
			fields=["from_date", "to_date", "total_leave_days"],
			order_by="from_date asc",
		)

		allowed_limit = 15
		running_total = 0
		extra_in_period = 0
		slip_start = getdate(start_date)
		slip_end = getdate(end_date)

		for app in leave_apps:
			leave_start = getdate(app.get("from_date"))
			leave_end = getdate(app.get("to_date"))
			day = leave_start
			while day <= leave_end:
				running_total += 1
				if running_total > allowed_limit and slip_start <= day <= slip_end:
					extra_in_period += 1
				day += timedelta(days=1)

		medical_leave = extra_in_period / 2

		annual_leave = frappe.db.count("Attendance", {
			"employee": employee,
			"status": "On Leave",
			"attendance_date": ["between", [start_date, end_date]],
			"leave_type": "Annual Leave",
			"docstatus": 1,
		})

		if flt(payment_days) > flt(lwp):
			payment_days = flt(payment_days) - flt(lwp) - flt(medical_leave) - flt(absent) - flt(annual_leave)
		else:
			payment_days = 0
	else:
		from hrms.payroll.doctype.salary_slip.salary_slip import get_lwp_or_ppl_for_date_range
		working_days_list = [add_days(getdate(start_date), days=day) for day in range(0, date_diff(end_date, start_date) + 1)]
		if not include_holidays:
			working_days_list = [d for d in working_days_list if d not in holidays]
		leaves = get_lwp_or_ppl_for_date_range(employee, start_date, end_date)
		lwp = 0
		for d in working_days_list:
			if relieving_date and d > getdate(relieving_date):
				continue
			leave = leaves.get(d)
			if not leave:
				continue
			if not leave.include_holiday and getdate(d) in holidays:
				continue
			if leave.is_ppl:
				lwp += flt(leave.fraction_of_daily_salary_per_leave or 1)
			else:
				lwp += 1
		payment_days = flt(payment_days) - flt(lwp)

	if payment_days < 0:
		payment_days = 0

	return total_working_days, payment_days

@frappe.whitelist()
def create_additional_salary(filename,payroll_date,company):
    frappe.errprint(payroll_date)
    filepath = get_file(filename)
    pps = read_csv_content(filepath[1])
    for pp in pps:
        if pp[0] != 'Employee':
            if pp[2] is None or not pp[2].strip():
                frappe.throw(f"Missing or invalid date in file for employee: {pp[0]}")
            try:
                formatted_date = datetime.strptime(pp[2], "%d-%m-%Y").strftime("%Y-%m-%d")
            except ValueError:
                frappe.throw(f"Invalid date format for employee {pp[0]}: {pp[2]}. Expected format is DD-MM-YYYY.")


            if float(pp[3]) > 0:
                if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"NOT Hours",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                    add = frappe.new_doc('Additional Salary')
                    add.employee = pp[0]
                    add.company = company
                    add.employee_name=pp[1]
                    add.salary_component ="NOT Hours"
                    # add.payroll_date = payroll_date
                    # formatted_date = datetime.strptime(pp[2], "%Y-%m-%d")
                    # frappe.errprint(formatted_date)
                    add.payroll_date = formatted_date
                    gross = frappe.get_value("Employee",{'name':pp[0]},['basic'])
                    add.not_hours = pp[3]
                    total_working_days, payment_days = get_employee_working_and_payment_days(pp[0], payroll_date)
                    basic = (int(gross) / total_working_days) * payment_days
                    amount = ((basic) / 30 / 8) * float(pp[3]) * 1.25
                    add.amount = math.floor(amount)
                    add.type = "Earning"
                    add.save(ignore_permissions=True)
                    add.submit()
                    frappe.db.commit()
            if float(pp[4]) > 0:
                if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"HOT Hours",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                    add = frappe.new_doc('Additional Salary')
                    add.employee = pp[0]
                    add.employee_name=pp[1]
                    add.company = company
                    add.salary_component ="HOT Hours"
                    # add.payroll_date = payroll_date
                    # formatted_date = datetime.strptime(pp[2], "%Y-%m-%d")
                    frappe.errprint(formatted_date)
                    add.payroll_date = formatted_date
                    gross = frappe.get_value("Employee",{'name':pp[0]},['basic'])
                    add.hot_hours = pp[4]
                    total_working_days, payment_days = get_employee_working_and_payment_days(pp[0], payroll_date)
                    basic = (int(gross) / total_working_days) * payment_days
                    amount = ((basic) / 30 / 8) * float(pp[4]) * 1.5
                    add.amount = math.floor(amount)
                    add.type = "Earning"
                    add.save(ignore_permissions=True)
                    add.submit()
                    frappe.db.commit()
            if float(pp[5])>0:
                if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"Previous Month Additionals",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                    add = frappe.new_doc('Additional Salary')
                    add.employee = pp[0]
                    add.salary_component ="Absent Previous Month Additionals"
                    add.employee_name=pp[1]
                    add.company = company
                    # add.payroll_date = payroll_date
                    # formatted_date = datetime.strptime(pp[2], "%Y-%m-%d")
                    frappe.errprint(formatted_date)
                    add.payroll_date = formatted_date
                    add.amount = pp[5]
                    add.type = "Earning"
                    add.save(ignore_permissions=True)
                    add.submit()
                    frappe.db.commit()	
            if float(pp[6])>0:
                if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"Others Additions",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                    add = frappe.new_doc('Additional Salary')
                    add.employee = pp[0]
                    add.employee_name=pp[1]
                    add.company = company
                    add.salary_component ="Others Additions"
                    # add.payroll_date = payroll_date
                    # formatted_date = datetime.strptime(pp[2], "%Y-%m-%d")
                    frappe.errprint(formatted_date)
                    add.payroll_date = formatted_date
                    add.amount = round(float(pp[6]))
                    add.type = "Earning"
                    add.save(ignore_permissions=True)
                    add.submit()
                    frappe.db.commit()
            if float(pp[7])>0:
                if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"Loan Deduction",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                    add = frappe.new_doc('Additional Salary')
                    add.employee = pp[0]
                    add.employee_name=pp[1]
                    add.company = company
                    add.salary_component ="Loan Deduction"
                    # add.payroll_date = payroll_date
                    # formatted_date = datetime.strptime(pp[2], "%Y-%m-%d")
                    frappe.errprint(formatted_date)
                    add.payroll_date = formatted_date
                    add.amount = round(float(pp[7]))
                    add.type = "Deduction"
                    add.save(ignore_permissions=True)
                    add.submit()
                    frappe.db.commit()
            if float(pp[8])>0:
                if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"Other/ Advance Deduction",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                    add = frappe.new_doc('Additional Salary')
                    add.employee = pp[0]
                    add.company = company
                    add.employee_name=pp[1]
                    add.salary_component ="Other/ Advance Deduction"
                    # add.payroll_date = payroll_date
                    # formatted_date = datetime.strptime(pp[2], "%Y-%m-%d")
                    frappe.errprint(formatted_date)
                    add.payroll_date = formatted_date
                    add.amount = round(float(pp[8]))
                    add.type = "Deduction"
                    add.save(ignore_permissions=True)
                    add.submit()
                    frappe.db.commit()
            if float(pp[9])>0:
                if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"Previous Month Abs Detection",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                    add = frappe.new_doc('Additional Salary')
                    add.employee = pp[0]
                    add.employee_name=pp[1]
                    add.company = company
                    # add.payroll_date = payroll_date
                    # formatted_date = datetime.strptime(pp[2], "%Y-%m-%d")
                    frappe.errprint(formatted_date)
                    add.payroll_date = formatted_date
                    add.salary_component ="Previous Month Abs Detection"			
                    add.no_of_days_absent_in_previous_month = pp[9]
                    gross = frappe.get_value("Employee",{'name':pp[0]},['gross_salary'])
                    per_day_amount = int(gross) / 30
                    tot_amount = float(per_day_amount) * float(pp[9])
                    add.amount = round(int(tot_amount))		
                    add.type = "Deduction"
                    add.save(ignore_permissions=True)
                    add.submit()
                    frappe.db.commit()
            if float(pp[10])>0:
                if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"Mess Advance",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                # if not frappe.db.exists("Additional Salary", {'employee': pp[0],'salary_component':"Mess Advance",'payroll_date': payroll_date,'company':company,'docstatus': ('!=',2)}):
                    add = frappe.new_doc('Additional Salary')
                    add.employee = pp[0]
                    add.company = company
                    add.employee_name=pp[1]
                    add.salary_component = "Mess Advance"
                    # add.payroll_date = payroll_date
                    # formatted_date = datetime.strptime(pp[2], "%Y-%m-%d")
                    frappe.errprint(formatted_date)
                    add.payroll_date = formatted_date
                    add.amount = round(float(pp[10]))
                    add.type = "Deduction"
                    add.save(ignore_permissions=True)
                    add.submit()
                    frappe.db.commit()
    return "OK"
