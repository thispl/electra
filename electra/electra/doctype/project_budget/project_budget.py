# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import math
from math import floor

class ProjectBudget(Document):
	# def on_cancel(self):
	# 	dsts = frappe.db.get_value("Sales Order",{'name':self.sales_order},['docstatus'])
	# 	if dsts == 1:
	# 		so = frappe.db.exists("Sales Order",{'project_budget':self.name})
	# 		if so:
	# 			so.cancel()

	def after_insert(self):
		self.check_7 = 0
		cost = frappe.get_doc("Cost Estimation",{'name':self.cost_estimation})
		cost.project_budget = self.name
		cost.save(ignore_permissions= True)
		frappe.errprint("CE")
		so = frappe.get_doc("Sales Order",{'name':self.sales_order})
		so.project_budget = self.name
		so.save(ignore_permissions= True)
		frappe.errprint("SO")


	# def before_submit(self):
	# 	so = frappe.get_doc('Sales Order',self.sales_order)
	# 	if self.amended_from:
	# 		so.so_revision = self.so_revision
	# 		so.pb_revision = self.pb_revision
	# 		so.save(ignore_permissions=True)

	def on_submit(self):
		total_bidding_price = 0
		w_house = frappe.db.get_value("Warehouse",{'company':self.company,'default_for_stock_transfer':1},['name'])
		so = frappe.get_doc('Sales Order',self.sales_order)
		if self.amended_from:
			so.so_revision = self.so_revision
			so.pb_revision = self.pb_revision
		if so.docstatus !=1:
			so.set('items', [])
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
				so.append("items", {
					"item_code": des.item,
					"msow": des.msow,
					"item_name": des.item_name,
					"qty": des.qty,
					"rate": des.rate_with_overheads,
					"warehouse" : w_house,
					"amount": des.amount_with_overheads,
					"description": frappe.db.get_value("Item",des.item,['description']),
					"uom": frappe.db.get_value("Item",des.item,['stock_uom']),
					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':des.item},['conversion_factor']),
				})
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
				})

			if self.company == "MEP DIVISION - ELECTRA":
				for mat in self.materials:
					so.append("items", {
						"msow":mat.msow,
						"item_code": mat.item,
						"item_name": mat.item_name,
						"qty": mat.qty,
						"rate": mat.rate_with_overheads,
						"warehouse" : w_house,
						"amount": mat.amount_with_overheads,
						"description": frappe.db.get_value("Item",mat.item,['description']),
						"uom": frappe.db.get_value("Item",mat.item,['stock_uom']),
						"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':mat.item},['conversion_factor']),
					})
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
					})
			else:
				for mat in self.materials:
					so.append("items", {
						"msow":mat.msow,
						"item_code": mat.item,
						"item_name": mat.item_name,
						"qty": mat.qty,
						"rate": mat.rate_with_overheads,
						"warehouse" : w_house,
						"amount": mat.amount_with_overheads,
						"description": frappe.db.get_value("Item",mat.item,['description']),
						"uom": frappe.db.get_value("Item",mat.item,['stock_uom']),
						"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':mat.item},['conversion_factor']),
					})
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
					})
			for ins in self.installation:
				so.append("items", {
					"msow":ins.msow,
					"item_code": ins.item,
					"item_name": ins.item_name,
					"qty": ins.qty,
					"rate": ins.rate_with_overheads,
					"warehouse" : w_house,
					"amount": ins.amount_with_overheads,
					"description": frappe.db.get_value("Item",ins.item,['description']),
					"uom": frappe.db.get_value("Item",ins.item,['stock_uom']),
					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':ins.item},['conversion_factor']),
				})
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
				})
			for hv in self.heavy_equipments:
				so.append("items", {
					"msow":hv.msow,
					"item_code": hv.item,
					"item_name": hv.item_name,
					"qty": hv.qty,
					"rate": hv.rate_with_overheads,
					"warehouse" : w_house,
					"amount": hv.amount_with_overheads,
					"description": frappe.db.get_value("Item",hv.item,['description']),
					"uom": frappe.db.get_value("Item",hv.item,['stock_uom']),
					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':hv.item},['conversion_factor']),
				})
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
				})

			for fg in self.finished_goods:
				if fg.bom:
					finished_good = frappe.get_doc("BOM",fg.bom)
					finished_good.project_budget = self.name
					finished_good.submit()
				so.append("items", {
					"msow":fg.msow,
					"item_code": fg.item,
					"item_name": fg.item_name,
					"qty": fg.qty,
					"rate": fg.rate_with_overheads,
					"warehouse" : w_house,
					"amount": fg.amount_with_overheads,
					"description": frappe.db.get_value("Item",fg.item,['description']),
					"uom": frappe.db.get_value("Item",fg.item,['stock_uom']),
					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':fg.item},['conversion_factor']),
				})
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
				})

			for ot in self.others:
				so.append("items", {
					"msow":ot.msow,
					"item_code": ot.item,
					"item_name": ot.item_name,
					"qty": ot.qty,
					"rate": ot.rate_with_overheads,
					"warehouse" : w_house,
					"amount": ot.amount_with_overheads,
					"description": frappe.db.get_value("Item",ot.item,['description']),
					"uom": frappe.db.get_value("Item",ot.item,['stock_uom']),
					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':ot.item},['conversion_factor']),
				})
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
				})
			for fw in self.finishing_work:
				so.append("items", {
					"msow":fw.msow,
					"item_code": fw.item,
					"item_name": fw.item_name,
					"qty": fw.qty,
					"rate": fw.rate_with_overheads,
					"warehouse" : w_house,
					"amount": fw.amount_with_overheads,
					"description": frappe.db.get_value("Item",fw.item,['description']),
					"uom": frappe.db.get_value("Item",fw.item,['stock_uom']),
					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':fw.item},['conversion_factor']),
				})
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
				})
			for ba in self.bolts_accessories:
				so.append("items", {
					"msow":ba.msow,
					"item_code": ba.item,
					"item_name": ba.item_name,
					"qty": ba.qty,
					"rate": ba.rate_with_overheads,
					"warehouse" : w_house,
					"amount": ba.amount_with_overheads,
					"description": frappe.db.get_value("Item",ba.item,['description']),
					"uom": frappe.db.get_value("Item",ba.item,['stock_uom']),
					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':ba.item},['conversion_factor']),
				})
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
				})
			for mn in self.manpower:
				so.append("items", {
					"msow":mn.msow,
					"item_code": mn.worker,
					"item_name": mn.worker,
					"qty": mn.total_workers,
					"rate": mn.rate_with_overheads,
					"warehouse" : w_house,
					"amount": mn.amount_with_overheads,
					"description": frappe.db.get_value("Item",mn.worker,['description']),
					"uom": frappe.db.get_value("Item",mn.worker,['stock_uom']),
					"conversion_factor": frappe.db.get_value("UOM Conversion Detail",{'parent':mn.worker},['conversion_factor']),
				})
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
				})
			so.total_bidding_price = total_bidding_price
			so.net_bidding_price = total_bidding_price - so.project_discount_amt
			so.save(ignore_permissions=True)


@frappe.whitelist()
def round(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

@frappe.whitelist()
def update_msows(document,sales_order):
	total_bidding_price = 0
	doc = frappe.get_doc("Project Budget",document)
	so = frappe.get_doc('Sales Order',sales_order)
	if doc.revision == "SO - Revision":
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
			})
		for work_title in doc.work_title_summary:
			so.append("so_work_title_item",{
				"item_name":work_title.item_name,
				"quantity":work_title.quantity,
				"amount":work_title.amount,
			})
		so.total_bidding_price = total_bidding_price
		so.net_bidding_price = total_bidding_price - so.project_discount_amt
		so.save(ignore_permissions=True)

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

				



