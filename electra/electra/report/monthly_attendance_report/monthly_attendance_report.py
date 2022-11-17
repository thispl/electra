# Copyright (c) 2013, Abdulla and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from select import select
from six.moves import range
from six import string_types
import frappe
import json
from frappe.utils import getdate, cint, add_months, date_diff, add_days, nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime
from datetime import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint, getdate
import pandas as pd
# from __future__ import unicode_literals
from functools import total_ordering
from itertools import count
import frappe
from frappe import permissions
from frappe.utils import cstr, cint, getdate, get_last_day, get_first_day, add_days
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from math import floor
from frappe import msgprint, _
from calendar import month, monthrange
from datetime import date, timedelta, datetime,time
from numpy import true_divide
import pandas as pd


def execute(filters=None):
    columns, data = [] ,[]
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters): 
    columns = [
        _('Emp ID') +':Link/Employee:70',
        _('Emp Name') +':Data:300',
		_('Payments Days') +':Data:150',
        _('Week Off') +':Data:150',
        _('Working Days') +':Data:150',
        _('Present Days') +':Data:150',
        _('Absent Days') +':Data:150'
    ]
    return columns

def get_data(filters):
    data = []
    if filters.employee:
        employee = frappe.db.get_all("Employee",{"status":"Active","name":filters.employee},['*'])
    elif filters.company:
        employee = frappe.db.get_all("Employee",{"status":"Active","company":filters.company},['*'])
    else:
        employee = frappe.db.get_all("Employee",{"status":"Active"},['*'])
    for emp in employee:
        present=0   
        absent=0
        on_leave=0
        weekoff= 0
        payment_days=0
        working_days=0
        paid_leave=0
        
        date_range = pd.date_range(filters.from_date,filters.to_date).tolist()
        from_date = filters.from_date
        to_date = filters.to_date
        
        holiday_list = frappe.db.exists('Holiday List',{'employee':emp.employee},['holiday_list'])

        
        if holiday_list:
            emp_holiday_list = holiday_list

        else:
            emp_holiday_list = frappe.get_value('Employee',emp.employee,'holiday_list')

        for d in date_range:
            payment_days+=1
            
            attendance = frappe.db.exists("Attendance",{'employee':emp.employee,"attendance_date":d})
            
            # frappe.errprint(attendance)
            if attendance:   
                # frappe.errprint(attendance)
                att = frappe.get_doc('Attendance',attendance)
                # frappe.errprint(att)

                if att.status=="Present" or att.status=="Work from Home":
                    present += 1    
                if att.status=="Absent":
                    absent += 1
                if att.status== "On Leave" :
                    on_leave +=1 
                if att.status== "On Leave" and att.leave_type!="Leave Without Pay":
                    paid_leave+=1
        
        # holiday = frappe.db.sql("""select * from `tabHoliday List`""",as_dict =1)
        holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
        left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date between '%s' and '%s' """%(emp_holiday_list,from_date,to_date),as_dict=True)
        for h in holiday:
            if h:
                if h.weekly_off >= 1:

                    weekoff += 1
        working_days=payment_days-weekoff  
        row = [emp.name,emp.employee_name,payment_days,weekoff,working_days,present,absent]
        data.append(row)
    return data    




   







