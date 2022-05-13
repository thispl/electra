# Copyright (c) 2013, Abdulla and contributors
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
from frappe.utils import cstr, cint, getdate

def execute(filters=None):
	columns, data = [] ,[]
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	column = [
		_('Supplier') + ':Data:250',
		_('Company') + ':Data:250',
		_('Requested Amount') + ':Currency:150',
		_('Paid Amount') + ':Currency:150',
		_('Outstandings') + ':Currency:150',
	]
	return column

def get_data(filters):
	data = []
	if not filters:
		supplier = frappe.get_all("Supplier")
	if filters:
		supplier = frappe.get_all("Supplier",{"name":filters.supplier})
	for i in supplier:
		if not filters:
			company = frappe.get_all("Company")
		if filters:
			company = frappe.get_all("Company",{"name":filters.company})
		for c in company:
			# pi = frappe.get_all("Purchase Invoice")
			pi = frappe.db.sql(""" select sum(rounded_total) as rounded_total from `tabPurchase Invoice` where supplier = '%s' and company = '%s' """%(i.name,c.name),as_dict=True)[0] or 0
			pe = frappe.db.sql(""" select sum(paid_amount) as paid_amount from `tabPayment Entry` where party_name = '%s' and company = '%s' and payment_type = 'Pay' """%(i.name,c.name),as_dict=True)[0] or 0
			if not pi["rounded_total"]:
				pi["rounded_total"] = 0
			if not pe["paid_amount"]:
				pe["paid_amount"] = 0
			row = [i.name,c.name,pi["rounded_total"],pe["paid_amount"],pi["rounded_total"] - pe["paid_amount"]]
			data.append(row)
	return data	