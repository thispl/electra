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
		_("Quotation") + ":Link/Quotation:200",
		_("Date") + ":Date/:95",
		_("Customer") + ":Data/:150",
		_("Phone No") + ":Data/:150",
		_("Enquiry Ref. No.") + ":Data/:100",
		_("Required Date") + ":Date/:100",
		_("Sales Person") + ":Data/:170",
		_("Discount Amount") + ":Currency/:100",
		_("Net Amount") + ":Currency/:100",
		_("Status") + ":Data/:100",
		_("Prepared By") + ":Data/:170",
		_("Project") + ":Data/:170",

	]
	return columns

def get_data(filters):
	data = []
	row = []
	if filters.valid_from_date:
		quotation = frappe.db.get_all("Quotation",{'company':filters.company,'order_type':filters.order_type,'status':filters.docstatus,"transaction_date":('between',(filters.from_date,filters.to_date)),"valid_till":('between',(filters.valid_from_date,filters.valid_to_date))},['*'])
	else:
		quotation = frappe.db.get_all("Quotation",{'company':filters.company,'order_type':filters.order_type,'status':filters.docstatus,"transaction_date":('between',(filters.from_date,filters.to_date))},['*'])
		for i in quotation:
			if i.status != "Cancelled":
				row = [i.name,i.transaction_date,i.party_name,i.mobile_no or i.contact_mobile,i.enquiry_reference_no,i.valid_till,i.converted_by,i.discount_amount,i.net_total,i.status,i.user_name]
				project_name = frappe.db.get_value("Sales Order", {'quotation': i.name}, 'project')
				row += [project_name]
				data.append(row)
	return data