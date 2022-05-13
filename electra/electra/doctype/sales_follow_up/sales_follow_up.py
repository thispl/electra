# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SalesFollowUP(Document):
	def validate(self):
		if self.follow_up_for == 'Lead':
			if self.status == 'Converted':
				self.status = 'Converted'
				self.has_customer = 1
				frappe.set_value("Lead",self.lead_customer,"status","Converted")
