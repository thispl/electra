# Copyright (c) 2024, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours


class AccountsLedgerSummaryReportDashboard(Document):
	pass

