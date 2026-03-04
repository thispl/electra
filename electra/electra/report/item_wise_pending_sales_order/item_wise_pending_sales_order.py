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
        _("Order Qty") + ":Data/:100",
        _("Delivered Qty") + ":Data/:100",
        _("Balance") + ":Data/:100",
        _("Cost") + ":Currency/:100",
        _("Value") + ":Currency/:100",
        # _("Profit") + ":Currency/:100" ,
        # _("Percentage") + ":Percentage/:100"
    ]
    return columns


def get_data(filters):
	data = []
	total = 0
	sa = frappe.get_list("Sales Order", {"transaction_date": ('between', (filters.from_date, filters.to_date)), "status": ('!=', "Closed"),"docstatus":1}, ["name", "transaction_date", "customer", "po_no"])
	for so in sa:
		sb = frappe.get_all("Sales Order Item", {"parent": so.name, "item_code": filters.item_code}, ["qty", "delivered_qty", "rate"])
		for j in sb:
			if j.qty == j.delivered_qty:
				continue
			else:
				bal = j.qty - j.delivered_qty
				total = bal * j.rate
				row = [so.name, so.transaction_date, so.customer,so.po_no,round(j.qty,2), round(j.delivered_qty,2),round(bal,2), round(j.rate,2), round(total,2)]
				data.append(row)

	return data