# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LegalComplianceMonitor(Document):
	def on_update(self):
		if self.sponsor_company :
			sponsor_company = frappe.get_doc("Sponsor Company",self.sponsor_company)
			if self.name_of_licence == 'Commercial Registration':
				sponsor_company.update({
					"cr_issue_date" : self.issue_date,
					"cr_expiry_date" : self.next_due
				})
			if self.name_of_licence == 'Computer Card':
				sponsor_company.update({
					"computer_card_issue_date" : self.issue_date,
					"computer_card_expiry_date" : self.next_due
				})
			if self.name_of_licence == 'Trade License':
				sponsor_company.update({
					"baldia_issue_date" : self.issue_date,
					"baldia_expiry_date" : self.next_due
				})
			sponsor_company.db_update()
