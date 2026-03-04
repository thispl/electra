# Copyright (c) 2024, Abdulla and contributors
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
	if filters.document == "Quotation":
		columns.extend([
			_("Refer No") + ":Link/Quotation:200",
		])
	elif filters.document == 'Sales Order':
		columns.extend([
			_("LPO No") + ":Link/Sales Order:200",
			
		])
	elif filters.document == 'Sales Invoice':
		columns.extend([
			_("Invoice Number") + ":Link/Sales Invoice:200",
			
		])
	elif filters.document == 'Delivery Note':
		columns.extend([
			_("Refer No") + ":Link/Delivery Note:200",
		
		])
	columns += [
		_("Customer/Party Name") + ":Link/Customer:240",
		_("Date") + ":Date/:120",
		_("Item") + ":Link/Item:150",
		_("Description") + ":Data:200",
		_("Qty") + ":Data/:90",
		_("Price") + ":Currency/:100",
		_("Amount") + ":Currency/:100",
	]
	if filters.document != 'Quotation':
		columns.extend([
			_("Customer's Purchase Order") + ":Data/:300"
		
		])
	columns += [
		_("Sales Person") + ":Link/Sales Person:240",
	]
	return columns

def get_data(filters):
	data = []
	row = []
	conditions=''
	params = {"company": filters.company}
	#Quotation
	if filters.document=="Quotation":
		conditions = "AND q.company = %(company)s"
		if filters.from_date:
			conditions += " AND q.transaction_date >= %(from_date)s"
			params["from_date"] = filters.from_date
		
		if filters.to_date:
			conditions += " AND q.transaction_date <= %(to_date)s"
			params["to_date"] = filters.to_date
		if filters.item:
			conditions += " AND qi.item_code = %(item)s"
			params["item"] = filters.item
		if filters.item_group:
			conditions += " AND qi.item_group = %(item_group)s"
			params["item_group"] = filters.item_group

		if filters.customer:
			conditions += " AND q.party_name = %(customer)s"
			params["customer"] = filters.customer

		if filters.sales_person:
			conditions += " AND q.converted_by = %(sales_person)s"
			params["sales_person"] = filters.sales_person

		if filters.project:
			pro=frappe.get_value("Project",{"name":filters.project},['project_name'])
			conditions += " AND q.title_of_project = %(pro)s"
			params["pro"] = filters.pro

		if filters.amount_from:
			conditions += " AND qi.amount >= %(amount_from)s"
			params["amount_from"] = filters.amount_from

		if filters.amount_to:
			conditions += " AND qi.amount <= %(amount_to)s"
			params["amount_to"] = filters.amount_to
		# quotation = frappe.db.sql("""
		# 	SELECT *
		# 	FROM `tabQuotation Item` qi 
		# 	INNER JOIN `tabQuotation` q ON q.name = qi.parent WHERE q.docstatus != 2 {conditions}
		# """.format(conditions=conditions), params, as_dict=True)
		quotation = frappe.db.sql("""
			SELECT *
			FROM `tabQuotation Item` qi 
			INNER JOIN `tabQuotation` q ON q.name = qi.parent WHERE q.docstatus != 2 {conditions} ORDER BY q.transaction_date DESC
		""".format(conditions=conditions), params, as_dict=True)
		for i in quotation:
			if i.status != "Cancelled":
				row = [i.name,i.party_name,i.transaction_date,i.item_code,i.description,i.qty,i.rate,i.amount,i.converted_by]
				data.append(row)
	
	
	#Sales Order
	elif filters.document=="Sales Order":
		conditions = "AND so.company = %(company)s"
		if filters.from_date:
			conditions += " AND so.transaction_date >= %(from_date)s"
			params["from_date"] = filters.from_date
		
		if filters.to_date:
			conditions += " AND so.transaction_date <= %(to_date)s"
			params["to_date"] = filters.to_date
		if filters.item:
			conditions += " AND soi.item_code = %(item)s"
			params["item"] = filters.item
		if filters.item_group:
			conditions += " AND soi.item_group = %(item_group)s"
			params["item_group"] = filters.item_group

		if filters.customer:
			conditions += " AND so.customer = %(customer)s"
			params["customer"] = filters.customer

		if filters.sales_person:
			conditions += " AND so.sales_person_user = %(sales_person)s"
			params["sales_person"] = filters.sales_person

		if filters.project:
			conditions += " AND so.project = %(project)s"
			params["project"] = filters.project

		if filters.amount_from:
			conditions += " AND soi.amount >= %(amount_from)s"
			params["amount_from"] = filters.amount_from

		if filters.amount_to:
			conditions += " AND soi.amount <= %(amount_to)s"
			params["amount_to"] = filters.amount_to
		# sales_order = frappe.db.sql("""
		# 	SELECT *
		# 	FROM `tabSales Order Item` soi 
		# 	INNER JOIN `tabSales Order` so ON so.name = soi.parent WHERE so.docstatus != 2 {conditions}
		# """.format(conditions=conditions), params, as_dict=True)
		sales_order = frappe.db.sql("""
			SELECT *
			FROM `tabSales Order Item` soi 
			INNER JOIN `tabSales Order` so ON so.name = soi.parent WHERE so.docstatus != 2 {conditions} ORDER BY so.transaction_date DESC
		""".format(conditions=conditions), params, as_dict=True)
		for i in sales_order:
			if i.status != "Cancelled":
				amt=i.qty*i.rate
				row = [i.name,i.customer,i.transaction_date,i.item_code,i.description,i.qty,i.rate,amt,i.po_no,i.sales_person_user]
				data.append(row)

	#Sales Invoice
	elif filters.document=="Sales Invoice":
		conditions = "AND si.company = %(company)s"
		if filters.from_date:
			conditions += " AND si.posting_date >= %(from_date)s"
			params["from_date"] = filters.from_date
		
		if filters.to_date:
			conditions += " AND si.posting_date <= %(to_date)s"
			params["to_date"] = filters.to_date
		if filters.item:
			conditions += " AND sii.item_code = %(item)s"
			params["item"] = filters.item
		if filters.item_group:
			conditions += " AND sii.item_group = %(item_group)s"
			params["item_group"] = filters.item_group

		if filters.customer:
			conditions += " AND si.customer = %(customer)s"
			params["customer"] = filters.customer

		if filters.sales_person:
			conditions += " AND si.sales_person_user = %(sales_person)s"
			params["sales_person"] = filters.sales_person

		if filters.project:
			conditions += " AND si.project = %(project)s"
			params["project"] = filters.project

		if filters.amount_from:
			conditions += " AND sii.amount >= %(amount_from)s"
			params["amount_from"] = filters.amount_from

		if filters.amount_to:
			conditions += " AND sii.amount <= %(amount_to)s"
			params["amount_to"] = filters.amount_to
		# sales_Invoice = frappe.db.sql("""
		# 	SELECT *
		# 	FROM `tabSales Invoice Item` sii 
		# 	INNER JOIN `tabSales Invoice` si ON si.name = sii.parent WHERE si.docstatus != 2 {conditions}
		# """.format(conditions=conditions), params, as_dict=True)
		sales_Invoice = frappe.db.sql("""
			SELECT *
			FROM `tabSales Invoice Item` sii 
			INNER JOIN `tabSales Invoice` si ON si.name = sii.parent WHERE si.docstatus != 2 {conditions} ORDER BY si.posting_date DESC
		""".format(conditions=conditions), params, as_dict=True)
		for i in sales_Invoice:
			if i.status != "Cancelled":
				if i.stock_transfer!='Stock Transfer':
					amt=i.qty*i.rate
					row = [i.name,i.customer,i.posting_date,i.item_code,i.description,i.qty,i.rate,amt,i.po_no,i.sales_person_user]
					data.append(row)
	
	
	#Delivery Note
	elif filters.document=="Delivery Note":
		conditions = "AND dn.company = %(company)s"
		if filters.from_date:
			conditions += " AND dn.posting_date >= %(from_date)s"
			params["from_date"] = filters.from_date
		
		if filters.to_date:
			conditions += " AND dn.posting_date <= %(to_date)s"
			params["to_date"] = filters.to_date
		if filters.item:
			conditions += " AND dni.item_code = %(item)s"
			params["item"] = filters.item
		if filters.item_group:
			conditions += " AND dni.item_group = %(item_group)s"
			params["item_group"] = filters.item_group

		if filters.customer:
			conditions += " AND dn.customer = %(customer)s"
			params["customer"] = filters.customer

		if filters.sales_person:
			conditions += " AND dn.sales_person_user = %(sales_person)s"
			params["sales_person"] = filters.sales_person

		if filters.project:
			conditions += " AND dn.project = %(project)s"
			params["project"] = filters.project

		if filters.amount_from:
			conditions += " AND dni.amount >= %(amount_from)s"
			params["amount_from"] = filters.amount_from

		if filters.amount_to:
			conditions += " AND dni.amount <= %(amount_to)s"
			params["amount_to"] = filters.amount_to
		# sales_Invoice = frappe.db.sql("""
		# 	SELECT *
		# 	FROM `tabDelivery Note Item` dni 
		# 	INNER JOIN `tabDelivery Note` dn ON dn.name = dni.parent WHERE dn.docstatus != 2 {conditions}
		# """.format(conditions=conditions), params, as_dict=True)
		sales_Invoice = frappe.db.sql("""
			SELECT *
			FROM `tabDelivery Note Item` dni 
			INNER JOIN `tabDelivery Note` dn ON dn.name = dni.parent WHERE dn.docstatus != 2 {conditions} ORDER BY dn.posting_date DESC
		""".format(conditions=conditions), params, as_dict=True)
		for i in sales_Invoice:
			if i.status != "Cancelled":
				amt=i.qty*i.rate
				row = [i.name,i.customer,i.posting_date,i.item_code,i.description,i.qty,i.rate,amt,i.po_no,i.sales_person_user]
				data.append(row)
	return data