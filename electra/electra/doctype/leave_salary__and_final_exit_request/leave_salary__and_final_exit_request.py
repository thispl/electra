# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
import frappe,erpnext

class LeaveSalaryandFinalExitRequest(Document):
	def validate(self):
		if self.is_new() and self.last_rejoin_date and self.type_of_request != 'End of Service':

			days = date_diff(self.request_date,self.last_rejoin_date)
			days1 = days+1

			if self.grade=="STAFF":
				value = 335 + int(self.total_leave_taken)
				if days1<value:
					frappe.throw("Not Applicable to apply for this document")
			else:
				value = 365 + int(self.total_leave_taken)
				if days1<value:
					frappe.throw("Not Applicable to apply for this document")
