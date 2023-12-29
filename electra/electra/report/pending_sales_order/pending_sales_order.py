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
		_("Sales Order") + ":Link/Sales Order:200",
		_("Date") + ":Date/:110",
		_("Customer") + ":Link/Customer:200",
		_("L.P.O.No") + ":Data/ :200",
		# _("Net Amount") + ":Currency/:100",
		_("Order Qty") + ":Float/:100",
		_("Delivered Qty") + ":Float/:100",
		_("Balance") + ":Float/:100",
		_("Cost") + ":Currency/:100",
		_("Value") + ":Currency/:100",
		# _("Profit") + ":Currency/:100" ,
		# _("Percentage") + ":Percentage/:100"
	]
	return columns
def get_data(filters):
	data = []
	total = 0
	sa = frappe.db.sql(""" select parent,qty,delivered_qty,rate from `tabSales Order Item` where `tabSales Order Item`.item_code = '%s' """ %(filters.item_code),as_dict=True)
	for i in sa:
		if i.qty == i.delivered_qty:
			pass
		else:
			sb = frappe.get_doc("Sales Order", i.parent)
			bal = i.qty - i.delivered_qty
			if sb.docstatus == 1:
				total = bal * i.rate
				row = [i.parent,sb.transaction_date,sb.customer,sb.po_no,i.qty,i.delivered_qty,bal,i.rate,total]
				data.append(row)
	return data	