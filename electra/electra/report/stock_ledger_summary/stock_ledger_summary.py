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
		_('Item') + ':Data:150',
		_('Date') + ':Data:100',
		_('Outward') + ':Data:100',
		_('Outward') + ':Data:100',
	]
	return column

def get_data(filters):
	data = []
	dn = frappe.db.sql(""" select `tabDelivery Note Item`.qty as qty ,`tabDelivery Note`.name as name,`tabDelivery Note`.posting_date as posting_date from `tabDelivery Note` left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent where `tabDelivery Note`.posting_date between '%s' and '%s' and `tabDelivery Note Item`.item_code = '%s'  """ %(filters.from_date,filters.to_date,filters.item),as_dict=True)
	for i in dn:
		# si = frappe.db.sql(""" select `tabSales Invoice Item`.qty as qty ,`tabSales Invoice`.name as name,`tabSales Invoice`.posting_date as posting_date from `tabSales Invoice` left join `tabSales Invoice Item` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent where `tabSales Invoice`.posting_date between '%s' and '%s' and `tabSales Invoice Item`.item_code = '%s'  """ %(filters.from_date,filters.to_date,filters.item),as_dict=True)
		# frappe.errprint(si)
		# for s in si:
		row = [i.name,i.posting_date,i.qty]
		data.append(row)
	return data	