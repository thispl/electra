# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt
import erpnext
import datetime
import calendar
from erpnext.accounts.report.financial_statements import (
	get_columns,
	get_data,
	get_filtered_list_for_consolidated_report,
	get_period_list,
)
def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data
def get_columns(filters):
	months = [
		_("January"), _("February"), _("March"), _("April"), _("May"), _("June"),_("July"), _("August"), _("September"), _("October"), _("November"), _("December"), _("Overall")
	]
	columns = []
	for month in months:
		columns += [
			month + ":Currency/:140",
			
		]
	columns.insert(0, _("Company") + ":Link/Company:300")
	return columns



import calendar
from datetime import datetime

def get_data(filters):
	year = int(filters.year)
	current_date = datetime.today()
	comp = frappe.db.sql("SELECT name FROM `tabCompany`", as_dict=True)
	result = []

	for company in comp:
		row = [company.name]
		monthly_incomes = []
		total = 0

		for month in range(1, 13):
			start_date = f"{year}-{month:02d}-01"
			end_day = calendar.monthrange(year, month)[1]
			end_date = f"{year}-{month:02d}-{end_day}"

			if datetime(year, month, 1) > current_date:
				income = 0
			else:
				income = get_income_amount(start_date, end_date, company.name, year)

			monthly_incomes.append(income)
			total += income
		if total > 0:
			row += monthly_incomes + [total]
			result.append(row)
	return result


class DotDict(dict):
	"""Enables both dot notation and .get() on a dict."""
	def __getattr__(self, name):
		return self.get(name, None)
	
	def __setattr__(self, name, value):
		self[name] = value
		
@frappe.whitelist()
def get_income_amount(from_date, to_date, company ,year):
	filters = DotDict({'company': company, 'filter_based_on': 'Date Range', 'period_start_date': from_date, 'period_end_date': to_date, 'from_fiscal_year': year, 'to_fiscal_year': year, 'periodicity': 'Monthly', 'cost_center': [], 'project': [], 'accumulated_values': 1})
	period_list = get_period_list(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)
	income = erpnext.accounts.report.financial_statements.get_data(
		filters.company,
		"Income",
		"Credit",
		period_list,
		filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True,
		ignore_accumulated_values_for_fy=True,
	)
	total_income = 0.0
	stock_transfer = 0.0
	other_income = 0.0

	for row in income:
		if row.get("account_name") == "Total Income (Credit)":
			total_income = row.get("total", 0.0)
			break
	
	for row in income:
		if row.get("account_name") == "Sales - Stock Transfer":
			stock_transfer = row.get("total", 0.0)
			break
	
	for row in income:
		if row.get("account_name") == "Other Income":
			other_income = row.get("total", 0.0)
			break

	return total_income - stock_transfer - other_income or 0

@frappe.whitelist()
def test_check():
	company = "TRADING DIVISION - ELECTRA"
	from_date = "2025-01-01"
	to_date = "2025-01-31"
	year = "2025"
	filters = DotDict({'company': company, 'filter_based_on': 'Date Range', 'period_start_date': from_date, 'period_end_date': to_date, 'from_fiscal_year': year, 'to_fiscal_year': year, 'periodicity': 'Monthly', 'cost_center': [], 'project': [], 'accumulated_values': 1})
	period_list = get_period_list(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)
	income = erpnext.accounts.report.financial_statements.get_data(
		filters.company,
		"Income",
		"Credit",
		period_list,
		filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True,
		ignore_accumulated_values_for_fy=True,
	)
	return income
	# total_income = 0.0

	# for row in income:
	# 	if row.get("account_name") == "Total Income (Credit)":
	# 		total_income = row.get("total", 0.0)
	# 		break

	# return total_income
