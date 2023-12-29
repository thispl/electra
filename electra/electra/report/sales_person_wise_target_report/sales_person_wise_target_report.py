# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from six import string_types
import frappe
import json
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from frappe.utils import get_first_day, today, get_last_day, format_datetime, add_years, date_diff, add_days, getdate, cint, format_date,get_url_to_form
from frappe.utils import add_months, add_days, format_time, today, nowdate, getdate, format_date
from datetime import datetime, time, timedelta
import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint
from erpnext.setup.utils import get_exchange_rate

def execute(filters=None):
	columns, data = [] ,[]
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	column = [
		_('Sales Person') + ':Data:180',
	]

	Month_1= ["January"]
	Month_2 =["February"]
	Month_3 =["March"]
	Month_4 =["April"]
	Month_5 =["May"]
	Month_6 =["June"]
	Month_7 =["July"]
	Month_8 =["August"]
	Month_9 =["September"]
	Month_10 =["October"]
	Month_11 =["November"]
	Month_12 =["December"]
	

	if filters.month == "January":
		for s in Month_1:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')
		
	if filters.month == "February":
		for s in Month_2:
			column.append(_(s) + ':Currency:/200')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "March":
		for s in Month_3:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "April":
		for s in Month_4:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "May":
		for s in Month_5:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "June":
		for s in Month_6:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "July":
		for s in Month_7:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "August":
		for s in Month_8:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "September":
		for s in Month_9:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "October":
		for s in Month_10:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "November":
		for s in Month_11:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	if filters.month == "December":
		for s in Month_12:
			column.append(_(s) + ':Currency:/250')
		column.append(_("MTD Var1") + ':Currency:/200')
		column.append(_("MTD Var%") + ':Float:/200')
		column.append(_("YTD Var1") + ':Currency:/200')
		column.append(_("YTD Var%") + ':Float:/200')
		column.append(_("Pending SO") + ':Float:/200')
		column.append(_("Monthly Target") + ':Currency:/200')
		column.append(_("Target") + ':Currency:/200')

	return column

def get_data(filters):
	year = filters.year
	data = []
	target = 1000000
	if filters.sales_person:
		sp = frappe.get_all("Sales Person",{"name":filters.sales_person,},["*"])
	else:
		sp = frappe.get_all("Sales Person",{'name': ['!=', 'Sales Team']},["*"])
	for s in sp:
		if filters.month == "January":
			si_1 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-01-01"), (str(year)+"-01-31")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-01-01"),(str(year)+"-01-31"),filters.sales_person),as_dict=True)
			total_1 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_1:
				total_1 = total_1 + i.grand_total
			mt = round(target/12,2)
			row_1 = [s.name,round(total_1,2),mt-total_1,(total_1-mt)/mt*100,target-total_1,(total_1-target)/target*100,so_total,mt,target]
			
			total_1 = 0
			so_total = 0
			
			data.append(row_1)

		if filters.month == "February":
			si_2 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between",[(str(year)+"-02-01"), (str(year)+"-02-28")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-02-01"),(str(year)+"-02-28"),filters.sales_person),as_dict=True)
			total_2 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_2:
				total_2 = total_2 + i.grand_total
			mt = round(target/12,2)
			row_2 = [s.name,round(total_2,2),mt-total_2,(total_2-mt)/mt*100,target-total_2,(total_2-target)/target*100,so_total,mt,target]
			
			total_2 = 0
			so_total = 0
			data.append(row_2)

		if filters.month == "March":
			si_3 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-03-01"), (str(year)+"-03-31")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-03-01"),(str(year)+"-03-31"),filters.sales_person),as_dict=True)
			total_3 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_3:
				total_3 = total_3 + i.grand_total
			mt = round(target/12,2)
			row_3 = [s.name,round(total_3,2),mt-total_3,(total_3-mt)/mt*100,target-total_3,(total_3-target)/target*100,so_total,mt,target]
			
			total_3 = 0
			so_total = 0
			data.append(row_3)

		if filters.month == "April":
			si_1 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-04-01"), (str(year)+"-04-30")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-04-01"),(str(year)+"-04-30"),filters.sales_person),as_dict=True)
			total_1 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_1:
				total_1 = total_1 + i.grand_total
			mt = round(target/12,2)
			row_4 = [s.name,round(total_1,2),mt-total_1,(total_1-mt)/mt*100,target-total_1,(total_1-target)/target*100,so_total,mt,target]
			
			total_1 = 0
			so_total = 0
			data.append(row_4)

		if filters.month == "May":
			si_2 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-05-01"), (str(year)+"-05-31")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-05-01"),(str(year)+"-05-31"),filters.sales_person),as_dict=True)
			total_2 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_2:
				total_2 = total_2 + i.grand_total
			mt = round(target/12,2)
			row_5 = [s.name,round(total_2,2),mt-total_2,(total_2-mt)/mt*100,target-total_2,(total_2-target)/target*100,so_total,mt,target]
			
			total_2 = 0
			so_total = 0
			data.append(row_5)

		if filters.month == "June":
			si_3 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between",[(str(year)+"-06-01"), (str(year)+"-06-30")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-06-01"),(str(year)+"-06-30"),filters.sales_person),as_dict=True)
			total_3 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_3:
				total_3 = total_3 + i.grand_total

			mt = round(target/12,2)
			row_6 = [s.name,round(total_3,2),mt-total_3,(total_3-mt)/mt*100,target-total_3,(total_3-target)/target*100,so_total,mt,target]
			
			total_3 = 0
			so_total = 0
			data.append(row_6)

		if filters.month == "July":
			si_1 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-07-01"), (str(year)+"-07-31")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-07-01"),(str(year)+"-07-31"),filters.sales_person),as_dict=True)
			total_1 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_1:
				total_1 = total_1 + i.grand_total
			mt = round(target/12,2)
			row_7 = [s.name,round(total_1,2),mt-total_1,(total_1-mt)/mt*100,target-total_1,(total_1-target)/target*100,so_total,mt,target]
			
			total_1 = 0
			so_total = 0
			data.append(row_7)

		if filters.month == "August":
			si_2 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-08-01"), (str(year)+"-08-31")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-08-01"),(str(year)+"-08-31"),filters.sales_person),as_dict=True)
			total_2 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_2:
				total_2 = total_2 + i.grand_total
			mt = round(target/12,2)
			row_8 = [s.name,round(total_2,2),mt-total_2,(total_2-mt)/mt*100,target-total_2,(total_2-target)/target*100,so_total,mt,target]
			
			total_2 = 0
			so_total = 0
			data.append(row_8)

		if filters.month == "September":
			si_3 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-09-01"), (str(year)+"-09-30")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-09-01"),(str(year)+"-09-30"),filters.sales_person),as_dict=True)
			total_3 = 0
			so_total = 0
			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_3:
				total_3 = total_3 + i.grand_total
			mt = round(target/12,2)
			row_9 = [s.name,round(total_3,2),mt-total_3,(total_3-mt)/mt*100,target-total_3,(total_3-target)/target*100,so_total,mt,target]
			
			total_3 = 0
			so_total = 0
			data.append(row_9)

		if filters.month == "October":
			si_1 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-10-01"), (str(year)+"-10-31")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-10-01"),(str(year)+"-10-31"),filters.sales_person),as_dict=True)
			total_1 = 0
			so_total = 0
			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_1:
				total_1 = total_1 + i.grand_total
			mt = round(target/12,2)
			row_10 = [s.name,round(total_1,2),mt-total_1,(total_1-mt)/mt*100,target-total_1,(total_1-target)/target*100,so_total,mt,target]
			
			total_1 = 0
			so_total = 0
			data.append(row_10)

		if filters.month == "November":
			si_2 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between",[(str(year)+"-11-01"), (str(year)+"-11-30")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-11-01"),(str(year)+"-11-30"),filters.sales_person),as_dict=True)
			total_2 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_2:
				total_2 = total_2 + i.grand_total
			mt = round(target/12,2)
			row_11 = [s.name,round(total_2,2),mt-total_2,(total_2-mt)/mt*100,target-total_2,(total_2-target)/target*100,so_total,mt,target]
			
			total_2 = 0
			so_total = 0
			data.append(row_11)

		if filters.month == "December":
			si_3 = frappe.get_all("Sales Invoice",{"sales_person_user":filters.sales_person,"posting_date": ["between", [(str(year)+"-12-01"), (str(year)+"-12-31")]]},["*"])
			so_1 = frappe.db.sql(""" select grand_total ,currency from `tabSales Order` where transaction_date between '%s' and '%s' and sales_person_user = '%s' and status != "Completed" """ %((str(year)+"-12-01"),(str(year)+"-12-31"),filters.sales_person),as_dict=True)
			total_3 = 0
			so_total = 0

			for i in so_1:
				so_total = so_total + i.grand_total

			for i in si_3:
				total_3 = total_3 + i.grand_total
			mt = round(target/12,2)
			row_12 = [s.name,round(total_3,2),mt-total_3,(total_3-mt)/mt*100,target-total_3,(total_3-target)/target*100,so_total,mt,target]
			
			total_3 = 0
			so_total = 0
			data.append(row_12)

	return data

