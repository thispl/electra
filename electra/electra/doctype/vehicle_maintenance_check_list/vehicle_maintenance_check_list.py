# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class VehicleMaintenanceCheckList(Document):

	def on_submit(self):
		pi = frappe.new_doc("Purchase Invoice")
		pi.supplier = self.supplier
		pi.posting_date = now()
		pi.company = self.company
		pi.append("items",{
			"item_code" : "Vehicle Maintenance Check",
			"qty":"1",
			"item_name":self.name,
			"amount":self.actual_expense,
		})
		pi.flags.ignore_mandatory = True
		pi.flags.ignore_validate = True
		pi.save(ignore_permissions = True)

		vehicle = frappe.get_doc("Vehicle",{'name':self.register_no})
		vehicle.last_odometer = self.present_kilometer
		vehicle.append('vehicle_maintanance_log',{
			"type":"Maintenance",
			"employee":self.employee_id,
			"date":self.work_finished_date,
			"remarks":self.hr_manager,
			"document":self.name
		})
		vehicle.save(ignore_permissions = True)
		frappe.db.commit()


@frappe.whitelist()
def register_no(register_no):
	frappe.errprint("hi")
	vehicle = frappe.db.sql("""SELECT work_finished_date, present_kilometer FROM `tabVehicle Maintenance Check List` WHERE register_no = '%s' """ % register_no, as_dict=True)[0] or "-"
	return vehicle
	

