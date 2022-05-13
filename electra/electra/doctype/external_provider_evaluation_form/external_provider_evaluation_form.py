# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, add_months,today,add_days,nowdate,flt
import datetime
from datetime import datetime

class ExternalProviderEvaluationForm(Document):
	def validate(self):
		epes = frappe.get_all("External Provider Evaluation",['*'])
		for epe in epes:
			range_from = epe['from']
			range_to = epe['to']
			eval_period = epe['evaluation_period']
			# if self.actual_score > int(range_from) and self.actual_score < int(range_to):
			# 	self.re_evaluation_date = add_months(today(),int(eval_period))

		
		
		
