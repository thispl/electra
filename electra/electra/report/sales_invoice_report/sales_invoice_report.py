# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext



def execute(filters=None):
	columns =[]
	data = []
	columns += [
		_("Sales Invoice") + ":Link/Sales Invoice:200",
		_("Date") + ":Date/:95",
		_("Customer") + ":Link/Customer:150",
        _("Sales Person") + ":Link/Sales Person:150",
		_("Discount Amount") + ":Currency/:100",
		_("Net Amount") + ":Currency/:100",
		_("Invoice Type") + ":Data/:100",
		_("Status") + ":Data/:100",
		_("Prepared By") + ":Data/:170"
	]
	data = get_invoice_data(filters)
	return columns, data

def get_invoice_data(filters):
	data =[]
	conditions = build_conditions(filters)
	query = """SELECT * FROM `tabSales Invoice` WHERE {conditions}""".format(conditions=conditions)
	sales = frappe.db.sql(query, as_dict=True)
	for i in sales:
		if i.status not in ['Draft','Cancelled']:
			emp_name = frappe.db.get_value("User",i.prepared_by,['full_name'])
			dn = frappe.get_doc("Sales Invoice",i.name)
			frappe.errprint("hi")
			for child in dn.items:
				row = [i.name,i.posting_date,i.customer,i.sales_person_user,i.discount_amount,i.grand_total,i.invoice_type,i.status,emp_name]
			data.append(row)
	return data

def build_conditions(filters):
    conditions = []
    if filters.get('company'):
        conditions.append("company = '{company}'".format(company=filters.get('company')))
    if filters.get('customer'):
        conditions.append("customer = '{customer}'".format(customer=filters.get('customer')))
    if filters.get('status'):
        conditions.append("status = '{status}'".format(status=filters.get('status')))
    if filters.get('from_date') and filters.get('to_date'):
        conditions.append("posting_date BETWEEN '{from_date}' AND '{to_date}'".format(from_date=filters.get('from_date'), to_date=filters.get('to_date')))    
    if filters.get('invoice_type'):
        conditions.append("invoice_type = '{invoice_type}'".format(invoice_type=filters.get('invoice_type')))
    conditions.append("docstatus = 1")  # Filter for approved invoices
    return " AND ".join(conditions)

