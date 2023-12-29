# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Sales Person") + ":Data/:110",
        _("Total") + ":100",
        _("Total") + ":100",
        _("Total") + ":100",
	]
	return columns

def get_data(filters):
	data = []
	row = []

	if filters.type:
		stock = frappe.db.sql(""" select sales_person_user,sum(grand_total) as total from `tabSales Invoice` where posting_date between '%s' and '%s'  group by sales_person_user """%("2023-01-01","2023-01-31"),as_dict=1)
		for i in stock:
			row += [i.sales_person_user,i.total]
			data.append(row)
		# stoc = frappe.db.sql(""" select sales_person_user,sum(grand_total) as total from `tabSales Invoice` where posting_date between '%s' and '%s'  group by sales_person_user """%("2023-02-01","2023-02-29"),as_dict=1)
		# for s in stoc:
		# 	row += [s.total]
		# 	data.append(row)
		# sto = frappe.db.sql(""" select sales_person_user,sum(grand_total) as total from `tabSales Invoice` where posting_date between '%s' and '%s'  group by sales_person_user """%("2023-03-01","2023-03-31"),as_dict=1)
		# for a in sto:
		# 	row += [a.total]
		# 	data.append(row)
		# data.append(row)
	return data
