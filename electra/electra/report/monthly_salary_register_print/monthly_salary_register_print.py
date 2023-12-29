# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt
import erpnext
from frappe.utils import formatdate

def execute(filters=None):

	if not filters:
		filters = {}
	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))
	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return [], []

	columns, earning_types, ded_types = get_columns(salary_slips)
	ss_earning_map = get_ss_earning_map(salary_slips, currency, company_currency)
	ss_ded_map = get_ss_ded_map(salary_slips, currency, company_currency)
	doj_map = get_employee_doj_map()
	

	data = []
	for ss in salary_slips:
		sum_emp = frappe.db.sql("""select sum(basic + hra + _other_allowance + transportation) as total from `tabEmployee` where employee='%s' """%(ss.employee),as_dict=1)[0]
		row = [
			ss.employee,
			ss.employee_name,
			frappe.db.get_value('Employee',ss.employee,'basic'),
			frappe.db.get_value('Employee',ss.employee,'hra'),
			frappe.db.get_value('Employee',ss.employee,'_other_allowance'),
			frappe.db.get_value('Employee',ss.employee,'transportation'),
			sum_emp['total'] or "-",
			ss.total_working_days,
		]

		if ss.branch is not None:
			columns[3] = columns[3].replace("-1", "120")
		if ss.department is not None:
			columns[4] = columns[4].replace("-1", "120")
		if ss.designation is not None:
			columns[5] = columns[5].replace("-1", "120")
		if ss.leave_without_pay is not None:
			columns[9] = columns[9].replace("-1", "130")

		row +=[
				ss.absent_days or 0,
				# int(frappe.get_value('Salary Detail',{'salary_component':"Basic",'parent':ss.name},["amount"]) or 0),
				# int(frappe.get_value('Salary Detail',{'salary_component':"House Rental Allowance",'parent':ss.name},["amount"]) or 0),
				# int(frappe.get_value('Salary Detail',{'salary_component':"Other Allowance",'parent':ss.name},["amount"]) or 0),
				# int(frappe.get_value('Salary Detail',{'salary_component':"Transportation",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Additional Salary',{'salary_component':"NOT Hours",'employee':ss.employee,'docstatus':1},['not_hours']) or 0),
				int(frappe.get_value('Additional Salary',{'salary_component':"HOT Hours",'employee':ss.employee,'docstatus':1},['hot_hours']) or 0),
				# ss.not_hours or 0,
				# ss.hot_hours or 0,
				int(frappe.get_value('Salary Detail',{'salary_component':"NOT Hours",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"HOT Hours",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Previous Month Additionals",'parent':ss.name},["amount"]) or 0),
				int(frappe.get_value('Salary Detail',{'salary_component':"Others Additions",'parent':ss.name},["amount"]) or 0)]

		if currency == company_currency:
			row += [int(flt(ss.gross_pay)) * int(flt(ss.exchange_rate))]
		else:
			row += [int(ss.gross_pay)]
			
		row +=[ 
				frappe.get_value('Salary Detail',{'salary_component':"Loan Deduction",'parent':ss.name},["amount"]) or 0,
				frappe.get_value('Salary Detail',{'salary_component':"Other/ Advance Deduction",'parent':ss.name},["amount"]) or 0,
				frappe.get_value('Salary Detail',{'salary_component':"Mess Advance",'parent':ss.name},["amount"]) or 0,
				frappe.get_value('Salary Detail',{'salary_component':"Previous Month Abs Detection",'parent':ss.name},["amount"]) or 0
				]
		
		if currency == company_currency:
			row += [
				int(flt(ss.net_pay)) * int(flt(ss.exchange_rate)),
			]
		else:
			row += [
				int(ss.net_pay) or "-",
			]

		row +=[
			frappe.db.get_value('Additional Salary',{'employee':ss.employee,"salary_component":"Previous Month Abs Detection","payroll_date":ss.start_date},['Remarks']) or "-"
		]

		data.append(row)
	return columns, data

def get_columns(salary_slips):
	columns = [
		_("Employee") + "::100",
		_("Employee Name") + "::130",
		_("Fixed Basic(QR)") + "::150",
		_("Fixed HRA(QR)") + "::140",
		_("Fixed Other Allowance(QR)") + "::200",
		_("Fixed Transportation Allowance(QR)") + "::250",
		_("Fixed Total(QR)") + "::150",
		_("Working Days") + ":Data:140",
		
	]
	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql(
		"""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.amount != 0 and sd.parent in (%s)"""
		% (", ".join(["%s"] * len(salary_slips))),
		tuple([d.name for d in salary_slips]),
		as_dict=1,
	):
		salary_components[_(component.type)].append(component.salary_component)

	columns = (
		columns
		+ [_("Absent Days") + ":Data:140"]
		# + [_("Basic(QR)") + "::110"]
		# + [_("House Rental Allowance(QR)") + "::250"]
		# + [_("Transportation(QR)") + "::150"]
		# + [_("Other Allowance(QR)") + "::180"]
		+ [_("NOT Hours") + ":Float:120"]
		+ [_("HOT Hours") + ":Float:120"]
		+ [_("NOT Amount(QR)") + "::160"]
		+ [_("HOT Amount(QR)") + "::160"]
		+ [_("Previous Month Additionals(QR)") + "::160"]
		+ [_("Others Additions(QR)") + "::180"]
		+ [_("Gross Pay(QR)") + "::150"]
		+ [_("Loan Deduction(QR)") + "::150"]
		+ [_("Other/ Advance Deduction(QR)") + "::250"]
		+ [_("Mess Advance(QR)") + "::150"]
		+ [_("Previous Month Abs Detection") + "::260"]
		+ [
			_("Net Pay(QR)") + "::150",
		]
		+ [_("Remarks") + "::260"]
	)
	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_salary_slips(filters, company_currency):
	filters.update({"from_date": filters.get("from_date"), "to_date": filters.get("to_date")})
	conditions, filters = get_conditions(filters, company_currency)
	salary_slips = frappe.db.sql(
		"""select * from `tabSalary Slip` where %s order by employee"""% conditions,
		filters,
		as_dict=1,
	)
	return salary_slips or []


def get_conditions(filters, company_currency):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])
	if filters.get("from_date"):
		conditions += " and start_date >= %(from_date)s"
	if filters.get("to_date"):
		conditions += " and end_date <= %(to_date)s"
	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("grade"):
		conditions += " and grade = %(grade)s"
	if filters.get("currency") and filters.get("currency") != company_currency:
		conditions += " and currency = %(currency)s"
	return conditions, filters

def get_employee_doj_map():
	return frappe._dict(frappe.db.sql("""SELECT employee,date_of_joining FROM `tabEmployee` """))

def get_ss_earning_map(salary_slips, currency, company_currency):
	ss_earnings = frappe.db.sql(
		"""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)"""
		% (", ".join(["%s"] * len(salary_slips))),
		tuple([d.name for d in salary_slips]),
		as_dict=1,
	)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_earning_map[d.parent][d.salary_component] += flt(d.amount)
	return ss_earning_map


def get_ss_ded_map(salary_slips, currency, company_currency):
	ss_deductions = frappe.db.sql(
		"""select sd.parent, sd.salary_component, sd.amount, ss.exchange_rate, ss.name
		from `tabSalary Detail` sd, `tabSalary Slip` ss where sd.parent=ss.name and sd.parent in (%s)"""
		% (", ".join(["%s"] * len(salary_slips))),
		tuple([d.name for d in salary_slips]),
		as_dict=1,
	)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_ded_map[d.parent][d.salary_component] += flt(d.amount)
	return ss_ded_map
