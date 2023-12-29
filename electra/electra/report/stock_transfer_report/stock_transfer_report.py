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
		_("Date") + ":Date/:110",
		_("Stock Request") + ":Link/Stock Request:200",
		_("Stock Transfer") + ":Link/Stock Transfer:200",
        _("Transfer From") + ":Data:200",
		_("Transfer To") + ":Data:200",
		_("Status") + ":Data:200",
        _("Remarks") + ":Data:200",
        _("Amount") + ":100"
	]
	return columns

def get_data(filters):
	data = []
	sa = []
	if filters.is_checked == 1:
		frappe.errprint('hi')
		if filters.from_company:
			from_len = str(filters.get('from_company'))
			from_company = tuple(filters.get('from_company'))
			from_com = ''.join(from_len)
			fromcompany = from_com.replace('[', '(').replace(']', ')')
			sa = frappe.db.sql(""" select * from `tabStock Transfer` where transferred_date between '%s' and '%s' and source_company in %s and  workflow_state ='Transferred' """%(filters.from_date,filters.to_date,fromcompany),as_dict=True)

			if sa:
				for i in sa:
					amt = frappe.db.get_value('Sales Invoice',{'stock_transfer_numner':i.name},['grand_total'])
					row = [i.transferred_date,i.ic_material_transfer_request,i.name,i.source_company,i.target_company,i.workflow_state,i.remarks,amt]
					data.append(row)
			return data
	else:
		frappe.errprint('hiiiii')
		if filters.from_company and filters.to_company:
			from_len = str(filters.get('from_company'))
			to_len = str(filters.get('to_company'))
			from_company = tuple(filters.get('from_company'))
			to_company = tuple(filters.get('to_company'))
			from_com = ''.join(from_len)
			fromcompany = from_com.replace('[', '(').replace(']', ')')
			to_com = ''.join(to_len)
			tocompany = to_com.replace('[', '(').replace(']', ')')
			sa = frappe.db.sql(""" select * from `tabStock Transfer` where transferred_date between '%s' and '%s' and source_company in %s and target_company in %s and workflow_state ='Transferred' """%(filters.from_date,filters.to_date,fromcompany,tocompany),as_dict=True)
			if sa:
				for i in sa:
					amt = frappe.db.get_value('Sales Invoice',{'stock_transfer_numner':i.name},['grand_total'])
					row = [i.transferred_date,i.ic_material_transfer_request,i.name,i.source_company,i.target_company,i.workflow_state,i.remarks,amt]
					data.append(row)
			return data