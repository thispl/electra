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
        _("Transfer From - Company") + ":Data:250",
		_("Transfer From - Warehouse") + ":Data:250",
        _("Transfer To - Company") + ":Data:250",
		_("Transfer To - Warehouse") + ":Data:250",
		_("Status") + ":Data:100",
        _("Amount") + ":Currency:150",
		_("Remarks") + ":Data:200"
	]
	return columns

def get_data(filters):
	data = []
	sa = []
	if filters.is_checked == 1:
		if filters.from_company:
			from_len = str(filters.get('from_company'))
			from_company = tuple(filters.get('from_company'))
			from_com = ''.join(from_len)
			fromcompany = from_com.replace('[', '(').replace(']', ')')
			sa = frappe.db.sql(""" select * from `tabStock Transfer` where transferred_date between '%s' and '%s' and source_company in %s and  workflow_state ='Transferred' """%(filters.from_date,filters.to_date,fromcompany),as_dict=True)
			mr_list = []
			if sa:
				for i in sa:
					si_name = frappe.db.get_value("Sales Invoice",{'stock_transfer_numner':i.name,'docstatus':1},['name'])
					from_wh = frappe.db.get_value("Sales Invoice Item",{'parent':si_name},['warehouse'])

					stc = frappe.db.get_value("Stock Confirmation",{'ic_material_transfer_confirmation':i.name},['name'])
					pi_name = frappe.db.get_value("Purchase Invoice",{'confirmation_number':stc,'docstatus':1},['name'])
					to_wh = frappe.db.get_value("Purchase Invoice Item",{'parent':pi_name},['warehouse'])


					amt = frappe.db.get_value('Sales Invoice',{'stock_transfer_numner':i.name,'docstatus':1},['grand_total'])
					# frappe.log_error('amt',amt)
					amt = round(amt, 2) if amt is not None else 0
					mr_list.append(i.ic_material_transfer_request)
					row = [i.transferred_date,i.ic_material_transfer_request,i.name,i.source_company,from_wh,i.target_company,to_wh,i.workflow_state,amt,i.remarks]
					data.append(row)
			return data
	else:
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
					si_name = frappe.db.get_value("Sales Invoice",{'stock_transfer_numner':i.name,'docstatus':1},['name'])
					from_wh = frappe.db.get_value("Sales Invoice Item",{'parent':si_name},['warehouse'])
					amt = frappe.db.get_value('Sales Invoice',{'stock_transfer_numner':i.name,'docstatus':1},['grand_total'])

					stc = frappe.db.get_value("Stock Confirmation",{'ic_material_transfer_confirmation':i.name},['name'])
					pi_name = frappe.db.get_value("Purchase Invoice",{'confirmation_number':stc,'docstatus':1},['name'])
					to_wh = frappe.db.get_value("Purchase Invoice Item",{'parent':pi_name},['warehouse'])
					row = [i.transferred_date,i.ic_material_transfer_request,i.name,i.source_company,from_wh,i.target_company,to_wh,i.workflow_state,round(amt,2),i.remarks]
					data.append(row)
			return data