# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class VehicleAccidentReport(Document):
	pass

	@frappe.whitelist()
	def on_submit(self):
		vehicle = frappe.get_doc("Vehicle",{'name':self.plate_no})
		vehicle.append('vehicle_accident_log',{
			"type":"Accident",
			"employee":self.emp_id,
			"date":self.date_of_accident,
			"remarks":self.remarks,
			"document":self.name
		})
		vehicle.save(ignore_permissions=True)
		frappe.db.commit()