# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CostEstimation(Document):
	def validate(self):
		master_sow = self.master_scope_of_work
		for msow in master_sow:
			if msow.msow:
				if frappe.db.exists('Master Scope of Work',msow.msow):
					msow_id = frappe.get_doc("Master Scope of Work",msow.msow)
				else:
					msow_id = frappe.new_doc("Master Scope of Work")
				msow_id.master_scope_of_work = msow.msow
				msow_id.desc = msow.msow_desc
				msow_id.save(ignore_permissions=True)
