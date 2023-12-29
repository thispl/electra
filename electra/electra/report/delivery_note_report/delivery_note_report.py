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
		_("Delivery Note") + ":Link/Delivery Note:200",
		_("Against Sales Order") + ":Link/Sales Order:200",
		_("Date") + ":Date/:95",
		_("Customer") + ":Link/Customer:150",
		_("Address") + ":Data/:150",
		_("Phone No") + ":Data/:150",
		_("Customer's PO No.") + ":Data/:160",
		_("Sales Person") + ":Data/:170",
		_("Discount Amount") + ":Currency/:100",
		_("Net Amount") + ":Currency/:100",
		_("Status") + ":Data/:100",
		_("Prepared By") + ":Data/:170"
	]
	return columns

def get_data(filters):
	data = []
	delivery_note = frappe.db.get_all("Delivery Note",{'company':filters.company,'status':filters.docstatus,"dummy_dn":filters.dummy_dn,"posting_date":('between',(filters.from_date,filters.to_date))},['*'])
	for i in delivery_note:
		if i.docstatus!=2:
			dn = frappe.get_doc("Delivery Note",i.name)
			for child in dn.items:
				row = [i.name,child.against_sales_order,i.posting_date,i.customer,i.address_display,i.mobile_no or i.contact_mobile,i.po_no,i.sales_person_user,i.discount_amount,i.net_total,i.status,i.prepared_by_username]
			data.append(row)
	return data