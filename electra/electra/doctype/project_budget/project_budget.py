# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ProjectBudget(Document):
	def after_insert(self):
		cost = frappe.get_doc("Cost Estimation",{'name':self.cost_estimation})
		cost.project_budget = self.name
		cost.save(ignore_permissions= True)
	def on_update(self):
		so = frappe.get_doc('Sales Order',self.sales_order)
		for it in so.items:
			if self.company == "MEP DIVISION - ELECTRA":
				for mat in self.materials:
					if mat.item == it.item_code:
						it.rate = mat.unit_price
						it.qty = mat.qty
						it.amount = mat.amount
			else:
				for mat in self.materials:
					if mat.item == it.item_code:
						it.rate = mat.rate_with_overheads
						it.qty = mat.qty
						it.amount = mat.amount_with_overheads
			for ins in self.installation:
				if ins.item == it.item_code:
					it.qty = ins.qty
					it.rate = ins.rate_with_overheads
					it.amount = ins.amount_with_overheads
			for des in self.design:
				if des.item == it.item_code:
					it.qty = des.qty
					it.rate = des.rate_with_overheads
					it.amount = des.amount_with_overheads
			for acc in self.bolts_accessories:
				if acc.item == it.item_code:
					it.qty = acc.qty
					it.rate = acc.rate_with_overheads
					it.amount = acc.amount_with_overheads
			for work in self.finishing_work:
				if work.item == it.item_code:
					it.qty = work.qty
					it.rate = work.rate_with_overheads
					it.amount = work.amount_with_overheads
			for man in self.manpower:
				if man.worker == it.item_code:
					it.qty = man.total_workers
					it.rate = man.rate_with_overheads
					it.amount = man.amount_with_overheads
			for heavy in self.heavy_equipments:
				if heavy.item == it.item_code:
					it.qty = heavy.qty
					it.rate = heavy.rate_with_overheads
					it.amount = heavy.amount_with_overheads
			for ot in self.others:
				if ot.item == it.item_code:
					it.qty = ot.qty
					it.rate = ot.rate_with_overheads
					it.amount = ot.amount_with_overheads
		so.save(ignore_permissions=True)



