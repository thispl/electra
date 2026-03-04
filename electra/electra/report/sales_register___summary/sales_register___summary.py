# Copyright (c) 2026, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.meta import get_field_precision
from frappe.query_builder.custom import ConstantColumn
from frappe.utils import flt, getdate
from pypika import Order
from frappe.utils.nestedset import get_descendants_of

from erpnext.accounts.party import get_party_account
from erpnext.accounts.report.utils import (
	apply_common_conditions,
	get_advance_taxes_and_charges,
	get_journal_entries,
	get_opening_row,
	get_party_details,
	get_payment_entries,
	get_query_columns,
	get_taxes_query,
	get_values_for_columns,
)


def execute(filters=None):
	return _execute(filters)

def _execute(filters, additional_table_columns=None):
	if not filters:
		filters = frappe._dict({})
	columns = get_columns_sview(filters)
	data = get_data_sview(filters)
	return columns, data

def get_columns_sview(filters):
	if filters.get("summarise_based_on")=='Item Group':
		return [
			{
				"label": _("Item Group"),
				"fieldtype": "Link",
				"fieldname": "item_group",
				"options": "Item Group",
				"width": 150
			},
			{
				"label": _("Total Amount"),
				"fieldtype": "Currency",
				"fieldname": "total_amount",
				"width": 150,
				"options":"currency"
			},
			{
				"label": _("Currency"),
				"fieldtype": "Link",
				"fieldname": "currency",
				"options": "Currency",
				"width": 100,
				"hidden":1
			}
		]
	
	return [
		{
			"label": _("Item Code"),
			"fieldtype": "Link",
			"fieldname": "item_code",
			"options": "Item",
			"width": 120
		},
		{
			"label": _("Item Name"),
			"fieldtype": "Data",
			"fieldname": "item_name",
			"width": 140
		},
		{
			"label": _("Item Group"),
			"fieldtype": "Link",
			"fieldname": "item_group",
			"options": "Item Group",
			"width": 120
		},


		{
			"label": _("Description"),
			"fieldtype": "Data",
			"fieldname": "description",
			"width": 150
		},
		{
			"label": _("Quantity"),
			"fieldtype": "Float",
			"fieldname": "quantity",
			"width": 150
		},
		{
			"label": _("UOM"),
			"fieldtype": "Link",
			"fieldname": "uom",
			"options": "UOM",
			"width": 100
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Currency",
			"width": 120,
			"options":"currency"
		},
		{
			"label": _("Amount"),
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120,
			"options":"currency"
		},
		{
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"fieldname": "sales_order",
			"options": "Sales Invoice",
			"width": 100
		},
		{
			"label": _("Transaction Date"),
			"fieldtype": "Date",
			"fieldname": "posting_date",
			"width": 90
		},
		{
			"label": _("Customer"),
			"fieldtype": "Link",
			"fieldname": "customer",
			"options": "Customer",
			"width": 100
		},
		{
			"label": _("Customer Name"),
			"fieldtype": "Data",
			"fieldname": "customer_name",
			"width": 140
		},
		{
			"label": _("Customer Group"),
			"fieldtype": "Link",
			"fieldname": "customer_group",
			"options": "Customer Group",
			"width": 120
		},
		{
			"label": _("Territory"),
			"fieldtype": "Link",
			"fieldname": "territory",
			"options": "Territory",
			"width": 100
		},
		{
			"label": _("Project"),
			"fieldtype": "Link",
			"fieldname": "project",
			"options": "Project",
			"width": 100
		},
		{
			"label": _("Delivered Quantity"),
			"fieldtype": "Float",
			"fieldname": "delivered_quantity",
			"width": 150
		},
		
		{
			"label": _("Company"),
			"fieldtype": "Link",
			"fieldname": "company",
			"options": "Company",
			"width": 100
		},
		{
			"label": _("Currency"),
			"fieldtype": "Link",
			"fieldname": "currency",
			"options": "Currency",
			"width": 100,
			"hidden":1
		}
	]

	

def get_data_sview(filters):
	default_currency = frappe.db.get_value("Company", filters.get("company"), "default_currency")
	if filters.get("summarise_based_on")=='Item Group':
		data = []

		company_list = get_descendants_of("Company", filters.get("company"))
		company_list.append(filters.get("company"))
		
		item_details = get_item_details()
		sales_order_records = get_sales_order_details(company_list, filters)

		grouped_data = {}

		for record in sales_order_records:
			item_record = item_details.get(record.item_code)
			item_group = item_record.get("item_group")
			amount = record.base_amount

			if item_group in grouped_data:
				grouped_data[item_group] += amount
			else:
				grouped_data[item_group] = amount

		grouped_list = [{"item_group": key, "total_amount": value, "currency": default_currency} for key, value in grouped_data.items()]

		return grouped_list
	
	data = []

	company_list = get_descendants_of("Company", filters.get("company"))
	company_list.append(filters.get("company"))

	customer_details = get_customer_details()
	item_details = get_item_details()
	sales_order_records = get_sales_order_details(company_list, filters)
	for record in sales_order_records:
		
		customer_record = customer_details.get(record.customer)
		item_record = item_details.get(record.item_code)
		
		row = {
			"item_code": record.item_code,
			"item_name": item_record.item_name,
			"item_group":  item_record.get("item_group"),
			"description": record.description,
			"quantity": record.qty,
			"uom": record.uom,
			"rate": record.base_rate,
			"amount": record.base_amount,
			"sales_order": record.name,
			"posting_date": record.posting_date,
			"customer": record.customer,
			"customer_name": customer_record.customer_name,
			"customer_group": customer_record.customer_group,
			"territory": record.territory,
			"project": record.project,
			"delivered_quantity": flt(record.delivered_qty),
			"company": record.company,
			"currency": default_currency
		}
		data.append(row)

	return data

def get_conditions_sview(filters):
	conditions = ''
	if filters.get('item_group'):
		conditions += "AND so_item.item_group = %s" %frappe.db.escape(filters.item_group)

	
	if filters.get('from_date'):
		conditions += "AND so.posting_date >= '%s'" %filters.from_date

	if filters.get('to_date'):
		conditions += "AND so.posting_date <= '%s'" %filters.to_date

	if filters.get("item_code"):
		conditions += "AND so_item.item_code = %s" %frappe.db.escape(filters.item_code)

	if filters.get("customer"):
		conditions += "AND so.customer = %s" %frappe.db.escape(filters.customer)

	if filters.get("customer_group"):
		conditions += "AND so.customer_group = %s" %frappe.db.escape(filters.customer_group)

	if filters.get("territory"):
		conditions += "AND so.territory = %s" %frappe.db.escape(filters.territory)
	
	if filters.get("sales_person_user"):
		conditions += "AND so.sales_person_user = %s" %frappe.db.escape(filters.sales_person_user)

	return conditions

def get_customer_details():
	details = frappe.get_all("Customer",
		fields=["name", "customer_name", "customer_group"])
	customer_details = {}
	for d in details:
		customer_details.setdefault(d.name, frappe._dict({
			"customer_name": d.customer_name,
			"customer_group": d.customer_group
		}))
	return customer_details

def get_item_details():
	details = frappe.db.get_all("Item",
		fields=["item_code", "item_name", "item_group"])
	item_details = {}
	for d in details:
		item_details.setdefault(d.item_code, frappe._dict({
			"item_name": d.item_name,
			"item_group": d.item_group,
		}))
	return item_details

def get_sales_order_details(company_list, filters):
	conditions = get_conditions_sview(filters)

	return frappe.db.sql("""
		SELECT
			so_item.item_code, so_item.description, so_item.qty,
			so_item.uom, so_item.base_rate, so_item.base_amount,
			so.name, so.posting_date, so.customer,so.territory,
			so.project, so_item.delivered_qty,
			so.company,soi.delivered_qty
		FROM
			`tabSales Invoice` so, `tabSales Invoice Item` so_item
			join `tabItem`  on `tabItem`.name = so_item.item_code
		LEFT JOIN
			`tabSales Order Item` soi
			ON soi.name = so_item.so_detail
		WHERE
			so.name = so_item.parent
			AND so.company in ({0})
			AND so.docstatus = 1 {1}
			AND so.stock_transfer != "Stock Transfer"
	""".format(','.join(["%s"] * len(company_list)), conditions), tuple(company_list), as_dict=1)


