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
	columns = [
		_("Sl No.Date") + ":Date:200",
		_("Transfer No") + ":Link/Stock Transfer:200",
		_("Stock Request No") + ":Link/Stock Request:200",
		_("From Company") + ":Link/Company:200",
		_("To Company") + ":Link/Company:200",
		_("Remarks") + ":Small Text:100",
		_("Amount") + ":Currency:100"
	]
	return columns

def get_data(filters):
	data = []
	if filters.from_date:
		sa = frappe.db.sql("""SELECT * FROM `tabStock Confirmation` WHERE source_company = '%s'and target_company = '%s' and requested_date BETWEEN '%s' AND '%s' """ %(filters.source_company, filters.target_company, filters.from_date, filters.to_date), as_dict=True)
	else:
		sa = frappe.db.sql("""SELECT * FROM `tabStock Transfer`
							WHERE source_company = '%s' AND target_company = '%s'""" %
							(filters.source_company, filters.target_company), as_dict=True)
	for i in sa:
		sb = frappe.get_value('Sales Invoice',
							  {"stock_transfer_numner": i.name},
							  ['grand_total'])
		row = [i.requested_date, i.name, i.ic_material_transfer_request,
			   i.source_company, i.target_company, i.remarks, sb]
		data.append(row)

	return data


