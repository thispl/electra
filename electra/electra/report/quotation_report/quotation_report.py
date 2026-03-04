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
		_("Date") + ":Date/:110",
		_("Customer") + ":Data/:300",
		
		# _("Required Date") + ":Date/:100",
		_("Sales Person") + ":Data/:200",
		_("Total Amount") + ":Currency/:150",
		_("Discount Amount") + ":Currency/:150",
		_("Net Amount") + ":Currency/:150",
		_("Status") + ":Data/:130",
		
		_("Phone No") + ":Data/:100",
		_("Enquiry Ref. No.") + ":Data/:170",
		_("Prepared By") + ":Data/:300",
		_("Project") + ":Data/:200",
		
		

	]
	return columns

# def get_data(filters):
# 	data = []
# 	row = []
# 	conditions = "transaction_date BETWEEN %(from_date)s AND %(to_date)s AND company = %(company)s"
# 	params = {"from_date": filters.from_date, "to_date": filters.to_date, "company": filters.company}

# 	if filters.order_type:
# 		conditions += " AND order_type = %(order_type)s"
# 		params["order_type"] = filters.order_type

# 	if filters.customer:
# 		conditions += " AND party_name = %(customer)s"
# 		params["customer"] = filters.customer

# 	if filters.sales_person:
# 		conditions += " AND converted_by = %(sales_person)s"
# 		params["sales_person"] = filters.sales_person

# 	if filters.docstatus:
# 		conditions += " AND status = %(docstatus)s"
# 		params["docstatus"] = filters.docstatus

# 	# if filters.valid_from_date:
# 	# 	conditions += " AND valid_till >= %(valid_from_date)s"
# 	# 	params["valid_from_date"] = filters.valid_from_date
	
# 	# if filters.valid_to_date:
# 	# 	conditions += " AND valid_till <= %(valid_to_date)s"
# 	# 	params["valid_to_date"] = filters.valid_to_date

# 	if filters.amount_from:
# 		conditions += " AND net_total >= %(amount_from)s"
# 		params["amount_from"] = filters.amount_from

# 	if filters.amount_to:
# 		conditions += " AND net_total <= %(amount_to)s"
# 		params["amount_to"] = filters.amount_to

# 	quotation = frappe.db.sql("""
#         SELECT *
#         FROM `tabQuotation` WHERE {conditions} AND docstatus=1 order by transaction_date
#     """.format(conditions=conditions), params, as_dict=True)
# 	for i in quotation:
# 		if i.status != "Cancelled":
# 			row = [i.name,i.transaction_date,i.party_name,i.converted_by,round(i.total,2),round(i.discount_amount,2),round(i.net_total,2),i.status,i.mobile_no or i.contact_mobile,i.enquiry_reference_no,i.user_name]
# 			project_name = frappe.db.get_value("Sales Order", {'quotation': i.name}, 'project')
# 			row += [project_name]
# 			data.append(row)
# 	return data

def get_data(filters):
    data = []
    row = []
    conditions = "transaction_date BETWEEN %(from_date)s AND %(to_date)s AND company = %(company)s"
    params = {"from_date": filters.from_date, "to_date": filters.to_date, "company": filters.company}

    if filters.order_type:
        conditions += " AND order_type = %(order_type)s"
        params["order_type"] = filters.order_type

    if filters.customer:
        conditions += " AND party_name = %(customer)s"
        params["customer"] = filters.customer

    if filters.sales_person:
        conditions += " AND converted_by = %(sales_person)s"
        params["sales_person"] = filters.sales_person

    if filters.docstatus:
        conditions += " AND status = %(docstatus)s"
        params["docstatus"] = filters.docstatus

    if filters.amount_condition and filters.amount_from is not None:
        if filters.amount_condition == ">":
            conditions += " AND net_total > %(amount_from)s"
            params["amount_from"] = filters.amount_from
        elif filters.amount_condition == "<":
            conditions += " AND net_total < %(amount_from)s"
            params["amount_from"] = filters.amount_from
        elif filters.amount_condition == "=":
            conditions += " AND net_total = %(amount_from)s"
            params["amount_from"] = filters.amount_from
        elif filters.amount_condition == "between":
            if filters.amount_from:
                conditions += " AND net_total >= %(amount_from)s"
                params["amount_from"] = filters.amount_from
            if filters.amount_to:
                conditions += " AND net_total <= %(amount_to)s"
                params["amount_to"] = filters.amount_to
    quotation = frappe.db.sql("""
        SELECT *
        FROM `tabQuotation` WHERE {conditions} ORDER BY transaction_date
    """.format(conditions=conditions), params, as_dict=True)

    for i in quotation:
        if i.status != "Cancelled":
            row = [
                i.name,
                i.transaction_date,
                i.party_name,
                i.converted_by,
                round(i.total, 2),
                round(i.discount_amount, 2),
                round(i.net_total, 2),
                i.status,
                i.mobile_no or i.contact_mobile,
                i.enquiry_reference_no,
                i.user_name
            ]
            project_name = frappe.db.get_value("Sales Order", {'quotation': i.name}, 'project')
            row += [project_name]
            data.append(row)
    return data
