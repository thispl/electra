# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
import math
from math import floor
import json
from frappe.utils import (
	add_days,
	add_months,
	cint,
	comma_and,
	flt,
	fmt_money,
	formatdate,
	get_last_day,
	get_link_to_form,
	getdate,
	nowdate,
	today,
)
from erpnext.stock.get_item_details import (
	_get_item_tax_template,
	get_conversion_factor,
	get_item_details,
	get_item_tax_map,
	get_item_warehouse,
)
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list
from frappe.model.workflow import get_workflow_name, is_transition_condition_satisfied

class ProjectBudget(Document):
	# def on_cancel(self):
	# 	dsts = frappe.db.get_value("Sales Order",{'name':self.sales_order},['docstatus'])
	# 	if dsts == 1:
	# 		so = frappe.db.exists("Sales Order",{'project_budget':self.name})
	# 		if so:
	# 			so.cancel()

	def after_insert(self):
		custom_sow_item_table=frappe.db.get_value("Sales Order",{'name':self.sales_order},['custom_sow_item_table'])
		if not custom_sow_item_table:
			frappe.sendmail(
				recipients=['gifty.p@groupteampro.com','abdulla.pi@groupteampro.com','amar.p@groupteampro.com'],
				subject='Project Budget is revised',
				message="""
				<b>Dear Sir/Mam,</b><br><br>
				Below Project Budget(SOW not as Item) <b>{}</b> against the Sales Order : <b>{}</b>is created<br><br>
				<br><br>
				Thanks & Regards,<br>ERP<br>
				<i>This email has been automatically generated. Please do not reply</i>
				""".format(self.name,self.sales_order)
			)
		self.check_7 = 0
		cost = frappe.get_doc("Cost Estimation",{'name':self.cost_estimation})
		cost.project_budget = self.name
		cost.save(ignore_permissions= True)
		so = frappe.get_doc("Sales Order",{'name':self.sales_order})
		so.project_budget = self.name
		so.save(ignore_permissions= True)
		dn_wip=frappe.get_all("Delivery Note WIP",{'sales_order':self.sales_order,'docstatus':('!=',2)},['name'])
		for dn in dn_wip:
			frappe.db.sql("update `tabDelivery Note WIP` set project_budget=%s where name=%s",(self.name,dn.name))

	# def before_submit(self):
	# 	so = frappe.get_doc('Sales Order',self.sales_order)
	# 	if self.amended_from:
	# 		so.so_revision = self.so_revision
	# 		so.pb_revision = self.pb_revision
	# 		so.save(ignore_permissions=True)
	def on_submit(self):
	
		#  Update mr qty in PB
		if frappe.db.exists("Material Request", {"project_budget": self.name, "docstatus": 1}):
			material_request = frappe.get_all("Material Request", {"project_budget": self.name, "docstatus": 1}, "name")
			for mrs in material_request:
				mr = frappe.get_doc("Material Request", mrs.name)
				for row in mr.items:
					for child in self.item_table:
						if child.item == row.item_code:
							child.custom_mr_qty = row.qty
			self.save()
	
		total_bidding_price = 0
		w_house = frappe.db.get_value("Warehouse",{'company':self.company,'default_for_stock_transfer':1},['name'])
		delivery_date = frappe.db.get_value('Sales Order',self.sales_order,'delivery_date')
		so = frappe.get_doc('Sales Order',self.sales_order)
		if self.amended_from:
			so.so_revision = self.so_revision
			so.pb_revision = self.pb_revision
		if so.docstatus == 0:
			# so.set('items',[])
			so.set('scope_of_work', [])
			so.set('materials', [])
			so.set('installation', [])
			so.set('heavy_equipments', [])
			so.set('finished_goods', [])
			so.set('others', [])
			so.set('accessories', [])
			so.set('finishing_work', [])
			so.set('manpower', [])
			so.set('design', [])
			so.set('so_work_title_item', [])

			# for msow in self.master_scope_of_work:
			# 	total_bidding_price += msow.total_bidding_price
			# 	so.append("items", {
			# 		"item_code": msow.msow,
			# 		"total_bidding_price": msow.total_bidding_price,
			# 		"msow_desc": msow.msow_desc,
			# 		"unit": msow.unit,
			# 		"qty": msow.qty,
			# 		"unit_price_company_currency": msow.unit_price * so.conversion_rate,
			# 		"unit_price": msow.unit_price,
			# 		"bidding_price_company_currency": msow.total_bidding_price * so.conversion_rate,
			# 	})
			for work_title in self.work_title_summary:
				so.append("so_work_title_item",{
					"item_name":work_title.item_name,
					"quantity":work_title.quantity,
					"amount":work_title.amount,
				})
			for msow in self.master_scope_of_work:
				total_bidding_price += msow.total_bidding_price
				so.append("scope_of_work", {
					"msow": msow.msow,
					"total_bidding_price": msow.total_bidding_price,
					"msow_desc": msow.msow_desc,
					"unit": msow.unit,
					"qty": msow.qty,
					"unit_price_company_currency": msow.unit_price * so.conversion_rate,
					"unit_price": msow.unit_price,
					"bidding_price_company_currency": msow.total_bidding_price * so.conversion_rate,
				})
				
			for des in self.design:
				so.append("design",{
					"msow":des.msow,
					"item":des.item,
					"item_name":des.item_name,
					"surface_area":des.surface_area,
					"item_group":des.item_group,
					"description":des.description,
					"unit":des.unit,
					"qty":des.qty,
					"unit_price":des.unit_price,
					"amount":des.amount,
					"difference":des.difference,
					"rate_with_overheads":des.rate_with_overheads,
					"amount_with_overheads":des.amount_with_overheads,
					"cost":des.cost,
					"cost_amount":des.cost_amount,
					"estimated_cost":des.estimated_cost,
					"estimated_amount":des.estimated_amount,
					"docname":des.docname,
				})
			if self.company == "MEP DIVISION - ELECTRA":
				for mat in self.materials:
					so.append("materials",{
						"msow":mat.msow,
						"item":mat.item,
						"item_name":mat.item_name,
						"surface_area":mat.surface_area,
						"item_group":mat.item_group,
						"description":mat.description,
						"unit":mat.unit,
						"qty":mat.qty,
						"unit_price":mat.unit_price,
						"amount":mat.amount,
						"difference":mat.difference,
						"rate_with_overheads":mat.rate_with_overheads,
						"amount_with_overheads":mat.amount_with_overheads,
						"cost":mat.cost,
						"cost_amount":mat.cost_amount,
						"estimated_cost":mat.estimated_cost,
						"estimated_amount":mat.estimated_amount,
						"docname":mat.docname,
					})
			else:
				for mat in self.materials:
					so.append("materials",{
						"msow":mat.msow,
						"item":mat.item,
						"item_name":mat.item_name,
						"surface_area":mat.surface_area,
						"item_group":mat.item_group,
						"description":mat.description,
						"unit":mat.unit,
						"qty":mat.qty,
						"unit_price":mat.unit_price,
						"amount":mat.amount,
						"difference":mat.difference,
						"rate_with_overheads":mat.rate_with_overheads,
						"amount_with_overheads":mat.amount_with_overheads,
						"cost":mat.cost,
						"cost_amount":mat.cost_amount,
						"estimated_cost":mat.estimated_cost,
						"estimated_amount":mat.estimated_amount,
						"docname":mat.docname,
					})
			for ins in self.installation:
				so.append("installation",{
					"msow":ins.msow,
					"item":ins.item,
					"item_name":ins.item_name,
					"surface_area":ins.surface_area,
					"item_group":ins.item_group,
					"description":ins.description,
					"unit":ins.unit,
					"qty":ins.qty,
					"unit_price":ins.unit_price,
					"amount":ins.amount,
					"difference":ins.difference,
					"rate_with_overheads":ins.rate_with_overheads,
					"amount_with_overheads":ins.amount_with_overheads,
					"cost":ins.cost,
					"cost_amount":ins.cost_amount,
					"estimated_cost":ins.estimated_cost,
					"estimated_amount":ins.estimated_amount,
					"docname":ins.docname,
				})
			for hv in self.heavy_equipments:
				so.append("heavy_equipments",{
					"msow":hv.msow,
					"item":hv.item,
					"item_name":hv.item_name,
					"surface_area":hv.surface_area,
					"item_group":hv.item_group,
					"description":hv.description,
					"unit":hv.unit,
					"qty":hv.qty,
					"unit_price":hv.unit_price,
					"amount":hv.amount,
					"difference":hv.difference,
					"rate_with_overheads":hv.rate_with_overheads,
					"amount_with_overheads":hv.amount_with_overheads,
					"cost":hv.cost,
					"cost_amount":hv.cost_amount,
					"estimated_cost":hv.estimated_cost,
					"estimated_amount":hv.estimated_amount,
					"docname":hv.docname,
				})
			for fg in self.finished_goods:
				if fg.bom:
					finished_good = frappe.get_doc("BOM",fg.bom)
					finished_good.project_budget = self.name
					finished_good.submit()
				so.append("finished_goods",{
					"msow":fg.msow,
					"item":fg.item,
					"item_name":fg.item_name,
					"surface_area":fg.surface_area,
					"item_group":fg.item_group,
					"description":fg.description,
					"unit":fg.unit,
					"qty":fg.qty,
					"unit_price":fg.unit_price,
					"amount":fg.amount,
					"difference":fg.difference,
					"rate_with_overheads":fg.rate_with_overheads,
					"amount_with_overheads":fg.amount_with_overheads,
					"cost":fg.cost,
					"cost_amount":fg.cost_amount,
					"estimated_cost":fg.estimated_cost,
					"estimated_amount":fg.estimated_amount,
					"docname":fg.docname,
				})
			for ot in self.others:
				so.append("others",{
					"msow":ot.msow,
					"item":ot.item,
					"item_name":ot.item_name,
					"surface_area":ot.surface_area,
					"item_group":ot.item_group,
					"description":ot.description,
					"unit":ot.unit,
					"qty":ot.qty,
					"unit_price":ot.unit_price,
					"amount":ot.amount,
					"difference":ot.difference,
					"rate_with_overheads":ot.rate_with_overheads,
					"amount_with_overheads":ot.amount_with_overheads,
					"cost":ot.cost,
					"cost_amount":ot.cost_amount,
					"estimated_cost":ot.estimated_cost,
					"estimated_amount":ot.estimated_amount,
					"docname":ot.docname,
				})
			for fw in self.finishing_work:
				so.append("finishing_work",{
					"msow":fw.msow,
					"item":fw.item,
					"item_name":fw.item_name,
					"surface_area":fw.surface_area,
					"item_group":fw.item_group,
					"description":fw.description,
					"unit":fw.unit,
					"qty":fw.qty,
					"unit_price":fw.unit_price,
					"amount":fw.amount,
					"difference":fw.difference,
					"rate_with_overheads":fw.rate_with_overheads,
					"amount_with_overheads":fw.amount_with_overheads,
					"cost":fw.cost,
					"cost_amount":fw.cost_amount,
					"estimated_cost":fw.estimated_cost,
					"estimated_amount":fw.estimated_amount,
					"docname":fw.docname,
				})
			for ba in self.bolts_accessories:
				so.append("accessories",{
					"msow":ba.msow,
					"item":ba.item,
					"item_name":ba.item_name,
					"surface_area":ba.surface_area,
					"item_group":ba.item_group,
					"description":ba.description,
					"unit":ba.unit,
					"qty":ba.qty,
					"unit_price":ba.unit_price,
					"amount":ba.amount,
					"difference":ba.difference,
					"rate_with_overheads":ba.rate_with_overheads,
					"amount_with_overheads":ba.amount_with_overheads,
					"cost":ba.cost,
					"cost_amount":ba.cost_amount,
					"estimated_cost":ba.estimated_cost,
					"estimated_amount":ba.estimated_amount,
					"docname":ba.docname,
				})
			for mn in self.manpower:
				so.append("manpower",{
					"msow":mn.msow,
					"total_workers":mn.total_workers,
					"worker":mn.worker,
					"working_hours":mn.working_hours,
					"days":mn.days,
					"unit_price":mn.unit_price,
					"rate":mn.rate,
					"amount":mn.amount,
					"rate_with_overheads":mn.rate_with_overheads,
					"amount_with_overheads":mn.amount_with_overheads,
					"cost":mn.cost,
					"cost_amount":mn.cost_amount,
					"estimated_cost":mn.estimated_cost,
					"estimated_amount":mn.estimated_amount,
					"docname":mn.docname,
				})
			so.total_bidding_price = total_bidding_price
			so.net_bidding_price = total_bidding_price - so.project_discount_amt
			so.save(ignore_permissions=True)


	# def on_submit(self):
	# 	total_bidding_price = 0
	# 	w_house = frappe.db.get_value("Warehouse",{'company':self.company,'default_for_stock_transfer':1},['name'])
	# 	delivery_date = frappe.db.get_value('Sales Order',self.sales_order,'delivery_date')
	# 	so = frappe.get_doc('Sales Order',self.sales_order)
	# 	if self.amended_from:
	# 		so.so_revision = self.so_revision
	# 		so.pb_revision = self.pb_revision
	# 	if so.docstatus !=1:
	# 		so.set('items', [])
	# 		so.set('scope_of_work', [])
	# 		so.set('materials', [])
	# 		so.set('installation', [])
	# 		so.set('heavy_equipments', [])
	# 		so.set('finished_goods', [])
	# 		so.set('others', [])
	# 		so.set('accessories', [])
	# 		so.set('finishing_work', [])
	# 		so.set('manpower', [])
	# 		so.set('design', [])
	# 		so.set('so_work_title_item', [])
	# 		for work_title in self.work_title_summary:
	# 			so.append("so_work_title_item",{
	# 				"item_name":work_title.item_name,
	# 				"quantity":work_title.quantity,
	# 				"amount":work_title.amount,
	# 			})
	# 		for msow in self.master_scope_of_work:
	# 			total_bidding_price += msow.total_bidding_price
	# 			so.append("scope_of_work", {
	# 				"msow": msow.msow,
	# 				"total_bidding_price": msow.total_bidding_price,
	# 				"msow_desc": msow.msow_desc,
	# 				"unit": msow.unit,
	# 				"qty": msow.qty,
	# 				"unit_price_company_currency": msow.unit_price * so.conversion_rate,
	# 				"unit_price": msow.unit_price,
	# 				"bidding_price_company_currency": msow.total_bidding_price * so.conversion_rate,
	# 			})
	# 		for des in self.design:
	# 			so.append("items", {
	# 				"work_title": "DESIGN",
	# 				"item_code": des.item,
	# 				"msow": des.msow,
	# 				"item_name": des.item_name,
	# 				"qty": des.qty,
	# 				"custom_so_qty": des.qty,
	# 				"rate": des.rate_with_overheads,
	# 				"warehouse" : w_house,
	# 				"delivery_date":delivery_date,
	# 				"amount": des.amount_with_overheads,
	# 				"description": frappe.db.get_value("Item",des.item,['description']),
	# 				"uom": frappe.db.get_value("Item",des.item,['stock_uom']),
	# 				"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':des.item},['conversion_factor']),
	# 				"prevdoc_docname":so.quotation
	# 			})
	# 			so.append("design",{
	# 				"msow":des.msow,
	# 				"item":des.item,
	# 				"item_name":des.item_name,
	# 				"surface_area":des.surface_area,
	# 				"item_group":des.item_group,
	# 				"description":des.description,
	# 				"unit":des.unit,
	# 				"qty":des.qty,
	# 				"unit_price":des.unit_price,
	# 				"amount":des.amount,
	# 				"difference":des.difference,
	# 				"rate_with_overheads":des.rate_with_overheads,
	# 				"amount_with_overheads":des.amount_with_overheads,
	# 				"cost":des.cost,
	# 				"cost_amount":des.cost_amount,
	# 				"estimated_cost":des.estimated_cost,
	# 				"estimated_amount":des.estimated_amount,
	# 			})
	# 		if self.company == "MEP DIVISION - ELECTRA":
	# 			for mat in self.materials:
	# 				so.append("items", {
	# 					"work_title": "SUPPLY MATERIALS",
	# 					"msow":mat.msow,
	# 					"item_code": mat.item,
	# 					"item_name": mat.item_name,
	# 					"qty": mat.qty,
	# 					"custom_so_qty": mat.qty,
	# 					"rate": mat.rate_with_overheads,
	# 					"warehouse" : w_house,
	# 					"delivery_date":delivery_date,
	# 					"amount": mat.amount_with_overheads,
	# 					"description": frappe.db.get_value("Item",mat.item,['description']),
	# 					"uom": frappe.db.get_value("Item",mat.item,['stock_uom']),
	# 					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':mat.item},['conversion_factor']),
	#   					"prevdoc_docname":so.quotation
	# 				})
	# 				so.append("materials",{
	# 					"msow":mat.msow,
	# 					"item":mat.item,
	# 					"item_name":mat.item_name,
	# 					"surface_area":mat.surface_area,
	# 					"item_group":mat.item_group,
	# 					"description":mat.description,
	# 					"unit":mat.unit,
	# 					"qty":mat.qty,
	# 					"unit_price":mat.unit_price,
	# 					"amount":mat.amount,
	# 					"difference":mat.difference,
	# 					"rate_with_overheads":mat.rate_with_overheads,
	# 					"amount_with_overheads":mat.amount_with_overheads,
	# 					"cost":mat.cost,
	# 					"cost_amount":mat.cost_amount,
	# 					"estimated_cost":mat.estimated_cost,
	# 					"estimated_amount":mat.estimated_amount,
	# 				})
	# 		else:
	# 			for mat in self.materials:
	# 				so.append("items", {
	# 					"work_title": "SUPPLY MATERIALS",
	# 					"msow":mat.msow,
	# 					"item_code": mat.item,
	# 					"item_name": mat.item_name,
	# 					"qty": mat.qty,
	# 					"custom_so_qty": mat.qty,
	# 					"rate": mat.rate_with_overheads,
	# 					"warehouse" : w_house,
	# 					"delivery_date":delivery_date,
	# 					"amount": mat.amount_with_overheads,
	# 					"description": frappe.db.get_value("Item",mat.item,['description']),
	# 					"uom": frappe.db.get_value("Item",mat.item,['stock_uom']),
	# 					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':mat.item},['conversion_factor']),
	# 					"prevdoc_docname":so.quotation
	# 				})
	# 				so.append("materials",{
	# 					"msow":mat.msow,
	# 					"item":mat.item,
	# 					"item_name":mat.item_name,
	# 					"surface_area":mat.surface_area,
	# 					"item_group":mat.item_group,
	# 					"description":mat.description,
	# 					"unit":mat.unit,
	# 					"qty":mat.qty,
	# 					"unit_price":mat.unit_price,
	# 					"amount":mat.amount,
	# 					"difference":mat.difference,
	# 					"rate_with_overheads":mat.rate_with_overheads,
	# 					"amount_with_overheads":mat.amount_with_overheads,
	# 					"cost":mat.cost,
	# 					"cost_amount":mat.cost_amount,
	# 					"estimated_cost":mat.estimated_cost,
	# 					"estimated_amount":mat.estimated_amount,
	# 				})
	# 		for ins in self.installation:
	# 			so.append("items", {
	# 				"work_title": "INSTALLATION",
	# 				"msow":ins.msow,
	# 				"item_code": ins.item,
	# 				"item_name": ins.item_name,
	# 				"qty": ins.qty,
	# 				"custom_so_qty": ins.qty,
	# 				"rate": ins.rate_with_overheads,
	# 				"warehouse" : w_house,
	# 				"delivery_date":delivery_date,
	# 				"amount": ins.amount_with_overheads,
	# 				"description": frappe.db.get_value("Item",ins.item,['description']),
	# 				"uom": frappe.db.get_value("Item",ins.item,['stock_uom']),
	# 				"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':ins.item},['conversion_factor']),
	# 				"prevdoc_docname":so.quotation
	# 			})
	# 			so.append("installation",{
	# 				"msow":ins.msow,
	# 				"item":ins.item,
	# 				"item_name":ins.item_name,
	# 				"surface_area":ins.surface_area,
	# 				"item_group":ins.item_group,
	# 				"description":ins.description,
	# 				"unit":ins.unit,
	# 				"qty":ins.qty,
	# 				"unit_price":ins.unit_price,
	# 				"amount":ins.amount,
	# 				"difference":ins.difference,
	# 				"rate_with_overheads":ins.rate_with_overheads,
	# 				"amount_with_overheads":ins.amount_with_overheads,
	# 				"cost":ins.cost,
	# 				"cost_amount":ins.cost_amount,
	# 				"estimated_cost":ins.estimated_cost,
	# 				"estimated_amount":ins.estimated_amount,
	# 			})
	# 		for hv in self.heavy_equipments:
	# 			so.append("items", {
	# 				"work_title": "TOOLS/EQUIPMENTS/TRANSPORT/OTHERS",
	# 				"msow":hv.msow,
	# 				"item_code": hv.item,
	# 				"item_name": hv.item_name,
	# 				"qty": hv.qty,
	# 				"custom_so_qty": hv.qty,
	# 				"rate": hv.rate_with_overheads,
	# 				"warehouse" : w_house,
	# 				"delivery_date":delivery_date,
	# 				"amount": hv.amount_with_overheads,
	# 				"description": frappe.db.get_value("Item",hv.item,['description']),
	# 				"uom": frappe.db.get_value("Item",hv.item,['stock_uom']),
	# 				"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':hv.item},['conversion_factor']),
	# 				"prevdoc_docname":so.quotation
	# 			})
	# 			so.append("heavy_equipments",{
	# 				"msow":hv.msow,
	# 				"item":hv.item,
	# 				"item_name":hv.item_name,
	# 				"surface_area":hv.surface_area,
	# 				"item_group":hv.item_group,
	# 				"description":hv.description,
	# 				"unit":hv.unit,
	# 				"qty":hv.qty,
	# 				"unit_price":hv.unit_price,
	# 				"amount":hv.amount,
	# 				"difference":hv.difference,
	# 				"rate_with_overheads":hv.rate_with_overheads,
	# 				"amount_with_overheads":hv.amount_with_overheads,
	# 				"cost":hv.cost,
	# 				"cost_amount":hv.cost_amount,
	# 				"estimated_cost":hv.estimated_cost,
	# 				"estimated_amount":hv.estimated_amount,
	# 			})
	# 		for fg in self.finished_goods:
	# 			if fg.bom:
	# 				finished_good = frappe.get_doc("BOM",fg.bom)
	# 				finished_good.project_budget = self.name
	# 				finished_good.submit()
	# 			so.append("items", {
	# 				"work_title": "FINISHED GOODS",
	# 				"msow":fg.msow,
	# 				"item_code": fg.item,
	# 				"item_name": fg.item_name,
	# 				"qty": fg.qty,
	# 				"custom_so_qty": fg.qty,
	# 				"rate": fg.rate_with_overheads,
	# 				"warehouse" : w_house,
	# 				"delivery_date":delivery_date,
	# 				"amount": fg.amount_with_overheads,
	# 				"description": frappe.db.get_value("Item",fg.item,['description']),
	# 				"uom": frappe.db.get_value("Item",fg.item,['stock_uom']),
	# 				"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':fg.item},['conversion_factor']),
	# 				"prevdoc_docname":so.quotation
	# 			})
	# 			so.append("finished_goods",{
	# 				"msow":fg.msow,
	# 				"item":fg.item,
	# 				"item_name":fg.item_name,
	# 				"surface_area":fg.surface_area,
	# 				"item_group":fg.item_group,
	# 				"description":fg.description,
	# 				"unit":fg.unit,
	# 				"qty":fg.qty,
	# 				"unit_price":fg.unit_price,
	# 				"amount":fg.amount,
	# 				"difference":fg.difference,
	# 				"rate_with_overheads":fg.rate_with_overheads,
	# 				"amount_with_overheads":fg.amount_with_overheads,
	# 				"cost":fg.cost,
	# 				"cost_amount":fg.cost_amount,
	# 				"estimated_cost":fg.estimated_cost,
	# 				"estimated_amount":fg.estimated_amount,
	# 			})
	# 		for ot in self.others:
	# 			so.append("items", {
	# 				"work_title": "SUBCONTRACT",
	# 				"msow":ot.msow,
	# 				"item_code": ot.item,
	# 				"item_name": ot.item_name,
	# 				"qty": ot.qty,
	# 				"custom_so_qty": ot.qty,
	# 				"rate": ot.rate_with_overheads,
	# 				"warehouse" : w_house,
	# 				"delivery_date":delivery_date,
	# 				"amount": ot.amount_with_overheads,
	# 				"description": frappe.db.get_value("Item",ot.item,['description']),
	# 				"uom": frappe.db.get_value("Item",ot.item,['stock_uom']),
	# 				"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':ot.item},['conversion_factor']),
	# 				"prevdoc_docname":so.quotation
	# 			})
	# 			so.append("others",{
	# 				"msow":ot.msow,
	# 				"item":ot.item,
	# 				"item_name":ot.item_name,
	# 				"surface_area":ot.surface_area,
	# 				"item_group":ot.item_group,
	# 				"description":ot.description,
	# 				"unit":ot.unit,
	# 				"qty":ot.qty,
	# 				"unit_price":ot.unit_price,
	# 				"amount":ot.amount,
	# 				"difference":ot.difference,
	# 				"rate_with_overheads":ot.rate_with_overheads,
	# 				"amount_with_overheads":ot.amount_with_overheads,
	# 				"cost":ot.cost,
	# 				"cost_amount":ot.cost_amount,
	# 				"estimated_cost":ot.estimated_cost,
	# 				"estimated_amount":ot.estimated_amount,
	# 			})
	# 		for fw in self.finishing_work:
	# 			so.append("items", {
	# 				"work_title": "FINISHING WORK",
	# 				"msow":fw.msow,
	# 				"item_code": fw.item,
	# 				"item_name": fw.item_name,
	# 				"qty": fw.qty,
	# 				"custom_so_qty": fw.qty,
	# 				"rate": fw.rate_with_overheads,
	# 				"warehouse" : w_house,
	# 				"delivery_date":delivery_date,
	# 				"amount": fw.amount_with_overheads,
	# 				"description": frappe.db.get_value("Item",fw.item,['description']),
	# 				"uom": frappe.db.get_value("Item",fw.item,['stock_uom']),
	# 				"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':fw.item},['conversion_factor']),
	# 				"prevdoc_docname":so.quotation
	# 			})
	# 			so.append("finishing_work",{
	# 				"msow":fw.msow,
	# 				"item":fw.item,
	# 				"item_name":fw.item_name,
	# 				"surface_area":fw.surface_area,
	# 				"item_group":fw.item_group,
	# 				"description":fw.description,
	# 				"unit":fw.unit,
	# 				"qty":fw.qty,
	# 				"unit_price":fw.unit_price,
	# 				"amount":fw.amount,
	# 				"difference":fw.difference,
	# 				"rate_with_overheads":fw.rate_with_overheads,
	# 				"amount_with_overheads":fw.amount_with_overheads,
	# 				"cost":fw.cost,
	# 				"cost_amount":fw.cost_amount,
	# 				"estimated_cost":fw.estimated_cost,
	# 				"estimated_amount":fw.estimated_amount,
	# 			})
	# 		for ba in self.bolts_accessories:
	# 			so.append("items", {
	# 				"work_title": "ACCESSORIES",
	# 				"msow":ba.msow,
	# 				"item_code": ba.item,
	# 				"item_name": ba.item_name,
	# 				"qty": ba.qty,
	# 				"custom_so_qty": ba.qty,
	# 				"rate": ba.rate_with_overheads,
	# 				"warehouse" : w_house,
	# 				"delivery_date":delivery_date,
	# 				"amount": ba.amount_with_overheads,
	# 				"description": frappe.db.get_value("Item",ba.item,['description']),
	# 				"uom": frappe.db.get_value("Item",ba.item,['stock_uom']),
	# 				"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':ba.item},['conversion_factor']),
	# 				"prevdoc_docname":so.quotation
	# 			})
	# 			so.append("accessories",{
	# 				"msow":ba.msow,
	# 				"item":ba.item,
	# 				"item_name":ba.item_name,
	# 				"surface_area":ba.surface_area,
	# 				"item_group":ba.item_group,
	# 				"description":ba.description,
	# 				"unit":ba.unit,
	# 				"qty":ba.qty,
	# 				"unit_price":ba.unit_price,
	# 				"amount":ba.amount,
	# 				"difference":ba.difference,
	# 				"rate_with_overheads":ba.rate_with_overheads,
	# 				"amount_with_overheads":ba.amount_with_overheads,
	# 				"cost":ba.cost,
	# 				"cost_amount":ba.cost_amount,
	# 				"estimated_cost":ba.estimated_cost,
	# 				"estimated_amount":ba.estimated_amount,
	# 			})
	# 		for mn in self.manpower:
	# 			so.append("items", {
	# 				"work_title": "MANPOWER",
	# 				"msow":mn.msow,
	# 				"item_code": mn.worker,
	# 				"item_name": mn.worker,
	# 				"qty": mn.total_workers,
	# 				"custom_so_qty": mn.total_workers,
	# 				"rate": mn.rate_with_overheads,
	# 				"warehouse" : w_house,
	# 				"delivery_date":delivery_date,
	# 				"amount": mn.amount_with_overheads,
	# 				"description": frappe.db.get_value("Item",mn.worker,['description']),
	# 				"uom": frappe.db.get_value("Item",mn.worker,['stock_uom']),
	# 				"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':mn.worker},['conversion_factor']),
	# 				"prevdoc_docname":so.quotation
	# 			})
	# 			so.append("manpower",{
	# 				"msow":mn.msow,
	# 				"total_workers":mn.total_workers,
	# 				"worker":mn.worker,
	# 				"working_hours":mn.working_hours,
	# 				"days":mn.days,
	# 				"unit_price":mn.unit_price,
	# 				"rate":mn.rate,
	# 				"amount":mn.amount,
	# 				"rate_with_overheads":mn.rate_with_overheads,
	# 				"amount_with_overheads":mn.amount_with_overheads,
	# 				"cost":mn.cost,
	# 				"cost_amount":mn.cost_amount,
	# 				"estimated_cost":mn.estimated_cost,
	# 				"estimated_amount":mn.estimated_amount,
	# 			})
	# 		so.total_bidding_price = total_bidding_price
	# 		so.net_bidding_price = total_bidding_price - so.project_discount_amt
	# 		so.save(ignore_permissions=True)


@frappe.whitelist()
def round(n, decimals=0):
	multiplier = 10 ** decimals
	return math.ceil(n * multiplier) / multiplier

@frappe.whitelist()
def update_msows(document,sales_order):
	total_bidding_price = 0
	total_amount_so=0
	doc = frappe.get_doc("Project Budget",document)
	if doc.company == "INTERIOR DIVISION - ELECTRA":
		warehouse = "Electra Interior Warehouse - INE"
	if doc.company == "ENGINEERING DIVISION - ELECTRA":
		warehouse = "Electra Engineering Warehouse - EED"
	if doc.company == "MEP DIVISION - ELECTRA":
		warehouse = "Electra MEP Warehouse - MEP"
	so = frappe.get_doc('Sales Order',sales_order)
	if so.docstatus==1:
		if doc.revision == "SO - Revision":
			if so.custom_sow_item_table == 1:
				so.set('items', [])
				for itm in doc.master_scope_of_work:
					total_amount_so += itm.total_bidding_price
					so.append("items", {
						"item_code": itm.msow,
						"item_name": itm.msow_desc,
						"msow": itm.msow,
						"qty": itm.qty,
						"uom": itm.unit_price,
						"custom_so_qty": itm.qty,
						"rate": itm.unit_price,
						"amount": itm.total_bidding_price,
						"conversion_factor": 1,
						"warehouse": warehouse
					})
				
			else:
				so.set('items', [])
				for itm in doc.item_table:
					total_amount_so += itm.amount_with_overheads
					so.append("items", {
						"item_code": itm.item,
						"item_name": itm.item_name,
						"msow": itm.msow,
						"qty": itm.qty,
						"uom": itm.unit_price,
						"custom_so_qty": itm.qty,
						"rate": itm.rate_with_overheads,
						"amount": itm.amount_with_overheads,
						"conversion_factor": 1,
						"warehouse": warehouse,
						"delivered_qty": itm.delivered_qty
					})
		elif doc.revision == "PB - Revision":
			if so.custom_sow_item_table == 1:
		# 		so.set('items', [])
				for itm in doc.master_scope_of_work:
					total_amount_so += itm.total_bidding_price
		# 			so.append("items", {
		# 				"item_code": itm.msow,
		# 				"item_name": itm.msow_desc,
		# 				"msow": itm.msow,
		# 				"qty": itm.qty,
		# 				"uom": itm.unit_price,
		# 				"custom_so_qty": itm.qty,
		# 				"rate": itm.unit_price,
		# 				"amount": itm.total_bidding_price,
		# 				"conversion_factor": 1
		# 			})
			else:
		# 		so.set('items', [])
				for itm in doc.item_table:
					total_amount_so += itm.amount_with_overheads
		# 			so.append("items", {
		# 				"item_code": itm.item,
		# 				"item_name": itm.item_name,
		# 				"msow": itm.msow,
		# 				"qty": itm.qty,
		# 				"uom": itm.unit_price,
		# 				"custom_so_qty": itm.qty,
		# 				"rate": itm.rate_with_overheads,
		# 				"amount": itm.amount_with_overheads,
		# 				"conversion_factor": 1
		# 			})
		so.set('so_work_title_item', [])
		so.set('scope_of_work', [])
		so.set('materials', [])
		so.set('installation', [])
		so.set('heavy_equipments', [])
		so.set('finished_goods', [])
		so.set('others', [])
		so.set('accessories', [])
		so.set('finishing_work', [])
		so.set('manpower', [])
		so.set('design', [])
		for msow in doc.master_scope_of_work:
			total_bidding_price += msow.total_bidding_price
			so.append("scope_of_work", {
				"msow": msow.msow,
				"total_bidding_price": msow.total_bidding_price,
				"msow_desc": msow.msow_desc,
				"unit": msow.unit,
				"unit_price": msow.unit_price,
				"qty": msow.qty,
				"unit_price_company_currency": msow.unit_price * so.conversion_rate,
				"bidding_price_company_currency": msow.total_bidding_price * so.conversion_rate,
			})
		for des in doc.design:
			so.append("design",{
				"msow":des.msow,
				"item":des.item,
				"item_name":des.item_name,
				"surface_area":des.surface_area,
				"item_group":des.item_group,
				"description":des.description,
				"unit":des.unit,
				"qty":des.qty,
				"unit_price":des.unit_price,
				"amount":des.amount,
				"difference":des.difference,
				"rate_with_overheads":des.rate_with_overheads,
				"amount_with_overheads":des.amount_with_overheads,
				"cost":des.cost,
				"cost_amount":des.cost_amount,
				"estimated_cost":des.estimated_cost,
				"estimated_amount":des.estimated_amount,
				"docname":des.docname,
			})

		if doc.company == "MEP DIVISION - ELECTRA":
			for mat in doc.materials:
				so.append("materials",{
					"msow":mat.msow,
					"item":mat.item,
					"item_name":mat.item_name,
					"surface_area":mat.surface_area,
					"item_group":mat.item_group,
					"description":mat.description,
					"unit":mat.unit,
					"qty":mat.qty,
					"unit_price":mat.unit_price,
					"amount":mat.amount,
					"difference":mat.difference,
					"rate_with_overheads":mat.rate_with_overheads,
					"amount_with_overheads":mat.amount_with_overheads,
					"cost":mat.cost,
					"cost_amount":mat.cost_amount,
					"estimated_cost":mat.estimated_cost,
					"estimated_amount":mat.estimated_amount,
					"docname":mat.docname,
				})
		else:
			for mat in doc.materials:
				so.append("materials",{
					"msow":mat.msow,
					"item":mat.item,
					"item_name":mat.item_name,
					"surface_area":mat.surface_area,
					"item_group":mat.item_group,
					"description":mat.description,
					"unit":mat.unit,
					"qty":mat.qty,
					"unit_price":mat.unit_price,
					"amount":mat.amount,
					"difference":mat.difference,
					"rate_with_overheads":mat.rate_with_overheads,
					"amount_with_overheads":mat.amount_with_overheads,
					"cost":mat.cost,
					"cost_amount":mat.cost_amount,
					"estimated_cost":mat.estimated_cost,
					"estimated_amount":mat.estimated_amount,
					"docname":mat.docname,
				})
		for ins in doc.installation:
			so.append("installation",{
				"msow":ins.msow,
				"item":ins.item,
				"item_name":ins.item_name,
				"surface_area":ins.surface_area,
				"item_group":ins.item_group,
				"description":ins.description,
				"unit":ins.unit,
				"qty":ins.qty,
				"unit_price":ins.unit_price,
				"amount":ins.amount,
				"difference":ins.difference,
				"rate_with_overheads":ins.rate_with_overheads,
				"amount_with_overheads":ins.amount_with_overheads,
				"cost":ins.cost,
				"cost_amount":ins.cost_amount,
				"estimated_cost":ins.estimated_cost,
				"estimated_amount":ins.estimated_amount,
				"docname":ins.docname,
			})
		for hv in doc.heavy_equipments:
			so.append("heavy_equipments",{
				"msow":hv.msow,
				"item":hv.item,
				"item_name":hv.item_name,
				"surface_area":hv.surface_area,
				"item_group":hv.item_group,
				"description":hv.description,
				"unit":hv.unit,
				"qty":hv.qty,
				"unit_price":hv.unit_price,
				"amount":hv.amount,
				"difference":hv.difference,
				"rate_with_overheads":hv.rate_with_overheads,
				"amount_with_overheads":hv.amount_with_overheads,
				"cost":hv.cost,
				"cost_amount":hv.cost_amount,
				"estimated_cost":hv.estimated_cost,
				"estimated_amount":hv.estimated_amount,
				"docname":hv.docname,
			})

		for fg in doc.finished_goods:
			so.append("finished_goods",{
				"msow":fg.msow,
				"item":fg.item,
				"item_name":fg.item_name,
				"surface_area":fg.surface_area,
				"item_group":fg.item_group,
				"description":fg.description,
				"unit":fg.unit,
				"qty":fg.qty,
				"unit_price":fg.unit_price,
				"amount":fg.amount,
				"difference":fg.difference,
				"rate_with_overheads":fg.rate_with_overheads,
				"amount_with_overheads":fg.amount_with_overheads,
				"cost":fg.cost,
				"cost_amount":fg.cost_amount,
				"estimated_cost":fg.estimated_cost,
				"estimated_amount":fg.estimated_amount,
				"docname":fg.docname,
			})

		for ot in doc.others:
			so.append("others",{
				"msow":ot.msow,
				"item":ot.item,
				"item_name":ot.item_name,
				"surface_area":ot.surface_area,
				"item_group":ot.item_group,
				"description":ot.description,
				"unit":ot.unit,
				"qty":ot.qty,
				"unit_price":ot.unit_price,
				"amount":ot.amount,
				"difference":ot.difference,
				"rate_with_overheads":ot.rate_with_overheads,
				"amount_with_overheads":ot.amount_with_overheads,
				"cost":ot.cost,
				"cost_amount":ot.cost_amount,
				"estimated_cost":ot.estimated_cost,
				"estimated_amount":ot.estimated_amount,
				"docname":ot.docname,
			})
		for fw in doc.finishing_work:
			so.append("finishing_work",{
				"msow":fw.msow,
				"item":fw.item,
				"item_name":fw.item_name,
				"surface_area":fw.surface_area,
				"item_group":fw.item_group,
				"description":fw.description,
				"unit":fw.unit,
				"qty":fw.qty,
				"unit_price":fw.unit_price,
				"amount":fw.amount,
				"difference":fw.difference,
				"rate_with_overheads":fw.rate_with_overheads,
				"amount_with_overheads":fw.amount_with_overheads,
				"cost":fw.cost,
				"cost_amount":fw.cost_amount,
				"estimated_cost":fw.estimated_cost,
				"estimated_amount":fw.estimated_amount,
				"docname":fw.docname,
			})
		for ba in doc.bolts_accessories:
			so.append("accessories",{
				"msow":ba.msow,
				"item":ba.item,
				"item_name":ba.item_name,
				"surface_area":ba.surface_area,
				"item_group":ba.item_group,
				"description":ba.description,
				"unit":ba.unit,
				"qty":ba.qty,
				"unit_price":ba.unit_price,
				"amount":ba.amount,
				"difference":ba.difference,
				"rate_with_overheads":ba.rate_with_overheads,
				"amount_with_overheads":ba.amount_with_overheads,
				"cost":ba.cost,
				"cost_amount":ba.cost_amount,
				"estimated_cost":ba.estimated_cost,
				"estimated_amount":ba.estimated_amount,
				"docname":ba.docname,
			})
		for mn in doc.manpower:
			so.append("manpower",{
				"msow":mn.msow,
				"total_workers":mn.total_workers,
				"worker":mn.worker,
				"working_hours":mn.working_hours,
				"days":mn.days,
				"unit_price":mn.unit_price,
				"rate":mn.rate,
				"amount":mn.amount,
				"rate_with_overheads":mn.rate_with_overheads,
				"amount_with_overheads":mn.amount_with_overheads,
				"cost":mn.cost,
				"cost_amount":mn.cost_amount,
				"estimated_cost":mn.estimated_cost,
				"estimated_amount":mn.estimated_amount,
				"docname":mn.docname,
			})
		for work_title in doc.work_title_summary:
			so.append("so_work_title_item",{
				"item_name":work_title.item_name,
				"quantity":work_title.quantity,
				"amount":work_title.amount,
			})
		so.total_bidding_price = total_bidding_price
		so.total = total_amount_so
		so.net_total =total_amount_so - so.discount_amount
		so.grand_total = total_amount_so - so.discount_amount
		so.net_bidding_price = total_bidding_price - so.project_discount_amt
		so.save(ignore_permissions=True)
		so.reload()

@frappe.whitelist()
def get_data(tc,ec,cp,gpp,tcc,tec,cpc,gppc,tcp,tpb,tbp,cmp,netp,neta,dis):
	if cmp == "MEP DIVISION - ELECTRA":		
		data  = ''
		data = "<table style='width:100%'>"
		data += "<tr><td colspan = 20 style ='text-align:center;text-align:center;border:1px solid black;background-color:orange'><b>TOTAL COST</b></td></tr>"
		data += "<tr style ='background-color:#a0a0a0;color:white'><td colspan = 2 style ='text-align:center;text-align:center;border:1px solid black'><b>S No</b></td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black'><b>Title</b></td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black'><b>Percentage(%)</b></td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black'><b>Amount(QAR)</b></td></tr>"
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>A</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Cost of the Project</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tcp), 2))	
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>B</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Gross Profit</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(gpp), 2),round(float(gppc), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>C</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Net Profit</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(netp),2),round(float(neta), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>D</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Business Promotion</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tpb), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>E</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Discount Amount</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(dis), 2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black;border-right-color:#a0a0a0;background-color:#a0a0a0'></td><td colspan = 12 style ='color:white;text-align:center;border:1px solid black;background-color:#a0a0a0'><b>Total Bidding Price</b>(A+C+D)</td><td colspan = 6 style ='color:white;background-color:#a0a0a0;text-align:center;border:1px solid black'><b>QAR  %s</b></td></tr>"%(round(float(tbp), 2))
		data += "</table>"
		
	if cmp != "MEP DIVISION - ELECTRA":
# 	# 	tot = (round(float(tec) , 2)) + round(float(cpc), 2) + round(float(tcc), 2)
# 	# 	nppc = (round(float(gppc), 2)) - (round(float(dpc), 2))
# 	# 	tbp = (round(float(tcp), 2)) + (round(float(nppc), 2)) + (round(float(tot), 2)) + (round(float(tpb), 2))
		eng = (round(float(tcp), 4)) + (round(float(neta), 4)) + (round(float(tcc), 4)) + (round(float(tec), 4)) +(round(float(cpc), 4)) + (round(float(tpb), 4)) 
# 	# 	npp = (round(float(gpp), 2)) - (round(float(dp), 2))
		
		data  = ''
		data = "<table style='width:100%'>"
		data += "<tr><td colspan = 20 style ='text-align:center;text-align:center;border:1px solid black;background-color:orange'><b>TOTAL COST</b></td></tr>"
		data += "<tr style ='background-color:#a0a0a0;color:white'><td colspan = 2 style ='text-align:center;text-align:center;border:1px solid black'><b>S No</b></td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black'><b>Title</b></td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black'><b>Percentage(%)</b></td><td  colspan = 6 style ='text-align:center;text-align:center;border:1px solid black'><b>Amount(QAR)</b></td></tr>"
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>A</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Cost of the Project</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tcp), 4))
		
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>B</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Overhead</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(tc), 4),round(float(tcc), 4))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>C</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Engineering Overhead</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(ec),4),round(float(tec), 4))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>D</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Contigency</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(cp),4),round(float(cpc), 4))
	# 	data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>E</b></td><td colspan = 12 style ='text-align:center;border:1px solid black'><b>Total Overhead</b>(B+C+D)</td><td colspan = 6 style ='text-align:center;border:1px solid black'><b>QAR  %s</b></td></tr>"%(round(float(tot),2))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>F</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Gross Profit</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(gpp), 4),round(float(gppc), 4))
		# data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>G</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'><b>Discount</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'><b>%s</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'><b>QAR    %s</b></td></tr>"%(round(float(dp), 4),round(float(dpc), 4))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>H</b></td><td colspan = 6 style ='text-align:left;border:1px solid black'><b>Net Profit</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>%s</td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR    %s</td></tr>"%(round(float(netp),4),round(float(neta), 4))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>I</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Total Business Promotion</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(tpb), 4))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black'><b>J</b></td><td colspan = 12 style ='text-align:left;border:1px solid black'><b>Discount Amount</b></td><td colspan = 6 style ='text-align:center;border:1px solid black'>QAR  %s</td></tr>"%(round(float(dis), 4))
		data += "<tr><td colspan = 2 style ='text-align:center;border:1px solid black;border-right-color:#a0a0a0;background-color:#a0a0a0'><td colspan = 12 style ='color:white;text-align:center;border:1px solid black;background-color:#a0a0a0'><b>Total Bidding Price</b>(A+B+C+D+H+I)</td><td colspan = 6 style ='color:white;background-color:#a0a0a0;text-align:center;border:1px solid black'><b>QAR  %s</b></td></tr>"%(round(float(tbp),3))
		data += "</table>"
	return data

@frappe.whitelist()
def update_child_qty_rate(parent_doctype, trans_items, parent_doctype_name, child_docname="items"):
	def check_doc_permissions(doc, perm_type="create"):
		try:
			doc.check_permission(perm_type)
		except frappe.PermissionError:
			actions = {"create": "add", "write": "update"}

			frappe.throw(
				_("You do not have permissions to {} items in a {}.").format(
					actions[perm_type], parent_doctype
				),
				title=_("Insufficient Permissions"),
			)

	def validate_workflow_conditions(doc):
		workflow = get_workflow_name(doc.doctype)
		if not workflow:
			return

		workflow_doc = frappe.get_doc("Workflow", workflow)
		current_state = doc.get(workflow_doc.workflow_state_field)
		roles = frappe.get_roles()

		transitions = []
		for transition in workflow_doc.transitions:
			if transition.next_state == current_state and transition.allowed in roles:
				if not is_transition_condition_satisfied(transition, doc):
					continue
				transitions.append(transition.as_dict())

		if not transitions:
			frappe.throw(
				_("You are not allowed to update as per the conditions set in {} Workflow.").format(
					get_link_to_form("Workflow", workflow)
				),
				title=_("Insufficient Permissions"),
			)

	def get_new_child_item(item_row):
		child_doctype = "Sales Order Item" if parent_doctype == "Sales Order" else "Purchase Order Item"
		return set_order_defaults(
			parent_doctype, parent_doctype_name, child_doctype, child_docname, item_row
		)

	def validate_quantity(child_item, new_data):
		if not flt(new_data.get("qty")):
			frappe.throw(
				_("Row # {0}: Quantity for Item {1} cannot be zero").format(
					new_data.get("idx"), frappe.bold(new_data.get("item_code"))
				),
				title=_("Invalid Qty"),
			)

		if parent_doctype == "Sales Order" and flt(new_data.get("qty")) < flt(child_item.delivered_qty):
			frappe.throw(_("Cannot set quantity less than delivered quantity"))

		if parent_doctype == "Purchase Order" and flt(new_data.get("qty")) < flt(
			child_item.received_qty
		):
			frappe.throw(_("Cannot set quantity less than received quantity"))

	def should_update_supplied_items(doc) -> bool:
		"""Subcontracted PO can allow following changes *after submit*:

		1. Change rate of subcontracting - regardless of other changes.
		2. Change qty and/or add new items and/or remove items
				Exception: Transfer/Consumption is already made, qty change not allowed.
		"""

		supplied_items_processed = any(
			item.supplied_qty or item.consumed_qty or item.returned_qty for item in doc.supplied_items
		)

		update_supplied_items = (
			any_qty_changed or items_added_or_removed or any_conversion_factor_changed
		)
		if update_supplied_items and supplied_items_processed:
			frappe.throw(_("Item qty can not be updated as raw materials are already processed."))

		return update_supplied_items

	def validate_fg_item_for_subcontracting(new_data, is_new):
		if is_new:
			if not new_data.get("fg_item"):
				frappe.throw(
					_("Finished Good Item is not specified for service item {0}").format(new_data["item_code"])
				)
			else:
				is_sub_contracted_item, default_bom = frappe.db.get_value(
					"Item", new_data["fg_item"], ["is_sub_contracted_item", "default_bom"]
				)

				if not is_sub_contracted_item:
					frappe.throw(
						_("Finished Good Item {0} must be a sub-contracted item").format(new_data["fg_item"])
					)
				elif not default_bom:
					frappe.throw(_("Default BOM not found for FG Item {0}").format(new_data["fg_item"]))

		if not new_data.get("fg_item_qty"):
			frappe.throw(_("Finished Good Item {0} Qty can not be zero").format(new_data["fg_item"]))

	data = json.loads(trans_items)

	any_qty_changed = False  # updated to true if any item's qty changes
	items_added_or_removed = False  # updated to true if any new item is added or removed
	any_conversion_factor_changed = False

	sales_doctypes = ["Sales Order", "Sales Invoice", "Delivery Note", "Quotation"]
	parent = frappe.get_doc(parent_doctype, parent_doctype_name)

	check_doc_permissions(parent, "write")
	_removed_items = validate_and_delete_children(parent, data)
	items_added_or_removed |= _removed_items

	for d in data:
		new_child_flag = False

		if not d.get("item_code"):
			# ignore empty rows
			continue

		if not d.get("item_code"):
			new_child_flag = True
			items_added_or_removed = True
			check_doc_permissions(parent, "create")
			child_item = get_new_child_item(d)
		else:
			check_doc_permissions(parent, "write")
			child_item = frappe.get_doc(parent_doctype + " Item", {'item_code':d.get("item_code"),'parent':parent_doctype_name})

			prev_rate, new_rate = flt(child_item.get("rate")), flt(d.get("rate"))
			prev_qty, new_qty = flt(child_item.get("qty")), flt(d.get("qty"))
			prev_fg_qty, new_fg_qty = flt(child_item.get("fg_item_qty")), flt(d.get("fg_item_qty"))
			prev_con_fac, new_con_fac = flt(child_item.get("conversion_factor")), flt(
				d.get("conversion_factor")
			)
			prev_uom, new_uom = child_item.get("uom"), d.get("uom")

			if parent_doctype == "Sales Order":
				prev_date, new_date = child_item.get("delivery_date"), d.get("delivery_date")
			elif parent_doctype == "Purchase Order":
				prev_date, new_date = child_item.get("schedule_date"), d.get("schedule_date")

			rate_unchanged = prev_rate == new_rate
			qty_unchanged = prev_qty == new_qty
			fg_qty_unchanged = prev_fg_qty == new_fg_qty
			uom_unchanged = prev_uom == new_uom
			conversion_factor_unchanged = prev_con_fac == new_con_fac
			any_conversion_factor_changed |= not conversion_factor_unchanged
			date_unchanged = (
				prev_date == getdate(new_date) if prev_date and new_date else False
			)  # in case of delivery note etc
			if (
				rate_unchanged
				and qty_unchanged
				and fg_qty_unchanged
				and conversion_factor_unchanged
				and uom_unchanged
				and date_unchanged
			):
				continue

		validate_quantity(child_item, d)
		if flt(child_item.get("qty")) != flt(d.get("qty")):
			any_qty_changed = True

		if (
			parent.doctype == "Purchase Order"
			and parent.is_subcontracted
			and not parent.is_old_subcontracting_flow
		):
			validate_fg_item_for_subcontracting(d, new_child_flag)
			child_item.fg_item_qty = flt(d["fg_item_qty"])

			if new_child_flag:
				child_item.fg_item = d["fg_item"]

		child_item.qty = flt(d.get("qty"))
		rate_precision = child_item.precision("rate") or 2
		conv_fac_precision = child_item.precision("conversion_factor") or 2
		qty_precision = child_item.precision("qty") or 2

		# Amount cannot be lesser than billed amount, except for negative amounts
		row_rate = flt(d.get("rate"), rate_precision)
		amount_below_billed_amt = flt(child_item.billed_amt, rate_precision) > flt(
			row_rate * flt(d.get("qty"), qty_precision), rate_precision
		)
		if amount_below_billed_amt and row_rate > 0.0:
			frappe.throw(
				_("Row #{0}: Cannot set Rate if amount is greater than billed amount for Item {1}.").format(
					child_item.idx, child_item.item_code
				)
			)
		else:
			child_item.rate = row_rate

		if d.get("conversion_factor"):
			if child_item.stock_uom == child_item.uom:
				child_item.conversion_factor = 1
			else:
				child_item.conversion_factor = flt(d.get("conversion_factor"), conv_fac_precision)

		if d.get("uom"):
			child_item.uom = d.get("uom")
			conversion_factor = flt(
				get_conversion_factor(child_item.item_code, child_item.uom).get("conversion_factor")
			)
			child_item.conversion_factor = (
				flt(d.get("conversion_factor"), conv_fac_precision) or conversion_factor
			)

		if d.get("delivery_date") and parent_doctype == "Sales Order":
			child_item.delivery_date = d.get("delivery_date")
		
		if d.get("msow") and parent_doctype == "Sales Order":
			child_item.msow = d.get("msow")
		if d.get("warehouse") and parent_doctype == "Sales Order":
			child_item.warehouse = d.get("warehouse")
		if d.get("custom_so_qty") and parent_doctype == "Sales Order":
			child_item.custom_so_qty = d.get("custom_so_qty")
		
		if d.get("work_title") and parent_doctype == "Sales Order":
			child_item.work_title = d.get("work_title")

		if d.get("schedule_date") and parent_doctype == "Purchase Order":
			child_item.schedule_date = d.get("schedule_date")

		if flt(child_item.price_list_rate):
			if flt(child_item.rate) > flt(child_item.price_list_rate):
				#  if rate is greater than price_list_rate, set margin
				#  or set discount
				child_item.discount_percentage = 0

				if parent_doctype in sales_doctypes:
					child_item.margin_type = "Amount"
					child_item.margin_rate_or_amount = flt(
						child_item.rate - child_item.price_list_rate, child_item.precision("margin_rate_or_amount")
					)
					child_item.rate_with_margin = child_item.rate
			else:
				child_item.discount_percentage = flt(
					(1 - flt(child_item.rate) / flt(child_item.price_list_rate)) * 100.0,
					child_item.precision("discount_percentage"),
				)
				child_item.discount_amount = flt(child_item.price_list_rate) - flt(child_item.rate)

				if parent_doctype in sales_doctypes:
					child_item.margin_type = ""
					child_item.margin_rate_or_amount = 0
					child_item.rate_with_margin = 0

		child_item.flags.ignore_validate_update_after_submit = True
		if new_child_flag:
			parent.load_from_db()
			child_item.idx = len(parent.items) + 1
			child_item.insert()
		else:
			child_item.save()

	parent.reload()
	parent.flags.ignore_validate_update_after_submit = True
	parent.set_qty_as_per_stock_uom()
	parent.calculate_taxes_and_totals()
	parent.set_total_in_words()
	if parent_doctype == "Sales Order":
		make_packing_list(parent)
		parent.set_gross_profit()
	frappe.get_doc("Authorization Control").validate_approving_authority(
		parent.doctype, parent.company, parent.base_grand_total
	)

	parent.set_payment_schedule()
	if parent_doctype == "Purchase Order":
		parent.validate_minimum_order_qty()
		parent.validate_budget()
		if parent.is_against_so():
			parent.update_status_updater()
	else:
		parent.check_credit_limit()

	# reset index of child table
	for idx, row in enumerate(parent.get(child_docname), start=1):
		row.idx = idx

	parent.save()

	if parent_doctype == "Purchase Order":
		update_last_purchase_rate(parent, is_submit=1)

		if any_qty_changed or items_added_or_removed or any_conversion_factor_changed:
			parent.update_prevdoc_status()

		parent.update_requested_qty()
		parent.update_ordered_qty()
		parent.update_ordered_and_reserved_qty()
		parent.update_receiving_percentage()

		if parent.is_subcontracted:
			if parent.is_old_subcontracting_flow:
				if should_update_supplied_items(parent):
					parent.update_reserved_qty_for_subcontract()
					parent.create_raw_materials_supplied()
				parent.save()
			else:
				if not parent.can_update_items():
					frappe.throw(
						_(
							"Items cannot be updated as Subcontracting Order is created against the Purchase Order {0}."
						).format(frappe.bold(parent.name))
					)
	else:  # Sales Order
		parent.validate_warehouse()
		parent.update_reserved_qty()
		parent.update_project()
		parent.update_prevdoc_status("submit")
		parent.update_delivery_status()

	parent.reload()
	validate_workflow_conditions(parent)

	parent.update_blanket_order()
	parent.update_billing_percentage()
	parent.set_status()

	# Cancel and Recreate Stock Reservation Entries.
	if parent_doctype == "Sales Order":
		from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
			cancel_stock_reservation_entries,
			has_reserved_stock,
		)

		if has_reserved_stock(parent.doctype, parent.name):
			cancel_stock_reservation_entries(parent.doctype, parent.name)

			if parent.per_picked == 0:
				parent.create_stock_reservation_entries()


def check_if_child_table_updated(
	child_table_before_update, child_table_after_update, fields_to_check
):
	accounting_dimensions = get_accounting_dimensions() + ["cost_center", "project"]
	# Check if any field affecting accounting entry is altered
	for index, item in enumerate(child_table_after_update):
		for field in fields_to_check:
			if child_table_before_update[index].get(field) != item.get(field):
				return True

		for dimension in accounting_dimensions:
			if child_table_before_update[index].get(dimension) != item.get(dimension):
				return True

	return False

@frappe.whitelist()
def validate_and_delete_children(parent, data) -> bool:
	deleted_children = []
	updated_item_names = [d.get("item_code") for d in data]
	for item in parent.items:
		if item.item_code not in updated_item_names:
			deleted_children.append(item)

	for d in deleted_children:
		# validate_child_on_delete(d, parent)
		d.cancel()
		d.delete(ignore_permissions=True)

	# need to update ordered qty in Material Request first
	# bin uses Material Request Items to recalculate & update
	parent.update_prevdoc_status()

	# for d in deleted_children:
	# 	# update_bin_on_delete(d, parent.doctype)

	return bool(deleted_children)



@frappe.whitelist()
def create_tasks(sales_order):
	if sales_order:
		so = frappe.get_doc("Sales Order",sales_order)
		for so_installation in so.installation:
			if not frappe.db.exists("Task",{'project':so.project,'msow':so_installation.msow,'item_code':so_installation.item}):
				task = frappe.new_doc("Task")
				task.update({
					"project": so.project,
					"msow":so_installation.msow,
					"item_code":so_installation.item,
					"subject": so_installation.item_name,
					"description":so_installation.description,
					"uom":so_installation.unit,
					"qty": so_installation.qty,
					"pending_qty": so_installation.qty,
					"cost":so_installation.cost,
					"cost_amount":so_installation.cost_amount,
					"budgeted_cost":so_installation.unit_price,
					"budgeted_amount":so_installation.amount,
					"selling_price":so_installation.rate_with_overheads,
					"selling_amount":so_installation.amount_with_overheads,
					"is_group": 0
				})
				task.save(ignore_permissions=True)

# Update the data in the Total Cost Section
@frappe.whitelist()
def udpate_total_cost_section(doc, method):
    pb_sow = frappe.get_all("PB SOW", {"project_budget": doc.name}, ["name", "pb_overhead_percent", "pb_overhead_amount", "pb_contigency_percent", "pb_engineering_overhead_percent", "pb_engineering_overhead_amount", "pb_business_promotion_amount", "pb_business_promotion_percent"])
    overhead_per = 0
    overhead_amount = 0
    contigency_per = 0
    contigency_amount = 0
    eng_overhead_per = 0
    eng_overhead_amount = 0
    bus_prom_amount = 0
    bus_prom_per = 0
    for i in pb_sow:
        overhead_per += i.pb_overhead_percent
        overhead_amount += i.pb_overhead_amount
        contigency_per += i.pb_contigency_percent
        contigency_amount += i.pb_contigency_amount
        eng_overhead_per += i.pb_engineering_overhead_percent
        eng_overhead_amount += i.pb_engineering_overhead_amount
        bus_prom_per += i.pb_business_promotion_percent
        bus_prom_amount += i.pb_business_promotion_amount
    
    
@frappe.whitelist()
def test_check():
    doc = frappe.get_doc("Project Budget", "INT-PB-2024-00010-10")
    pb_sow = frappe.get_all("PB SOW", {"project_budget": doc.name}, ["name", "pb_overhead_percent", "pb_overhead_amount", "pb_contigency_percent", "pb_engineering_overhead_percent", "pb_engineering_overhead_amount", "pb_business_promotion_amount"])
    overhead_per = 0
    overhead_amount = 0
    contigency_per = 0
    contigency_amount = 0
    eng_overhead_per = 0
    eng_overhead_amount = 0
    bus_prom_amount = 0
    for i in pb_sow:
        overhead_per += i.pb_overhead_percent or 0
        overhead_amount += i.pb_overhead_amount or 0
        contigency_per += i.pb_contigency_percent or 0
        contigency_amount += i.pb_contigency_amount or 0
        eng_overhead_per += i.pb_engineering_overhead_percent or 0
        eng_overhead_amount += i.pb_engineering_overhead_amount or 0
        bus_prom_amount += i.pb_business_promotion_amount or 0
    doc.total_overhead = overhead_per
    doc.engineering_overhead = eng_overhead_per
    doc.contigency_percent = contigency_per
    doc.total_amount_as_overhead = overhead_amount
    doc.total_amount_as_engineering_overhead = eng_overhead_amount
    doc.contigency = contigency_amount
    doc.total_business_promotion = bus_prom_amount
    doc.save(ignore_permissions=True)
    
# Create Sow as Item
@frappe.whitelist()
def create_item_for_sow(project_budget):
	doc = frappe.get_doc("Project Budget", project_budget)
	if doc.master_scope_of_work:
		for i in doc.master_scope_of_work:
			exists = frappe.db.exists("Item",i.msow)
			if not exists:
				item = frappe.new_doc("Item")
				item.item_code = i.msow
				item.item_name = i.msow_desc
				item.description = i.msow_desc
				item.is_stock_item = 0
				item.stock_uom = i.unit
				item.item_group = "Projects"
				item.save(ignore_permissions = True)
				frappe.db.commit()
	
# @frappe.whitelist()
# def update_msows_new(document,sales_order):
# 	total_bidding_price = 0
# 	total_amount_so=0
# 	doc = frappe.get_doc("Project Budget",document)
# 	if doc.company == "INTERIOR DIVISION - ELECTRA":
# 		warehouse = "Electra Interior Warehouse - INE"
# 	if doc.company == "ENGINEERING DIVISION - ELECTRA":
# 		warehouse = "Electra Engineering Warehouse - EED"
# 	if doc.company == "MEP DIVISION - ELECTRA":
# 		warehouse = "Electra MEP Warehouse - MEP"
# 	so = frappe.get_doc('Sales Order',sales_order)
# 	if so.docstatus==1:
		
# 		if so.custom_sow_item_table == 1:
# 	# 		so.set('items', [])
# 			for itm in doc.master_scope_of_work:
# 				total_amount_so += itm.total_bidding_price
# 	# 			so.append("items", {
# 	# 				"item_code": itm.msow,
# 	# 				"item_name": itm.msow_desc,
# 	# 				"msow": itm.msow,
# 	# 				"qty": itm.qty,
# 	# 				"uom": itm.unit,
# 	# 				"custom_so_qty": itm.qty,
# 	# 				"rate": itm.unit_price,
# 	# 				"amount": itm.total_bidding_price,
# 	# 				"conversion_factor": 1,
# 	# 				"warehouse": warehouse
# 	# 			})
# 		else:
# 			so.set('items', [])
# 			for itm in doc.item_table:
# 				total_amount_so += itm.amount_with_overheads
# 				so.append("items", {
# 					"item_code": itm.item,
# 					"item_name": itm.item_name,
# 					"msow": itm.msow,
# 					"qty": itm.qty,
# 					"uom": itm.unit,
# 					"custom_so_qty": itm.qty,
# 					"rate": itm.rate_with_overheads,
# 					"amount": itm.amount_with_overheads,
# 					"conversion_factor": 1,
# 					"warehouse": warehouse,
# 					"delivered_qty": itm.delivered_qty,
# 					'work_title':itm.work_title
# 				})
# 		so.total = total_amount_so
# 		so.net_total =total_amount_so - so.discount_amount
# 		so.grand_total = total_amount_so - so.discount_amount
# 		so.save(ignore_permissions=True)
# 		so.reload()

