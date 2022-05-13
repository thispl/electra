# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SponsorCompany(Document):
	# def validate(self):
	# 	self.test_location_dict = {'type': 'FeatureCollection', 'features': [
	# 		{'type': 'Feature', 'properties': {}, "geometry": {'type': 'Point', 'coordinates': [49.20433, 55.753395]}}]}
	# 	self.location = frappe.get_doc({'name': 'Test Location', 'doctype': 'Location',
	# 										 'location': str(self.test_location_dict)})
	def on_update(self):
		update_cr(self)
		update_cc(self)
		update_tl(self)
		update_cd(self)

def update_cr(self):
	if frappe.db.exists("Legal Compliance Monitor",{'reference_number':self.cr_number}):
		lcmid = frappe.get_value("Legal Compliance Monitor",{'reference_number':self.cr_number},["name"])
		lcm = frappe.get_doc("Legal Compliance Monitor",lcmid)
	else:	
		lcm = frappe.new_doc("Legal Compliance Monitor")
	lcm.sponsor_company = self.company_name
	lcm.name_of_licence = "Commercial Registration"
	lcm.reference_number = self.cr_number
	lcm.category = 'Government'
	lcm.group = 'Sponsor Company'
	lcm.sponsor_company = self.name
	lcm.issue_date = self.cr_issue_date
	lcm.last_renewal_date = self.cr_issue_date
	lcm.next_due = self.cr_expiry_date
	lcm.attach_file = self.cr_attachment
	lcm.save(ignore_permissions=True)
	frappe.db.commit()

def update_cc(self):
	if frappe.db.exists("Legal Compliance Monitor",{'reference_number':self.computer_card_number}):
		lcmid = frappe.get_value("Legal Compliance Monitor",{'reference_number':self.computer_card_number},["name"])
		lcm = frappe.get_doc("Legal Compliance Monitor",lcmid)
	else:	
		lcm = frappe.new_doc("Legal Compliance Monitor")
	lcm.sponsor_company = self.company_name
	lcm.name_of_licence = "Computer Card"
	lcm.reference_number = self.computer_card_number
	lcm.category = 'Government'
	lcm.group = 'Sponsor Company'
	lcm.sponsor_company = self.name
	lcm.issue_date = self.computer_card_issue_date
	lcm.last_renewal_date = self.computer_card_issue_date
	lcm.next_due = self.computer_card_expiry_date
	lcm.attach_file = self.computer_card_attachment
	lcm.save(ignore_permissions=True)
	frappe.db.commit()

def update_tl(self):
	if frappe.db.exists("Legal Compliance Monitor",{'reference_number':self.trade_license_number}):
		lcmid = frappe.get_value("Legal Compliance Monitor",{'reference_number':self.trade_license_number},["name"])
		lcm = frappe.get_doc("Legal Compliance Monitor",lcmid)
	else:	
		lcm = frappe.new_doc("Legal Compliance Monitor")
	lcm.sponsor_company = self.company_name
	lcm.name_of_licence = "Trade License"
	lcm.reference_number = self.trade_license_number
	lcm.category = 'Government'
	lcm.group = 'Sponsor Company'
	lcm.sponsor_company = self.name
	lcm.issue_date = self.baldia_issue_date
	lcm.last_renewal_date = self.baldia_issue_date
	lcm.next_due = self.baldia_expiry_date
	lcm.attach_file = self.baldia_attachment
	lcm.save(ignore_permissions=True)
	frappe.db.commit()


def update_cd(self):
	if frappe.db.exists("Legal Compliance Monitor",{'reference_number':self.civil_defense_id}):
		lcmid = frappe.get_value("Legal Compliance Monitor",{'reference_number':self.civil_defense_id},["name"])
		lcm = frappe.get_doc("Legal Compliance Monitor",lcmid)
	else:	
		lcm = frappe.new_doc("Legal Compliance Monitor")
	lcm.sponsor_company = self.company_name
	lcm.name_of_licence = "Civil Defense"
	lcm.reference_number = self.civil_defense_id
	lcm.category = 'Government'
	lcm.group = 'Sponsor Company'
	lcm.sponsor_company = self.name
	lcm.issue_date = self.civil_defense_issued_date
	lcm.last_renewal_date = self.civil_defense_issued_date
	lcm.next_due = self.civil_defense_expiry_date
	lcm.attach_file = self.civil_defense_attachment
	lcm.save(ignore_permissions=True)
	frappe.db.commit()