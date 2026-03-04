# Copyright (c) 2026, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from collections import defaultdict
from frappe.utils import get_datetime

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	if filters.get("consolidate_invoices"):
		columns += [
			_("Company") + ":Link/Company:200",
			_("Project Budget") + ":Link/Project Budget:200",
			_("Sales Order") + ":Link/Sales Order:200",
			_("Item") + ":Data:180",
			_("Delivered") + ":Float:150",
			_("Actual Delivered") + ":Float:150",
			_("Billed") + ":Float:150",
			_("Actual Billed") + ":Float:150",
			_("Difference in Billed") + ":Float:150",
			_("Issued") + ":Float:150",
			_("Balance to Issue") + ":Float:150",
		]
	else:
		columns += [
			_("Project Budget") + ":Link/Project Budget:200",
			_("Sales Order") + ":Link/Sales Order:200",
			_("Posting Date") + ":Date:180",
			_("Posting Time") + ":Time:150",
			_("Sales Invoice") + ":Link/Sales Invoice:200",
			_("Item") + ":Data:180",
			_("Delivered") + ":Float:150",
			_("Billed") + ":Float:150",
			# _("Total Billed") + ":Float:150",
			_("Actual Billed") + ":Float:150",
			_("Issued") + ":Float:150",
			_("Balance to Issue") + ":Float:150",
		]
	return columns

def get_columns(filters):
	columns = []

	if filters.get("consolidate_invoices"):
		columns += [
			{"label": _("Project Budget"),"fieldname": "project_budget","fieldtype": "Link","options": "Project Budget","width": 200,},
			{"label": _("Sales Order"),"fieldname": "sales_order","fieldtype": "Link","options": "Sales Order","width": 200,},
			{"label": _("Item"), "fieldname": "item", "fieldtype": "Data", "width": 180},
			{"label": _("Delivered"), "fieldname": "delivered", "fieldtype": "Float", "width": 150},
			{"label": _("Actual Delivered"), "fieldname": "actual_delivered", "fieldtype": "Float", "width": 150},
			{"label": _("Billed"), "fieldname": "billed", "fieldtype": "Float", "width": 150},
			{"label": _("Actual Billed"), "fieldname": "actual_billed", "fieldtype": "Float", "width": 150},
			{"label": _("Difference in Billed"), "fieldname": "difference_in_billed", "fieldtype": "Float", "width": 150},
			{"label": _("Issued"), "fieldname": "issued", "fieldtype": "Float", "width": 150},
			{"label": _("Balance to Issue"), "fieldname": "balance_to_issue", "fieldtype": "Float", "width": 150},
		]

	else:
		columns += [
			{"label": _("Company"),"fieldname": "company","fieldtype": "Link","options": "Company","width": 200,},
			{"label": _("Project Budget"),"fieldname": "project_budget","fieldtype": "Link","options": "Project Budget","width": 200,},
			{"label": _("Sales Order"),"fieldname": "sales_order","fieldtype": "Link","options": "Sales Order","width": 200,},
			{"label": _("Posting Date"),"fieldname": "posting_date","fieldtype": "Date","width": 180,},
			{"label": _("Posting Time"),"fieldname": "posting_time","fieldtype": "Time","width": 150,},
			{"label": _("Sales Invoice"),"fieldname": "sales_invoice","fieldtype": "Link","options": "Sales Invoice","width": 200,},
			{"label": _("Item"), "fieldname": "item", "fieldtype": "Data", "width": 180},
			{"label": _("Delivered"), "fieldname": "delivered", "fieldtype": "Float", "width": 150},
			{"label": _("Billed"), "fieldname": "billed", "fieldtype": "Float", "width": 150},
			{"label": _("Actual Billed"), "fieldname": "actual_billed", "fieldtype": "Float", "width": 150},
			{"label": _("Issued"), "fieldname": "issued", "fieldtype": "Float", "width": 150},
			{"label": _("Balance to Issue"), "fieldname": "balance_to_issue", "fieldtype": "Float", "width": 150},
		]

	return columns


def get_data(filters):
	data = []

	delivery_map = get_delivery_map()
	issue_map = get_issue_map()

	if not filters.get("project_budget"):
		project_budgets = frappe.get_all("Project Budget", {"docstatus": 1}, pluck="name")
	else:
		project_budgets = [filters.get("project_budget")]

	for project_budget in project_budgets:
		pb_doc = frappe.get_doc("Project Budget", project_budget)
		sales_order = pb_doc.sales_order
		company = pb_doc.company

		sales_invoices = frappe.db.sql("""
			SELECT name, posting_date, posting_time,
				   TIMESTAMP(posting_date, posting_time) as ts
			FROM `tabSales Invoice`
			WHERE docstatus = 1 AND so_no = %s
			ORDER BY ts
		""", (sales_order,), as_dict=True)

		already_billed_map = {}

		for idx, si in enumerate(sales_invoices):
			next_si = sales_invoices[idx + 1]["name"] if idx + 1 < len(sales_invoices) else None
			si_ts = si.ts

			pb_item_map = defaultdict(lambda: {
				"delivered_qty": 0,
				"billed_qty": 0,
				"docnames": []
			})
			
			for row in pb_doc.item_table:
				pb_item_map[row.item]["delivered_qty"] += row.delivered_qty
				pb_item_map[row.item]["billed_qty"] += row.billed_qty
   
			for item_code, info in pb_item_map.items():

				key = (item_code, sales_order)

				total_billed = sum(
					qty for ts, qty in delivery_map.get(key, [])
					if ts <= si_ts
				)

				previous_billed = already_billed_map.get(item_code, 0)
				actual_billed = max(total_billed - previous_billed, 0)
				already_billed_map[item_code] = total_billed

				issued = issue_map.get((item_code, si.name), 0)

				next_issued = issue_map.get((item_code, next_si), 0) if next_si else 0

				balance_to_issue = actual_billed - issued
				pending_to_issue = balance_to_issue - next_issued

				data.append({
					"company": company,
					"project_budget": project_budget,
					"sales_order": sales_order,
					"posting_date": si.posting_date,
					"posting_time": si.posting_time,
					"sales_invoice": si.name,
					"item": item_code,
					"delivered": info["delivered_qty"],
					"actual_delivered": total_billed,
					"billed": info["billed_qty"],
					"actual_billed": actual_billed,
					"difference_in_billed": info["billed_qty"] - total_billed,
					"issued": issued,
					"balance_to_issue": balance_to_issue,
					"pending_to_issue": pending_to_issue,
				})


	return data

# Report Helpers --

def get_delivery_map():
	rows = frappe.db.sql("""

		-- 1️⃣ WIP normal items
		SELECT
			dni.item_code,
			dnw.sales_order,
			TIMESTAMP(dnw.posting_date, dnw.posting_time) AS ts,
			SUM(dni.qty) AS qty
		FROM `tabDelivery Note Item` dni
		JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
		WHERE
			dnw.docstatus = 1
			AND dnw.is_return = 0
			AND dni.parentfield = 'items'
		GROUP BY dni.item_code, dnw.sales_order, ts

		UNION ALL

		-- 2️⃣ WIP return items
		SELECT
			dni.item_code,
			dnw.sales_order,
			TIMESTAMP(dnw.posting_date, dnw.posting_time) AS ts,
			SUM(dni.qty) AS qty
		FROM `tabDelivery Note Item` dni
		JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
		WHERE
			dnw.docstatus = 1
			AND dnw.is_return = 1
			AND dni.parentfield = 'return_item'
		GROUP BY dni.item_code, dnw.sales_order, ts

		UNION ALL

		-- 3️⃣ Normal Delivery Note
		SELECT
			dni.item_code,
			dn.sales_order,
			TIMESTAMP(dn.posting_date, dn.posting_time) AS ts,
			SUM(dni.qty) AS qty
		FROM `tabDelivery Note Item` dni
		JOIN `tabDelivery Note` dn ON dni.parent = dn.name
		WHERE
			dn.docstatus = 1
		GROUP BY dni.item_code, dn.sales_order, ts

	""", as_dict=True)

	delivery_map = defaultdict(list)
	for r in rows:
		key = (r.item_code, r.sales_order)
		delivery_map[key].append((r.ts, r.qty))

	return delivery_map

def get_issue_map():
	rows = frappe.db.sql("""
		SELECT
			sed.item_code,
			si.reference_number AS sales_invoice,
			SUM(sed.qty) AS qty
		FROM `tabStock Entry Detail` sed
		JOIN `tabStock Entry` si ON sed.parent = si.name
		WHERE
			si.docstatus = 1
			AND si.stock_entry_type = 'Material Issue'
			AND si.custom_reference_type = 'Sales Invoice'
		GROUP BY sed.item_code, si.reference_number
	""", as_dict=True)

	return {
		(r.item_code, r.sales_invoice): r.qty
		for r in rows
	}


# Ṣtock Entry Creations --

@frappe.whitelist()
def process_stock_issue(project_budget=None):
	frappe.enqueue(
		method="electra.electra.report.stock_in_hand_wip_test.stock_in_hand_wip_test.make_stock_entry",
		queue="long",
		timeout=10000,
		project_budget=project_budget
	)
	
@frappe.whitelist()
def make_stock_entry(project_budget):
	
	if not project_budget:
		project_budgets = frappe.get_all("Project Budget", {"docstatus": 1}, pluck="name")
	else:
		project_budgets = [project_budget]
  
	no_of_project_budgets = len(project_budgets)

	for i,project_budget in enumerate(project_budgets, start=1):
		# Progrss Bar
		frappe.publish_progress(
			percent=int((i / no_of_project_budgets) * 100),
			title="Issuing Stocks",
			description=f"{project_budget} - {i}/{no_of_project_budgets}"
		)
		query = """UPDATE `tabProject Budget Items` set billed_qty = 0 where parent = '%s'""" %(project_budget)
		frappe.db.sql(query)
  
		project_budget_doc = frappe.get_doc("Project Budget", project_budget)
		sales_order = project_budget_doc.sales_order
		project = frappe.db.get_value("Project", {"sales_order": sales_order}, "name")
		company = project_budget_doc.company
		if frappe.db.exists("Sales Order", {"docstatus": 1, "name": sales_order}):
			sales_invoices = frappe.db.get_all("Sales Invoice", {"docstatus": 1, "sales_order": sales_order}, order_by="posting_date asc, posting_time asc", pluck="name")
			already_billed_map = {}
			for sales_invoice in sales_invoices:
				sales_invoice_posting_date = frappe.db.get_value("Sales Invoice", sales_invoice, "posting_date")
				sales_invoice_posting_time = frappe.db.get_value("Sales Invoice", sales_invoice, "posting_time")
				next_si = frappe.db.sql("""
					SELECT name
					FROM `tabSales Invoice`
					WHERE TIMESTAMP(posting_date, posting_time) > TIMESTAMP(%s, %s)
						AND so_no = %s
						AND docstatus = 1
					ORDER BY TIMESTAMP(posting_date, posting_time) ASC
					LIMIT 1
				""", (sales_invoice_posting_date, sales_invoice_posting_time, sales_order), as_dict=True)
				next_sales_invoice = next_si[0]["name"] if next_si else None
	
				item_details = []
	
				for item in project_budget_doc.item_table:
					key = f"{item.item}"
					delivered = item.delivered_qty
					dn_wip_qty = frappe.db.sql(
							"""SELECT SUM(dni.qty) AS billable_qty
							FROM `tabDelivery Note Item` dni
							INNER JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
							WHERE dni.item_code = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND dnw.is_return = 0 AND parentfield = 'items' AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
							(item.item, sales_order, sales_invoice_posting_date, sales_invoice_posting_time),
							as_dict=True
						)[0].get("billable_qty") or 0
					dn_wip_qty_return = frappe.db.sql(
							"""SELECT SUM(dni.qty) AS billable_qty
							FROM `tabDelivery Note Item` dni
							INNER JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
							WHERE dni.item_code = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND dnw.is_return = 1 AND parentfield = 'return_item' AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
							(item.item, sales_order, sales_invoice_posting_date, sales_invoice_posting_time),
							as_dict=True
						)[0].get("billable_qty") or 0
					dn_qty = frappe.db.sql(
							"""SELECT SUM(dni.qty) AS billable_qty
							FROM `tabDelivery Note Item` dni
							INNER JOIN `tabDelivery Note` dnw ON dni.parent = dnw.name
							WHERE dni.item_code = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
							(item.item, sales_order, sales_invoice_posting_date, sales_invoice_posting_time),
							as_dict=True
						)[0].get("billable_qty") or 0
					actual_delivered = dn_qty + dn_wip_qty + dn_wip_qty_return
	
					billed = item.billed_qty
				
					total_billed = dn_qty + dn_wip_qty + dn_wip_qty_return
	
					previous_billed = already_billed_map.get(key, 0)
					actual_billed = total_billed - previous_billed if total_billed - previous_billed > 0 else 0
					already_billed_map[key] = total_billed
					difference_in_billed = billed - total_billed
					
					stock_issued_qty = frappe.db.sql("""
						SELECT SUM(sed.qty) AS qty
						FROM `tabStock Entry Detail` sed
						INNER JOIN `tabStock Entry` si ON sed.parent = si.name
						WHERE sed.item_code = %s AND si.docstatus = 1
							AND si.stock_entry_type = 'Material Issue'
							AND si.custom_reference_type = 'Sales Invoice' AND si.reference_number = %s
							
							
					""", (item.item, sales_invoice), as_dict=True)[0].get("qty") or 0
					issued = stock_issued_qty
					balance_to_issue = actual_billed - issued
					
					pending_to_issue = 0
					if next_sales_invoice:
						next_sales_invoice_stock_out_qty = frappe.db.sql("""
							SELECT SUM(sed.qty) AS qty
							FROM `tabStock Entry Detail` sed
							INNER JOIN `tabStock Entry` si ON sed.parent = si.name
							WHERE sed.item_code = %s AND si.docstatus = 1
								AND si.stock_entry_type = 'Material Issue'
								AND si.custom_reference_type = 'Sales Invoice' AND si.reference_number = %s
								
								
						""", (item.item, next_sales_invoice), as_dict=True)[0].get("qty") or 0
						pending_to_issue = balance_to_issue - next_sales_invoice_stock_out_qty
					item_details.append({
						"item": item.item,
						"billed_qty": actual_billed,
						"issued_qty": issued,
						"qty": actual_billed - issued,
						"unit": item.unit,
						"rate_with_overheads": item.rate_with_overheads,
						"pb_doctype": item.pb_doctype,
					})
					frappe.db.set_value("Project Budget Items", item.name, "billed_qty", item.billed_qty + actual_billed - issued)
				
				create_stock_entry(
					company=company, 
					posting_date = sales_invoice_posting_date, 
					posting_time = sales_invoice_posting_time,
					reference_number = sales_invoice,
					reference_type = "Sales Invoice",
					project = project,
					project_budget = project_budget,
					item_details = item_details
				)

def create_stock_entry(company, posting_date, posting_time, reference_number, reference_type, project, project_budget, item_details):
	project_budget_doc = frappe.get_doc("Project Budget", project_budget)
	se = frappe.new_doc("Stock Entry")
	se.stock_entry_type = "Material Issue" 
	se.set_posting_time = 1
	se.posting_date=posting_date
	se.posting_time=posting_time
	se.company = company
	se.reference_number = reference_number
	se.custom_reference_type = reference_type
	posting_time = frappe.utils.format_time(posting_time)
	set_warehouse = frappe.db.get_value("Warehouse",{'warehouse_name': ['like', '%Work In Progress%'],'company':company},'name')
	for item in item_details:
		if item.get('qty') > 0:
			if frappe.db.exists("Item", {'name': item.get('item'), 'is_stock_item': 1}):
				se.append("items",{
					's_warehouse':set_warehouse,
					'item_code':item.get('item'),
					'transfer_qty':(item.get('qty')),
					'uom':item.get('unit'),
					'stock_uom':frappe.get_value('Item',item.get('item'),'stock_uom'),
					'conversion_factor': 1,
					'qty':(item.get('qty')),
					'basic_rate':item.get('rate_with_overheads'),
					'project':project
				})

			# do.billed_qty += (item.get('qty'))
			# do.save(ignore_permissions=True)
   
	if len(se.items) > 0:
		se.save(ignore_permissions=True)
		
		# try:
		# 	se.submit()
		# except Exception:
		# 	frappe.log_error(
		# 		message=frappe.get_traceback(),
		# 		title=f"Stock Entry Failed | PB: {project_budget} | SI: {reference_number}",
		# 		reference_doctype = "Sales Invoice",
		# 		reference_name = reference_number
		# 	)
  
	# project_budget_doc.flags.ignore_validate_update_after_submit = True
	# project_budget_doc.save(ignore_permissions=True)
 
def update_stock_qty():
	stock_entries = frappe.db.get_all("Stock Entry", {"custom_reference_type": "Sales Invoice", "docstatus": 0}, ["name", "posting_date", "posting_time"])
	count = 0
	for stock_entry in stock_entries:
		count += 1
		print([count, stock_entry])
		se = frappe.get_doc("Stock Entry", stock_entry.name)
		for item in se.items:
			available_qty = get_stock_at_datetime(
				item_code=item.item_code,
				warehouse=item.s_warehouse,
				posting_date=stock_entry.posting_date,
				posting_time=stock_entry.posting_time
			)
			if item.qty > available_qty:
				print([item.item_code, available_qty])
				frappe.db.set_value("Stock Entry Detail", item.name, "qty", available_qty)
   
def get_stock_at_datetime(item_code, warehouse, posting_date, posting_time):
	dt = get_datetime(f"{posting_date} {posting_time}")

	sle = frappe.db.sql("""
		SELECT qty_after_transaction
		FROM `tabStock Ledger Entry`
		WHERE item_code = %s
			AND warehouse = %s
			AND TIMESTAMP(posting_date, posting_time) <= %s
			AND is_cancelled = 0
		ORDER BY posting_date DESC, posting_time DESC, creation DESC
		LIMIT 1
	""", (item_code, warehouse, dt), as_dict=True)

	return sle[0].qty_after_transaction if sle else 0

def remove_items_with_zero_qty():
	stock_entries = frappe.db.get_all(
		"Stock Entry",
		{"custom_reference_type": "Sales Invoice", "docstatus": 0},
		["name"]
	)

	for se_row in stock_entries:
		se = frappe.get_doc("Stock Entry", se_row.name)

		# iterate on copy, because we are removing
		for row in list(se.items):
			if row.qty == 0:
				se.remove(row)

		se.save(ignore_permissions=True)
