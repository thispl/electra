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
	if filters.group_by == "Item":
		columns += [
			{"label": _("Purchase Invoice"), "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 200},
			{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 180},
			{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 300},
			{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 150},
			{"label": _("Brand"), "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 150},
   			{"label": _("Invoice QAR Value"), "fieldname": "invoice_qar_value", "fieldtype": "Currency", "width": 150},
			{"label": _("Overhead Cost"), "fieldname": "overhead_cost", "fieldtype": "Currency", "width": 150},
			{"label": _("Total Purchase"), "fieldname": "total_purchase", "fieldtype": "Currency", "width": 150},
		]
	else:
		columns += [
			{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 120},
			{"label": _("Invoice No"), "fieldname": "invoice_no", "fieldtype": "Data", "width": 200},
			{"label": _("Purchase Invoice"), "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 200},
			{"label": _("Supplier Name"), "fieldname": "supplier_name", "fieldtype": "Data", "width": 150},
			{"label": _("Currency"), "fieldname": "currency", "fieldtype": "Data", "width": 70},
			{"label": _("Invoice Value"), "fieldname": "invoice_value", "fieldtype": "Currency", "width": 150},
			{"label": _("Invoice QAR Value"), "fieldname": "invoice_qar_value", "fieldtype": "Currency", "width": 150},
			{"label": _("Overhead Cost"), "fieldname": "overhead_cost", "fieldtype": "Currency", "width": 150},
			{"label": _("Total Purchase"), "fieldname": "total_purchase", "fieldtype": "Currency", "width": 150},
		]

	return columns

def get_data(filters):
	data = []
	if filters.group_by == "Item":
		items = frappe.db.sql("""
			SELECT pii.item_code, pii.purchase_receipt, pii.item_name, pii.item_group, pii.pr_detail,
				pi.posting_date, pi.bill_no, pi.name, pi.supplier,
				pi.currency, pii.net_amount, pii.base_net_amount, pii.qty
			FROM `tabPurchase Invoice` pi
			INNER JOIN `tabPurchase Invoice Item` pii
				ON pii.parent = pi.name
			WHERE posting_date BETWEEN %s AND %s
				AND custom_is_internal = 0
				AND stock_confirmation NOT IN ("Stock Confirmation")
				AND status NOT IN ("Cancelled","Draft")
				AND company = %s
			ORDER BY posting_date
		""", (filters.from_date, filters.to_date, filters.company), as_dict=1)

		consolidated = {}
		count = 0
		for i in items:
			value = 0

			if i.purchase_receipt:
				lc = frappe.db.sql("""
					SELECT `tabLanded Cost Item`.applicable_charges as pd, `tabLanded Cost Item`.item_code, `tabLanded Cost Item`.receipt_document, 
						`tabLanded Cost Item`.qty
					FROM `tabLanded Cost Voucher`
					INNER JOIN `tabLanded Cost Item`
						ON `tabLanded Cost Voucher`.name = `tabLanded Cost Item`.parent
					WHERE `tabLanded Cost Item`.receipt_document = %s
						AND `tabLanded Cost Item`.item_code = %s
						AND `tabLanded Cost Item`.purchase_receipt_item = %s
						AND `tabLanded Cost Voucher`.docstatus = 1
				""", (i.purchase_receipt, i.item_code, i.pr_detail), as_dict=1)
				if filters.company == "TRADING DIVISION - ELECTRA":
					lc = frappe.db.sql("""
						SELECT `tabLanded Cost Item`.applicable_charges as pd, `tabLanded Cost Item`.item_code, `tabLanded Cost Item`.receipt_document, 
							`tabLanded Cost Item`.qty
						FROM `tabLanded Cost Voucher`
						INNER JOIN `tabLanded Cost Item`
							ON `tabLanded Cost Voucher`.name = `tabLanded Cost Item`.parent
						WHERE `tabLanded Cost Item`.receipt_document = %s
							AND `tabLanded Cost Item`.item_code = %s
							AND `tabLanded Cost Voucher`.docstatus = 1
					""", (i.purchase_receipt, i.item_code), as_dict=1)
				if lc:
					value = lc[0].pd or 0

			key = (i.item_code, i.item_name, i.item_group, i.name)

			if key not in consolidated:
				brand = frappe.db.get_value("Item", i.item_code, "brand")
				consolidated[key] = {
					"purchase_invoice": i.name,
					"item_code": i.item_code,
					"item_name": i.item_name,
					"item_group": i.item_group,
					"brand": brand,
					"invoice_qar_value": 0,
					"overhead_cost": 0,
					"total_purchase": 0,
				}

			base = round(i.base_net_amount or 0, 2)
			overhead = round(value or 0, 2)
			total = round(base + overhead, 2)

			consolidated[key]["invoice_qar_value"] += base
			consolidated[key]["overhead_cost"] += overhead
			consolidated[key]["total_purchase"] += total

		# Final data list
		data = list(consolidated.values())

	else: 
		purchase_invoice = frappe.db.get_all(
			"Purchase Invoice",
			{'company':filters.company,
			"posting_date":('between',(filters.from_date,filters.to_date)),
			"custom_is_internal":0,
			"stock_confirmation": ('not in',("Stock Confirmation")),
			"status":('not in',("Cancelled","Draft"))},['*'], order_by="posting_date")
		for i in purchase_invoice:
			gt = frappe.get_doc("Purchase Invoice",i.name)
			for j in gt.items[:1]:
				lc = frappe.db.sql("""select total_taxes_and_charges,sum(`tabLanded Cost Item`.applicable_charges) as pd from `tabLanded Cost Voucher`
				left join `tabLanded Cost Item` on `tabLanded Cost Voucher`.name = `tabLanded Cost Item`.parent
				where `tabLanded Cost Item`.receipt_document = '%s' and  `tabLanded Cost Voucher`.docstatus =1 """%(j.purchase_receipt),as_dict=True)
				if lc:
					for l in lc:
						if l.pd:
							p = l.pd
						else:
							p = 0
				else:
					p = 0
				value = lc[0].total_taxes_and_charges if lc and lc[0].total_taxes_and_charges is not None else 0
				tot = round((i.base_net_total+(value)),2)
				data.append({
					"date": i.posting_date,
					"invoice_no": i.bill_no,
					"purchase_invoice": i.name,
					"supplier_name": i.supplier,
					"currency": i.currency,
					"invoice_value": round(i.net_total, 2),
					"invoice_qar_value": round(i.base_net_total, 2),
					"overhead_cost": round(value, 2),
					"total_purchase": round(tot, 2)
				})
	return data

def test_check():
	filters = {
		"from_date": "2025-01-01",
		"to_date": "2025-12-31",
		"company": "TRADING DIVISION - ELECTRA",
		"group_by": "Item"
	}
	get_data(frappe._dict(filters))
 
# def get_data(filters):
# 	data = []
# 	items = frappe.db.sql("""
# 				SELECT lci.applicable_charges, lci.item_code, lci.receipt_document, lci.item_name, lci.purchase_receipt_item,
# 					lci.qty
# 				FROM `tabLanded Cost Voucher` lcv
# 				INNER JOIN `tabLanded Cost Item` lci
# 					ON lcv.name = lci.parent
# 				WHERE lcv.docstatus = 1
# 			""", as_dict=1)

# 	consolidated = {}
# 	count = 0
# 	for i in items:
# 		value = 0

# 		if i.purchase_receipt:
# 			lc = frappe.db.sql("""
# 				SELECT `tabLanded Cost Item`.applicable_charges as pd, `tabLanded Cost Item`.item_code, `tabLanded Cost Item`.receipt_document, 
# 					`tabLanded Cost Item`.qty
# 				FROM `tabLanded Cost Voucher`
# 				INNER JOIN `tabLanded Cost Item`
# 					ON `tabLanded Cost Voucher`.name = `tabLanded Cost Item`.parent
# 				WHERE `tabLanded Cost Item`.receipt_document = %s
# 					AND `tabLanded Cost Item`.item_code = %s
# 					AND `tabLanded Cost Item`.qty = %s
# 					AND `tabLanded Cost Voucher`.docstatus = 1
# 			""", (i.purchase_receipt, i.item_code, i.qty), as_dict=1)
# 			if lc:
# 				value = lc[0].pd or 0

# 		key = (i.item_code, i.item_name, i.item_group)

# 		if key not in consolidated:
# 			brand = frappe.db.get_value("Item", i.item_code, "brand")
# 			consolidated[key] = {
# 				"item_code": i.item_code,
# 				"item_name": i.item_name,
# 				"item_group": i.item_group,
# 				"brand": brand,
# 				"invoice_qar_value": 0,
# 				"overhead_cost": 0,
# 				"total_purchase": 0,
# 			}

# 		base = round(i.base_net_amount or 0, 2)
# 		overhead = round(value or 0, 2)
# 		total = round(base + overhead, 2)

# 		consolidated[key]["invoice_qar_value"] += base
# 		consolidated[key]["overhead_cost"] += overhead
# 		consolidated[key]["total_purchase"] += total

# 	# Final data list
# 	data = list(consolidated.values())
# 	return data
