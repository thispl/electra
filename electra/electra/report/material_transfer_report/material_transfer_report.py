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
		_("Material Transfer") + ":Link/Material Transfer:200",
		_("Transfer From") + ":Data:200",
		_("Transfer To") + ":Data:200",
		_("Status") + ":Data:200",
		_("Remarks") + ":Data:200",
		_("Amount") + ":Data:200",
	]
	return columns

def get_data(filters):
	data = []
	sa = []
	if filters.source_company:
		if filters.from_date and filters.to_date:
			source_company = tuple(filters.source_company)
			sa = frappe.db.sql("""
				SELECT requested_date, name, source_company, to_warehouse, workflow_state, remarks
				FROM `tabMaterial Transfer`
				WHERE requested_date BETWEEN %s AND %s
					AND source_company IN %s
					AND company = %s
					AND workflow_state = 'Approved'
			""", (filters.from_date, filters.to_date, source_company, filters.company), as_dict=True)

			data = [[i.requested_date, i.name, i.source_company, i.to_warehouse, i.workflow_state, i.remarks,frappe.db.get_value("Stock Entry",{'material_transfer': i.name},'total_outgoing_value')] for i in sa]

			return data
		else:
			source_company = tuple(filters.source_company)
			sa = frappe.db.sql("""
				SELECT requested_date, name, source_company, to_warehouse, workflow_state, remarks
				FROM `tabMaterial Transfer`
				WHERE source_company IN %s
					AND company = %s
					AND workflow_state = 'Approved'
			""", (source_company, filters.company), as_dict=True)

			data = [[i.requested_date, i.name, i.source_company, i.to_warehouse, i.workflow_state, i.remarks,frappe.db.get_value("Stock Entry",{'material_transfer': i.name},'total_outgoing_value')] for i in sa]

			return data
	elif filters.to_warehouse:
		if filters.from_date and filters.to_date:
			to_warehouse = tuple(filters.to_warehouse)
			sa = frappe.db.sql("""
				SELECT requested_date, name, source_company, to_warehouse, workflow_state, remarks
				FROM `tabMaterial Transfer`
				WHERE requested_date BETWEEN %s AND %s
					AND to_warehouse IN %s
					AND company = %s
					AND workflow_state = 'Approved'
			""", (filters.from_date, filters.to_date, to_warehouse, filters.company), as_dict=True)

			data = [[i.requested_date, i.name, i.source_company, i.to_warehouse, i.workflow_state, i.remarks,frappe.db.get_value("Stock Entry",{'material_transfer': i.name},'total_outgoing_value')] for i in sa]

			return data
		else:
			to_warehouse = tuple(filters.to_warehouse)
			sa = frappe.db.sql("""
				SELECT requested_date, name, source_company, to_warehouse, workflow_state, remarks
				FROM `tabMaterial Transfer`
				WHERE to_warehouse IN %s
					AND company = %s
					AND workflow_state = 'Approved'
			""", (to_warehouse, filters.company), as_dict=True)

			data = [[i.requested_date, i.name, i.source_company, i.to_warehouse, i.workflow_state, i.remarks,frappe.db.get_value("Stock Entry",{'material_transfer': i.name},'total_outgoing_value')] for i in sa]

			return data
	
	elif filters.to_warehouse and filters.source_company:
		if filters.from_date and filters.to_date:
			to_warehouse = tuple(filters.to_warehouse)
			source_company = tuple(filters.source_company)
			sa = frappe.db.sql("""
				SELECT requested_date, name, source_company, to_warehouse, workflow_state, remarks
				FROM `tabMaterial Transfer`
				WHERE requested_date BETWEEN %s AND %s
					AND to_warehouse IN %s AND source_company IN %s
					AND company = %s
					AND workflow_state = 'Approved'
			""", (filters.from_date, filters.to_date, to_warehouse,source_company,filters.company), as_dict=True)

			data = [[i.requested_date, i.name, i.source_company, i.to_warehouse, i.workflow_state, i.remarks,frappe.db.get_value("Stock Entry",{'material_transfer': i.name},'total_outgoing_value')] for i in sa]

			return data
		else:
			to_warehouse = tuple(filters.to_warehouse)
			source_company = tuple(filters.source_company)
			sa = frappe.db.sql("""
				SELECT requested_date, name, source_company, to_warehouse, workflow_state, remarks
				FROM `tabMaterial Transfer`
				WHERE to_warehouse IN %s AND source_company IN %s
					AND company = %s
					AND workflow_state = 'Approved'
			""", (to_warehouse,source_company,filters.company), as_dict=True)

			data = [[i.requested_date, i.name, i.source_company, i.to_warehouse, i.workflow_state, i.remarks,frappe.db.get_value("Stock Entry",{'material_transfer': i.name},'total_outgoing_value')] for i in sa]

			return data

	else:
		if filters.from_date and filters.to_date:
			sa = frappe.db.sql("""
				SELECT requested_date, name, source_company, to_warehouse, workflow_state, remarks
				FROM `tabMaterial Transfer`
				WHERE requested_date BETWEEN %s AND %s
					AND company = %s
					AND workflow_state = 'Approved'
			""", (filters.from_date, filters.to_date,filters.company), as_dict=True)

			data = [[i.requested_date, i.name, i.source_company, i.to_warehouse, i.workflow_state, i.remarks,frappe.db.get_value("Stock Entry",{'material_transfer': i.name},'total_outgoing_value')] for i in sa]

			return data
		else:
			sa = frappe.db.sql("""
				SELECT requested_date, name, source_company, to_warehouse, workflow_state, remarks
				FROM `tabMaterial Transfer`
				WHERE company = %s
					AND workflow_state = 'Approved'
			""", (filters.company), as_dict=True)

			data = [[i.requested_date, i.name, i.source_company, i.to_warehouse, i.workflow_state, i.remarks,frappe.db.get_value("Stock Entry",{'material_transfer': i.name},'total_outgoing_value')] for i in sa]

			return data

	