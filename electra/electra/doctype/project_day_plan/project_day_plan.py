# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import date, datetime, timedelta
import time

class ProjectDayPlan(Document):
	def on_submit(self):
		pdp = frappe.new_doc("Project Day Plan Timesheet")
		pdp.plan_date = self.plan_date
		pdp.company = self.company
		pdp.project_day_plan = self.name
		for pdpe in self.project_day_plan_employee:
			pdp.append("project_day_plan_employee", {
					"project": pdpe.project,
					"project_name": pdpe.project_name,
					"employee": pdpe.employee,
					"employee_name": pdpe.employee_name,
					"designation": pdpe.designation,
					"from_time":"00:00:00",
					"to_time":"00:00:00",
					"lunch_break":"01:00:00",
					"total_working_hours":"00:00:00",
					"ot":"00:00:00"
				})

		pdp.save(ignore_permissions=True)