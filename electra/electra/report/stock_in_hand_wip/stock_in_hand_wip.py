# Copyright (c) 2026, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _


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
			_("Docname") + ":Data:180",
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
			_("Docname") + ":Data:180",
			_("Delivered") + ":Float:150",
			_("Billed") + ":Float:150",
			# _("Total Billed") + ":Float:150",
			_("Actual Billed") + ":Float:150",
			_("Issued") + ":Float:150",
			_("Balance to Issue") + ":Float:150",
			_("Pending to Issue") + ":Float:150",
		]
	return columns

def get_data(filters):
	data = []
	
	if not filters.get("project_budget"):
		project_budgets = frappe.get_all("Project Budget", {"docstatus": 1}, pluck="name")
	else:
		project_budgets = [filters.get("project_budget")]

	if not filters.get("consolidate_invoices"):
		for project_budget in project_budgets:
			project_budget_doc = frappe.get_doc("Project Budget", project_budget)
			sales_order = project_budget_doc.sales_order
			company = project_budget_doc.company
			if frappe.db.exists("Sales Order", {"docstatus": 1, "name": sales_order}):
				sales_invoices = frappe.db.get_all("Sales Invoice", {"docstatus": 1, "sales_order": sales_order}, distinct=True, order_by="posting_date asc, posting_time asc", pluck="name")
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
	 
					for item in project_budget_doc.item_table:
						key = f"{item.item}-{item.docname}"
						delivered = item.delivered_qty
						dn_wip_qty = frappe.db.sql(
								"""SELECT SUM(dni.qty) AS billable_qty
								FROM `tabDelivery Note Item` dni
								INNER JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
								WHERE dni.item_code = %s AND dni.custom_against_pbsow = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
								(item.item, item.docname, sales_order, sales_invoice_posting_date, sales_invoice_posting_time),
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
						actual_delivered = dn_qty + dn_wip_qty
		
						billed = item.billed_qty
					
						dn_wip_qty = frappe.db.sql(
								"""SELECT SUM(dni.qty) AS billable_qty
								FROM `tabDelivery Note Item` dni
								INNER JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
								WHERE dni.item_code = %s AND dni.custom_against_pbsow = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
								(item.item, item.docname, sales_order, sales_invoice_posting_date, sales_invoice_posting_time),
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
						total_billed = dn_qty + dn_wip_qty
		
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
								AND sed.custom_against_pb = %s
								
						""", (item.item, sales_invoice, item.docname), as_dict=True)[0].get("qty") or 0
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
									AND sed.custom_against_pb = %s
									
							""", (item.item, next_sales_invoice, item.docname), as_dict=True)[0].get("qty") or 0
							pending_to_issue = balance_to_issue - next_sales_invoice_stock_out_qty
						data.append({
							"company": company,
							"project_budget": project_budget,
							"sales_order": sales_order,
							"sales_invoice": sales_invoice,
							"item": item.item,
							"docname": item.docname,
							"delivered": delivered,
							"actual_delivered": actual_delivered,
							"billed": billed,
							"total_billed": total_billed,
							"actual_billed": actual_billed,
							"difference_in_billed": difference_in_billed,
							"issued": issued,
							"balance_to_issue": balance_to_issue,
							"pending_to_issue": pending_to_issue,
						})
	  
	else:
		data = []
		consolidated = {}
  
		if not filters.get("project_budget"):
			project_budgets = frappe.get_all("Project Budget", {"docstatus": 1}, pluck="name")
		else:
			project_budgets = [filters.get("project_budget")]

		for project_budget in project_budgets:
			project_budget_doc = frappe.get_doc("Project Budget", project_budget)
			sales_order = project_budget_doc.sales_order
	
			if frappe.db.exists("Sales Order", {"docstatus": 1, "name": sales_order}):
				sales_invoices = frappe.db.get_all("Sales Invoice", {"docstatus": 1, "sales_order": sales_order}, distinct=True, order_by="posting_date asc, posting_time asc", pluck="name")
				already_billed_map = {}
				
				for sales_invoice in sales_invoices:
					sales_invoice_posting_date = frappe.db.get_value("Sales Invoice", sales_invoice, "posting_date")
					sales_invoice_posting_time = frappe.db.get_value("Sales Invoice", sales_invoice, "posting_time")
		
					for item in project_budget_doc.item_table:
						key = f"{item.item}-{item.docname}"
						delivered = item.delivered_qty
						dn_wip_qty = frappe.db.sql(
								"""SELECT SUM(dni.qty) AS billable_qty
								FROM `tabDelivery Note Item` dni
								INNER JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
								WHERE dni.item_code = %s AND dni.custom_against_pbsow = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
								(item.item, item.docname, sales_order, sales_invoice_posting_date, sales_invoice_posting_time),
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
						actual_delivered = dn_qty + dn_wip_qty
		
						billed = item.billed_qty
					
						dn_wip_qty = frappe.db.sql(
								"""SELECT SUM(dni.qty) AS billable_qty
								FROM `tabDelivery Note Item` dni
								INNER JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
								WHERE dni.item_code = %s AND dni.custom_against_pbsow = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
								(item.item, item.docname, sales_order, sales_invoice_posting_date, sales_invoice_posting_time),
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
						actual_billed = dn_qty + dn_wip_qty
		
						previous_billed = already_billed_map.get(key, 0)
						already_billed_map[key] = actual_billed
						difference_in_billed = billed - actual_billed
						
						stock_issued_qty = frappe.db.sql("""
							SELECT SUM(sed.qty) AS qty
							FROM `tabStock Entry Detail` sed
							INNER JOIN `tabStock Entry` si ON sed.parent = si.name
							WHERE sed.item_code = %s AND si.docstatus = 1
								AND si.stock_entry_type = 'Material Issue'
								AND si.custom_reference_type = 'Sales Invoice' AND si.reference_number = %s
								AND sed.custom_against_pb = %s
								
						""", (item.item, sales_invoice, item.docname), as_dict=True)[0].get("qty") or 0
						issued = stock_issued_qty
						balance_to_issue = actual_billed - issued

						key = (project_budget, sales_order, item.item, item.docname)
						if key not in consolidated:
							consolidated[key] = {
								"project_budget": project_budget,
								"sales_order": sales_order,
								"item": item.item,
								"docname": item.docname,
								"delivered": 0,
								"actual_delivered": 0,
								"billed": 0,
								"actual_billed": 0,
								"difference_in_billed": 0,
								"issued": 0,
								"balance_to_issue": 0,
							}
	   
						consolidated[key]["delivered"] = delivered
						consolidated[key]["actual_delivered"] = actual_delivered
						consolidated[key]["billed"] = billed
						consolidated[key]["actual_billed"] = actual_billed
						consolidated[key]["difference_in_billed"] = billed - actual_billed
						consolidated[key]["issued"] += issued
						consolidated[key]["balance_to_issue"] = actual_billed - consolidated[key]["issued"]
		data = list(consolidated.values())	

	return data

@frappe.whitelist()
def process_stock_issue(project_budget=None):
	frappe.enqueue(
		method="electra.electra.report.stock_in_hand_wip.stock_in_hand_wip.make_stock_entry",
		queue="long",
		timeout=600,
		project_budget=project_budget
	)

@frappe.whitelist()
def make_stock_entry(project_budget=None):
	if project_budget:
		project_budgets = [project_budget]
	else:
		project_budgets = frappe.db.get_all("Project Budget", {"docstatus": 1, "workflow_state": "Approved"},  pluck="name")
	no_of_project_budgets = len(project_budgets)
	
	for i,project_budget in enumerate(project_budgets, start=1):
		# Progress Bar
		frappe.publish_progress(
			percent=int((i / no_of_project_budgets) * 100),
			title="Issuing Stocks",
			description=f"{project_budget} - {i}/{no_of_project_budgets}"
		)
		
		project_budget_doc = frappe.get_doc("Project Budget", project_budget)
		sales_order = project_budget_doc.sales_order
		
		if not frappe.db.exists("Sales Order", {"docstatus": 1, "name": sales_order}):
			frappe.log_error(
				message=f"{sales_order} is not a submitted document",
				title=f"Invalid DocStatus - {sales_order}",
				reference_doctype = "Project Budget",
				reference_name = project_budget
			)
			
		# frappe.db.set_value("Project Budget Items", {"parent": project_budget}, "billed_qty", 0)
		query = """UPDATE `tabProject Budget Items` set billed_qty = 0 where parent = '%s'""" %(project_budget)
		frappe.db.sql(query)
		frappe.db.commit()
  
		sales_invoices = frappe.db.get_all("Sales Invoice", {"docstatus": 1, "sales_order": sales_order}, distinct=True, order_by="posting_date asc, posting_time asc", pluck="name")
		
		for sales_invoice in sales_invoices:
			try:
				sales_invoice_doc = frappe.get_doc("Sales Invoice", sales_invoice)
				create_stock_entry_for_invoice(sales_invoice_doc)

			except Exception:
				frappe.log_error(
					message=frappe.get_traceback(),
					title=f"Stock Entry Failed | PB: {project_budget} | SI: {sales_invoice}",
					reference_doctype = "Sales Invoice",
					reference_name = sales_invoice
				)
				continue
				
def create_stock_entry_for_invoice(doc):
	se_items = []
	project=frappe.get_value("Sales Order",{'name':doc.so_no},['project'])
	if doc.order_type =="Project":
		if doc.is_return==0:
			project_budget = frappe.db.get_value("Sales Order",doc.so_no,'project_budget')
			pb = frappe.get_doc("Project Budget", project_budget)
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Issue" 
			se.set_posting_time = 1
			se.posting_date=doc.posting_date
			se.posting_time=doc.posting_time
			se.company = doc.company
			se.reference_number = doc.name
			se.custom_reference_type = "Sales Invoice"
			posting_time = frappe.utils.format_time(doc.posting_time)
			set_warehouse = frappe.db.get_value("Warehouse",{'warehouse_name': ['like', '%Work In Progress%'],'company':doc.company},'name')
			for i in pb.item_table:
				if i.delivered_qty:
					to_bill_qty = i.delivered_qty - i.billed_qty
					if to_bill_qty > 0:
						tot_bill_qty = 0
						if frappe.db.exists("Item", {'name': i.item, 'is_stock_item': 1}):
							dn_wip_qty = frappe.db.sql(
								"""SELECT SUM(dni.qty) AS billable_qty
								FROM `tabDelivery Note Item` dni
								INNER JOIN `tabDelivery Note WIP` dnw ON dni.parent = dnw.name
								WHERE dni.item_code = %s AND dni.custom_against_pbsow = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
								(i.item,i.docname, doc.so_no,doc.posting_date,posting_time),
								as_dict=True
							)
							dn_qty = frappe.db.sql(
								"""SELECT SUM(dni.qty) AS billable_qty
								FROM `tabDelivery Note Item` dni
								INNER JOIN `tabDelivery Note` dnw ON dni.parent = dnw.name
								WHERE dni.item_code = %s AND dnw.sales_order = %s AND dnw.docstatus = 1 AND TIMESTAMP(dnw.posting_date, dnw.posting_time) <= TIMESTAMP(%s, %s)""",
								(i.item, doc.so_no,doc.posting_date,posting_time),
								as_dict=True
							)
							print([dn_wip_qty, dn_qty])
							billable_qty = dn_wip_qty[0].billable_qty if dn_wip_qty and dn_wip_qty[0].billable_qty else 0
							billable_qty_dn = dn_qty[0].billable_qty if dn_qty and dn_qty[0].billable_qty else 0
							tot_bill_qty += (billable_qty + billable_qty_dn)
							if (tot_bill_qty - i.billed_qty) > 0:
								se.append("items",{
									's_warehouse':set_warehouse,
									'item_code':i.item,
									'transfer_qty':(tot_bill_qty - i.billed_qty),
									'uom':i.unit,
									'stock_uom':frappe.get_value('Item',i.item,'stock_uom'),
									'conversion_factor': 1,
									'qty':(tot_bill_qty - i.billed_qty),
									'basic_rate':i.rate_with_overheads,
									'custom_against_pb':i.docname,
									'project':project
								})
						if (tot_bill_qty - i.billed_qty)>0:
							do = frappe.get_doc(i.pb_doctype,i.docname)
							do.billed_qty += (tot_bill_qty - i.billed_qty)
							do.save(ignore_permissions=True)
							i.billed_qty += (tot_bill_qty - i.billed_qty)
							
						else:
							do = frappe.get_doc(i.pb_doctype,i.docname)
							do.billed_qty += to_bill_qty
							do.save(ignore_permissions=True)
							i.billed_qty += to_bill_qty
								
			if len(se.items) > 0:
				se.save(ignore_permissions=True)
				se.submit()
			pb.flags.ignore_validate_update_after_submit = True
			pb.save(ignore_permissions=True)
		else:
			project_budget = frappe.db.get_value("Sales Order",doc.so_no,'project_budget')
			so = frappe.get_doc("Project Budget",project_budget)
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Receipt" 
			se.company = doc.company
			se.reference_number = doc.name
			se.custom_reference_type = "Sales Invoice"
			set_warehouse = frappe.db.get_value("Warehouse",{'warehouse_name': ['like', '%Work In Progress%'],'company':doc.company},'name')
			for i in doc.custom_project_materials:
				if i.quantity:
					se.append("items",{
						't_warehouse':set_warehouse,
						'item_code':i.item_code,
						'qty':-(i.quantity),
						'basic_rate':0,
						'project':i.project
					})
					for j in so.item_table:
						if i.item_code==j.item:
							j.billed_qty += i.quantity
							do = frappe.get_doc(i.pb_doctype,i.docname)
							do.billed_qty += i.quantity
							do.save(ignore_permissions=True)
			so.flags.ignore_validate_update_after_submit = True
			so.save(ignore_permissions=True)
			se.save(ignore_permissions=True)
			se.submit()
	