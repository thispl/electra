# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Sales Invoice") + ":Link/Sales Invoice:200",
		_("Date") + ":Date/:110",
		_("Customer") + ":Link/Customer:200",
		_("Sales Person User") + ":Link/Sales Person :200",
		_("Invoice Amount") + ":Currency/:100",
		_("Tax Amount") + ":Currency/:100",
		_("Net Amount") + ":Currency/:100",
		_("Cost") + ":Currency/:100",
		_("Profit") + ":Currency/:100" ,
		_("Percentage") + ":Percent/:100"
	]
	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and posting_date between %(from_date)s and %(to_date)s"
	if filters.get("company"):
		conditions += " and company = %(company)s"
	if filters.get("sales_person_user"):
		conditions += " and sales_person_user= %(sales_person_user)s"
	return conditions, filters
	
def get_data(filters):
	data = []
	total_calc = 0
	total_add = 0
	base_grand_total = 0
	total = 0
	total_percentage = 0
	total_tax = 0
	count = 0
	conditions, filters = get_conditions(filters)
	sa = []
	sa = frappe.db.sql(""" select * from `tabSales Invoice` where docstatus = 1 %s and stock_transfer!='Stock Transfer' order by sales_person_user asc"""%conditions, filters,as_dict=True)
	# if filters.from_date:
	# 	sa = frappe.db.sql(""" select * from `tabSales Invoice` where posting_date between '%s' and '%s' order by sales_person_user asc"""%(filters.from_date,filters.to_date),as_dict=True)
	# else:
	# 	sa = frappe.db.sql(""" select * from `tabSales Invoice` order by sales_person_user asc""",as_dict=True)
	for i in sa:
		if i.sales_person_user:
			sb = frappe.get_doc('Sales Invoice', i.name)
			add = 0
			prof = 0
			tax = 0
			for c in sb.taxes:
				tax += c.tax_amount
			total_tax +=tax
			for j in sb.items:
				add += j.qty * j.valuation_rate
			total_add += add
			calc = i.base_grand_total - add
			total_calc += calc
			base_grand_total += i.base_grand_total
			total +=i.base_grand_total
			if i.base_grand_total > 0:
				prof = (calc / i.grand_total) * 100
			row = [i.name,i.posting_date,i.customer,i.sales_person_user,round(i.base_grand_total,2),round(tax,2),round(i.base_grand_total,2),round(add,2),round(calc,2),round(prof,2)]
			count +=1
			total_percentage +=prof
			data.append(row)
	if count !=0:
		# prc = total_percentage/count
		prc=(total_calc/base_grand_total)*100
	else:
		prc=0
	to = ["TOTAL","","","",round(total,2),round(tax,2),round(base_grand_total,2),round(total_add,2),round(total_calc,2),round(prc,2)]
	data.append(to)
	return data

