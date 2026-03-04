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
		_("Retention Invoice") + ":Link/Retention Invoice:200",
		_("Posting Date") + ":Date:110",
		_("Sales Order") + ":Link/Sales Order:200",
		_("Customer") + ":Link/Customer:250",
		_("Sales Person") + ":Link/Sales Person:150",
		_("Company") + ":Link/Company:150",
		_("Project") + ":Link/Project:150",
		_("Bidding Price") + ":Currency:110",
		_("Retention Amount") + ":Currency:110",
		_("Outstanding Amount") + ":Currency:110",

		
	]
	data = get_order_data(filters)
	return columns, data

def get_order_data(filters):
	data =[]
	conditions = build_conditions(filters)
	query = """SELECT * FROM `tabRetention Invoice` WHERE {conditions}""".format(conditions=conditions)
	sales = frappe.db.sql(query, as_dict=True)
	for i in sales:
		if i.docstatus!=2:
			row = [i.name,i.transaction_date,i.sales_order,i.customer,i.sales_person_user,i.company,i.project,round(i.total_bidding_price,2),round(i.advance_amount1,2),round(i.advance_amount,2)]
			data.append(row)
	return data

def build_conditions(filters):
	conditions = []
	if filters.get('sales_person_user'):
		conditions.append("sales_person_user = '{sales_person_user}'".format(sales_person_user=filters.get('sales_person_user')))
	if filters.get('from_date') and filters.get('to_date'):
		conditions.append("transaction_date BETWEEN '{from_date}' AND '{to_date}'".format(from_date=filters.get('from_date'), to_date=filters.get('to_date')))    
	if filters.get('customer'):
		conditions.append("customer = '{customer}'".format(customer=filters.get('customer')))
	if filters.get('project'):
		conditions.append("project = '{project}'".format(project=filters.get('project')))

	return " AND ".join(conditions)
