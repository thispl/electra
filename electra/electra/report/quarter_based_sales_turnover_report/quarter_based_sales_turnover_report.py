from __future__ import unicode_literals
from six import string_types
import frappe
import json
from frappe.utils import (getdate, cint, add_months, date_diff, add_days,
	nowdate, get_datetime_str, cstr, get_datetime, now_datetime, format_datetime)
from frappe.utils import get_first_day, today, get_last_day, format_datetime, add_years, date_diff, add_days, getdate, cint, format_date,get_url_to_form
from frappe.utils import add_months, add_days, format_time, today, nowdate, getdate, format_date
from datetime import datetime, time, timedelta
import datetime
from calendar import monthrange
from frappe import _, msgprint
from frappe.utils import flt
from frappe.utils import cstr, cint
from erpnext.setup.utils import get_exchange_rate

def execute(filters=None):
	columns, data = [] ,[]
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	Quarter_1 = ["January", "February", "March"]
	Quarter_2 = ["April", "May", "June"]
	Quarter_3 = ["July", "August", "September"]
	Quarter_4 = ["October", "November", "December"]
	columns = []
	columns = [_("Company") + ":Link/Company:300"] 
	if filters.quarter == "Quarter 1":
		for s in Quarter_1:
			columns.append(s + "(Sales):Currency/:90")
			columns.append(s + " (Stock Transfer):Currency/:90")
			columns.append(s + " (Project):Currency/:90")
	
	if filters.quarter == "Quarter 2":
		for s in Quarter_2:
			columns.append(s + "(Sales):Currency/:90")
			columns.append(s + " (Stock Transfer):Currency/:90")
			columns.append(s + " (Project):Currency/:90")
	
	if filters.quarter == "Quarter 3":
		for s in Quarter_3:
			columns.append(s + "(Sales):Currency/:90")
			columns.append(s + " (Stock Transfer):Currency/:90")
			columns.append(s + " (Project):Currency/:90")
	
	if filters.quarter == "Quarter 4":
		for s in Quarter_4:
			columns.append(s + "(Sales):Currency/:90")
			columns.append(s + " (Stock Transfer):Currency/:90")
			columns.append(s + " (Project):Currency/:90")
	
	return columns

def get_data(filters):
	year = filters.year
	data = []
	row = []
	comp = frappe.db.sql(""" select name from `tabCompany`""",as_dict=True)
	for j in comp:
		row = [j.name]
		if filters.quarter == "Quarter 1":
			january = frappe.db.sql(""" SELECT SUM(grand_total) AS grand_total,
			SUM(CASE WHEN stock_transfer is null and order_type != 'Project' THEN grand_total ELSE 0 END) AS normal, 
			SUM(CASE WHEN stock_transfer = "Stock Transfer" THEN grand_total ELSE 0 END) AS stock, 
			SUM(CASE WHEN order_type = 'Project' THEN grand_total ELSE 0 END) AS project
			FROM `tabSales Invoice` WHERE posting_date between '%s' and '%s' and company = '%s' and docstatus = 1 """%((str(year)+"-01-01"),(str(year)+"-01-31"),j.name),as_dict=True)
			for jan in january:
				row += [jan.normal,jan.stock,jan.project]
	
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
	
		if filters.quarter == "Quarter 2":
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
		
		if filters.quarter == "Quarter 3":
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
	
		if filters.quarter == "Quarter 4":
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

			frappe.errprint(row)
		data.append(row)
	return data

			
	

	


	



				
			
			
			
			