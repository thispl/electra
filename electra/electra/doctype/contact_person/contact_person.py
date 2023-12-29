# Copyright (c) 2023, Teampro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ContactPerson(Document):
	def on_submit(self):
		contact = frappe.new_doc('Contact')  
		contact.first_name = self.first_name
		contact.contact_person_name = self.name
		contact.append('email_ids',{
			'email_id':self.email_id,
			
		})
		contact.append('phone_nos',{
			'phone':self.mobile_number,
			
		})
		contact.append('links',{
			'link_doctype':'Customer',
			"link_name": self.customer
			
		})
		contact.save(ignore_permissions=True)
	   