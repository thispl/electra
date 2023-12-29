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
		_("Customer") + ":Data/:200",
		_("Sales Order No.") + ":Link/Sales Order:170",
		_("Project No.") + ":Link/Project:170",
		_("Order Value") + ":Currency/:110",
		_("Invoice Value Till Date") + ":Currency/:110",
		_("Cost Till Date") + ":Currency/:110",
		_("Gross Profit") + ":Currency/:110",
		_("Percentage of Gross Profit") + ":Currency/:110",
		_("Balance to Invoice") + ":Currency/:110",
		_("Total Collection") + ":Currency/:110",
		_("Outstanding Receipts") + ":Currency/:110",
		# _("Progress Bills Raised Current Year") + ":Currency/:110",
		# _("Revenue Recognised upto Previous Year") + ":Currency/:110",
		# _("Revenue for the Current Year") + ":Currency/:110",
		# _("Short/(Excess) Revenue Over Billings") + ":Currency/:110",
		# _("Percentage to be Completed") + ":Percentage/:110",
		# _("Value to be Executed") + ":Currency/:110",
	]
	return columns
def get_data(filters):
	data = []
	pb = frappe.db.sql(""" select * from `tabProject Budget` where company = '%s' and docstatus = 1 """%(filters.company),as_dict=True)
	for i in pb:
		project_name,lead_customer = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['project_name','lead_customer'])
		project = frappe.db.get_value("Project",{'budgeting':i.name},['name'])
		saleorder = frappe.db.get_value("Project",{'budgeting':i.name},['sales_order'])
		grand = frappe.db.get_value("Sales Order",{'project':project},['grand_total'])
		
		
		# print(tot)

		percent_total = frappe.db.get_value("Project",{'budgeting':i.name},['percent_complete'])
		if not percent_total:
			percent_total = 0
		total_costing_amount = frappe.db.get_value("Project",{'budgeting':i.name},['total_costing_amount'])
		if not total_costing_amount:
			total_costing_amount = 0
		total_purchase_cost = frappe.db.get_value("Project",{'budgeting':i.name},['total_purchase_cost'])
		if not total_purchase_cost:
			total_purchase_cost = 0
		purch_inv = total_purchase_cost + total_costing_amount
		ce = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['total_bidding_price'])
		per_to_complete = (100 - percent_total)
		perc = str(per_to_complete) + '%'
		to_complete = (per_to_complete/100) * i.total_bidding_price

		if project:			
			sales_in = frappe.db.sql(""" select sum(grand_total) as total from `tabSales Invoice` where project = '%s' """%(project),as_dict=True)[0]
			revenue = frappe.db.sql(""" select sum(paid_amount) as amt from `tabPayment Entry` where project = '%s' """%(project),as_dict=True)[0]
			
			tot = 0
			dn_list = frappe.db.get_list("Delivery Note",{'project':project})
			if dn_list:
				for d_list in dn_list:
					dn = frappe.get_doc("Delivery Note",d_list.name)
					for d in dn.items:
						w_house = frappe.db.get_value("Warehouse",{'company':dn.company,'default_for_stock_transfer':1},['name'])
						val = frappe.db.get_value("Bin",{"item_code":d.item_code,"warehouse":w_house},['valuation_rate'])
						total = val * d.qty
						tot+=total
			prof = grand - tot
			gp = (prof / grand)*100
			if not sales_in["total"]:
				sales_in["total"] = 0
			bal = grand - sales_in["total"]
			if not revenue["amt"]:
				revenue["amt"] = 0
			out = grand - revenue["amt"]
			
			row = [lead_customer,saleorder,project,grand,sales_in["total"] or 0,tot,prof,gp,bal,revenue["amt"] or 0,out]
			data.append(row)
	return data	