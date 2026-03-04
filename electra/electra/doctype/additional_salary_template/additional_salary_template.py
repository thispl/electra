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
                    amount = (int(gross)/ 30 / 8) * float(pp[3]) * 1.25
                    add.amount = round(amount)
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
                    amount = (int(gross)/ 30 / 8) * float( pp[4]) * 1.5
                    add.amount = round(amount)
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
