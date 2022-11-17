# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DaySchedule(Document):
	pass
	# def on_submit(self):
	# 	dp = frappe.new_doc("Day Plan")
	# 	for i in self.schedule:
	# 		dp.customer = i.customer
	# 		dp.project = i.project
	# 		dp.project_name = i.project_name
	# 		dp.company = self.company
	# 		dp.planned_date = self.schedule_date
	# 		dp.staff = i.staff
	# 		dp.worker = i.worker
	# 		dp.supervisor = i.supervisor
	# 		dp.day_schedule = self.name
	# 		dp.flags.ignore_mandatory = True
	# 		dp.save(ignore_permissions = True)

