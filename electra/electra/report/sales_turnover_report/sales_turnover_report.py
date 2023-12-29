# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt
import erpnext
import datetime
import calendar

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
            month + "(Sales):Currency/:140",
            month + " (Stock Transfer):Currency/:140",
		month + " (Project):Currency/:140",
        ]
    columns.insert(0, _("Company") + ":Link/Company:300")
    return columns



def get_data(filters):
	year = filters.year
	data = []
	row = []
	comp = frappe.db.sql(""" select name from `tabCompany`""",as_dict=True)
	result = []

	for j in comp:
		january = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-01-01"),(str(year)+"-01-31"),j.name),as_dict=True)
		for jan in january:
			row = [j.name,jan.normal,jan.stock,jan.project]
		
		february = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-02-01"),(str(year)+"-02-28"),j.name),as_dict=True)
		for feb in february:
			row += [feb.normal,feb.stock,feb.project]

		
		march = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-03-01"),(str(year)+"-03-31"),j.name),as_dict=True)
		for mar in march:
			row += [mar.normal,mar.stock,mar.project]

		april = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-04-01"),(str(year)+"-04-30"),j.name),as_dict=True)
		for apr in april:
			row += [apr.normal,apr.stock,apr.project]
		
		may = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-05-01"),(str(year)+"-05-31"),j.name),as_dict=True)
		for ma in may:
			row += [ma.normal,ma.stock,ma.project]

		june = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-06-01"),(str(year)+"-06-30"),j.name),as_dict=True)
		for jun in june:
			row += [jun.normal,jun.stock,jun.project]

		july = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-07-01"),(str(year)+"-07-31"),j.name),as_dict=True)
		for jul in july:
			row += [jul.normal,jul.stock,jul.project]

		august = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-08-01"),(str(year)+"-08-31"),j.name),as_dict=True)
		for aug in august:
			row += [aug.normal,aug.stock,aug.project]

		september = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-09-01"),(str(year)+"-09-30"),j.name),as_dict=True)
		for sep in september:
			row += [sep.normal,sep.stock,sep.project]


		october = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-10-01"),(str(year)+"-10-31"),j.name),as_dict=True)
		for oct in october:
			row += [oct.normal,oct.stock,oct.project]

		november = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-11-01"),(str(year)+"-11-30"),j.name),as_dict=True)
		for nov in november:
			row += [nov.normal,nov.stock,nov.project]


		december = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-12-01"),(str(year)+"-12-31"),j.name),as_dict=True)
		for dec in december:
			row += [dec.normal,dec.stock,dec.project]
		
		overall = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
		SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
		SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
		SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
		FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-01-01"),(str(year)+"-12-31"),j.name),as_dict=True)
		for ove in overall:
			row += [ove.normal,ove.stock,ove.project]


			data.append(row)
		
	return data

	