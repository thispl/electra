from __future__ import unicode_literals
import json
from re import S
from unicodedata import name
from datetime import datetime
from datetime import date, timedelta
import calendar
from erpnext.stock.get_item_details import get_item_price
import frappe
from frappe import _
from frappe.utils import cstr, add_days, date_diff, getdate, format_date, fmt_money
from frappe.utils import flt
from erpnext.selling.doctype.customer.customer import get_customer_outstanding, get_credit_limit
from erpnext.stock.get_item_details import get_valuation_rate
from frappe.utils.background_jobs import enqueue
from frappe.utils import (
	add_days,
	add_months,
	cint,
	date_diff,
	flt,
	get_first_day,
	get_last_day,
	get_link_to_form,
	getdate,
	rounded,
	today,
)
import json


@frappe.whitelist()
def get_project_dashboard(doc):
	project = json.loads(doc)
	so = project['sales_order']
	name = project['name']
	project_budget = project["budgeting"]
	cost_estimation = frappe.db.get_value("Project Budget",project['budgeting'],['cost_estimation'])
	val = frappe.db.get_value("Cost Estimation",cost_estimation,['total_bidding_price']) or 0
	deliver = frappe.db.get_value("Sales Order",project['sales_order'],['per_delivered'])
	if deliver:
		deliver = deliver
	else:
		deliver = 0
	deliver = 100 - deliver
	total_cost = project_cost_till_date(name)
	pb = frappe.db.sql(""" select * from `tabProject Budget` where name = '%s' and docstatus = 1 """%(project['budgeting']),as_dict=True)
	user = frappe.session.user
	user_roles = frappe.get_roles(user)
	revised_contract_value = frappe.db.get_value("Sales Order", project['sales_order'], "net_bidding_price")
 
	sales_in = frappe.db.sql(
		""" SELECT SUM(custom_total_invoice_amount - discount_amount) as total FROM `tabSales Invoice` WHERE project = %s and docstatus = 1""",
		(project['name'],),
		as_dict=True)[0]
	if not sales_in["total"]:
		sales_in["total"] = 0
	invoiced_value = sales_in["total"]
	total_gross_profit = (invoiced_value - total_cost)
	if sales_in["total"] > 0:
		total_gross_profit_percent = (total_gross_profit / invoiced_value) * 100
	else:
		total_gross_profit_percent = 0
 
	for i in pb:
		project_name,lead_customer = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['project_name','lead_customer'])
		project = frappe.db.get_value("Project",{'budgeting':i.name},['name'])
		percent_complete = frappe.db.get_value("Project",{'budgeting':i.name},['percent_complete'])
		if not percent_complete:
			percent_complete = 0
		total_costing_amount = frappe.db.get_value("Project",{'budgeting':i.name},['total_costing_amount'])
		if not total_costing_amount:
			total_costing_amount = 0
		total_purchase_cost = frappe.db.get_value("Project",{'budgeting':i.name},['total_purchase_cost'])
		if not total_purchase_cost:
			total_purchase_cost = 0
		purch_inv = total_purchase_cost + total_costing_amount
		ce = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['total_bidding_price'])
		per_to_complete = (100 - percent_complete)
		per_complete = str(percent_complete) + '%'
		perc = str(per_to_complete) + '%'
		to_complete = (per_to_complete/100) * i.total_bidding_price
		
		estimated_gross_profit = revised_contract_value - i.total_cost_of_the_project
		estimated_gross_profit_percent = (estimated_gross_profit / revised_contract_value) * 100
		if project:
			new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order` left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent	where `tabSales Order`.name = '%s' and `tabSales Order`.status != "Closed" """ % (so), as_dict=True)[0]
			if not new_so['qty']:
				new_so['qty'] = 0
			if not new_so['d_qty']:
				new_so['d_qty'] = 0
			del_total = new_so['qty'] - new_so['d_qty']
			pending_task_qty = frappe.db.sql("""select sum(`tabTask`.pending_qty) as qty from `tabTask` where `tabTask`.project = '%s' """ % (name),
			as_dict=True)[0]
			
			task_complete = frappe.db.sql("""select  sum(`tabTask`.qty) as qty ,sum(`tabTask`.completed_qty) as completed_qty  from `tabTask` where `tabTask`.project = '%s' """ %(name),as_dict=True)[0]
			if task_complete['qty']:
				total_qty = task_complete["qty"]
				total_completed_qty = task_complete["completed_qty"]
				complete_qty = (total_completed_qty / total_qty) * 100
				not_complete = 100 - complete_qty
			else:
				total_qty = 0
				total_completed_qty = 0
				complete_qty = 0
				not_complete = 0
		
						
		html = frappe.render_template(
			"templates/pages/project_dashboard.html",
			{
				"doc": doc,
				"so":so,
				"name":name,
				"val":fmt_money(round(val, 2), currency="QAR"),
				"project_budget":project_budget,
				"estimated_cost":fmt_money(round(i.total_cost_of_the_project,2), currency="QAR"),
				"total_cost":fmt_money(round(total_cost ,2), currency="QAR"),
				"bid":fmt_money(round(revised_contract_value,2), currency="QAR"),
				"ce":ce,
				"to_complete":round(to_complete,2),
				"net_profit_amount":round(i.net_profit_amount,2),
				"percent_complete":per_complete,
				"perc":perc,
				"deliver":round(deliver,2),
				"cost_estimation":i.cost_estimation,
				"to_supply":del_total,
				"pending_task_qty":pending_task_qty['qty'],
				"complete_qty":complete_qty,
				"not_complete":not_complete,
				'est_gross_profit':fmt_money(round(estimated_gross_profit, 2), currency="QAR"),
				'total_gross_profit':fmt_money(round(total_gross_profit, 2), currency="QAR"),
				'profit':round(i.gross_profit_percent),
				'invoice_value': fmt_money(round(invoiced_value, 2), currency="QAR"),
				'bal': round((revised_contract_value - invoiced_value), 2),
				'est_gross_profit_percent': round(estimated_gross_profit_percent, 2),
				'total_gross_profit_percent': round(total_gross_profit_percent, 2),
			},
		)
		return html
	
@frappe.whitelist()
def project_cost_till_date(name):
	project = name
	
	total = (total_dn_cost(project) + 
			 total_dnwip_cost(project) + 
			 total_jl_cost(project) + 
			 total_cost_by_timesheet(project))
	return total


@frappe.whitelist()
def total_dn_cost(project):
	project_budget = frappe.db.get_value("Project", project, "budgeting")
	pb = frappe.get_doc("Project Budget", project_budget)
 
	data = {}
	project_name = project
	
	if pb.docname_updated_in_dn == 1:
		for item in pb.item_table:
			dn_data = frappe.db.sql(
				"""
				SELECT 
					dni.item_code, 
					dni.qty,
					(
						SELECT sle.valuation_rate 
						FROM `tabStock Ledger Entry` sle 
						WHERE sle.item_code = dni.item_code 
						AND sle.voucher_no = dn.name 
						ORDER BY sle.creation DESC 
						LIMIT 1
					) AS valuation_rate
				FROM `tabDelivery Note` dn
				LEFT JOIN `tabDelivery Note Item` dni 
					ON dn.name = dni.parent
				WHERE dni.item_code = %s 
				AND dni.custom_docname = %s
				AND dn.project = %s 
				""",
				(item.item, item.docname, project_name),
				as_dict=True
			) or []

			# Process fetched data
			for i in dn_data:
				item_code = i.item_code
				qty = i.qty or 0
				valuation_rate = i.valuation_rate or 0
				amount = qty * valuation_rate

				# Store data in dictionary
				if item_code in data:
					data[item_code]["total_qty"] += qty
					data[item_code]["total_amount"] += amount
				else:
					data[item_code] = {
						"total_qty": qty,
						"total_amount": amount
					}

		total_amount = sum(d["total_amount"] for d in data.values())
	else:
		for item in pb.item_table:
			dn_data = frappe.db.sql(
				"""
				SELECT 
					dni.item_code, 
					dni.qty,
					(
						SELECT sle.valuation_rate 
						FROM `tabStock Ledger Entry` sle 
						WHERE sle.item_code = dni.item_code 
						AND sle.voucher_no = dn.name 
						ORDER BY sle.creation DESC 
						LIMIT 1
					) AS valuation_rate
				FROM `tabDelivery Note` dn
				LEFT JOIN `tabDelivery Note Item` dni 
					ON dn.name = dni.parent
				WHERE dni.item_code = %s 
				AND dn.project = %s 
				""",
				(item.item, project_name),
				as_dict=True
			) or []

			# Process fetched data
			for i in dn_data:
				item_code = i.item_code
				qty = i.qty or 0
				valuation_rate = i.valuation_rate or 0
				amount = qty * valuation_rate

				# Store data in dictionary
				if item_code in data:
					data[item_code]["total_qty"] += qty
					data[item_code]["total_amount"] += amount
				else:
					data[item_code] = {
						"total_qty": qty,
						"total_amount": amount
					}

		total_amount = sum(d["total_amount"] for d in data.values())
	return round(total_amount, 2)

@frappe.whitelist()
def total_jl_cost(project):
	journal_entry = frappe.db.sql("""
		SELECT SUM(c.debit_in_account_currency) AS cost 
		FROM `tabJournal Entry` jl 
		INNER JOIN `tabJournal Entry Account` c ON c.parent = jl.name 
		WHERE c.project = %s AND jl.docstatus = 1 
		GROUP BY c.project
	""", (project,), as_dict=True)
	
	return round(journal_entry[0].cost, 2) if journal_entry else 0

@frappe.whitelist()
def total_cost_by_timesheet(project):
	timesheet = frappe.db.sql("""
		SELECT SUM(c.costing_amount) AS cost 
		FROM `tabTimesheet` p 
		INNER JOIN `tabTimesheet Detail` c ON c.parent = p.name 
		WHERE c.project = %s AND p.docstatus = 1 
		GROUP BY c.project
	""", (project,), as_dict=True)
	return round(timesheet[0].cost, 2) if timesheet else 0

@frappe.whitelist()
def total_dnwip_cost(project):
	sales_order = frappe.db.get_value("Sales Order", {"project": project}, "name")
	pb_name = frappe.db.get_value("Project", project, "budgeting")
	pb = frappe.get_doc("Project Budget", pb_name)

	# Fetch all relevant Delivery Note WIP names in bulk
	dn_wip_list = frappe.get_all(
		"Delivery Note WIP",
		filters={"sales_order": sales_order, "is_return": 0, "docstatus": 1},
		pluck="name"
	)

	if not dn_wip_list:
		return 0

	# Fetch all relevant Delivery Note WIP items in bulk
	dn_wip_items = frappe.db.sql("""
		SELECT dni.parent AS dn_wip_name, dni.item_code, dni.qty, dni.custom_against_pbsow
		FROM `tabDelivery Note Item` dni
		WHERE dni.parent IN %(dn_wip_list)s
	""", {"dn_wip_list": dn_wip_list}, as_dict=True)

	# Group quantities by (dn_wip_name, item_code, custom_against_pbsow)
	item_qty_map = {}
	for i in dn_wip_items:
		key = (i.dn_wip_name, i.item_code, i.custom_against_pbsow)
		item_qty_map[key] = item_qty_map.get(key, 0) + i.qty

	# Fetch Stock Entry rates in bulk
	stock_entry_data = frappe.db.sql("""
		SELECT se.reference_number, sei.item_code, sei.basic_rate, sei.qty
		FROM `tabStock Entry` se
		JOIN `tabStock Entry Detail` sei ON se.name = sei.parent
		WHERE se.stock_entry_type = 'Material Transfer'
		AND se.docstatus = 1
		AND se.reference_number IN %(dn_wip_list)s
	""", {"dn_wip_list": dn_wip_list}, as_dict=True)

	# Store stock rates in a dictionary with weighted rate calculation
	stock_entries = {}
	for entry in stock_entry_data:
		key = (entry.reference_number, entry.item_code)
		if key in stock_entries:
			stock_entries[key]['total_value'] += entry.basic_rate * entry.qty
			stock_entries[key]['total_qty'] += entry.qty
		else:
			stock_entries[key] = {'total_value': entry.basic_rate * entry.qty, 'total_qty': entry.qty}

	# Calculate the correct weighted average rate
	stock_rates = {}
	for key, values in stock_entries.items():
		stock_rates[key] = values['total_value'] / values['total_qty'] if values['total_qty'] > 0 else 0

	amount = 0

	# Calculate total amount using correct stock rates
	for child in pb.item_table:
		total_item_qty = 0
		weighted_rate_sum = 0
		total_rate_qty = 0  # Used for calculating weighted avg

		for dn_wip in dn_wip_list:
			key = (dn_wip, child.item, child.docname)
			if key in item_qty_map:
				item_qty = item_qty_map[key]
				total_item_qty += item_qty

				if (dn_wip, child.item) in stock_rates:
					rate = stock_rates[(dn_wip, child.item)]
					weighted_rate_sum += rate * item_qty
					total_rate_qty += item_qty

		# Compute weighted average rate
		final_rate = weighted_rate_sum / total_rate_qty if total_rate_qty > 0 else 0

		amount += final_rate * total_item_qty

	return amount


