from __future__ import unicode_literals
import frappe,erpnext
from frappe.utils import cint
from frappe.utils import flt, fmt_money
import json
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today, time_diff_in_hours

from frappe.model.mapper import get_mapped_doc
from frappe.utils.file_manager import get_file
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
import datetime
from datetime import date,datetime,timedelta
from electra.utils import get_dn_return_series
import openpyxl
from collections import defaultdict
from openpyxl import Workbook
import openpyxl
import xlrd
import re
from frappe.utils import date_diff,today,cstr
from datetime import datetime
from dateutil import relativedelta
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import GradientFill, PatternFill
import pandas as pd
from frappe.utils import formatdate
from frappe.utils import now
from erpnext.setup.utils import get_exchange_rate
from frappe import throw,_, db, get_doc, throw, whitelist


from frappe.utils import (
	add_days,
	cint,
	cstr,
	date_diff,
	flt,
	formatdate,
	get_first_day,
	get_link_to_form,
	getdate,
	money_in_words,
	rounded,
)

@frappe.whitelist()
def create_hooks_ems():
	job = frappe.db.exists('Scheduled Job Type', 'daily_emp_salary')
	if not job:
		emc = frappe.new_doc("Scheduled Job Type")
		emc.update({
			"method": 'electra.custom.update_employee_salary',
			"frequency": 'Cron',
			"cron_format": '00 01 * * *'
		})
		emc.save(ignore_permissions=True)


@frappe.whitelist()
def get_leave_details(name,from_date,to_date,leave,lea_ty):
	doc = frappe.get_doc('Leave Application',name)
	leave_type = doc.leave_type
	frappe.errprint(leave_type)
	frappe.errprint(doc.leave_type)
	frappe.errprint(lea_ty)
	leave_days = frappe.db.get_value('Leave Type',{'name':doc.leave_type},'max_leaves_allowed')
	ticket=  frappe.db.get_value('Leave Type',{'name':doc.leave_type},'leave_ticket')
	if ticket == True:
		ticket="Yes"
	else:
		ticket="No"

	salary= frappe.db.get_value('Leave Type',{'name':doc.leave_type},'leave_salary')
	if salary == True:
		salary="Yes"
	else:
		salary="No"

	leaving_date = from_date
	rdoj = add_days(to_date ,1)
	leave_taken = leave
	leave_status =  flt(leave_days)-flt(leave_taken)
	data = """<tr>
		<td>Leave Type</td>
		<td>Leave Days</td>
		<td>Leave Ticket</td>
		<td>Leave Salary</td>
		<td>Leaving Date</td>
		<td>Re-Joining Date</td>
		<td>Leave Taken</td>
		<td>Leave Status</td></tr>
		<tr>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		<td>%s</td>
		</tr>"""%(leave_type,leave_days,ticket,salary,leaving_date,rdoj,leave_taken,leave_status)
	return data

@frappe.whitelist()
def get_role(employee):
	user_id = frappe.get_value('Employee',{'employee':employee},['user_id'])
	hod = frappe.get_value('User',{'email':user_id},['name'])
	role = "HOD"
	hod = frappe.get_value('Has Role',{'role':role,'parent':hod})
	if hod:
		return  "HI"
	else:
		return "HII"

@frappe.whitelist()
def get_md_role(employee):
	user_id = frappe.get_value('Employee',{'employee':employee},['user_id'])
	md = frappe.get_value('User',{'email':user_id},['name'])
	role = "Need MD Approval"
	md = frappe.get_value('Has Role',{'role':role,'parent':md})
	if md:
		return  "HI"
	else:
		return "HII"

def visa_creation(doc,method):
	if doc.visa_application_num:
		# v = frappe.db.exists('Visa Approval Monitor',{'visa_application_no':doc.visa_application_number})
		# if v:
		#      c = frappe.get_value('Visa Approval Monitor',v,'balance')
		#      if c:
		vam = frappe.get_doc('Visa Approval Monitor',doc.visa_application_num)
		used_visa = cint(vam.used_visa)
		balance = cint(vam.balance)
		used_visa += 1
		if vam.balance:
			balance -= 1
		vam.used_visa = used_visa
		vam.balance = balance
		vam.save(ignore_permissions=True)
		frappe.db.commit()

# def rejoin_form_creation(doc,method):
# 	rj=frappe.new_doc("Re Joining From Leave")
# 	rj.emp_no = doc.employee
# 	# rj.employee_name = doc.employee_name
# 	# rj.designation = doc.designation1
# 	# rj.department = doc.department
# 	# rj.date_of_joining = doc.date_of_joining0
# 	# rj.resident_id_number = doc.resident_id_number
# 	rj.start = doc.from_date
# 	rj.end = doc.to_date
# 	rj.total_leave_in_days = doc.total_leave_days
# 	rj.nature_of_leave = doc.leave_type
# 	rj.save(ignore_permissions = True)
# 	frappe.db.commit()

@frappe.whitelist()
def get_stock_balance_from_wh(item_code,warehouse):
	actual_qty = 0
	try:
		actual_qty = frappe.db.sql("""select actual_qty from tabBin
			where item_code = '%s' and warehouse = '%s' """%(item_code,warehouse),as_dict=True)
	except:
		pass
	return actual_qty

@frappe.whitelist()
def get_stock_balance(item_table):
	item_table = json.loads(item_table)
	data = []
	for item in item_table:
		try:
			item_name = frappe.get_value('Item',{'name':item['item_code']},"item_name")
			stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
				where item_code = '%s' """%(item["item_code"]),as_dict=True)
			for stock in stocks:
				data.append([item['item_code'],item_name,stock.warehouse,stock.actual_qty,stock.stock_uom,stock.stock_value])
		except:
			pass
	return data

@frappe.whitelist()
def get_previous_po(item_table):
	item_table = json.loads(item_table)
	data = []
	for item in item_table:
		if not item["item_code"] == "001":
			try:
				item_name = frappe.get_value('Item',{'name':item['item_code']},"item_name")
				pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.amount as amount,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
				left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
				where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """%(item["item_code"]),as_dict=True)

				for po in pos:
					data.append([item['item_code'],item_name,po.supplier,po.qty,po.date,po.amount,po.po])
			except:
				pass
	return data



@frappe.whitelist()
def set_previous_po(item_table):
	item_table = json.loads(item_table)
	data = []
	for item in item_table:
		try:
			item_name = frappe.get_value('Item',{'name':item['item_code']},"item_name")
			pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
			left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
			where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """%(item["item_code"]),as_dict=True)
			for po in pos:
				data.append([item['item_code'],item_name,po.qty])
		except:
			pass
	return data
@frappe.whitelist()
def previous_po_html(item_code):
	data = ""
	item_name = frappe.get_value('Item',{'item_code':item_code},"item_name")
	frappe.errprint(item_name)
	pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order Item`.amount as amount,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
	left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
	where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by date"""%(item_code),as_dict=True)


	data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:orange" colspan=6><center>Previous Purchase Order</center></th></tr>'
	data += '''
	<tr><td colspan =2 style="padding:1px;border: 1px solid black;width:300px" ><b>Item Code</b></td>
	<td style="padding:1px;border: 1px solid black;width:200px" colspan =4>%s</td></tr>
	<tr><td colspan =2 style="padding:1px;border: 1px solid black" ><b>Item Name</b></td>
	<td style="padding:1px;border: 1px solid black" colspan =4>%s</td></tr>

	<tr><td style="padding:1px;border: 1px solid black" colspan =1><b>Supplier Name</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>Previous Purchase Order</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>PO Date</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>PO Rate</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>PO Quantity</b></td>
	<td style="padding:1px;border: 1px solid black" colspan=1><b>PO Amount</b>
	</td></tr>'''%(item_code,item_name)
	for po in pos:
		data += '''<tr>
			<td style="padding:1px;border: 1px solid black" colspan =1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(po.supplier,po.po,po.date,po.rate,po.qty,po.amount)

	data += '</table>'
	return data

# @frappe.whitelist()
# def get_sales_invoice(item_table):
#     item_table = json.loads(item_table)
#     data = []
#     for item in item_table:
#         try:
#             item_name = frappe.get_value('Item',{'name':item['item_code']},"item_name")
#             pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.amount as amount,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
#             left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
#             where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """%(item["item_code"]),as_dict=True)
#             for po in pos:
#                 data.append([item['item_code'],item_name,po.supplier,po.qty,po.date,po.amount,po.po])
#         except:
#             pass
#     return data

@frappe.whitelist()
def get_out_qty(item_table):
	item_table = json.loads(item_table)
	data = []
	for item in item_table:
		try:
			sles = frappe.db.sql("""select * from `tabStock Ledger Entry`
			left join `tabStock Entry` on `tabStock Ledger Entry`.voucher_no = `tabStock Entry`.name where `tabStock Ledger Entry`.posting_date between '%s' and '%s' and `tabStock Ledger Entry`.item_code = '%s' and `tabStock Ledger Entry`.actual_qty < 0 and `tabStock Ledger Entry`.voucher_type = 'Stock Entry' and `tabStock Entry`.stock_entry_type = 'Material Issue' """%(add_months(today(),-6),today(),item['item_code']),as_dict=True)
			for sl in sles:
				data.append([item['item_code'],sl.warehouse,abs(sl.actual_qty),sl.posting_date,sl.voucher_type])
		except:
			pass
	return data

@frappe.whitelist()
def get_under_so(item_table):
	item_table = json.loads(item_table)
	data = []
	for item in item_table:
		try:
			item_name = frappe.get_value('Item',{'name':item['item_code']},"item_name")
			sos = frappe.db.sql("""select `tabSales Order Item`.item_code as item_code,`tabSales Order Item`.item_name as item_name, `tabSales Order Item`.qty as qty,`tabSales Order`.transaction_date as date from `tabSales Order`
			left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
			where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus != 2 """%(item["item_code"]),as_dict=True)
			for so in sos:
				data.append([item['item_code'],item_name,so.qty,so.date])
		except:
			pass
	return data

# @frappe.whitelist()
# def get_out_qty(item_table):
#     item_table = json.loads(item_table)
#     data = []
#     for item in item_table:
#         sles = frappe.db.sql("""select * from `tabStock Ledger Entry`
#         left join `tabStock Entry` on `tabStock Ledger Entry`.voucher_no = `tabStock Entry`.name where `tabStock Ledger Entry`.posting_date between '%s' and '%s' and `tabStock Ledger Entry`.item_code = '%s' and `tabStock Ledger Entry`.actual_qty < 0 and `tabStock Ledger Entry`.voucher_type = 'Stock Entry' and `tabStock Entry`.stock_entry_type = 'Material Issue' """%(add_months(today(),-6),today(),item['item_code']),as_dict=True)
#         for sl in sles:
#             data.append([item['item_code'],sl.warehouse,abs(sl.actual_qty),sl.posting_date,sl.voucher_type])
#     return data

@frappe.whitelist()
def create_lcv_je(doc,method):
	from electra.utils import get_series
	tnc = doc.taxes
	for tn in tnc:
		if tn.supplier:
			jv = frappe.new_doc("Journal Entry")
			jv.naming_series = get_series(doc.company,"Journal Entry")
			jv.voucher_type = "Journal Entry"
			jv.company = doc.company
			jv.posting_date = nowdate()
			jv.bill_no = tn.bill_no
			jv.bill_date = nowdate()
			jv.append("accounts", {
				"account": tn.expense_account,
				"debit": tn.base_amount,
				"cost_center": erpnext.get_default_cost_center(doc.company),
				"debit_in_account_currency": tn.amount
			})

			jv.append("accounts", {
				"account": frappe.get_cached_value('Company', doc.company, 'default_payable_account'),
				"party_type": "Supplier",
				"party":tn.supplier,
				"cost_center": erpnext.get_default_cost_center(doc.company),
				"credit": tn.base_amount,
				"credit_in_account_currency": tn.amount
			})
			jv.landed_cost_voucher = doc.name
			jv.insert()
			jv.submit()

@frappe.whitelist()
def cancel_lcv_je(doc,method):
	jes = frappe.get_all("Journal Entry",{'landed_cost_voucher':doc.name})
	for je in jes:
		jv = frappe.get_doc("Journal Entry",je.name)
		if jv.docstatus == 1:
			jv.cancel()
			frappe.db.commit()

@frappe.whitelist()
def make_cost_estimation(source_name, target_doc=None):
	doc = frappe.get_doc("Opportunity",source_name)
	if doc.party_name and doc.opportunity_from == 'Customer':
		customer_name = frappe.db.get_value("Customer", doc.party_name, "customer_name")
	elif doc.party_name and doc.opportunity_from == 'Lead':
		lead_name = frappe.db.get_value("Lead", doc.party_name, "lead_name")
		customer_name = lead_name
	doclist = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Cost Estimation",
			"field_map": {
				"name": "opportunity",
				"opportunity_from":"cost_estimation_for",
				"customer_name" : "lead_customer_name",
				"party_name":"lead_customer",
				"title_of_project":"project_name"
			}
		},
		"Opportunity Item": {
			"doctype": "CE MATERIALS",
			"field_map": {
				"item_code": "item",
				"uom": "unit",
				"qty": "qty"
			}
		},
		"Opportunity Scope of Work": {
			"doctype": "CE Master Scope of Work",
			"field_map": {
				"msow": "msow",
				"msow_desc": "msow_desc"
			}
		}
	}, target_doc)
	return doclist

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	doc = frappe.get_doc("Cost Estimation",source_name)
	doclist = get_mapped_doc("Cost Estimation", source_name, {
		"Cost Estimation": {
			"doctype": "Quotation",
			"field_map": {
				"cost_estimation_for": "quotation_to",
				"name": "cost_estimation",
				"project_name":"title_of_project",
				"lead_customer": "party_name",
				"prepared_by":"user_id"
			}
		},
		# "CE MATERIALS": {
		#     "doctype": "Quotation Item",
		#     "field_map": {
		#         "item": "item_code",
		#         "unit": "uom",
		#         "qty": "qty"
		#     }
		# },
		"Cost Estimation Scope Of Work": {
			"doctype": "Quotation Scope of Work",
			"field_map": {
				"msow": "msow",
				"ssow": "ssow",
				"msow_desc": "msow_desc",
				"ssow_desc" : "ssow_desc",
				"qty": "qty",
				"unit":"unit",
				"unit_price":"unit_price"
			}
		}
	}, target_doc)
	return doclist

@frappe.whitelist()
def make_project_so(source_name, target_doc=None):
	doc = frappe.get_doc("Project Budget",source_name)
	order_type = "Project"
	doclist = get_mapped_doc("Project Budget", source_name, {
		"Project Budget": {
			"doctype": "Sales Order",
			"field_map": {
				"name": "project_budget",
				"customer":"customer",
				"order_type":"Project",
				"user_id":"prepared_by"
			}
		},
		# "Quotation Scope of Work": {
		#     "doctype": "SO Scope of Work",
		#     "field_map": {
		#         "msow": "msow",
		#         "ssow": "ssow",
		#         "msow_desc": "msow_desc",
		#         "ssow_desc" : "ssow_desc"
		#     }
		# }
	}, target_doc)
	return doclist

@frappe.whitelist()
def make_so(source_name, target_doc=None):
	doc = frappe.get_doc("Quotation",source_name)
	doclist = get_mapped_doc("Quotation", source_name, {
		"Quotation": {
			"doctype": "Sales Order",
			"field_map": {
				"name": "quotation",
				"customer":"customer",
				"user_id":"prepared_by"
			}
		},
		"Quotation Scope of Work": {
			"doctype": "SO Scope of Work",
			"field_map": {
				"msow": "msow",
				"ssow": "ssow",
				"msow_desc": "msow_desc",
				"ssow_desc" : "ssow_desc"
			}
		}
		# "CE MATERIALS": {
		#     "doctype": "Quotation Item",
		#     "field_map": {
		#         "item": "item_code",
		#         "unit": "uom",
		#         "qty": "qty"
		#     }
		# }
	}, target_doc)
	return doclist

@frappe.whitelist()
def make_project_budget(source_name, target_doc=None):
	doc = frappe.get_doc("Sales Order",source_name)
	cost_estimation = doc.cost_estimation
	doclist = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Project Budget",
			"field_map": {
				"title_of_project": "title_of_project",
				"name": "sales_order",
			}
		}
	}, target_doc)
	return doclist

@frappe.whitelist()
def make_project(source_name, target_doc=None):
	doc = frappe.get_doc("Budgeting",source_name)
	doclist = get_mapped_doc("Budgeting", source_name, {
		"Budgeting": {
			"doctype": "Project",
			"field_map": {
				"title_of_project": "project_name",
				"sales_order": "sales_order",
				"name" : "budgeting"
							}
		}
	}, target_doc)
	return doclist

# @frappe.whitelist()
# def stock_popup(item_code):
#     item = frappe.get_value('Item',{'item_code':item_code},'item_code')
#     # item_price= frappe.get_value('Item Price',{item:'item_code'},'price_list_rate')
#     data = ''
#     stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
#         where item_code = '%s' """%(item),as_dict=True)
#     # frappe.errprint(stocks)
#     # pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.amount as amount,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.company as company,`tabPurchase Order`.name as po from `tabPurchase Order`
#     # left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
#     # where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 1   order by amount desc limit 1"""%(item),as_dict=True)



#     pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
#     left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
#     where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by rate asc limit 1""" % (item), as_dict=True)
#     frappe.errprint(stocks)
#     data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:orange" colspan=4><center>Stock Availability</center></th></tr>'
#     data += '''
#     <tr><td style="padding:1px;border: 1px solid black;width:300px" ><b>Item Code</b></td>
#     <td style="padding:1px;border: 1px solid black;width:200px" colspan =3>%s</td></tr>
#     <tr><td style="padding:1px;border: 1px solid black" ><b>Item Name</b></td>
#     <td style="padding:1px;border: 1px solid black" colspan =3>%s</td></tr>
#     <tr>
#     <td style="padding:1px;border: 1px solid black;"  ><b>Warehouse</b></td>
#     <td style="padding:1px;border: 1px solid black;max-width:50px"  ><b>QTY</b></td>
#     <td style="padding:1px;border: 1px solid black;max-width:50px;" colspan ='1' ><b>Previous Purchase Order</b></td>
#     <td style="padding:1px;border: 1px solid black;max-width:50px;" colspan ='1' ><b>PPQ</b></td></tr>'''%(item,frappe.db.get_value('Item',item,'item_name'))


#     i = 0
#     if pos:
#         for po in pos:
#             for stock in stocks:
#                 if stock.actual_qty > 0:
#                     data += '''<tr>
#                     <td style="padding:1px;border: 1px solid black" colspan =1>%s</td><td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
#                     <td style="padding:1px;border: 1px solid black" colspan=1>-</td><td style="padding:1px;border: 1px solid black" colspan=1>-</td></tr>'''%(stock.warehouse,stock.actual_qty)
#     else:
#         for stock in stocks:
#             if stock.actual_qty > 0:
#                 data += '''<tr>
#                 <td style="padding:1px;border: 1px solid black" colspan =1>%s</td><td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
#                 <td style="padding:1px;border: 1px solid black" colspan=1>-</td><td style="padding:1px;border: 1px solid black" colspan=1>-</td></tr>'''%(stock.warehouse,stock.actual_qty)
#     i += 1

#     data += '</table>'

#     return data



@frappe.whitelist()
def stock_popup(item_code,company):
	w_house = frappe.db.get_value("Warehouse",{'company':company,'default_for_stock_transfer':1},['name'])
	item = frappe.get_value('Item',{'item_code':item_code},'item_code')
	data = ''
	stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
		where item_code = '%s' order by warehouse """%(item),as_dict=True)
	pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
	left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
	where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """ % (item_code), as_dict=True)
	data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:orange" colspan=5><center>Stock Availability</center></th></tr>'
	data += '''
	<tr><td style="padding:1px;border: 1px solid black;width:300px" ><b>Item Code</b></td>
	<td style="padding:1px;border: 1px solid black;width:200px" colspan =4>%s</td></tr>
	<tr><td style="padding:1px;border: 1px solid black" ><b>Item Name</b></td>
	<td style="padding:1px;border: 1px solid black" colspan =4>%s</td></tr>'''%(item,frappe.db.get_value('Item',item,'item_name'))
	data += '''
	<td style="padding:1px;border: 1px solid black;background-color:orange;color:white;"  ><b>Company</b></td>
	<td style="padding:1px;border: 1px solid black;background-color:orange;color:white;"  ><b>Warehouse</b></td>
	<td style="padding:1px;border: 1px solid black;background-color:orange;color:white;width:13%"  ><b>Stock Qty</b></td>
	<td style="padding:1px;border: 1px solid black;background-color:orange;color:white;width:13%;" colspan ='1' ><b>PENDING TO RECEIVE</b></td>
	<td style="padding:1px;border: 1px solid black;background-color:orange;color:white;width:13%;" colspan ='1' ><b>PENDING TO SELL</b></td></tr>'''
	for stock in stocks:
		if stock.warehouse == w_house:
			comp = frappe.get_value("Warehouse",stock.warehouse,['company'])

			new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order`
			left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
			where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 and `tabPurchase Order`.company = '%s' """ % (item_code,comp), as_dict=True)[0]
			if not new_po['qty']:
				new_po['qty'] = 0
			if not new_po['d_qty']:
				new_po['d_qty'] = 0
			ppoc_total = new_po['qty'] - new_po['d_qty']	

		
			new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
			left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
			where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1 and `tabSales Order`.company = '%s' """ % (item_code,comp), as_dict=True)[0]
			if not new_so['qty']:
				new_so['qty'] = 0
			if not new_so['d_qty']:
				new_so['d_qty'] = 0
			del_total = new_so['qty'] - new_so['d_qty']
			data +=''' <tr><td style="padding:1px;border: 1px solid black;background-color:#ffe9ad;color:black;font-weight:bold" colspan =1>%s</td><td style="padding:1px;border: 1px solid black;background-color:#ffe9ad;color:black;font-weight:bold" colspan=1>%s</td><td style="padding:1px;border: 1px solid black;background-color:#ffe9ad;color:black;font-weight:bold" colspan=1>%s</td>
				<td style="padding:1px;border: 1px solid black;background-color:#ffe9ad;color:black;font-weight:bold" colspan=1>%s</td><td style="padding:1px;border: 1px solid black;background-color:#ffe9ad;color:black;font-weight:bold" colspan=1>%s</td></tr>'''%(comp,stock.warehouse,stock.actual_qty,ppoc_total,del_total)


	
	i = 0
	for stock in stocks:
		if stock.warehouse != w_house:
			# if stock.actual_qty > 0:
			comp = frappe.get_value("Warehouse",stock.warehouse,['company'])
			new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order`
			left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
			where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 and `tabPurchase Order`.company = '%s' """ % (item_code,comp), as_dict=True)[0]
			if not new_po['qty']:
				new_po['qty'] = 0
			if not new_po['d_qty']:
				new_po['d_qty'] = 0
			ppoc_total = new_po['qty'] - new_po['d_qty']
		
			
			new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
			left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
			where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1 and `tabSales Order`.company = '%s' """ % (item_code,comp), as_dict=True)[0]
			if not new_so['qty']:
				new_so['qty'] = 0
			if not new_so['d_qty']:
				new_so['d_qty'] = 0
			del_total = new_so['qty'] - new_so['d_qty']

			data += '''<tr>
			<td style="padding:1px;border: 1px solid black" colspan =1>%s</td><td style="padding:1px;border: 1px solid black" colspan=1>%s</td><td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
			<td style="padding:1px;border: 1px solid black" colspan=1>%s</td><td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(comp,stock.warehouse,stock.actual_qty,ppoc_total,del_total)
			
	
	i += 1
	p_po_total = 0
	p_so_total = 0
	stock_qty = 0 
	for stock in stocks:

		comp = frappe.get_value("Warehouse",stock.warehouse,['company'])
		new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 and `tabPurchase Order`.company = '%s' """ % (item_code,comp), as_dict=True)[0]
		if not new_po['qty']:
			new_po['qty'] = 0
		if not new_po['d_qty']:
			new_po['d_qty'] = 0
		ppoc_total = new_po['qty'] - new_po['d_qty']
	
		
		new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
		left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
		where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1 and `tabSales Order`.company = '%s' """ % (item_code,comp), as_dict=True)[0]
		if not new_so['qty']:
			new_so['qty'] = 0
		if not new_so['d_qty']:
			new_so['d_qty'] = 0
		del_total = new_so['qty'] - new_so['d_qty']


		p_po_total += ppoc_total
		p_so_total += del_total
		stock_qty += stock.actual_qty
	data += '''<tr>
	<td style="background-color:#ffe9ad;padding:1px;border: 1px solid black;text-align:right;font-weight:bold" colspan =2>%s</td><td style="background-color:#ffe9ad;padding:1px;border: 1px solid black;font-weight:bold" colspan=1>%s</td>
	<td style="background-color:#ffe9ad;padding:1px;border: 1px solid black;font-weight:bold" colspan=1>%s</td><td style="background-color:#ffe9ad;padding:1px;border: 1px solid black;font-weight:bold" colspan=1>%s</td></tr>'''%("Total     ",stock_qty,p_po_total,p_so_total)
			
	data += '</table>'

	return data




# @frappe.whitelist()
# def get_stock_price():
#     data =''
#     price = frappe.db.sql("""select `tabQuotation Item`.item_code as item_code,`tabQuotation Item`.item_name as item_name,`tabItem Price`.item_code as item_code,`tabItem Price`.price_list_rate as price_list_rate
#     left join `tabQuotation Item` on `tabItem Price`.name =`tabQuotation Item`.parent
#     where `tabItem Price`.item_code = '%s' and `tabItem Price`
#     """)

@frappe.whitelist()
def po_popup(item_code):
	item = frappe.get_value('Item',{'item_name':item_code},'item_code')

	data = ''
	pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.amount as amount,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
	left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
	where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """%(item),as_dict=True)
	data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black" colspan=6><center>Previous Purchase Order</center></th></tr>'
	data += '<tr><td style="padding:1px;border: 1px solid black"><b>Item Code</b></td><td style="padding:1px;border: 1px solid black"><b>Item Name</b></td><td style="padding:1px;border: 1px solid black"><b>Supplier</b></td><td style="padding:1px;border: 1px solid black"><b>QTY</b></td><td style="padding:1px;border: 1px solid black"><b>PO Date</b></td><td style="padding:1px;border: 1px solid black"><b>Amount</b></td></tr>'
	for po in pos:
		data += '<tr><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td></tr>'%(po.item_code,po.item_name,po.supplier,po.qty,po.date,po.amount)
	data += '</table>'
	if pos:
		return data



@frappe.whitelist()
def out_qty_popup(item):
	data = ''
	sles = frappe.db.sql("""select * from `tabStock Ledger Entry`
	left join `tabStock Entry` on `tabStock Ledger Entry`.voucher_no = `tabStock Entry`.name where `tabStock Ledger Entry`.posting_date between '%s' and '%s' and `tabStock Ledger Entry`.item_code = '%s' and `tabStock Ledger Entry`.actual_qty < 0 and `tabStock Ledger Entry`.voucher_type = 'Stock Entry' and `tabStock Entry`.stock_entry_type = 'Material Issue' """%(add_months(today(),-6),today(),item),as_dict=True)
	data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black" colspan=6><center>6 Months Stock Out Qty</center></th></tr>'
	data += '<tr><td style="padding:1px;border: 1px solid black"><b>Item Code</b></td><td style="padding:1px;border: 1px solid black"><b>Warehouse</b></td><td style="padding:1px;border: 1px solid black"><b>QTY</b></td><td style="padding:1px;border: 1px solid black"><b>Date</b></td><td style="padding:1px;border: 1px solid black"><b>Out Type</b></td></tr>'
	for sl in sles:
		data += '<tr><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td></tr>'%(sl.item_code,sl.warehouse,abs(sl.actual_qty),sl.posting_date,sl.voucher_type)
	data += '</table>'
	if sles:
		return data

@frappe.whitelist()
def create_tasks(doc,method):
	if doc.sales_order:
		so = frappe.get_doc("Sales Order",doc.sales_order)
		frappe.errprint(so.installation)
		for so_installation in so.installation:
			task = frappe.new_doc("Task")
			task.update({
				"project": doc.name,
				"msow":so_installation.msow,
				"item_code":so_installation.item,
				"subject": so_installation.item_name,
				"description":so_installation.description,
				"uom":so_installation.unit,
				"qty": so_installation.qty,
				"pending_qty": so_installation.qty,
				"cost":so_installation.cost,
				"cost_amount":so_installation.cost_amount,
				"budgeted_cost":so_installation.unit_price,
				"budgeted_amount":so_installation.amount,
				"selling_price":so_installation.rate_with_overheads,
				"selling_amount":so_installation.amount_with_overheads,
				"is_group": 0
			})
			task.save(ignore_permissions=True)

	# for item in so.items:
	#     if item.work_title:
	#         parent_item = frappe.get_value("Task",{'subject':item.work_title},'name')
	#         task_name = item.item_name
	#         task = frappe.new_doc("Task")
	#         task.update({
	#             "subject": task_name,
	#             "project": doc.name,
	#             "parent_task": parent_item
	#         })
	#         task.save(ignore_permissions=True)

# @frappe.whitelist()
# def employee_conversion():
# 	employee=frappe.get_all('Employee',{'employment_type':'Probation'},['date_of_joining','grade','employee_name','employee_number'])
# 	day = datetime.strptime(str(today()),"%Y-%m-%d").date()
# 	for emp in employee:
# 		date = emp.date_of_joining
# 		worker = emp.grade
# 		staff = emp.grade
# 		if worker:
# 			six = add_months(date,5)
# 			if six== day:
# 				frappe.sendmail(
# 					recipients = ["jagadeesan@groupteampro.com"],
# 					subject = 'probation period of employee ',
# 					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,6))
# 				)

# 			fifteen_days = add_days(six,15)
# 			if fifteen_days== day:
# 				frappe.sendmail(
# 					recipients = ["jagadeesan.a@groupteampro.com"],
# 					subject = 'probation period ends ',
# 					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,6))
# 				)

# 			seven_days = add_days(fifteen_days,8)
# 			if seven_days== day:
# 				frappe.sendmail(
# 					recipients = ["jagadeesan.a@groupteampro.com"],
# 					subject = 'probation period ends ',
# 					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,6))
# 				)
# 		if staff:
# 			three = add_months(date,2)
# 			if three == day:
# 				print(day)
# 				frappe.sendmail(
# 					recipients = ["jagadeesan.a@groupteampro.com"],
# 					subject = 'probation period ends ',
# 					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,3))
# 				)

# 			fifteen_days_ = add_days(three,15)
# 			if fifteen_days_== day:
# 				frappe.sendmail(
# 					recipients = ["jagadeesan.a@groupteampro.com"],
# 					sender = sender['email'],
# 					subject = 'probation period of employee ',
# 					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,3))
# 				)

# 			seven_days_ = add_days(fifteen_days_,8)
# 			if seven_days_== day:
# 				frappe.sendmail(
# 					recipients = ["jagadeesan.a@groupteampro.com"],
# 					sender = sender['email'],
# 					subject = 'probation period  ',
# 					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,3))
# 				)


# @frappe.whitelist()
# def check_discount_percent(user,discount):
#     user_roles = frappe.get_roles(user)
#     max_discount = 0
#     for role in user_roles:
#         d = frappe.db.get_value("Quotation Discount",{'role':role,'parent':'Sales Settings'},['role','max_dis'])
#         if d:
#             if max_discount < d[1]:
#                 max_discount = d[1]
#     if max_discount == 0:
#         return 'invalid'
#     elif float(discount) > max_discount:
#         return max_discount


@frappe.whitelist()
def get_query(doctype, txt, searchfield, start, page_len,filters):
	return frappe.db.sql(""" select follow_up_for from `tabSales Follow UP` where follow_up_for = '%s' and account_manager = '%s' """ %(filters.quotation_to,filters.user), as_dict=1)

# @frappe.whitelist()
# def alert_to_substitute(doc,method):
# 	frappe.sendmail(
# 		recipients='janisha.g@groupteampro.com',
# 		subject=('ASSIGNED AS SUBSTITUTE'),
# 		header=(''),
# 		message="""
# 			Dear %s,<br>
# 			%s %s %s is going for vacation %s to %s so you assigned as substitute<br>
# 			and getting into trainee to probation.<br>
# 			"""%(doc.sub_employee_id,doc.employee_name,doc.employee,doc.department,doc.from_date,doc.to_date)
# 	)

@frappe.whitelist()
def isthimara_exp_mail(doc,method):
	vehicle_main = frappe.get_value('Vehicle Maintenance Check List',{'register_no':doc.register_no},['expiry_date'])
	Previous_Date = vehicle_main - timedelta(days=30)
	if Previous_Date:
		frappe.sendmail(
		recipients='chitra@electraqatar.com',
		subject=('Isthimara Expiry'),
		cc = 'rejin@electraqtar.com',
		message="""
			Dear Sir/Madam,<br>
			Vehicle No %s is going for Expire.Kindly Renew before Due date
			"""%(doc.register_no)

		)
		frappe.errprint (Previous_Date)

@frappe.whitelist()
def grade(name,grade):
	doc = frappe.get_doc('Employee Grade',name)
	ticket = doc.air_ticket_allowance_
	print(ticket)

@frappe.whitelist()
def create_contact(name,email,designation,customer_name,mobile_no):
	contact = frappe.new_doc("Contact")
	contact.first_name = name
	contact.designation = designation
	contact.mobile_no = mobile_no
	contact.contact_person_email_id_ = email
	contact.append('email_ids',{
		'email_id':email,
		'is_primary':True,
	})
	# contact.append('phone_nos',{
	# 'phone': contact_no,
	# 'is_primary_phone':True,
	# 'is_primary_mobile_no':True,
	# })
	contact.append('links',{
		'link_doctype':"Customer",
		'link_name':customer_name,
	})
	contact.save(ignore_permissions=True)
	# contact = frappe.get_doc("Contact",{"first_name":name)
	# contact.contact_person_name = name
	# contact.email_id = email
	# contact.contact_number = contact_no


# @frappe.whitelist()
# def get_due_date(doc,method):
#     due = doc.payment_schedule
#     due_date = []
#     for dd in due:
#         due.append(dd.due_date)
#     sales_invoice = frappe.get_doc("Sales Invoice",doc.name)
#     sales_invoice.due_date = due_date
#     frappe.errprint(due_date)
#     sales_invoice.save(ignore_permissions=True)
#     frappe.db.commit()

@frappe.whitelist()
def additional_salary(import_file):
	filepath = get_file(import_file)
	pps = read_csv_content(filepath[1])
	for pp in pps:
		if frappe.db.exists('Salary Structure Assignment',{'employee':pp[0]}):
			if pp[0] != "Employee":
				doj = frappe.db.get_value('Employee',{'employee':pp[0]},['date_of_joining'])
				if doj:
					if pd.to_datetime(pp[3]).date() > doj:
						company = frappe.db.get_value("Employee",{'employee':pp[0]},['company'])
						print(company)
						if company:
							doc = frappe.new_doc("Additional Salary")
							doc.employee = pp[0]
							doc.company = company
							doc.salary_component = pp[1]
							doc.amount = int(str(pp[2]).replace(',',''))
							doc.payroll_date = '2022-02-16'
							doc.save(ignore_permissions = True)
							doc.submit

@frappe.whitelist()
def gratuity_calc(employee):
	basic, doj = frappe.db.get_value('Employee', employee, ['basic', 'date_of_joining'])
	date_2 = datetime.now()
	diff = relativedelta.relativedelta(date_2, doj)
	current_yoe = cstr(diff.years) + ' years, ' + cstr(diff.months) + ' months and ' + cstr(diff.days) + ' days'
	exp_years = diff.years
	exp_month = diff.months
	exp_days = diff.days
	total_days = (exp_years * 365) + (exp_month * 30) + exp_days
	basic_salary = basic
	per_day_basic = (basic_salary / 30 * 21) / 365
	total_gratuity = per_day_basic * total_days

	if current_yoe <= "5 years, 0 months and 0 days":
		if diff.years > 1:
			return total_gratuity
	else:
		if diff.years < 1:
			return total_gratuity

	return total_gratuity


@frappe.whitelist()
def gratuity_calc_sr(employee,basic):
	doj = frappe.db.get_value('Employee',employee,['date_of_joining'])
	current_yoe_days = date_diff(nowdate(),doj)
	current_yoe = round((current_yoe_days / 365),1)
	# yoe = add_years(doc[1],5)
	if current_yoe < 5:
		gratuity_per_year = (int(basic)/30) * 21
		total_gratuity = current_yoe * gratuity_per_year
		return total_gratuity
	if current_yoe >= 5:
		total_yoe = current_yoe
		first_five_yr = ((int(basic)/30) * 21) * 5
		total_yoe -= 5
		rest_of_yrs = ((int(basic)/30) * 30) * total_yoe
		total_gratuity = first_five_yr + rest_of_yrs
		return total_gratuity


@frappe.whitelist()
def check_discount_percent(discount):
	max_discount = 0
	d = frappe.db.get_value("Quotation Discount",{'user':frappe.session.user,'parent':'Sales settings'},['user','max_dis'])
	if d:
		if max_discount < d[1]:
			max_discount = d[1]
	if max_discount == 0:
		return ''
	elif float(discount) > max_discount:
		return max_discount

# @frappe.whitelist()
# def get_dn_list_sales_invoice(doc,method):
#     sii = doc.items
#     dn_list = []
#     dummy = []
#     for i in sii:
#         if  i.delivery_note:
#             if i.delivery_note not in dn_list:
#                 dn_list.append(i.delivery_note or "")
#             else:
#                 dummy.append(i.delivery_note or "")
#     si = frappe.get_doc("Sales Invoice",doc.name)
#     si.delivery_note_list = str(dn_list)
#     si.save(ignore_permissions=True)
#     frappe.db.commit()

@frappe.whitelist()
def item_price():
	sellin_price = 200
	percentage = 10
	value = sellin_price * (1 + (percentage/100))
	print(round(value))

@frappe.whitelist()
def create_address(name,address_1,address_2,city):
	doc = frappe.new_doc("Address")
	doc.address_title = name
	doc.address_line1 = address_1
	doc.address_line1 = address_2
	doc.city = city
	doc.append('links',{
		"link_doctype":"Customer",
		"link_name" : name,
		"link_title" : name,
	})
	doc.save(ignore_permissions=True)

@frappe.whitelist()
def create_sales_person(name,department,employee):
	doc = frappe.new_doc("Sales Person")
	doc.sales_person_name = employee
	doc.parent_sales_person = "Sales Team"
	doc.employee = name
	doc.department = department
	doc.enabled = True
	doc.save(ignore_permissions=True)

@frappe.whitelist()
def calculate_commission_for_item():
	items = frappe.get_all('Item',['*'])
	for item in items:
		item_group = frappe.get_all('Item Group',['*'])
		for item_g in item_group:
			if item.item_group == item_g.name:
				item.commission_ = item_g.commission

@frappe.whitelist()
def mail_trigger():
	day = datetime.strptime(str(today()),"%Y-%m-%d").date()
	past_two_day = add_days(day,-2)


	day_plan = frappe.db.get_all('Day Plan Timesheet',{'docstatus':'Draft','worked_date':past_two_day},['*'])
	for dp in day_plan:

		project = frappe.get_all('Project',{'status':'Open'},['*'])
		for p in project:
			# print(p.name)
			if dp.project == p.name:
				print(dp.project == p.name)
				frappe.sendmail(
					recipients =['mohamedyousuf.e@groupteampro.com'],
					subject = 'NO Day Plan Timesheet',
					message = 'Dear Sir <br> For the project %s Day Plan TimeSheet is not submitted'%(dp.project)
			)
				print(dp.project)


@frappe.whitelist()
def get_default_warehouse(company):
	w_house = frappe.db.get_value("Warehouse",{'company':company,'default_for_stock_transfer':1},['name'])
	return w_house

@frappe.whitelist()
def product_bundle(item_code):
	bundle = frappe.db.exists("Product Bundle",{'name':item_code})
	if bundle:
		bundle_item = frappe.get_doc("Product Bundle",item_code)
		frappe.errprint(bundle_item)
		return bundle_item.items


@frappe.whitelist()
def create_payment_entry(doc, method):
	if doc.is_paid == 1:
		doc.status = "Paid"
		pe = frappe.new_doc("Payment Entry")
		pe.posting_date = doc.posting_date
		pe.payment_type = "Pay"
		pe.company = doc.company
		pe.paid_amount = doc.total
		pe.received_amount = doc.total
		pe.paid_to_account_currency = doc.currency
		pe.paid_from_account_currency = doc.currency
		pe.paid_from = doc.debit_to
		pe.party_type = "Supplier"
		pe.party = "INDUSTRIAL EQUIPMENT & SERVICES CO."
		pe.save(ignore_permissions=True)


@frappe.whitelist()
def cancel_ce(cost_estimation,quotation):
	if cost_estimation:
		cost_estimation = frappe.get_doc("Cost Estimation",cost_estimation)
		cost_estimation.cancel()

# @frappe.whitelist()
# def cancel_pb(doc,method):
#     frappe.errprint("Cancelling PB")
#     project_bud = frappe.get_doc("Project Budget",{'sales_order':doc.name})
#     project_bud.cancel()

@frappe.whitelist()
def amend_ce(doc,method):
	if doc.amended_from:
		ce_sow = frappe.get_all("CE SOW",{'cost_estimation':doc.amended_from},['name','cost_estimation'])
		for ce in ce_sow:
			ces = frappe.get_doc("CE SOW",{'name':ce.name,'cost_estimation':ce.cost_estimation})
			ces.cost_estimation = doc.name
			ces.save(ignore_permissions=True)


@frappe.whitelist()
def amend_pb(doc,method):
	if doc.amended_from:
		pro = frappe.db.exists("Project",{'budgeting':doc.amended_from})
		if pro:
			project = frappe.get_doc("Project",{'budgeting':doc.amended_from})
			project.budgeting = doc.name
			project.save(ignore_permissions = True)
		pb_sow = frappe.get_all("PB SOW",{'project_budget':doc.amended_from},['name','project_budget'])
		for pb in pb_sow:
			pbs = frappe.get_doc("PB SOW",{'name':pb.name,'project_budget':pb.project_budget})
			pbs.project_budget = doc.name
			pbs.save(ignore_permissions=True)


@frappe.whitelist()
def find_item():
	items = frappe.db.sql(""" select name from `tabItem` where owner = 'rizni@electraqatar.com' """, as_dict=1)
	for item in items:
		po = frappe.db.sql(""" select count(*) as count from `tabPurchase Order Item` where item_code = '%s' """%(item.name),as_dict = 1)[0]
		if po['count'] == 0:
			pi = frappe.db.sql(""" select count(*) as count from `tabPurchase Invoice Item` where item_code = '%s' """%(item.name),as_dict = 1)[0]
			if pi['count'] == 0:
				pr = frappe.db.sql(""" select count(*) as count from `tabPurchase Receipt Item` where item_code = '%s' """%(item.name),as_dict = 1)[0]
				if pr['count'] == 0:
					si = frappe.db.sql(""" select count(*) as count from `tabSales Invoice Item` where item_code = '%s' """%(item.name),as_dict = 1)[0]
					if si['count'] == 0:
						so = frappe.db.sql(""" select count(*) as count from `tabSales Order Item` where item_code = '%s' """%(item.name),as_dict = 1)[0]
						if so['count'] == 0:
							qo = frappe.db.sql(""" select count(*) as count from `tabQuotation Item` where item_code = '%s' """%(item.name),as_dict = 1)[0]
							if qo['count'] == 1:
								print(item.name)



		# quotation = frappe.db.sql(""" select `tabQuotation`.name from `tabQuotation` left join `tabQuotation Item` on `tabQuotation`.name = `tabQuotation Item`.parent where `tabQuotation Item`.item_code ='%s' """%(it.name),  as_dict=1)
		# if not quotation:
			# print(it.name)
			# sales_order = frappe.db.sql(""" select `tabSales Invoice`.name from `tabSales Invoice` left join `tabSales Invoice Item` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent where `tabSales Invoice Item`.item_code ='%s' """%(it.name),  as_dict=1)

@frappe.whitelist()
def visa_expire():
	visa = frappe.db.sql(""" select name,visa_expiry_date from `tabVisa Approval Monitor`""",as_dict = 1)
	data = ''
	data += '<table class = table table - bordered><tr><td colspan = 5>Expired Visa</td></tr>'
	for date in visa:
		expire = date.visa_expiry_date
		if expire:
			str_date = datetime.strptime(str(today()),'%Y-%m-%d').date()
			expiry = add_days(today(),30)
			expiry_date = datetime.strptime(str(expiry),'%Y-%m-%d').date()
			if expire < expiry_date:
				print(expire)
				data += '<tr><td>%s</td><td>%s</td></tr>'%(expire,date.name)
	data += '</table>'
	frappe.sendmail(
			recipients=['mohamedshajith.j@groupteampro.com'],
			subject=('Visa Expiry'),
			header=('Visa Expiry List'),
			message="""
					Dear Sir,<br><br>
					%s
					""" % (data)
		)



@frappe.whitelist()
def change_name():
	emp = frappe.db.get_all('Employee',{'status':'Active'},['employee'])
	for em in emp:
		name = frappe.get_doc('Employee',em.employee)
		print(name)
		fname = name.first_name
		f_name = fname.title()
		name.first_name = f_name
		if name.last_name:
			lname = name.last_name
			l_name = lname.title()
			name.last_name = l_name
			name.save(ignore_permissions=True)
			frappe.db.commit()

@frappe.whitelist()
def employee_number(doc,method):
	emp = frappe.db.sql(""" select employee_number from `tabEmployee` order by name """,as_dict = 1)[-1]
	last = emp.employee_number
	las = int(last)
	new = las+1
	# doc.employee_number = new
	# doc.name = new
	# frappe.db.set_value('Job Offer',doc.name,'employee_number',new)
	# frappe.errprint(new)


@frappe.whitelist()
def record(name):
	maintenance = frappe.db.exists("Vehicle Maintenance Check List",{'register_no':name})
	if maintenance:
		main = frappe.db.get_all("Vehicle Maintenance Check List",{'register_no':name},['complaint','employee_id','vehicle_handover_date','garage_name'])[0]

	accident = frappe.db.exists("Vehicle Accident Report",{'plate_no':name})
	if accident:
		acc = frappe.db.get_all("Vehicle Accident Report",{'plate_no':name},['name','emp_id','date_of_accident','remarks'])[0]

		return main,acc

@frappe.whitelist()
def get_so_items(parent):
	so = frappe.get_doc("Sales Order",parent)
	return so.items

@frappe.whitelist()
def get_payment_schedule(parent):
	so = frappe.get_doc("Sales Order",parent)
	return so.payment_schedule_2s

@frappe.whitelist()
def get_rb_report():
	context = {'po_no':'TRD-PO-2022-00281'}
	rb_report = frappe.get_doc('RB Report', 'RB Purchase Order')
	pdf = rb_report.get_pdf(context=context)

@frappe.whitelist()
def get_po_name(doc,method):
	so = frappe.get_doc("Sales Order",doc.sales_order)
	so.project = doc.name
	so.save(ignore_permissions=True)

@frappe.whitelist()
def projectbudget_name(doc,method):
	if doc.project_budget:
		pb = frappe.get_doc("Project Budget",doc.project_budget)
		pb.sales_order = doc.name
		pb.save(ignore_permissions=True)

@frappe.whitelist()
def automate_pos(doc,method):
	# pos_profile = frappe.get_list("POS Profile",['name','company'])
	today = date.today()
	# yesterday = today - timedelta(days = 9)
	# print(yesterday)
	poprof = frappe.get_doc("POS Profile",doc.pos_profile)
	pos_open = frappe.new_doc("POS Opening Entry")
	pos_open.period_start_date = today
	pos_open.posting_date = now()
	for ps in poprof.applicable_for_users:
		pos_open.user = ps.user
	pos_open.company = doc.company
	pos_open.pos_profile = poprof.name
	for ps in poprof.payments:
		pos_open.append('balance_details',{
			'mode_of_payment':ps.mode_of_payment,
			'opening_amount':0
		})
	pos_open.save(ignore_permissions=True)
	pos_open.submit()
	frappe.db.commit()

	# pos_invoice = frappe.get_list("POS Invoice",{'status':"Paid",'company':i.company},['name','posting_date','grand_total','customer'])
	pos_invoice = frappe.db.sql(""" select name,posting_date,grand_total,customer from `tabPOS Invoice` where status = "Paid" and docstatus != '2' and company = '%s' and posting_date='%s'"""%(doc.company,today),as_dict = 1)
	pos_close = frappe.new_doc("POS Closing Entry")
	pos_close.period_start_date = today
	pos_close.period_end_date = now()
	pos_close.posting_date = now()
	pos_close.posting_time = now()
	pos_close.pos_opening_entry = pos_open.name
	for ps in poprof.applicable_for_users:
		pos_close.user = ps.user
	pos_close.company = doc.company
	pos_close.pos_profile = poprof.name
	for i in pos_invoice:
		pos_close.append('pos_transactions',{
				'pos_invoice':i.name,
				'posting_date':i.posting_date,
				'grand_total':i.grand_total,
				'customer':i.customer,
				'is_return': i.is_return
			})
		frappe.log_error(title='pos',message=pos_close)

	pos_close.save(ignore_permissions=True)
	pos_close.submit()
	frappe.db.commit()


def create_scheduled_job_type():
	pos = frappe.db.exists('Scheduled Job Type', 'reset_general_entry_purchase_rate')
	if not pos:
		sjt = frappe.new_doc("Scheduled Job Type")
		sjt.update({
			"method" : 'electra.utils.reset_general_entry_purchase_rate',
			"frequency" : 'Hourly'
		})
		sjt.save(ignore_permissions=True)

# @frappe.whitelist()
# def bulk_item_cancel(filename):
#     from frappe.utils.file_manager import get_file
#     _file = frappe.get_doc("File", {"file_name": filename})
#     filepath = get_file(filename)
#     pps = read_csv_content(filepath[1])
#     for pp in pps:
#         if pp[0] is not None:
#             print(pp[0])
#             item = frappe.db.sql(""" update `tabItem` set brand = '' where name = '%s'  """%(pp[0]))
#             print(item)

@frappe.whitelist()
def return_purchase_invoice(supplier):
	purchase_invoice = frappe.get_list("Purchase Invoice",{"status": ('not in',("Paid","Cancelled")),'supplier':supplier},['conversion_rate','currency','name','grand_total','posting_date','outstanding_amount','supplier','company','bill_no'])
	pur_order = []
	po = frappe.db.get_list("Purchase Order",{"supplier":supplier,"docstatus":1},['name'])
	for i in po:
		pi_item = frappe.get_value("Purchase Invoice Item",{"purchase_order":i.name},['parent'])
		if not pi_item:
			pur = frappe.db.get_list("Purchase Order",{"docstatus":1,"name":i.name},['conversion_rate','currency','name','transaction_date','grand_total','advance_paid','supplier','company','project'])
			if pur not in pur_order:
				pur_order.append(pur)

	# jv = frappe.db.get_list("Journal Entry",{'voucher_type':"Journal Entry","title":supplier,"docstatus":1},['name','total_amount_currency','posting_date','total_credit','total_debit','company','title','bill_no'])
	jv = frappe.db.sql("""select `tabJournal Entry`.name,`tabJournal Entry`.company,`tabJournal Entry`.title,`tabJournal Entry`.bill_no,`tabJournal Entry`.posting_date,`tabJournal Entry Account`.credit_in_account_currency as total_credit from `tabJournal Entry`
				left join `tabJournal Entry Account` on `tabJournal Entry`.name = `tabJournal Entry Account`.parent
				where `tabJournal Entry Account`.party = '%s' and `tabJournal Entry Account`.party_type = 'Supplier' and `tabJournal Entry`.voucher_type = 'Journal Entry' and `tabJournal Entry`.docstatus != 2 and `tabJournal Entry Account`.credit_in_account_currency > 0  ORDER BY
			`tabJournal Entry`.posting_date ASC"""%(supplier),as_dict=True)
	return purchase_invoice,pur_order,jv

@frappe.whitelist()
def return_list():
	jv = frappe.db.sql("""select `tabJournal Entry`.name,`tabJournal Entry`.company,`tabJournal Entry`.title,`tabJournal Entry`.bill_no,`tabJournal Entry`.posting_date,`tabJournal Entry Account`.credit_in_account_currency as total_credit from `tabJournal Entry`
				left join `tabJournal Entry Account` on `tabJournal Entry`.name = `tabJournal Entry Account`.parent
			where `tabJournal Entry Account`.party = '%s' and `tabJournal Entry Account`.party_type = 'Supplier' and `tabJournal Entry`.voucher_type = 'Journal Entry' and `tabJournal Entry`.title = '%s' and `tabJournal Entry`.docstatus != 2 """%("GLOBEL LINK WESTSTAR SHIPPING WLL","GLOBEL LINK WESTSTAR SHIPPING WLL"),as_dict=True)
	
	# jv = frappe.db.get_list("Journal Entry",{'party_type':"Supplier",'name':"TRD-JV-2023-00079","party":"GLOBEL LINK WESTSTAR SHIPPING WLL"},['name','total_amount_currency','posting_date','total_credit','debit','company','title','bill_no'])
	print(jv)

@frappe.whitelist()
def payment_summary(supplier):
	summary = frappe.db.sql("""select company,sum(outstanding_amount) as total from `tabPurchase Invoice` where status != 'Paid' and docstatus != 2 and supplier = '%s' group by company """%(supplier),as_dict=True)
	data = ''
	data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:orange" colspan=4><center>Payment Summary</center></th></tr>'
	data += '''
	<tr><td style="padding:1px;border: 1px solid black" ><b>Company</b></td><td style="padding:1px;border: 1px solid black" ><b>Amount</b></td></tr>'''
	i = 0
	for ps in summary:
		data += '''
		<tr><td style="padding:1px;border: 1px solid black;"  >%s</td>
		<td style="padding:1px;border: 1px solid black;" >%s</td></tr>'''%(ps.company,ps.total)
		frappe.errprint(ps.total)
	i += 1



	data += '</table>'

	return data

@frappe.whitelist()
def return_order_invoice(customer):
	sales_invoice = frappe.get_list("Sales Invoice",{"status": ('not in',("Paid","Cancelled")),'customer':customer},['conversion_rate','currency','name','grand_total','posting_date','outstanding_amount','customer','company'])
	sal_order = []
	so = frappe.db.get_list("Sales Order",{"customer":customer,"docstatus":1},['name'])
	for i in so:
		si_item = frappe.get_value("Sales Invoice Item",{"sales_order":i.name},['parent'])
		if not si_item:
			sal = frappe.db.get_list("Sales Order",{"docstatus":1,"name":i.name},['conversion_rate','currency','name','transaction_date','grand_total','advance_paid','customer','company','project'])
			if sal not in sal_order:
				sal_order.append(sal)

	jv = frappe.get_list("Journal Entry",{'voucher_type':"Journal Entry",'party_type':"Customer","title":customer},['name','total_amount_currency','posting_date','total_credit','total_debit','company','title','bill_no'])
	return sales_invoice,sal_order,jv
	



	data += '</table>'

	return data

@frappe.whitelist()
def get_all_dn_details(delivery_note):
	dn = frappe.get_all('Delivery Note',{'name':delivery_note},['*'])
	return dn


@frappe.whitelist()
def get_all_dn_table(delivery_note):
	dn = frappe.get_doc('Delivery Note',delivery_note)
	return dn.items

@frappe.whitelist()
def sales_invoice_remarks(doc,method):
	if doc.delivery_note:
		if doc.po_no and doc.po_date:
			doc.remarks = ("Against Customer Order {0} dated {1} and Delivery Note {2}").format(
				doc.po_no, formatdate(doc.po_date),doc.delivery_note
			)


@frappe.whitelist()
def get_cred_lim(customer):
	empty = "empty"
	cust = frappe.get_doc("Customer",customer)
	if cust.credit_limits:
		return cust.credit_limits
	else:
		return empty


@frappe.whitelist()
def get_trans_perc(item_group):
	if item_group:
		item_group = frappe.get_doc("Item Group",item_group)
		for ig_def in item_group.item_group_defaults:
			return ig_def.transfer_percentage

@frappe.whitelist()
def cred_limit_upload(doc,method):
	companies = [
			{"company":"ELECTRA  - NAJMA SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"STEEL DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"MARAZEEM SECURITY SERVICES - HO","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"MEP DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ELECTRA - BINOMRAN SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"KINGFISHER TRADING AND CONTRACTING COMPANY","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"KINGFISHER - SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"KINGFISHER - TRANSPORTATION","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"MARAZEEM SECURITY SERVICES - SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"MARAZEEM SECURITY SERVICES","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ELECTRA - BARWA SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ELECTRICAL DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ENGINEERING DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"INTERIOR DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"INDUSTRIAL TOOLS DIVISION","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ELECTRA - ALKHOR SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"TRADING DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)","credit_limit" : 100000,"bypass_credit_limit_check":1},
					]


	if doc.customer_type == "Company":
		if not doc.credit_limits:
			for company in companies:
				doc.append("credit_limits",{
					"company":company['company'],
					"credit_limit":company['credit_limit'],
					"bypass_credit_limit_check":company['bypass_credit_limit_check']
				})
			doc.save(ignore_permissions=True)

@frappe.whitelist()
def cred_list_upload():
	companies = [
			{"company":"ELECTRA  - NAJMA SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"STEEL DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"MARAZEEM SECURITY SERVICES - HO","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"MEP DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ELECTRA - BINOMRAN SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"KINGFISHER TRADING AND CONTRACTING COMPANY","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"KINGFISHER - SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"KINGFISHER - TRANSPORTATION","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"MARAZEEM SECURITY SERVICES - SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"MARAZEEM SECURITY SERVICES","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ELECTRA - BARWA SHOWROOM","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ELECTRICAL DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company":"ENGINEERING DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company": "INTERIOR DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company": "TRADING DIVISION - ELECTRA","credit_limit" : 100000,"bypass_credit_limit_check":1},
			{"company" :"Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)","credit_limit" : 100000,"bypass_credit_limit_check":1},
					]
	# cred_lim = frappe.get_list("Customer",{'customer_type':"Company"},['name'])
	# for cust in cred_lim:
	#     cred = frappe.get_doc("Customer",cust.name)
	#     if cred.credit_limits:
	#         for company in companies:
	#             cre = frappe.get_doc("Customer Credit Limit",{'parent':'sad'},['company','credit_limit','bypass_credit_limit_check'])
	#             cre.company = company['company']
	#             cre.credit_limit = company['credit_limit']
	#             cre.bypass_credit_limit_check = company['bypass_credit_limit_check']
	#             cre.save(ignore_permissions=True)
	cred_lim = frappe.get_list("Customer",{'customer_type':"Company","name": ('not in',("Al Attiyah Architectural Group Holding","GULF CONTRACTING CO WLL","Tekfen Construction & Installation Co.Inc","MARBU CONTRACTING COMPANY W.L.L","Skycool Trading & COntracting Co. WLL","SEG QATAR","STARK SECURITY SERVICES","ESHHAR SECURITY","International Metal Working Solutions","WONDER NETWORK TRADING","WAST BUSTERS TRADING & CLEANING SERVICES","AG Middle East WLL","ledd Technologies","UrbaCon Trading & Contracting LLC","CENTURY TRADING & CONTRACTING W.L.L","SMEET Precast W.L.L","Global Electric Company","ARABIAN MEP CONTRACTING","Absolute security services","INTEGRA PROJECTS & FACILITY MANAGEMENT W.L.L","Regency Technology","Elegancia Group-Facilities Management","EMCO Qatar","Buzwair Advanced Technologies","Johnson Controls","The Qatari Modern Maintenance Company","Remal Security Services W.L.L","Gulf Contracting Company","Albaker Networks & Engineering","k3 international trading&contracting L.L.C","Norden Singapore PTE Ltd","Lausanne Security","Contraco W.L.L.","Pixel Technology Solutions","TECHNOLOGY PROFESSIONALS TRADING","AL JABER ENGINEERING","MICROTECH","ARABELLA TRADING","Qatar Factory","INTERNATIONAL SHADE CO.","Al Darwish  Engineering","Al Hamra Tents & Trading LLC","Bluu Qatar","test 3","BLACK ARROW TRADING AND CONTRACTING","Energy Technical Services WLL","Boom General Contractors W.L.L"))},['name'],limit_start=0, limit_page_length=50)
	for cust in cred_lim:
		cred = frappe.get_doc("Customer",cust.name)
		if cred.credit_limits:
			if len(cred.credit_limits) == 18:
				print(cust.name)
		# cred = frappe.get_doc("Customer",cust.name)
		# if cred.credit_limits:
				cred.set('credit_limits', [])
				for company in companies:
					cred.append("credit_limits",{
						"company":company['company'],
						"credit_limit":company['credit_limit'],
						"bypass_credit_limit_check":company['bypass_credit_limit_check']
					})
				cred.save(ignore_permissions=True)
	# cred_lim = frappe.db.sql(""" select name from `tabCustomer` where creation between "2023-01-04" and "2023-01-04" """,as_dict=1)
	# skip = []
	# cred_lim = frappe.get_list("Customer",{'customer_type':"Company","name": ('not in',("Robsten Contracting and Services","Meac Water Systems Co. Wll","ELECTRA - BARWA SHOWROOM","ELECTRA  - NAJMA SHOWROOM"))},['name'])
	# for i in cred_lim:
	#     cred = frappe.get_doc("Customer",{'name':i.name})
	#     if not cred.credit_limits:
	#         print(i.name)
	#     # # cred.set('credit_limits', [])
	#         for company in companies:
	#             cred.append("credit_limits",{
	#                 "company":company['company'],
	#                 "credit_limit":company['credit_limit'],
	#                 "bypass_credit_limit_check":company['bypass_credit_limit_check']
	#             })
	#         cred.save(ignore_permissions=True)


@frappe.whitelist()
def stock_request(item_code):
	stocking = frappe.db.sql("""select actual_qty,warehouse from tabBin where item_code = '%s' """%(item_code),as_dict=True)
	return stocking

@frappe.whitelist()
def warehouse_stock_check(item_code,warehouse):
	stocking = frappe.db.sql("""select actual_qty from tabBin where item_code = '%s' and warehouse = '%s' """%(item_code,warehouse),as_dict=True)
	return stocking

@frappe.whitelist()
def bom_duplicate(material_request):
	childtab = frappe.db.sql(""" select `tabMaterial Request Item`.item_code,`tabMaterial Request Item`.item_name,`tabMaterial Request Item`.description,`tabMaterial Request Item`.schedule_date,sum(`tabMaterial Request Item`.qty) as qty,
	`tabMaterial Request Item`.uom,`tabMaterial Request Item`.conversion_factor,`tabMaterial Request Item`.warehouse
	from `tabMaterial Request`
	left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent where `tabMaterial Request`.name = '%s' group by `tabMaterial Request Item`.item_code"""%(material_request),as_dict = 1)
	return childtab

@frappe.whitelist()
def si_duplicate(sales_invoice,item_details):
	item_details = json.loads(item_details)
	dn_list = []
	if item_details:
		for i in item_details:
			if i not in dn_list:
				dn_list.append(i or "")
			dnlist = str(dn_list)

	sales_invoice = frappe.db.sql(""" select `tabSales Invoice Item`.item_code,`tabSales Invoice Item`.income_account,`tabSales Invoice Item`.expense_account,`tabSales Invoice Item`.item_name,`tabSales Invoice Item`.description,sum(`tabSales Invoice Item`.qty) as qty,
	`tabSales Invoice Item`.uom,`tabSales Invoice Item`.conversion_factor,`tabSales Invoice Item`.warehouse,`tabSales Invoice Item`.rate,
	`tabSales Invoice Item`.base_rate,
	`tabSales Invoice Item`.amount,
	`tabSales Invoice Item`.base_amount,
	`tabSales Invoice Item`.net_rate,`tabSales Invoice Item`.base_net_rate,
	`tabSales Invoice Item`.net_amount,`tabSales Invoice Item`.base_net_amount
	from `tabSales Invoice`
	left join `tabSales Invoice Item` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent where `tabSales Invoice`.name = '%s' group by `tabSales Invoice Item`.item_code"""%(sales_invoice),as_dict = 1)
	return sales_invoice,dnlist or 'null' ,item_details

@frappe.whitelist()
def mr_duplicate(item_details):
	item_details = json.loads(item_details)
	dn_list = []
	if item_details:
		for i in item_details:
			if i not in dn_list:
				dn_list.append(i or "")
			dnlist = str(dn_list)

	return dnlist or 'null'

@frappe.whitelist()
def project_duplicate(item_details):
	item_details = json.loads(item_details)
	dn_list = []
	if item_details:
		for i in item_details:
			if i not in dn_list:
				dn_list.append(i or "")
			dnlist = str(dn_list)

	return dnlist or 'null'

@frappe.whitelist()
def proj_day_plan_emp(multi_project_day_plan):
	proj = frappe.get_doc("Multi Project Day Plan",multi_project_day_plan)
	return proj.project_day_plan_employee

@frappe.whitelist()
def prob_eval(employee_name):
	prob = frappe.db.exists("Staff Probation Evaluation Form",employee_name)
	if prob:
		return True
	else:
		return False


@frappe.whitelist()
def single_proj_day_plan(day_schedule):
	ds = frappe.get_doc("Day Schedule",day_schedule)
	return ds.schedule

@frappe.whitelist()
def is_dummy_dn_approved(doc,method):
	if doc.dummy_dn:
		if not doc.is_approved == 1:
			frappe.throw("Delivery Note Not Approved")

@frappe.whitelist()
def is_si_approved(doc,method):
	if doc.is_third_party_commission_applicable:
		if not doc.is_approved == 1:
			frappe.throw("Sales Order Not Approved")


@frappe.whitelist()
def work_order_bom(item_code,company,qty,sales_order,project):
	boms = frappe.db.get_all("BOM",{'item':item_code},'name')
	if boms:
		for i in boms:
			bom = frappe.get_doc("BOM",i.name)
			work = frappe.new_doc("Work Order")
			work.qty = int(qty)
			work.company = company
			work.sales_order = sales_order
			work.project = project
			work.status = "In Process"
			work.bom_no = i.name
			work.production_item = bom.item
			work.wip_warehouse = frappe.db.get_value('Warehouse', filters={'name': ['like', '%Work In Progress%'],'company':company})
			work.fg_warehouse = frappe.db.get_value('Warehouse', filters={'name': ['like', "%" + project + "%"]})
			work.source_warehouse = frappe.db.get_value('Warehouse', {'company':company,'default_for_stock_transfer':1}, 'name')
			work.planned_start_date = now()
			for b in bom.items:
				work.append("required_items",{
					"item_code": b.item_code,
					"source_warehouse": frappe.db.get_value('Warehouse', {'company':company,'default_for_stock_transfer':1}, 'name'),
					"include_item_in_manufacturing":1,
					"item_name": b.item_name,
					"qty": b.qty * int(qty),
					"rate": b.rate,
					"amount": b.rate *(b.qty * int(qty)),
				})
			work.save(ignore_permissions=True)
			work.submit()

@frappe.whitelist()
def set_title():
	title = frappe.db.get_list("Sales Invoice",{'posting_date':"31-01-2023"},['name'])
	for i in title:
		doc = frappe.get_doc("Sales Invoice",i.name)
		doc.title = doc.customer
		doc.save(ignore_permissions=True)
		print(i.name)

@frappe.whitelist()
def contact_details(name,email,mobile,customer,designation):
	# values = json.loads(values)
	contact = frappe.new_doc("Contact")
	contact.first_name = name
	contact.contact_person_email_id_ = email
	contact.mobile_no = mobile
	contact.designation = designation
	contact.append('email_ids',{
		'email_id': email
	})
	contact.append('phone_nos',{
		'phone':mobile,
	})
	contact.append('links',{
		'link_doctype':'Customer',
		"link_name": customer
	})
	contact.save(ignore_permissions=True)
	frappe.msgprint("Contact Created")
	return contact.name

@frappe.whitelist()
def update_employee_salary():
	sal = frappe.db.sql("""select * from `tabSalary Revision` where docstatus = 1""", as_dict=1)
	if sal:
		for ss in sal:
			if ss.salary_revision_status == "Permanent":
				if ss.effective_date == datetime.strptime((today()), '%Y-%m-%d').date():
					emp = frappe.get_doc("Employee",{'employee':ss.employee,'status': 'Active' })
					emp.salary_mode = ss.salary_mode
					emp.salary_currency = ss.salary_currency
					emp.basic = ss.basic
					emp.hra = ss.hra
					emp.accommodation = ss.accommodation
					emp.mobile_allowance = ss.mobile_allowance
					emp.transportation = ss.transport_allowance
					emp._other_allowance = ss.other_allowance
					emp.medical_allowance_ = ss.medical_allowance
					emp.leave_salary = ss.leave_salary
					emp.air_ticket_allowance_ = ss.air_ticket_allowance
					emp.qid_cost = ss.qid_cost
					emp.medical_renewal = ss.medical_renewal
					emp.visa_cost_ = ss.visa_cost
					emp.gross_salary = ss.gross_salary
					emp.gratuity = ss.gratuity
					emp.ctc = ss.cost_to_company
					emp.per_hour_cost = ss.per_hour_cost
					emp.append('history',{
					"date":ss.effective_date,
					"basic":ss.basic,
					"hra":ss.hra,
					"other_allowance":ss.other_allowance,
					"transport_allowance":ss.transport_allowance,
					"medical_allowance":ss.medical_allowance,
					"air_ticket_allowance":ss.air_ticket_allowance,
					"mobile_allowance":ss.mobile_allowance,
					"visa_cost":ss.visa_cost,
					"accommodation":ss.accommodation,
					"leave_salary":ss.leave_salary,
					"qid_cost":ss.qid_cost,
					"medical_renewal":ss.medical_renewal,
					"remark":ss.remarks
				})
					emp.save(ignore_permissions=True)
					frappe.db.commit()
			else:
				if ss.effective__to_date == datetime.strptime((today()), '%Y-%m-%d').date():
					emp = frappe.get_doc("Employee",{'employee':ss.employee,'status': 'Active' })
					emp.salary_mode = ss.salary_mode1
					emp.salary_currency = ss.salary_currency1
					emp.basic = ss.basic1
					emp.hra = ss.hra1
					emp.accommodation = ss.accommodation1
					emp.mobile_allowance = ss.mobile_allowance1
					emp.transportation = ss.transport_allowance1
					emp._other_allowance = ss.other_allowance1
					emp.medical_allowance_ = ss.medical_allowance1
					emp.leave_salary = ss.leave_salary1
					emp.air_ticket_allowance_ = ss.air_ticket_allowance1
					emp.qid_cost = ss.qid_cost1
					emp.medical_renewal = ss.medical_renewal1
					emp.visa_cost_ = ss.visa_cost1
					emp.gross_salary = ss.gross_salary1
					emp.gratuity = ss.gratuity1
					emp.ctc = ss.cost_to_company1
					emp.per_hour_cost = ss.per_hour_cost1
					emp.save(ignore_permissions=True)
					frappe.db.commit()
				if ss.effective__from_date == datetime.strptime((today()), '%Y-%m-%d').date():
					emp = frappe.get_doc("Employee",{'employee':ss.employee,'status': 'Active' })
					emp.salary_mode = ss.salary_mode1
					emp.salary_currency = ss.salary_currency1
					emp.basic = ss.basic2
					emp.hra = ss.hra2
					emp.accommodation = ss.accommodation2
					emp.mobile_allowance = ss.mobile_allowance2
					emp.transportation = ss.transport_allowance2
					emp._other_allowance = ss.other_allowance2
					emp.medical_allowance_ = ss.medical_allowance2
					emp.leave_salary = ss.leave_salary2
					emp.air_ticket_allowance_ = ss.air_ticket_allowance2
					emp.qid_cost = ss.qid_cost2
					emp.medical_renewal = ss.medical_renewal2
					emp.visa_cost_ = ss.visa_cost2
					emp.gross_salary = ss.gross_salary2
					emp.gratuity = ss.gratuity2
					emp.ctc = ss.cost_to_company2
					emp.per_hour_cost = ss.per_hour_cost2
					emp.save(ignore_permissions=True)
					frappe.db.commit()

@frappe.whitelist()
def margin_html(mar_dis_per,mar_tot_cost,mar_gross_tot,mar_dis_amt,total_selling,prof_per,margin_profit):
	data = ''
	data = "<table style='width:85%'>"
	data += "<tr><td style ='background-color:#dedede;font-weight:bold;text-align:center;border:1px solid black'>TOTAL COST</td><td style ='font-weight:bold;text-align:center;border:1px solid black'>%s</td><td style ='background-color:#dedede;font-weight:bold;text-align:center;border:1px solid black'>GROSS TOTAL SELLING</td><td style ='font-weight:bold;text-align:center;border:1px solid black'>%s</td></tr>"%(round(float(mar_tot_cost),2),round(float(mar_gross_tot),2))
	data += "<tr><td colspan  = 2 style = 'border:1px solid black;border-right-color:#dedede;background-color:#dedede;'><td style ='border-left-color:#dedede;background-color:#dedede;font-weight:bold;text-align:center;border:1px solid black'>DISCOUNT PERCENTAGE</td><td style ='background-color:#74cee7;font-weight:bold;text-align:center;border:1px solid black'>%s</td></tr>"%(round(float(mar_dis_per),2))
	data += "<tr><td style ='background-color:#dedede;font-weight:bold;text-align:center;border:1px solid black'>PROFIT PERCENTAGE</td><td style ='background-color:#74cee7;font-weight:bold;text-align:center;border:1px solid black'>%s</td><td style ='background-color:#dedede;font-weight:bold;text-align:center;border:1px solid black'>DISCOUNT AMOUNT</td><td style ='background-color:#74cee7;font-weight:bold;text-align:center;border:1px solid black'>%s</td></tr>"%(round(float(prof_per),2),round(float(mar_dis_amt),2))
	data += "<tr><td style ='background-color:#dedede;font-weight:bold;text-align:center;border:1px solid black'>PROFIT AMOUNT</td><td style ='background-color:#74cee7;font-weight:bold;text-align:center;border:1px solid black'>%s</td><td style ='background-color:#dedede;font-weight:bold;text-align:center;border:1px solid black'>TOTAL SELLING</td><td style ='font-weight:bold;text-align:center;border:1px solid black'>%s</td></tr>"%(round(float(margin_profit),2),round(float(total_selling),2))
	data += "</table>"
	return data



# @frappe.whitelist()
# def create_leave_salary(name,emp_id,grade,department,designation,status,date_of_joining):
# 	# employee = frappe.get_value("Employee",{'employee':employee,'status': 'Active' },["hra","gross_salary","air_ticket_allowance_","leave_salary"])
# 	# frappe.errprint(employee)
#         leave_sal = frappe.new_doc('Leave Salary')
#         leave_sal.employee_name = name
#         leave_sal.employee_number = emp_id
#         leave_sal.grade = grade
#         leave_sal.department = department
#         leave_sal.designation = designation
#         leave_sal.status = status
#         leave_sal.joining_date = date_of_joining
#         leave_sal.save(ignore_permissions=True)
#         frappe.msgprint("Leave Salary Created Sucessfully")

@frappe.whitelist()
def update_status():
	status = frappe.db.sql("""update `tabAdditional Salary` set docstatus = 0 where payroll_date between '2022-12-16' and '2023-01-15' and company = "TRADING DIVISION - ELECTRA" and salary_component = 'Abs Deduction' """)
	print(status)

@frappe.whitelist()
def update_si_status():
	status = frappe.db.sql("""update `tabSales Invoice` set docstatus = 1 where name = "ITD-CRD-2023-00012" """)
	print(status)

# @frappe.whitelist()
# def gratuity_calc_sr(employee,basic):
# 	doj = frappe.db.get_value('Employee',employee,['date_of_joining'])
# 	current_yoe_days = date_diff(nowdate(),doj)
# 	current_yoe = round((current_yoe_days / 365),1)
# 	# yoe = add_years(doc[1],5)
# 	if current_yoe < 5:
# 		gratuity_per_year = (int(basic)/30) * 21
# 		total_gratuity = current_yoe * gratuity_per_year
# 		return total_gratuity
# 	if current_yoe >= 5:
# 		total_yoe = current_yoe
# 		first_five_yr = ((int(basic)/30) * 21) * 5
# 		total_yoe -= 5
# 		rest_of_yrs = ((int(basic)/30) * 30) * total_yoe
# 		total_gratuity = first_five_yr + rest_of_yrs
# 		return total_gratuity


@frappe.whitelist()
def get_data(employee):
	emp = frappe.get_value("Employee",{'employee':employee,'status': 'Active' },["basic","hra","_other_allowance","accommodation","transportation","air_ticket_allowance_","mobile_allowance","medical_renewal","visa_cost_","medical_allowance_","leave_salary","gratuity","qid_cost","gross_salary","ctc","per_hour_cost",'compensationemployee_insurence'])
	return emp

@frappe.whitelist()
def get_values(employee,basic,hra,other_allowance,accommodation,transport_allowance,air_ticket_allowance,mobile_allowance,medical_renewal,visa_cost,medical_allowance,leave_salary,qid_cost,comp):
	gratuity = 0
	doj = frappe.db.get_value('Employee',employee,['date_of_joining'])
	current_yoe_days = date_diff(nowdate(),doj)
	current_yoe = round((current_yoe_days / 365),1)
	if current_yoe < 5:
		gratuity_per_year = (int(basic)/30) * 21
		gratuity = current_yoe * gratuity_per_year
	if current_yoe >= 5:
		total_yoe = current_yoe
		first_five_yr = ((int(basic)/30) * 21) * 5
		total_yoe -= 5
		rest_of_yrs = ((int(basic)/30) * 30) * total_yoe
		gratuity = first_five_yr + rest_of_yrs
	gross = int(basic) + int(hra) + int(other_allowance) + int(accommodation) + int(transport_allowance) + int(mobile_allowance)
	ctc = int(air_ticket_allowance) + int(gross) + int(medical_renewal) + int(visa_cost) + int(medical_allowance) + int(leave_salary) + int(gratuity) + int(qid_cost) + int(comp)
	phc = (int(ctc)/(30*8))
	return gratuity,gross,ctc,phc


@frappe.whitelist()
def get_purchase_rate(purchase_receipt):
	pr = frappe.db.sql("""select `tabPurchase Invoice Item`.base_rate,`tabPurchase Invoice Item`.parent,`tabPurchase Invoice Item`.item_code from `tabPurchase Invoice Item`
	where `tabPurchase Invoice Item`.purchase_receipt = '%s' """%(purchase_receipt),as_dict=True)
	if pr:
		tax = frappe.get_doc("Purchase Invoice",pr[0].parent)
		return pr[0].base_rate,pr[0].item_code,tax.taxes

@frappe.whitelist()
def get_def_currency(supplier):
	supp = frappe.db.get_value("Supplier",supplier,['default_currency'])
	conversion = get_exchange_rate(supp, "QAR")
	return supp or 'QAR',conversion or 1

@frappe.whitelist()
def get_clear():
	status = frappe.db.sql("""Update `tabSalary Structure` set docstatus = 0 where company = 'INTERIOR DIVISION - ELECTRA' """)
	print(status)
	# status = frappe.db.sql("""delete from `tabSalary Structure Assignment` """)
	# print(status)
	# status = frappe.db.sql("""delete from `tabPayroll Entry` """)
	# print(status)

@frappe.whitelist()
def get_norden_item(item):
	url = "https://erp.nordencommunication.com/api/method/norden.custom.get_electra_details?item=%s" % (item)
	headers = { 'Content-Type': 'application/json','Authorization': 'token 28a1f5da5dffd46:812f4d4d2671af2'}
	# params = {"limit_start": 0,"limit_page_length": 20000}

	response = requests.request('GET',url,headers=headers)
	res = json.loads(response.text)
	return res

@frappe.whitelist()
def update_all_desc():
	item = frappe.db.get_all("Item",{"modified":('between',("2023-03-19","2023-03-22"))},["name"])
	for i in item:
		itm = frappe.get_doc("Item",i.name)
		itm.description = itm.item_name
		itm.save(ignore_permissions=True)
		print()

@frappe.whitelist()
def get_again_so():
	sales_order = frappe.db.sql("""select `tabSales Invoice Item`.sales_order from `tabSales Invoice` left join `tabSales Invoice Item` on `tabSales Invoice`.name = `tabSales Invoice Item`.parent where `tabSales Invoice`.name = '%s' """%("SHBW-SR-2023-00032"),as_dict=True)[0]
	print(sales_order)

@frappe.whitelist()
def copy_doc():
	sn = frappe.get_doc("Sales Invoice","SHMS-STI-2023-00118")
	dn = frappe.copy_doc(sn)
	# dn.set("items",[])
	dn.flags.ignore_permissions = True
	dn.flags.ignore_mandatory = True
	dn.insert()

@frappe.whitelist()
def update_stock_after_return(doc,method):
	if doc.is_return == 1:
		if doc.update_stock == 0:
			sn = frappe.get_doc("Delivery Note",doc.delivery_note)
			dn = frappe.copy_doc(sn)
			dn.is_return = 1
			dn.delivery_return = doc.delivery_note_list
			dn.posting_date = doc.posting_date
			s = doc.delivery_note_list
			dn.naming_series = get_dn_return_series(doc.company,"Delivery Note")
			dn.set("items",[])
			stat = s.strip("[']'")
			dn_lst = stat.split(",")
			for s in dn_lst:
				dn.append("return_delivery_note",{
					"delivery_note":s.strip().lstrip("'").rstrip("'")
				})
			for i in doc.items:
				dn.append("items",{
					"item_code":i.item_code,
					"item_name":i.item_name,
					"description":i.description,
					"qty":i.qty,
					"uom":i.uom,
					"stock_uom":i.uom,
					"rate":i.rate,
					"conversion_factor":1,
					"base_rate":i.base_rate,
					"amount":i.amount,
					"warehouse":i.warehouse,
					"base_amount":i.base_amount,
				})
			dn.save(ignore_permissions = True)
			dn.submit()
			
@frappe.whitelist()
def get_so_child(sales_order):
	if sales_order:
		so = frappe.get_doc("Sales Order",sales_order)
		return so.items


@frappe.whitelist()
# def enqueue_checkin_bulk_upload_csv(filename):
# 	frappe.enqueue(
# 		checkin_bulk_upload_csv, # python function or a module path as string
# 		queue="long", # one of short, default, long
# 		timeout=36000, # pass timeout manually
# 		is_async=True, # if this is True, method is run in worker
# 		now=False, # if this is True, method is run directly (not in a worker) 
# 		job_name='Salary Component Updated', # specify a job name
# 		enqueue_after_commit=False, # enqueue the job after the database commit is done at the end of the request
# 		filename=filename, # kwargs are passed to the method as arguments
# 	)    
def checkin_bulk_upload_csv():
	# filename = "/files/Salary_Component.csv"
	from frappe.utils.file_manager import get_file
	_file = frappe.get_doc("File", {"file_url": "/files/Salary_Component.csv"})
	filepath = get_file("/files/Salary_Component.csv")
	pps = read_csv_content(filepath[1])
	for pp in pps:
		print(pp[0])
		if frappe.db.exists('Salary Component',{'name':pp[0]}):
			sc = frappe.db.exists('Salary Component',{'name':pp[0]},['name'])
			ac = frappe.db.sql("""select * from `tabSalary Component Account` where `tabSalary Component Account`.parent = '%s' """%(sc),as_dict=True)
			for i in ac:
				print("HI")
				


@frappe.whitelist()
def update():
	le = frappe.db.sql("""update `tabJob Offer` set company = "KINGFISHER - TRANSPORTATION" where name = 'HR-OFF-2023-00012' """)

# @frappe.whitelist()
# def validate_loan_amount(doc, method):
#     applicant = doc.applicant
#     loan_type = doc.loan_type
#     loan_amount = doc.loan_amount

#     # Calculate the sum of loan amounts for the employee and loan type
#     total_loan_amount = frappe.db.sql("""
#         SELECT SUM(loan_amount)
#         FROM `tabLoan Application`
#         WHERE applicant = %s
#             AND loan_type = %s
#             AND docstatus = 1
#     """, (applicant, loan_type))[0][0] or 0

#     loan_type_doc = frappe.get_doc("Loan Type", loan_type)

#     if total_loan_amount + loan_amount > loan_type_doc.maximum_loan_amount:
#         frappe.throw(_("Total Loan Amount for the employee cannot exceed Maximum Loan Amount for the Loan Type."))




# import frappe
# from datetime import datetime
# from dateutil import relativedelta

# @frappe.whitelist()
# def check_loan_amount(employee, loan_amount, interest_rate,loan_type):
# 	# Get the employee's basic amount
# 	basic_amount = frappe.db.get_value('Employee', employee, 'basic')
# 	print(basic_amount)
# 	employees = frappe.get_all('Employee', {'status': 'Active'}, ['name', 'employee_name', 'date_of_joining'])
# 	for emp in employees:
# 		date_2 = datetime.now()
# 		# Get the interval between two dates
# 		diff = relativedelta.relativedelta(date_2, emp.date_of_joining)
# 		yos = str(diff.years) + ' years, ' + str(diff.months) + ' months and ' + str(diff.days) + ' days'
# 		exp_years = diff.years
# 		exp_month = diff.months
# 		exp_days = diff.days
# 		total_days = (exp_years * 365) + (exp_month * 30) + exp_days
# 		print(total_days)
# 		per_day_basic = (float(basic_amount) / 30 * 21) / 365
# 		total_gratuity = per_day_basic * total_days
# 		gratuity = (total_gratuity * 80 /100)
# 	frappe.errprint(gratuity)
# 	# Convert loan_amount and interest_rate to appropriate numeric types
# 	loan_amount = float(loan_amount)
# 	interest_rate = int(interest_rate)

# 	# Calculate the loan amount plus the calculated interest
# 	calculated_amount = loan_amount
# 	frappe.errprint(calculated_amount)

# 	# Check if the calculated amount exceeds the basic amount
	
# 	if calculated_amount > gratuity :
# 		if loan_type == "Loan Against Gratuity" or "Loan Against Gratuity_2" or "Loan Against Gratuity_3" :
# 			frappe.throw(_('Loan amount must be Greater than Employee Gratuity'))

# 	if loan_type == "Loan Against Leave  Settlement_1" or "Loan Against Leave  Settlement" or "Loan Against Leave  Settlement_2" :
# 		gross = frappe.db.get_value('Employee', employee, 'gross_salary')
# 		frappe.errprint(gross)
# 		loan_amount = float(loan_amount)
# 		interest_rate = int(interest_rate)

# 	# Calculate the loan amount plus the calculated interest
# 		calculated_amount = loan_amount
# 		frappe.errprint(calculated_amount)
# 		if calculated_amount > gross :
# 			frappe.throw(_('Loan amount must be Greater than Employee Gratuity'))
		
# 	# Calculate the loan amount plus the calculated interest
		

# @frappe.whitelist()
# def get_sales_person_invoice(name):
# 	data = "<table  width = 100% border= 1px solid black><tr style= background-color:#4682B4 ; ><td colspan = 1  width = 10 ><b style = color:white ; text-align:center;>SL.NO</b></td><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;>Date</b></td><td colspan = 1 width=10 style = color:white ><b style = color:white ; text-align:center;>Invoice Number</b></td><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;>Customer Name</b></td><td colspan = 1 width= 10 style = color:white><b style = color:white ; text-align:center;>LPO NO</b><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;>Gross Amount</b></td><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;>Discount</b></td><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;> Ret.Amount</b></td><td width=10 style = color:white><b style = color:white ; text-align:center;>Net</b></td><td colspan = 1 width=5 style = color:white><b style = color:white ; text-align:center;> Collected </b></td><td colspan = 1 width=5 style = color:white><b style = color:white ; text-align:center;>Balance</b></td></tr>"
# 	sales_person = frappe.get_all("Sales Person",fields=["name"])
# 	for s in sales_person:
# 		# print(s.name)
# 		data += '<tr><td colspan = 11 style="border: 1px solid black; background-color:#EBF4FA" ><b style= color:"red">%s</b></td></tr>'%(s.name)
# 		sales_invoice = frappe.get_all("Sales Invoice",{"sales_person_user":s.name,"is_return":0},["name","customer","total","discount_amount","posting_date","outstanding_amount","po_no"])
# 		j=1
# 		for i in sales_invoice:
# 			net = (i.total - i.discount_amount)
# 			net_int = int(net)
# 			net_amount = (i.total - net)
# 			convert_float = int(net_amount)
# 			print(net)

# 			collected = (net - i.outstanding_amount)
# 			collected_int = int(collected)
# 			# data += "<tr><td rowspan = '%s' >%s</td><td>%s</td></tr>"%(emp_name_len,i['project_name'],i['employee_name'][0])
# 			data += '<tr><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan=1 style="border:1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td></tr>'%(j,i.posting_date,i.name,i.customer,i.po_no,i.total,i.discount_amount,convert_float,net_int,collected_int,i.outstanding_amount)
# 			# print(i.name,i.customer,i.grand_total,i.discount_amount)

# 			j += 1
# 	data += '</table>'
# 	return data
@frappe.whitelist()
def get_accounts_ledger(doc):
	total_amount = 0
	total_paid = 0
	total_credit_note = 0
	total_outstanding = 0
	total_0_30 = 0
	total_31_60 = 0
	total_61_90 = 0
	total_91_above = 0
	sales_invoices = frappe.get_all("Sales Invoice", {'company': doc.company, 'customer': doc.customer}, ['posting_date', 'name', 'total', 'outstanding_amount'])
	if sales_invoices:
		data = "<table width=100% border=1px solid black><tr style=background-color:#e35310;font-size:8px><td colspan=1 ><b style=color:white; text-align:center;width:320px>Invoice No</b></td><td colspan=2  style=color:white><b style=color:white; text-align:center;>Date</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Age</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Amount QR</b></td><td colspan=1 style=color:white><b style=color:white; text-align:center;>Paid QR</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Credit Note QR</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Outstanding QR</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>0-30</b></td><td  style=color:white><b style=color:white; text-align:center;>31-60</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>61-90</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>91-Above</b></td></tr>"
		for i in sales_invoices:
			days = date_diff(doc.from_date, i.posting_date)
			if 0 <= days <= 120:
				total_amount += i.total
				total_outstanding += i.outstanding_amount
				data += f'<tr><td colspan=1 style="border: 1px solid black; font-size:8px" >{i.name}</td><td colspan=2 style="border: 1px solid black; font-size:8px" >{i.posting_date}</td><td colspan=1 style="border: 1px solid black; font-size:8px" >{days}</td><td colspan=1 style="border: 1px solid black; font-size:8px" >{i.total}</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >{i.outstanding_amount}</td>'
				if 0 <= days <= 30:
					total_0_30 += i.total
					data += f'<td colspan=1 style="border: 1px solid black; font-size:8px" >{i.total}</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td>'
				if 31 <= days <= 60:
					total_31_60 += i.total
					data += f'<td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >{i.total}</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td>'
				if 61 <= days <= 90:
					total_61_90 += i.total
					data += f'<td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >{i.total}</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td>'
				if 91 <= days <= 120:
					total_91_above += i.total
					data += f'<td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >-</td><td colspan=1 style="border: 1px solid black; font-size:8px" >{i.total}</td>'					
		data += '</tr>'
		data += f'<tr><td colspan=4 style="border: 1px solid black; font-size:8px" >Total</td><td style="border: 1px solid black; font-size:8px" >{total_amount}</td><td style="border: 1px solid black; font-size:8px" >-</td><td style="border: 1px solid black; font-size:8px" >-</td><td style="border: 1px solid black; font-size:8px" >{total_outstanding}</td><td style="border: 1px solid black; font-size:8px" >{total_0_30}</td><td style="border: 1px solid black; font-size:8px" >{total_31_60}</td><td style="border: 1px solid black; font-size:8px" >{total_61_90}</td><td style="border: 1px solid black; font-size:8px" >{total_91_above}</td></tr>'
		data += '</table>'
	else:
		data = "<table width=100% border=1px solid black><tr style=background-color:#e35310;font-size:10px;text-align:center><td colspan=1 ><b style=color:white; text-align:center;width:320px>Sales Invoice Documents Not Avaliable</b></td></tr>"

	return data


@frappe.whitelist()
def get_sales_person(doc, name, from_date, to_date, company, sales_person_user):
	data = "<table width=100% border=1px solid black><tr style=background-color:#4682B4;font-size:8px><td colspan=1 ><b style=color:white; text-align:center;width:320px>SL.NO</b></td><td colspan=2  style=color:white><b style=color:white; text-align:center;>Date</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Invoice Number</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Customer Name</b></td><td colspan=1 style=color:white><b style=color:white; text-align:center;>LPO NO</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Gross Amount</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Discount</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Ret. Amount</b></td><td  style=color:white><b style=color:white; text-align:center;>Net</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Collected</b></td><td colspan=1  style=color:white><b style=color:white; text-align:center;>Balance</b></td></tr>"

	if not doc.company_multiselect and not sales_person_user:
		sales_person = frappe.get_all("Sales Person", fields=["name"])
		j = 1
		for s in sales_person:
			company_set = set()
			prev_company_name = None
			sales = frappe.get_all("Sales Invoice", {"is_return": 0, 'posting_date': ('between', (from_date, to_date)), 'sales_person_user': s.name}, ["name", "customer", "total", "discount_amount", "posting_date", "outstanding_amount", "po_no", "company"])
			company_totals = {}  
			salesperson_totals = {} 

			if sales:
				data += '<tr><td colspan=12 style="border: 1px solid black; background-color:#EBF4FA; font:size:8px" ><b style=color:"red">%s</b></td></tr>' % (s.name)

			for i in sales:
				company_name = i["company"]
				if company_name not in company_set:
					if prev_company_name:
						data += f'<tr style = font-size:8px><td colspan=6 style="border: 1px solid black"><b>Total for {prev_company_name}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["discount_amount"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["convert_float"]}</b></td><td style="border: 1px solid black"><b>{company_totals[prev_company_name]["net_total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["collected_total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["balance"]}</b></td></tr>'

					data += f'<tr><td colspan=12 style="border: 1px solid black; background-color:#EBF4FA;font-size:8px" ><b style=color:"red">{company_name}</b></td></tr>'
					prev_company_name = company_name
					company_set.add(company_name)

				net = (i.total - i.discount_amount)
				net_int = int(net)
				net_amount = (i.total - net)
				convert_float = int(net_amount)
				collected = (net - i.outstanding_amount)
				collected_int = int(collected)

				data += f'<tr style=font-size:8px width:100 height:50><td colspan=1 style="border: 1px solid black">{j}</td>'
				data += f'<td colspan=2 style="border: 1px solid black" nowrap>{i.posting_date}</td>'
				data += f'<td colspan=1 style="border: 1px solid black" nowrap>{i.name}</td>'
				data += f'<td colspan=1 style="border: 1px solid black">{i.customer}</td>'
				data += f'<td colspan=1 style="border: 1px solid black">{i.po_no}</td>'
				data += f'<td colspan=1 style="border: 1px solid black">{i.total}</td>'
				data += f'<td colspan=1 style="border: 1px solid black">{i.discount_amount}</td>'
				data += f'<td colspan=1 style="border: 1px solid black">{convert_float}</td>'
				data += f'<td style="border: 1px solid black">{net_int}</td>'
				data += f'<td colspan=1 style="border: 1px solid black">{collected_int}</td>'
				data += f'<td colspan=1 style="border: 1px solid black">{i.outstanding_amount}</td></tr>'

	
				if company_name not in company_totals:
					company_totals[company_name] = {
						"total": i.total,
						"discount_amount": i.discount_amount,
						"net_total": net_int,
						"convert_float": convert_float,
						"collected_total": collected_int,
						"balance": i.outstanding_amount
					}
				else:
					company_totals[company_name]["total"] += i.total
					company_totals[company_name]["discount_amount"] += i.discount_amount
					company_totals[company_name]["net_total"] += net_int
					company_totals[company_name]["convert_float"] += convert_float
					company_totals[company_name]["collected_total"] += collected_int
					company_totals[company_name]["balance"] += i.outstanding_amount

				
				if s.name not in salesperson_totals:
					salesperson_totals[s.name] = {
						"total": i.total,
						"discount_amount": i.discount_amount,
						"net_total": net_int,
						"convert_float": convert_float,
						"collected_total": collected_int,
						"balance": i.outstanding_amount
					}
				else:
					salesperson_totals[s.name]["total"] += i.total
					salesperson_totals[s.name]["discount_amount"] += i.discount_amount
					salesperson_totals[s.name]["net_total"] += net_int
					salesperson_totals[s.name]["convert_float"] += convert_float
					salesperson_totals[s.name]["collected_total"] += collected_int
					salesperson_totals[s.name]["balance"] += i.outstanding_amount

				j += 1

			if prev_company_name:
				
				data += f'<tr style = font-size:8px><td colspan=6 style="border: 1px solid black"><b>Total for {prev_company_name}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["discount_amount"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["convert_float"]}</b></td><td style="border: 1px solid black"><b>{company_totals[prev_company_name]["net_total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["collected_total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{company_totals[prev_company_name]["balance"]}</b></td></tr>'

			prev_company_name = None

			
			if s.name in salesperson_totals:
				data += f'<tr style= font-size:8px><td colspan=6 style="border: 1px solid black"><b>Total for {s.name}</b></td><td colspan=1 style="border: 1px solid black"><b>{salesperson_totals[s.name]["total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{salesperson_totals[s.name]["discount_amount"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{salesperson_totals[s.name]["convert_float"]}</b></td><td style="border: 1px solid black"><b>{salesperson_totals[s.name]["net_total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{salesperson_totals[s.name]["collected_total"]}</b></td><td colspan=1 style="border: 1px solid black"><b>{salesperson_totals[s.name]["balance"]}</b></td></tr>'
  
	elif not doc.company_multiselect and sales_person_user:
		company = frappe.get_all("Company", fields=["name"])
		data += f'<tr><td colspan="12" style="border: 1px solid black; background-color:#EBF4FA"><b style="color:black;font-size:8px">{sales_person_user}</b></td></tr>'
		all_companies_total = {
			"total": 0,
			"discount_amount": 0,
			"convert_float": 0,
			"net_total": 0,
			"collected_total": 0,
			"balance": 0
		}

		for c in company:
			sales_invoice = frappe.get_all("Sales Invoice", {"sales_person_user": sales_person_user, "is_return": 0, 'posting_date': ('between', (from_date, to_date)), 'company': c.name}, ["name", "customer", "total", "discount_amount", "posting_date", "outstanding_amount", "po_no"])
			if sales_invoice:
				data += f'<tr><td colspan="12" style="border: 1px solid black; background-color:#EBF4FA"><b style="color:black;font-size:8px" height:25%>{c.name}</b></td></tr>'
				j = 1
				company_totals = {}
				
				for i in sales_invoice:
					net = (i.total - i.discount_amount)
					net_int = int(net)
					net_amount = (i.total - net)
					convert_float = int(net_amount)
					collected = (net - i.outstanding_amount)
					collected_int = int(collected)
					data += f'<tr style = font-size:8px><td colspan="1" style="border: 1px solid black;" height:25%>{j}</td>'
					data += f'<td colspan="2" style="border: 1px solid black;" height:25% nowrap>{i.posting_date}</td>'
					data += f'<td colspan="1" style="border: 1px solid black;" height:25%>{i.name}</td>'
					data += f'<td colspan="1" style="border: 1px solid black;" height:25%>{i.customer}</td>'
					data += f'<td colspan="1" style="border: 1px solid black;" height:25%>{i.po_no}</td>'
					data += f'<td colspan="1" style="border: 1px solid black;" height:25%>{i.total}</td>'
					data += f'<td colspan="1" style="border: 1px solid black;" height:25%>{i.discount_amount}</td>'
					data += f'<td colspan="1" style="border: 1px solid black;" height:25%>{convert_float}</td>'
					data += f'<td style="border: 1px solid black;">{net_int}</td>'
					data += f'<td colspan="1" style="border: 1px solid black;">{collected_int}</td>'
					data += f'<td colspan="1" style="border: 1px solid black;">{i.outstanding_amount}</td></tr>'
					if c.name not in company_totals:
						company_totals[c.name] = {
							"total": i.total,
							"discount_amount": i.discount_amount,
							"net_total": net_int,
							"convert_float": convert_float,
							"collected_total": collected_int,
							"balance": i.outstanding_amount
						}
					else:
						company_totals[c.name]["total"] += i.total
						company_totals[c.name]["discount_amount"] += i.discount_amount
						company_totals[c.name]["net_total"] += net_int
						company_totals[c.name]['convert_float'] += convert_float
						company_totals[c.name]["collected_total"] += collected_int
						company_totals[c.name]['balance'] += i.outstanding_amount
					j += 1
				data += f'<tr style = font-size:8px>'
				data += f'<td colspan="6" style="border: 1px solid black;"><b>Total for {c.name}</b></td>'
				data += f'<td colspan="1" style="border: 1px solid black;"><b>{company_totals[c.name].get("total", 0)}</b></td>'
				data += f'<td colspan="1" style="border: 1px solid black;"><b>{company_totals[c.name].get("discount_amount", 0)}</b></td>'
				data += f'<td colspan="1" style="border: 1px solid black;"><b>{company_totals[c.name].get("convert_float", 0)}</b></td>'
				data += f'<td style="border: 1px solid black;"><b>{company_totals[c.name].get("net_total", 0)}</b></td>'
				data += f'<td colspan="1" style="border: 1px solid black;"><b>{company_totals[c.name].get("collected_total", 0)}</b></td>'
				data += f'<td colspan="1" style="border: 1px solid black;"><b>{company_totals[c.name].get("balance", 0)}</b></td></tr>'

				all_companies_total["total"] += company_totals[c.name].get("total", 0)
				all_companies_total["discount_amount"] += company_totals[c.name].get("discount_amount", 0)
				all_companies_total["convert_float"] += company_totals[c.name].get("convert_float", 0)
				all_companies_total["net_total"] += company_totals[c.name].get("net_total", 0)
				all_companies_total["collected_total"] += company_totals[c.name].get("collected_total", 0)
				all_companies_total["balance"] += company_totals[c.name].get("balance", 0)
		data += f'<tr style =font-size:8px>'
		data += f'<td colspan="6" style="border: 1px solid black;"><b>Total for {sales_person_user}</b></td>'
		data += f'<td colspan="1" style="border: 1px solid black;"><b>{all_companies_total["total"]}</b></td>'
		data += f'<td colspan="1" style="border: 1px solid black;"><b>{all_companies_total["discount_amount"]}</b></td>'
		data += f'<td colspan="1" style="border: 1px solid black;"><b>{all_companies_total["convert_float"]}</b></td>'
		data += f'<td style="border: 1px solid black;"><b>{all_companies_total["net_total"]}</b></td>'
		data += f'<td colspan="1" style="border: 1px solid black;"><b>{all_companies_total["collected_total"]}</b></td>'
		data += f'<td colspan="1" style="border: 1px solid black;"><b>{all_companies_total["balance"]}</b></td>'
		data += '</tr>'

		
	elif doc.company_multiselect and not sales_person_user:
		for c in doc.company_multiselect:
			company_name_printed = False
			company_totals = {
				"total": 0,
				"discount_amount": 0,
				"convert_float": 0,
				"net_total": 0,
				"collected_total": 0,
				"balance": 0
			}
			
			sales_person = frappe.get_all("Sales Person", fields=["name"])
			for s in sales_person:
				sales_invoice = frappe.get_all("Sales Invoice", {"sales_person_user": s.name, "is_return": 0, 'posting_date': ('between', (from_date, to_date)), 'company': c.company}, ["name", "customer", "total", "discount_amount", "posting_date", "outstanding_amount", "po_no"])
				j = 1

				if sales_invoice:
					data += '<tr style =font-size:8px><td colspan="12" style="border: 1px solid black; background-color:#EBF4FA"><b style="color:black">%s</b></td></tr>' % (s.name)
					if not company_name_printed:
						data += '<tr style =font-size:8px><td colspan="12" style="border: 1px solid black; background-color:#EBF4FA"><b style="color:black">%s</b></td></tr>' % (c.company)
						company_name_printed = True

					sales_person_totals = {
						"total": 0,
						"discount_amount": 0,
						"convert_float": 0,
						"net_total": 0,
						"collected_total": 0,
						"balance": 0
					}

					for i in sales_invoice:
						net = (i.total - i.discount_amount)
						net_int = int(net)
						net_amount = (i.total - net)
						convert_float = int(net_amount)
						collected = (net - i.outstanding_amount)
						collected_int = int(collected)
						data += '<tr style =font-size:8px><td colspan="1" style="border: 1px solid black">%s</td><td colspan="2" style="border: 1px solid black" nowrap>%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td></tr>' % (j, i.posting_date, i.name, i.customer, i.po_no, i.total, i.discount_amount, convert_float, net_int, collected_int, i.outstanding_amount)
						j += 1
						sales_person_totals["total"] += i.total
						sales_person_totals["discount_amount"] += i.discount_amount
						sales_person_totals["convert_float"] += convert_float
						sales_person_totals["net_total"] += net_int
						sales_person_totals["collected_total"] += collected_int
						sales_person_totals["balance"] += i.outstanding_amount
						
						company_totals["total"] += i.total
						company_totals["discount_amount"] += i.discount_amount
						company_totals["convert_float"] += convert_float
						company_totals["net_total"] += net_int
						company_totals["collected_total"] += collected_int
						company_totals["balance"] += i.outstanding_amount

					data += '<tr style =font-size:8px><td colspan="6" style="border: 1px solid black"><b>Total for %s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td></tr>' % (s.name, sales_person_totals["total"], sales_person_totals["discount_amount"], sales_person_totals["convert_float"], sales_person_totals["net_total"], sales_person_totals["collected_total"], sales_person_totals["balance"])
		
			data += '<tr style =font-size:8px><td colspan="6" style="border: 1px solid black"><b>Total for %s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td></tr>' % (c.company, company_totals["total"], company_totals["discount_amount"], company_totals["convert_float"], company_totals["net_total"], company_totals["collected_total"], company_totals["balance"])

	else:
		salesperson_totals = {
			"total": 0,
			"discount_amount": 0,
			"convert_float": 0,
			"net_total": 0,
			"collected_total": 0,
			"balance": 0
		}
		
		for c in doc.company_multiselect:
			company_name_printed = False
			company_totals = {
				"total": 0,
				"discount_amount": 0,
				"convert_float": 0,
				"net_total": 0,
				"collected_total": 0,
				"balance": 0
			}
			
			sales_invoice = frappe.get_all("Sales Invoice", {"sales_person_user": sales_person_user, "is_return": 0, 'posting_date': ('between', (from_date, to_date)), 'company': c.company}, ["name", "customer", "total", "discount_amount", "posting_date", "outstanding_amount", "po_no"])
			j = 1
			
			if sales_invoice:
				if not company_name_printed:
					data += '<tr style =font-size:8px><td colspan="12" style="border: 1px solid black; background-color:#EBF4FA"><b style="color:black">%s</b></td></tr>' % (c.company)
					company_name_printed = True
				
				data += '<tr style =font-size:8px><td colspan="12" style="border: 1px solid black; background-color:#EBF4FA"><b style="color:black">%s</b></td></tr>' % (sales_person_user)
				
				for i in sales_invoice:
					net = (i.total - i.discount_amount)
					net_int = int(net)
					net_amount = (i.total - net)
					convert_float = int(net_amount)
					collected = (net - i.outstanding_amount)
					collected_int = int(collected)
					data += '<tr style =font-size:8px><td colspan="1" style="border: 1px solid black">%s</td><td colspan="2" style="border: 1px solid black" nowrap>%s</td><td colspan="1" style="border: 1px solid black" nowrap>%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td><td colspan="1" style="border: 1px solid black">%s</td></tr>' % (j, i.posting_date, i.name, i.customer, i.po_no, i.total, i.discount_amount, convert_float, net_int, collected_int, i.outstanding_amount)
					j += 1

					company_totals["total"] += i.total
					company_totals["discount_amount"] += i.discount_amount
					company_totals["convert_float"] += convert_float
					company_totals["net_total"] += net_int
					company_totals["collected_total"] += collected_int
					company_totals["balance"] += i.outstanding_amount
				
				data += '<tr style =font-size:8px><td colspan="6" style="border: 1px solid black"><b>Total for %s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td></tr>' % (c.company, company_totals["total"], company_totals["discount_amount"], company_totals["convert_float"], company_totals["net_total"], company_totals["collected_total"], company_totals["balance"])
				
				salesperson_totals["total"] += company_totals["total"]
				salesperson_totals["discount_amount"] += company_totals["discount_amount"]
				salesperson_totals["convert_float"] += company_totals["convert_float"]
				salesperson_totals["net_total"] += company_totals["net_total"]
				salesperson_totals["collected_total"] += company_totals["collected_total"]
				salesperson_totals["balance"] += company_totals["balance"]
		
		data += '<tr style =font-size:8px><td colspan="6" style="border: 1px solid black"><b>Total for %s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td><td colspan="1" style="border: 1px solid black"><b>%s</b></td></tr>' % (sales_person_user, salesperson_totals["total"], salesperson_totals["discount_amount"], salesperson_totals["convert_float"], salesperson_totals["net_total"], salesperson_totals["collected_total"], salesperson_totals["balance"])
		
	data += '</table>'
	return data

@frappe.whitelist()
def get_items(doc):
	data = "<table  width = 100% border= 1px solid black><tr style= background-color:#e35310; ><td colspan = 1  width = 10 ><b style = color:white ; text-align:center;>S.No</b></td><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;>Item Code</b></td><td colspan = 1 width=10 style = color:white ><b style = color:white ; text-align:center;>Description</b></td><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;>Quantity</b></td><td colspan = 1 width= 10 style = color:white><b style = color:white ; text-align:center;>Unit</b><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;>Rate</b></td><td colspan = 1 width=10 style = color:white><b style = color:white ; text-align:center;>Amount</b></td></tr>"
	j=1
	for i in doc.items:
		list_item = []
		designation = frappe.db.get_list("Designation",['name'])
		for k in designation:
			list_item.append(k.name)
		if i.item_code not in list_item:
		# for j in designation:
			# if i.item_code != j.name:
			data += '<tr><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan=1 style="border:1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td><td colspan = 1 style="border: 1px solid black">%s</td></tr>'%(j,i.item_code,i.description,i.qty,i.uom,i.rate,i.amount)
			j+=1
	data += '</table>'
	return data


@frappe.whitelist()
def get_items_list():
	list_item = []
	designation = frappe.db.get_list("Designation",['name'])
	for i in designation:
		list_item.append(i.name)
	print(list_item)



@frappe.whitelist()
def calculate_abs_detec(days,pd,gross):
	import datetime
	specific_date = datetime.datetime.strptime(pd, "%Y-%m-%d").date()
	# first_day_current_month = datetime.date(specific_date.year, specific_date.month, 1)
	# first_day_previous_month = first_day_current_month - datetime.timedelta(days=1)
	# previous_month_num_days = first_day_previous_month.day
	per_day_amount = int(gross) / 30
	tot_amount = float(per_day_amount) * float(days)
	return int(tot_amount)

@frappe.whitelist()
def calculate_add(days,pd,gross):
	import datetime
	import calendar
	# specific_date = datetime.datetime.strptime(pd, "%Y-%m-%d").date()
	# first_day_current_month = datetime.date(specific_date.year, specific_date.month, 1)
	# last_day = calendar.monthrange(first_day_current_month.year, first_day_current_month.month)[1]
	per_day_amount = int(gross) / int(30)
	tot_amount = float(per_day_amount) * float(days)
	frappe.errprint(tot_amount)
	return int(tot_amount)


@frappe.whitelist()
def calculate_hot(hours,gross):
	amount = (int(gross)/(240)) * int(hours) * 1.5
	# frappe.errprint(amount)
	return round(amount)

@frappe.whitelist()
def calculate_not(hours,gross):
	amount = (int(gross)/(240)) * float(hours) * 1.25
	# frappe.errprint(amount)
	return round(amount)

@frappe.whitelist()
def take_po():
	po = frappe.db.get_list("Purchase Order",{"supplier":"AFFIX SCAFFOLDING WLL.","docstatus":1},['name'])
	for i in po:
		pi_item = frappe.get_value("Purchase Invoice Item",{"purchase_order":i.name},['parent'])
		if not pi_item:
			print(i.name)

import frappe
from datetime import datetime
from dateutil import relativedelta

@frappe.whitelist()
def check_loan_amount(doc,method):
	# Get the employee's basic amount
	basic_amount = frappe.db.get_value('Employee', doc.applicant, 'basic')
	print(basic_amount)
	employees = frappe.get_all('Employee', {'status': 'Active'}, ['name', 'employee_name', 'date_of_joining'])
	for emp in employees:
		date_2 = datetime.now()
		# Get the interval between two dates
		diff = relativedelta.relativedelta(date_2, emp.date_of_joining)
		yos = str(diff.years) + ' years, ' + str(diff.months) + ' months and ' + str(diff.days) + ' days'
		exp_years = diff.years
		exp_month = diff.months
		exp_days = diff.days
		total_days = (exp_years * 365) + (exp_month * 30) + exp_days
		print(total_days)
		per_day_basic = (float(basic_amount) / 30 * 21) / 365
		total_gratuity = per_day_basic * total_days
		gratuity = (total_gratuity * 80 /100)
	frappe.errprint(gratuity)
	# Convert loan_amount and interest_rate to appropriate numeric types
	loan_amount = float(doc.loan_amount)
	interest_rate = int(doc.rate_of_interest)

	# Calculate the loan amount plus the calculated interest
	calculated_amount = loan_amount
	frappe.errprint(calculated_amount)

	# Check if the calculated amount exceeds the basic amount
	
	if calculated_amount > gratuity :
		if doc.loan_type in ["Loan Against Gratuity","Loan Against Gratuity_2","Loan Against Gratuity_3"] :
			frappe.throw(_('Loan amount must be Greater than Employee Gratuity'))

	elif doc.loan_type in ["Loan Against Leave  Settlement_1","Loan Against Leave  Settlement","Loan Against Leave  Settlement_2" ]:
		gross = frappe.db.get_value('Employee', doc.applicant, 'gross_salary')
		frappe.errprint(gross)
		loan_amount = float(doc.loan_amount)
		calculated_amount = loan_amount
		frappe.errprint(calculated_amount)
		if calculated_amount > gross :
			frappe.throw(_('Loan amount must be Greater than Employee Gross'))   

	   


@frappe.whitelist()
def pen_consolidated_req(name):
	con = frappe.db.sql(""" select * from `tabPurchase Invoice List` where parent = '%s' """%(name),as_dict=True)
	def calculate_outstanding_payment_difference(child_table):
		amounts_by_company = defaultdict(float)
		for row in child_table:
			company = row.get("company", "")
			outstanding_amount = row.get("outstanding_amount", 0.0)
			payment_amount = row.get("payment_amount", 0.0)
			amounts_by_company[company] += (outstanding_amount - payment_amount)
		result = []
		data = '<table width="100%"><tr><td style="color:white;background-color:#e35310;padding:1px;font-weight:bold;border:1px solid black">Company</td><td style="font-weight:bold;color:white;background-color:#e35310;padding:1px;border:1px solid black">Amount</td></tr>'
		for company, difference in amounts_by_company.items():
			result.append({"company": company, "value": difference})

		for item in result:
			data += '<tr><td style="padding:1px;border:1px solid black">{}</td><td style="padding:1px;border:1px solid black">{}</td></tr>'.format(item["company"], item["value"])

		data += '</table>'

		return data

	child_table = con
	amounts_difference_by_company = calculate_outstanding_payment_difference(child_table)
	return amounts_difference_by_company



@frappe.whitelist()
def pay_consolidated_req(name):
	con = frappe.db.sql("""SELECT * FROM `tabPurchase Invoice List` WHERE parent = '%s' """ % (name), as_dict=True)

	def calculate_outstanding_payment_difference(child_table):
		amounts_by_company = defaultdict(float)
		total = 0.0

		for row in child_table:
			company = row.get("company", "")
			outstanding_amount = row.get("outstanding_amount", 0.0)
			payment_amount = row.get("payment_amount", 0.0)
			amounts_by_company[company] += payment_amount
			total += payment_amount

		result = []

		for company, difference in amounts_by_company.items():
			result.append({"company": company, "value": difference})

		# Append the total row to the result
		result.append({"company": "Total", "value": total})

		data = ''
		data += '<table width="61%"><tr><td style="color:white;background-color:#e35310;padding:1px;font-weight:bold;border: 1px solid black">Company</td><td style="font-weight:bold;color:white;background-color:#e35310;padding:1px;border: 1px solid black">Amount</td></tr>'

		for i in result:
			formatted_value = '{:,.2f}'.format(i["value"])
			data += '<tr><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td></tr>' % (i["company"],formatted_value)

		data += '</table>'
		return data

	child_table = con
	amounts_difference_by_company = calculate_outstanding_payment_difference(child_table)
	return amounts_difference_by_company


@frappe.whitelist()
def check_for_duplicate_payment(name,doc_type,doc_name):
	li = []
	dat = frappe.get_value(doc_type,name,["grand_total"])
	pos = frappe.db.sql("""select sum(`tabPurchase Invoice List`.payment_amount) as payment_amount,`tabPurchase Invoice List`.parent as name from `tabConsolidated Payment Request`
	left join `tabPurchase Invoice List` on `tabConsolidated Payment Request`.name = `tabPurchase Invoice List`.parent
	where `tabPurchase Invoice List`.name1 = '%s' """%(name),as_dict=True)[0]
	po = frappe.db.sql("""select `tabPurchase Invoice List`.parent as name from `tabConsolidated Payment Request`
	left join `tabPurchase Invoice List` on `tabConsolidated Payment Request`.name = `tabPurchase Invoice List`.parent
	where `tabPurchase Invoice List`.name1 = '%s' and `tabConsolidated Payment Request`.docstatus = 0 """%(name),as_dict=True)
	for i in po:
		if i.name != doc_name:
			li.append(i.name)
	if not pos["payment_amount"]:
		pos["payment_amount"] = 0
	return pos["payment_amount"] or 0,li,dat or 0



from frappe.utils import cstr, cint, getdate,get_first_day, get_last_day, today
@frappe.whitelist()
def get_payroll_date():
	date = datetime.strptime(today(), '%Y-%m-%d').date()
	if date.day > 15:
		payroll_date = add_days(get_first_day(add_months(date,0)),0)
		return payroll_date
	else:
		payroll_date = add_days(get_first_day(add_months(date,-1)),0)
		return payroll_date


@frappe.whitelist()
def le():
	sale = frappe.db.sql("""SELECT sales_person_user,COUNT(*) AS document_count FROM (SELECT sales_person_user FROM `tabQuotation` WHERE sales_person_user = 'Rinshad Chithuparambu Mohammedunni' and status != 'Cancelled' UNION ALL SELECT sales_person_user FROM `tabSales Order` WHERE sales_person_user = 'Rinshad Chithuparambu Mohammedunni'and status != 'Cancelled') AS combined_sales GROUP BY sales_person_user;""",as_dict=True)
	print(sale)

@frappe.whitelist()
def update_ctc():
	employee_id= frappe.db.sql("""select * from `tabEmployee` where status = 'Active' """,as_dict=1)
	for t in employee_id:
		print(t.basic)
		ctc = t.basic + t.hra + t._other_allowance + t.accommodation + t.transportation + t.mobile_allowance + t.air_ticket_allowance_ + t.medical_renewal + t.visa_cost_ + t.qid_cost + t.gratuity + t.medical_allowance_ + t.leave_salary + t.compensationemployee_insurence
		print(ctc)
		print(t.name)
		t.ctc = ctc
		emp = frappe.db.sql("""update `tabEmployee`set ctc = '%s' where status = 'Active' """%(ctc),as_dict=1)


@frappe.whitelist()
def return_total_amt(from_date,to_date,account):
	acct = account.split(' - ')
	if len(acct) == 2:
		acc = acct[0]
	if len(acct) == 3:
		acc = acct[1]
	ac = '%'+acc+'%'
	data = '<table  border= 1px solid black width = 100%>'
	data += '<tr style = "background-color:#D9E2ED"><td colspan =1><b></b></td><td colspan =2 style = "text-align:center"><b>Opening</b></td><td colspan =2 style = "text-align:center"><b>Movement</b></td><td colspan =2 style = "text-align:center"><b>Closing</b></td></tr>'

	data += '<tr style = "background-color:#e35310;color:white"><td  style = "text-align:center;font-weight:bold;color:white">Company</td><td  style = "text-align:center;font-weight:bold;color:white">Debit</td><td  style = "text-align:center;font-weight:bold;color:white">Credit</td><td  style = "text-align:center;font-weight:bold;color:white">Debit</td><td  style = "text-align:center;font-weight:bold;color:white">Credit</td><td  style = "text-align:center;font-weight:bold;color:white">Debit</td><td  style = "text-align:center;font-weight:bold;color:white">Credit</td></tr>'
	op_credit = 0
	op_debit = 0
	total_op_debit = 0
	total_op_credit = 0
	t_c_credit = 0
	t_p_credit = 0
	t_c_debit = 0
	t_p_debit = 0
	li = []
	company = frappe.db.sql(""" select name from `tabCompany` where is_group = 1""",as_dict=1)
	for com in company:
		li.append(com.name)
		comp = frappe.db.get_list("Company",{"parent_company":com.name},['name'])
		for j in comp:
			li.append(j.name)
	for c in li:
		gle = frappe.db.sql("""select account, sum(debit) as opening_debit, sum(credit) as opening_credit from `tabGL Entry` where company = '%s'	and (posting_date < '%s' or (ifnull(is_opening, 'No') = 'Yes' and posting_date >= '%s')) and account like '%s' and is_cancelled = 0  """%(c,from_date,to_date,ac),as_dict=True)
		for g in gle:
			if not g.opening_debit:
				g.opening_debit = 0
			if not g.opening_credit:
				g.opening_credit = 0
			t_p_debit += g.opening_debit
			t_p_credit += g.opening_credit
			balance_op = t_p_debit - t_p_credit
			data += '<tr><td>%s</td><td style = text-align:right >%s</td><td style = text-align:right >%s</td>'%(c,fmt_money(g.opening_debit, currency="QAR"),fmt_money(g.opening_credit, currency="QAR"))
			
			sq = frappe.db.sql(""" select company,sum(debit_in_account_currency) as debit,sum(credit_in_account_currency) as credit from `tabGL Entry` where company = '%s' and account like '%s' and posting_date between '%s' and '%s' and is_opening = 'No' and is_cancelled = 0 """%(c,ac,from_date,to_date),as_dict=True)
			for i in sq:
				if not i.credit:
					i.credit = 0
				if not i.debit:
					i.debit = 0
				op_credit = g.opening_credit + i.credit
				op_debit = g.opening_debit + i.debit
				total_op_debit += i.debit
				total_op_credit += i.credit
				t_c_credit += op_credit
				t_c_debit += op_debit
				balance_cl = t_c_debit - t_c_credit
				data += '<td style = text-align:right >%s</td><td style = text-align:right >%s</td><td style = text-align:right >%s</td><td style = text-align:right >%s</td></tr>'%(fmt_money(i.debit, currency="QAR"),fmt_money(i.credit, currency="QAR"),fmt_money(op_debit, currency="QAR"),fmt_money(op_credit, currency="QAR"))
	data += '<tr style = "text-align:right;font-weight:bold"><td style = "text-align:center;font-weight:bold">Total</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'%(fmt_money(t_p_debit, currency="QAR"),fmt_money(t_p_credit, currency="QAR"),fmt_money(total_op_debit, currency="QAR"),fmt_money(total_op_credit, currency="QAR"),fmt_money(t_c_debit, currency="QAR"),fmt_money(t_c_credit, currency="QAR"))
	data += '<tr style = "text-align:right;font-weight:bold"><td style = "text-align:center;font-weight:bold">Balance</td><td colspan =2>%s</td><td colspan =2></td><td colspan=2>%s</td></tr>'%(fmt_money(balance_op, currency="QAR"),fmt_money(balance_cl, currency="QAR"))
	data += '</table>'
	return data

@frappe.whitelist()
def pb_update_status():
	pb = frappe.db.sql("""update `tabProject Budget` set docstatus = 0 where name = 'INT-PB-2023-00006-2'  """,as_dict=1)


@frappe.whitelist()
def comp():
	acc = ''
	account = "FUEL EXPENSE - ASTCC"
	acct = account.split(' - ')
	if len(acct) == 2:
		acc = acct[0]
	if len(acct) == 3:
		acc = acct[1]
	print(acc)

@frappe.whitelist()
def get_name_pb(so):
	sale = frappe.get_doc("Sales Order",so)
	return sale.items


# @frappe.whitelist()
# def get_st_name():
# 	name = "SHBW-STI-2023-00037"
# 	si = frappe.get_doc("Sales Invoice",name)
# 	for i in si.items:
# 		count = i.idx
# 		# print(count)
# 		vs = name.split('-')[0]
# 		filt = '%'+vs+'%'
# 		st = frappe.db.get_all("Stock Transfer",{'name': ['like', filt]},['name'])
# 		for j in st:
# 			sto = frappe.get_doc("Stock Transfer",j.name)
# 			for k in sto.items:
# 				cnt = k.idx
# 			if cnt == count:
# 				pass
# 				# print(j.name)
# 			for a in sto.items:
# 				if a.item_code == i.item_code:
# 					print(j.name)
# 	# print(st)



@frappe.whitelist()
def set_stock_qty():
	stock = frappe.db.sql(""" select sales_person_user,sum(grand_total) as total from `tabSales Invoice` where posting_date between '%s' and '%s'  group by sales_person_user """%("2023-01-01","2023-12-31"),as_dict=1)
	print(stock)



@frappe.whitelist()
def get_st_qty():
	item = "122-31P090BL"
	# count = frappe.db.sql(""" select sum(actual_qty) as sum from `tabStock Ledger Entry` where item_code = '%s' and company = 'ELECTRA - BARWA SHOWROOM' and posting_date between '%s' and '%s' group by item_code """%(item,"2023-01-01","2023-07-01"),as_dict=1)[0]
	coun = frappe.db.sql(""" select sum(actual_qty) as sum from `tabStock Ledger Entry` where item_code = '%s' and company = 'ELECTRA - BARWA SHOWROOM' group by item_code """%(item),as_dict=1)[0]
	# print(count)
	print(coun['sum'])
	# print(count['sum'])
	# print(coun['sum'] - count['sum'])



@frappe.whitelist()
def get_leave_details_le(employee):
	frappe.errprint(employee)
	leave_application = frappe.get_list(
		"Leave Application",
		filters={
			"employee": employee,
			"status": "Approved",
			"leave_type": "Annual Leave"
		},
		fields=["name", "from_date", "to_date"],
		order_by="creation desc",
		limit=1
	)
	if leave_application:
		leave_details = leave_application[0]
		return {
			"leave_application": leave_details.name,
			"from_date": leave_details.from_date,
			"to_date": leave_details.to_date
		}

	else:
		frappe.throw(_("No approved annual leave application found for the employee."))


@frappe.whitelist()
def updat_series():
	from electra.utils import get_series
	ab = get_series("TRADING DIVISION - ELECTRA","Purchase Invoice")
	bc = ab.split('-')
	print(bc[0]+'-'+bc[1]+'-'+'STC-'+bc[2]+'-')
 
 
@frappe.whitelist()    
def mark_absent():
	from_date = add_days(today(),-1)  
	to_date = today()
	# from_date = "2023-10-02"
	# to_date = "2023-10-03"
	dates = [from_date,to_date]
	for date in dates:
		employee = frappe.db.get_all('Employee',{'status':'Active','date_of_joining':['<=',from_date]},['*'])
		for emp in employee:
			hh = check_holiday(date,emp.name)
			if not hh:
				if not frappe.db.exists('Attendance',{'attendance_date':date,'employee':emp.name,'docstatus':('!=','2')}):
					att = frappe.new_doc('Attendance')
					att.employee = emp.name
					att.status = 'Absent'
					att.attendance_date = date
					att.company = emp.company
					att.save(ignore_permissions=True)
					frappe.db.commit() 
					print(date)  
	return "ok"

from datetime import date, timedelta

def get_dates_between(start_date, end_date):
	"""
	Get a list of dates between start_date and end_date (inclusive).

	Args:
	start_date (datetime.date): The start date.
	end_date (datetime.date): The end date.

	Returns:
	list: A list of datetime.date objects representing the dates.
	"""
	dates = []
	current_date = start_date
	while current_date <= end_date:
		dates.append(current_date)
		current_date += timedelta(days=1)
	return dates


def check_holiday(date,emp):
	holiday_list = frappe.db.get_value('Employee',emp,'holiday_list')
	holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
	left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(holiday_list,date),as_dict=True)
	if holiday:
		if holiday[0].weekly_off == 1:
			return "WW"
		else:
			return "HH"

@frappe.whitelist()
def create_hooks_att():
	job = frappe.db.exists('Scheduled Job Type', 'electra.custom.mark_absent')
	if not job:
		att = frappe.new_doc("Scheduled Job Type")
		att.update({
			"method": 'electra.custom.mark_absent',
			"frequency": 'Cron',
			"cron_format": '30 10 * * *'
		})
		att.save(ignore_permissions=True)
  


@frappe.whitelist()
def get_norden_details(**args):
	data = ''
	data1 = ''
	i = 0
	aa = args['item']
	item = frappe.get_value('Item',{'item_code':args['item']},'item_code')
	if item:
		rate = frappe.get_value('Item',{'item_code':args['item']},'valuation_rate')
		group = frappe.get_value('Item',{'item_code':args['item']},'item_group')
		des = frappe.get_value('Item',{'item_code':args['item']},'description')
		price = frappe.get_value('Item Price',{'item_code':args['item'],'price_list':'Cost'},'price_list_rate')
		c_s_p = frappe.get_value('Item Price',{'item_code':args['item'],'price_list':'Standard Selling'},'price_list_rate') or 0
		spn = frappe.db.sql(""" select supplier_part_no from `tabItem` left join `tabItem Supplier` on `tabItem`.name = `tabItem Supplier`.parent 
		where `tabItem`.item_code = '%s' """%(args['item']),as_dict=True)[0]
		csp = 'Current Selling Price'
		cpp = 'Current Purchase Price'
		cost = 'COST'
		pso = 'Pending Sales order'
		po ='Total Purchase Order'
		ppo = 'Pending Purchase order'
		cspp_rate = 0
		cppp_rate = 0
		del_total = 0
		psoc = 0
		ppoc = 0
		ppoc_total = 0
		cspp_query = frappe.db.sql("""select `tabSales Order Item`.rate as rate, `tabSales Order`.creation from `tabSales Order`
		left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
		where `tabSales Order Item`.item_code = '%s' order by `tabSales Order`.creation """ % (item), as_dict=True)
		if cspp_query:
				cspp = cspp_query[-1]
				cspp_rate = cspp['rate']

		cppp_query = frappe.db.sql("""select `tabPurchase Order Item`.rate as rate, `tabPurchase Order`.creation  from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' order by `tabPurchase Order`.creation """ % (item), as_dict=True)
		if cppp_query:
				cppp = cppp_query[-1]
				cppp_rate = cppp['rate']

		new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
		left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
		where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1  """ % (item), as_dict=True)[0]
		if not new_so['qty']:
			new_so['qty'] = 0
		if not new_so['d_qty']:
			new_so['d_qty'] = 0
		del_total = new_so['qty'] - new_so['d_qty']		
				
		new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1  """ % (item), as_dict=True)[0]
		if not new_po['qty']:
			new_po['qty'] = 0
		if not new_po['d_qty']:
			new_po['d_qty'] = 0
		ppoc_total = new_po['qty'] - new_po['d_qty']	



		a = frappe.db.sql("""select `tabPurchase Receipt Item`.purchase_order as name from `tabPurchase Receipt`
				left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
				where `tabPurchase Receipt Item`.item_code = '%s' """ % (aa), as_dict=True) or "-"

		b = frappe.db.sql("""select `tabPurchase Receipt`.name as name from `tabPurchase Receipt`
				left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
				where `tabPurchase Receipt Item`.item_code = '%s' """ % (aa), as_dict=True) or "-"
		
		data = ''
		stocks_query = frappe.db.sql("""select actual_qty,warehouse,valuation_rate,stock_uom,stock_value from tabBin
				where item_code = '%s' """%(item),as_dict=True)
		if stocks_query:
				stocks = stocks_query
		data += '<table class="table table-bordered" style="width:70%"><tr><th style="padding:1px;border: 1px solid black;background-color:#fe3f0c;color:white" colspan=5><center> ELECTRA PRODUCT SEARCH</center></th></tr>'
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>Item Code</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(item)
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: left"><b>Item Name</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(frappe.db.get_value('Item',item,'item_name'))
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: left"><b>Item Group</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(group)
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(pso,del_total)
		if ppoc_total != 0.0:
				data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(ppo,ppoc_total)
		else:
				data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(ppo,ppoc_total) 
		if ppoc_total > 0 :
				ppoc_date_query = frappe.db.sql("""select `tabPurchase Order Item`.schedule_date  as date from `tabPurchase Order`
				left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
				where `tabPurchase Order Item`.item_code = '%s' """ % (item), as_dict=True)[0]
				if ppoc_date_query:
					po_date = ppoc_date_query['date']
			
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 3 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(csp,(c_s_p))
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>Warehouse</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>QTY</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>UOM</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>COST</b></center></td></tr>'		
		i = 0
		cou = 0
		tot = 'Total'
		uom = 'Nos'
		for stock in stocks_query:
			if stock.actual_qty >= 0:       
				comp = frappe.db.get_value("Employee",{'user_id':frappe.session.user},'company')
				w_house = frappe.db.get_value("Warehouse",{'company':comp,'default_for_stock_transfer':1},['name'])
				if w_house == stock.warehouse:
					data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-',(round(float(stock.valuation_rate) , 2)) or '-')
					i += 1
					cou += stock.actual_qty  

		for stock in stocks_query:
			if stock.actual_qty >= 0:       
				comp = frappe.db.get_value("Employee",{'user_id':frappe.session.user},'company')
				w_house = frappe.db.get_value("Warehouse",{'company':comp,'default_for_stock_transfer':1},['name'])
				if w_house != stock.warehouse:
					data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-',(round(float(stock.valuation_rate) , 2)) or '-')
					i += 1
					cou += stock.actual_qty
		data += '<tr><td align="right" colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><b>%s</b></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>-</b></center></td></tr>'%(tot,int(cou),uom)
		data += '</table>'
	else:
		i += 1
		data1 += '<table width = "100%"><tr><td align="center" colspan = 10  style="padding:1px;border: 1px solid black;background-color:#fe3f0c;color:white;"><b>No Stock Available</b></td></tr>'
		data1 += '</table>'
		data += data1
	if i > 0:
		return data
	
@frappe.whitelist()
def norden_details(**args):
	data = ''
	data1 = ''
	i = 0
	aa = args['item']
	item = frappe.get_value('Item',{'item_code':args['item']},'item_code')
	if item:
		rate = frappe.get_value('Item',{'item_code':args['item']},'valuation_rate')
		group = frappe.get_value('Item',{'item_code':args['item']},'item_group')
		des = frappe.get_value('Item',{'item_code':args['item']},'description')
		price = frappe.get_value('Item Price',{'item_code':args['item'],'price_list':'Cost'},'price_list_rate')
		c_s_p = frappe.get_value('Item Price',{'item_code':args['item'],'price_list':'Standard Selling'},'price_list_rate') or 0
		spn = frappe.db.sql(""" select supplier_part_no from `tabItem` left join `tabItem Supplier` on `tabItem`.name = `tabItem Supplier`.parent 
		where `tabItem`.item_code = '%s' """%(args['item']),as_dict=True)[0]
		csp = 'Current Selling Price'
		cpp = 'Current Purchase Price'
		cost = 'COST'
		pso = 'Pending Sales order'
		po ='Total Purchase Order'
		ppo = 'Pending Purchase order'
		cspp_rate = 0
		cppp_rate = 0
		psoc = 0
		del_total = 0
		ppoc = 0
		ppoc_total = 0
		cspp_query = frappe.db.sql("""select `tabSales Order Item`.rate as rate, `tabSales Order`.creation from `tabSales Order`
		left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
		where `tabSales Order Item`.item_code = '%s' order by `tabSales Order`.creation """ % (item), as_dict=True)
		if cspp_query:
			cspp = cspp_query[-1]
			cspp_rate = cspp['rate']

		cppp_query = frappe.db.sql("""select `tabPurchase Order Item`.rate as rate, `tabPurchase Order`.creation  from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' order by `tabPurchase Order`.creation """ % (item), as_dict=True)
		if cppp_query:
			cppp = cppp_query[-1]
			cppp_rate = cppp['rate']


		new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
		left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
		where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1  """ % (item), as_dict=True)[0]
		if not new_so['qty']:
			new_so['qty'] = 0
		if not new_so['d_qty']:
			new_so['d_qty'] = 0
		del_total = new_so['qty'] - new_so['d_qty']		

		new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order`
		left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
		where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1  """ % (item), as_dict=True)[0]
		if not new_po['qty']:
			new_po['qty'] = 0
		if not new_po['d_qty']:
			new_po['d_qty'] = 0
		ppoc_total = new_po['qty'] - new_po['d_qty']	


		a = frappe.db.sql("""select `tabPurchase Receipt Item`.purchase_order as name from `tabPurchase Receipt`
			left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
			where `tabPurchase Receipt Item`.item_code = '%s' """ % (aa), as_dict=True) or "-"
		b = frappe.db.sql("""select `tabPurchase Receipt`.name as name from `tabPurchase Receipt`
			left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
			where `tabPurchase Receipt Item`.item_code = '%s' """ % (aa), as_dict=True) or "-"
		data = ''
		stocks_query = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
			where item_code = '%s' """%(item),as_dict=True)
		if stocks_query:
			stocks = stocks_query
		data += '<table class="table table-bordered" style="width:50%"><tr><th style="padding:1px;border: 1px solid black;background-color:#fe3f0c;" colspan=4><center>ELECTRA PRODUCT SEARCH</center></th></tr>'
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>Item Code</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(item)
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: left"><b>Item Name</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(frappe.db.get_value('Item',item,'item_name'))
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;text-align: left"><b>Item Group</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(group)
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(pso,del_total)
		if ppoc_total != 0.0:
			data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(ppo,ppoc_total)
		else:
			data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(ppo,ppoc_total) 
		if ppoc_total > 0 :
			ppoc_date_query = frappe.db.sql("""select `tabPurchase Order Item`.schedule_date  as date from `tabPurchase Order`
			left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
			where `tabPurchase Order Item`.item_code = '%s' """ % (item), as_dict=True)[0]
			if ppoc_date_query:
				po_date = ppoc_date_query['date']
			
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;color:white;background-color:#6f6f6f;text-align: left"><b>%s</b></td><td colspan = 2 style="padding:1px;border: 1px solid black;text-align: left"><b>%s</b></td></tr>'%(csp,(c_s_p))
		data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>Warehouse</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>QTY</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>UOM</b></center></tr>'
		i = 0
		cou = 0
		tot = 'Total'
		uom = 'Nos'
  
		for stock in stocks_query:
			if int(stock.actual_qty) >= 0:
				comp = frappe.db.get_value("Employee",{'user_id':frappe.session.user},'company')
				w_house = frappe.db.get_value("Warehouse",{'company':comp,'default_for_stock_transfer':1},['name'])
				if w_house == stock.warehouse:        
					data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-')
					i += 1
					cou += stock.actual_qty

		for stock in stocks_query:
			if int(stock.actual_qty) >= 0:
				comp = frappe.db.get_value("Employee",{'user_id':frappe.session.user},'company')
				w_house = frappe.db.get_value("Warehouse",{'company':comp,'default_for_stock_transfer':1},['name'])
				if w_house != stock.warehouse:        
					data += '<tr><td colspan = 2 style="padding:1px;border: 1px solid black">%s</td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black"><center><b>%s</b></center></td></tr>'%(stock.warehouse,int(stock.actual_qty) or '-',stock.stock_uom or '-')
					i += 1
					cou += stock.actual_qty
		data += '<tr><td align="right" colspan = 2 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><b>%s</b></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td><td colspan = 1 style="padding:1px;border: 1px solid black;background-color:#6f6f6f;color:white;"><center><b>%s</b></center></td></tr>'%(tot,int(cou),uom)
		data += '</table>'
	else:
		i += 1
		data1 += '<table width = "100%"><tr><td align="center" colspan = 10  style="padding:1px;border: 1px solid black;background-color:#fe3f0c;color:white;"><b>No Stock Available</b></td></tr>'
		data1 += '</table>'
		data += data1
	if i > 0:
		return data

	

@frappe.whitelist()
def val_rate():
	valuation_rate = 0
	source_warehouse = frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company': "TRADING DIVISION - ELECTRA" }, ["name"])
	latest_vr = frappe.db.sql("""select valuation_rate as vr from tabBin
			where item_code = '%s' and warehouse = '%s' """%("AF21036",source_warehouse),as_dict=True)

	if len(latest_vr) > 0:
		valuation_rate = latest_vr[0]["vr"]
	# else:
	#     val_rate = []
	#     l_vr = frappe.db.sql("""select valuation_rate as vr from tabBin
	#             where item_code = '%s' """%("AF21036"),as_dict=True)
	#     for item in l_vr: 
	#         if item not in val_rate: 
	#             val_rate.append(item.vr)
	#     if len(val_rate) > 1 :
	#         valuation_rate = max(val_rate)
	print(valuation_rate)


@frappe.whitelist()
def get_project_name():
	pro = frappe.db.sql("""SELECT
		`tabProject Budget`.name AS project_budget_name
	FROM
		`tabProject`
	JOIN
		`tabProject Budget` ON `tabProject`.`budgeting` = `tabProject Budget`.name and `tabProject`.name = 'ENG-PRO-2023-00014';
	""")
	
	# project = frappe.db.sql(""" select `tabProject Budget`.name from `tabProject Budget` left join `tabProject` where `tabProject Budget`.name = `tabProject`.budgeting   """)
	print(pro)

@frappe.whitelist()
def update_workflow_state():
	stock = frappe.db.get_list("Stock Request",{"docstatus":2},["workflow_state","name"])
	for i in stock:
		if i.workflow_state == "Transfer Requested":
			frappe.db.set_value("Stock Request",i.name,"workflow_state","Cancelled")
			print(i.name)

from frappe.utils.file_manager import get_file
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe import _, get_file_items
@frappe.whitelist()
def update_att(import_file):
	filepath = get_file(import_file)
	pps = read_csv_content(filepath[1])
	for pp in pps:
		print(pp[0])
		if not frappe.db.exists('Attendance',{'attendance_date':pp[1],'employee':pp[0],'docstatus':('!=','2')}):
			att = frappe.new_doc('Attendance')
			att.employee = pp[0]
			att.status = pp[4]
			att.attendance_date = pp[1]
			att.leave_type = pp[2]
			att.leave_application = pp[3]
			att.save(ignore_permissions=True)
			frappe.db.commit() 
		else:
			att = frappe.get_doc('Attendance',{'attendance_date':pp[1],'employee':pp[0],'docstatus':('!=','2')})
			att.employee = pp[0]
			att.status = pp[4]
			att.attendance_date = pp[1]
			att.leave_type = pp[2]
			att.leave_application = pp[3]
			att.save(ignore_permissions=True)
			frappe.db.commit() 

	return 'ok'
	

@frappe.whitelist()
def salary_payroll(doc,method):
	# frappe.errprint(doc.payroll_date)
	# frappe.errprint(doc.salary_component)
	# frappe.errprint(doc.employee)
	# frappe.errprint(doc.name)
	salary = frappe.db.exists("Additional Salary",{"payroll_date":doc.payroll_date,"salary_component":doc.salary_component,"employee":doc.employee,'docstatus':('!=','2'),'name':('!=',doc.name)})
	if salary:
		print("HI")
		frappe.throw(_('This employee already has a Additional Salary against same component & same payroll period'))
	

@frappe.whitelist()
def update_workflow_state_po():
	po = frappe.db.get_list("Purchase Order",{"docstatus":2},["workflow_state","name"])
	for i in po:
		if i.workflow_state == "Submitted":
			frappe.db.set_value("Purchase Order",i.name,"workflow_state","Cancelled")
			print(i.name)

@frappe.whitelist()
def get_date():
	doc =frappe.db.get_list("Delivery Note",["name","date","posting_date"])
	for i in doc:
		frappe.db.set_value("Delivery Note",i.name,"date",i.posting_date)

@frappe.whitelist()
def get_project(company):
	value = frappe.db.get_list("Project",{"company":company,"status":"Open"},["name","customer","project_name"])
	return value

		
@frappe.whitelist()
def get_day_plan_details(day_plan):
	doc = frappe.get_doc("Single Project Day Plan",day_plan)
	day_plan_details = []
	for i in doc.worker_multiselect:
		day_plan_details.append(frappe._dict({
			'project': doc.project,
			'project_name': doc.project_name,
			'employee': i.employee,
			'employee_name' : i.non_staff,
			'designation' : i.designation,
		}))
	for s in doc.staff_multiselect:
		day_plan_details.append(frappe._dict({
			'project': doc.project,
			'project_name': doc.project_name,
			'employee': s.employee,
			'employee_name' : s.staff,
			'designation' : s.designation,
		}))
	for p in doc.supervisor_multiselect:
		day_plan_details.append(frappe._dict({
			'project': doc.project,
			'project_name': doc.project_name,
			'employee': p.employee,
			'employee_name' : p.supervisor,
			'designation' : p.designation,
		}))
	return day_plan_details

@frappe.whitelist()
def scope_of_work(doc):
	list=[]
	for i in doc.scope_of_work:
		if(i.delivery):
			list.append(i.delivery)
	return len(list)

@frappe.whitelist()
def list_ce():
	val = frappe.db.get_value('Quotation', { 'cost_estimation': "INT-CE-2023-00145-1"}, 'name',order_by='transaction_date asc',)
	print(val)


# @frappe.whitelist()
# def is_cost_estimation_submitted(cost_estimation):
#     cost_estimation_doc = frappe.get_doc("Cost Estimation", cost_estimation)
	
#     if cost_estimation_doc.docstatus == 1:
#         return True 
#     else:
#         return False 

# @frappe.whitelist()
# def is_cost_estimation_submitted(cost_estimation):
# 	cost_estimation_doc = frappe.get_doc("Cost Estimation", cost_estimation)

# 	if cost_estimation_doc.docstatus == 1:
# 		frappe.permissions.update_permission_property(
# 			"CE SOW", cost_estimation_doc.name, "total_overhead", "read_only", 1
# 		)
# 	else:
# 		frappe.permissions.update_permission_property(
# 			"CE SOW", cost_estimation_doc.name, "total_overhead", "read_only", 0
# 		)

@frappe.whitelist()
def consumables_table(delivery_note):
	item_list = []
	tot = []
	total = 0
	dn = frappe.get_doc("Delivery Note",delivery_note)
	for i in dn.items:
		if i.item_code not in  item_list:
			item_list.append(i.item_code)
		if i.item_code == "CONS":
			tot.append(i.amount)
	if "CONS" in item_list:
		for ele in range(0, len(tot)):
			total = total + tot[ele]
		return 1,total
	else:
		return 0,total
	

@frappe.whitelist()
def return_consumables_sales_price(item_code):
	price = frappe.get_value('Item Price',{'item_code':item_code,'price_list':'Standard Selling'},'price_list_rate') or 0
	return price

@frappe.whitelist()
def create_stock_out(doc,method):
	if doc.cons_items:
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Issue" 
		se.company = doc.company
		se.reference_number = doc.name
		for i in doc.cons_items:
			se.append("items",{
				's_warehouse':doc.set_warehouse,
				'item_code':i.item_code,
				'qty':i.qty,
				'basic_rate':i.rate
			})
		se.save(ignore_permissions=True)
		se.submit()

@frappe.whitelist()
def on_cancel_dn(doc,method):
	se = frappe.db.get_value("Stock Entry",{"reference_number":doc.name},['name'])
	if se:
		se_cancel = frappe.get_doc("Stock Entry",se)
		se_cancel.cancel()
		se_cancel.delete()

@frappe.whitelist()
def get_company():
	sa=frappe.db.sql("""select name from `tabCompany`""",as_dict=True)
	return sa

@frappe.whitelist()
def get_sales_person_name():
	sa=frappe.db.sql("""select name from `tabSales Person`""",as_dict=True)
	return sa

@frappe.whitelist()
def sales_order_cancel(doc,method):
	dn_link = frappe.db.sql("""SELECT `tabDelivery Note`.name , `tabDelivery Note`.docstatus FROM `tabDelivery Note` LEFT JOIN `tabDelivery Note Item` ON `tabDelivery Note`.name = `tabDelivery Note Item`.parent WHERE
				`tabDelivery Note Item`.against_sales_order = '%s'
		""" % (doc.name), as_dict=True)
	if dn_link:
		for i in dn_link:
			if i.docstatus == 0:
				frappe.throw(_("Sales Order is linked to a Delivery Note "+i.name+" . Cannot cancel."))

@frappe.whitelist()
def salary_employee():
	value=frappe.db.get_all("Employee",{"status":"Active"},["status","name","company"])
	for i in value:
		# print(i.name)
		if frappe.db.exists('Salary Structure Assignment',{'employee':i.name,'docstatus':('!=','2')}):
			ad = frappe.db.sql("""select * from `tabSalary Structure Assignment` where employee = '%s' and docstatus = 1 ORDER BY from_date DESC LIMIT 1  """%(i.name),as_dict=True)[0]
			if i.company != ad.company:
				print(i.name)
			# print(ad.company)
   
@frappe.whitelist()
def customer_credit_note(customer):
	cust = frappe.get_doc("Customer",customer)
	return cust.credit_limits

# @frappe.whitelist()
# def invoice(doc,method):
# 	total = 0
# 	for i in doc.sow:
# 		for j in doc.items:
# 			if j.msow==i.msow:
# 				total += j.amount
# 		i.invoice_amount = total
# 		i.invoice_percent = (i.invoice_amount/i.total_bidding_price)*100
# 		total = 0
# 		so = frappe.get_doc("Sales Order",doc.sales_order)
# 		for k in so.scope_of_work:
# 			k.invoice_amount += i.invoice_amount
# 			k.invoice_percent += k.invoice_percent
			

@frappe.whitelist()
def invoice(doc, method):
	if doc.order_type == "Project":
		total = 0
		for i in doc.sow:
			for j in doc.items:
				if j.msow == i.msow:
					total += j.amount
			i.invoice_amount = total
			i.invoice_percent = (i.invoice_amount / i.total_bidding_price) * 100
			total = 0
		if doc.sales_order:
			so = frappe.get_doc("Sales Order", doc.sales_order)			
			for i in doc.sow:
				for k in so.scope_of_work:
					if i.msow == k.msow:
						k.invoice_amount += i.invoice_amount
						k.invoice_percent += i.invoice_percent
			so.save()

@frappe.whitelist()
def invoice_cancel(doc, method):
	if doc.order_type == "Project":
		total = 0
		for i in doc.sow:
			for j in doc.items:
				if j.msow == i.msow:
					total += j.amount
			i.invoice_amount = total
			i.invoice_percent = (i.invoice_amount / i.total_bidding_price) * 100
			total = 0
		if doc.sales_order:
			so = frappe.get_doc("Sales Order", doc.sales_order)
			
			for i in doc.sow:
				for k in so.scope_of_work:
					if i.msow == k.msow and k.invoice_amount != 0:
						k.invoice_amount -= i.invoice_amount
						k.invoice_percent -= i.invoice_percent

			so.save()

	
@frappe.whitelist()
def update_bidding_price(doc,method):
	total_bidding_price = 0
	for i in doc.scope_of_work:
		total_bidding_price += i.total_bidding_price
	doc.total_bidding_price = total_bidding_price
	doc.total_bidding_price = total_bidding_price - doc.project_discount_amt

@frappe.whitelist()
def update_jv():
	jv = frappe.db.get_list("Journal Entry",{"total_amount":0,"docstatus":1},['name','total_credit'])
	for i in jv:
		frappe.db.set_value("Journal Entry",i.name,"total_amount",i.total_credit)
		print(i.name)
		print(i.total_credit)

@frappe.whitelist()
def sal_consolidated_req(name):
	con = frappe.db.sql("""SELECT * FROM `tabOrder Invoice List` WHERE parent = %s""", name, as_dict=True)
	child_table = con

	def calculate_outstanding_payment_difference(child_table):
		amounts_by_company = defaultdict(float)
		for row in child_table:
			company = row.get("company", "")
			outstanding_amount = row.get("outstanding_amount", 0.0)
			payment_amount = row.get("receivable_amount", 0.0)
			amounts_by_company[company] += (outstanding_amount - payment_amount)
		
		result = []
		for company, difference in amounts_by_company.items():
			result.append({"company": company, "value": difference})
		# Build the HTML table
		data = '<table width="100%"><tr><td style="color:white;background-color:#e35310;padding:1px;font-weight:bold;border:1px solid black">Company</td><td style="font-weight:bold;color:white;background-color:#e35310;padding:1px;border:1px solid black">Amount</td></tr>'
		for i in result:
			data += '<tr><td style="padding:1px;border:1px solid black">%s</td><td style="padding:1px;border:1px solid black">%s</td></tr>' % (i["company"], i["value"])
		data += '</table>'
		return data

	amounts_difference_by_company = calculate_outstanding_payment_difference(child_table)
	return amounts_difference_by_company

@frappe.whitelist()
def update_pr():
	frappe.db.set_value("Purchase Invoice Item",{"parent":"TRD-PI-2023-00362"},'purchase_receipt',"TRD-PR-2023-00184-1",update_modified=False)

@frappe.whitelist()
def get_dn_no(sale_ord):
	dn_list = frappe.get_all("Delivery Note Item",{"against_sales_order":sale_ord,"docstatus":1},["parent"])
	dn_list_items = []
	if dn_list:
		for i in dn_list:
			if i not in dn_list_items:
				dn_list_items.append(i['parent'] or "")
			dnlist = str(dn_list_items)
		return dnlist
	
# import requests

# @frappe.whitelist()
# def fetch_location_name(pickup_point):
#     api_key = '583681db58de9d7'
#     geocoding_url = f'https://maps.googleapis.com/maps/api/geocode/json?key={api_key}&address={pickup_point}'

#     try:
#         response = requests.get(geocoding_url)
#         data = response.json()

#         if data.get('status') == 'OK' and data.get('results'):
#             location_name = data['results'][0]['formatted_address']
#             return {"location_name": location_name}
#         else:
#             return {"location_name": "Location Not Found"}
#     except Exception as e:
#         frappe.log_error(f'Error fetching location name: {str(e)}')
#         return {"location_name": "Error"}




@frappe.whitelist()
def lcv_value():
	lc = frappe.db.sql("""select sum(`tabLanded Cost Item`.applicable_charges) as pd from `tabLanded Cost Voucher`
			left join `tabLanded Cost Item` on `tabLanded Cost Voucher`.name = `tabLanded Cost Item`.parent
			where `tabLanded Cost Item`.receipt_document = '%s' and `tabLanded Cost Voucher`.docstatus =1 """%("INT-PR-2023-00008"),as_dict=True)
	
	print(lc)

@frappe.whitelist()    
def monthly_expiry_doc():
	current_date = nowdate()
	next_date = add_days(current_date , 30)
	doc=frappe.get_all("Legal Compliance Monitor",{'next_due': ('between', (current_date, next_date))},['name','days_left','next_due'])
	documents = ''
	documents += '<table class = table table - bordered style=border-width:2px><tr><td colspan = 6><b>Legal Compliance Monitor List</b></td></tr>'
	documents += '<tr><td colspan=2>Document Name</td><td colspan=2>Expiry Date</td><td colspan=2>Days Left</td>'
	for i in doc:
		documents += '<tr><td colspan = 2>%s</td><td colspan=2>%s</td><td colspan=2>%s</td></tr>'%(i.name,formatdate(i.next_due),i.days_left)
	documents += '</table>' 
	frappe.sendmail(
			   recipients=['suvarna@electraqatar.com'],
			 cc = ['yahia@electraqatar.com','veeramayandi.p@groupteampro.com','jenisha.p@groupteampro.com'],
			 subject=('Legal Compliance Monitor'),
			 message="""
					Dear Sir/Mam,<br>
					<p>Kindly find the attached Legal Compliance Monitor List for Expiry Soon</p>
					%s
					""" % (documents)
		) 
	
	return True

@frappe.whitelist()
def return_valu():
	frappe.errprint(frappe.db.get_value("Sales Order Item", '3f49977de7', 'rate'))
	doc = frappe.get_all("Sales Order Item",{'parent':"ENG-SO-2023-00185"},['name'])
	print(doc)

@frappe.whitelist()
def update_vmc():
	sep = frappe.db.sql("""update `tabVehicle Maintenance Check List` set docstatus = 0 where name = "ELE/HRA/05/00466" """,as_dict = True)
	print(sep)
 
 
@frappe.whitelist()
def get_so_details(sales):
	dict_list = []
	so = frappe.get_doc("Sales Order",sales)
	for i in so.items:
		dict_list.append(frappe._dict({"name":i.name,"item_code":i.item_code,"pending_qty":i.qty,"bom":i.bom_no,"description": i.description,"warehouse":i.warehouse,"rate":i.rate,"amount":i.amount}))
	return dict_list




@frappe.whitelist()
def make_material_request(items, prepared,sales_order, company, project=None):
	"""Make Work Orders against the given Sales Order for the given `items`"""
	items = json.loads(items).get("items")    
	material_req = frappe.get_doc({
		"doctype": "Material Request",
		"company": company,
		"sales_order": sales_order,
		"project": project,
		"prepared_by":prepared,
	})    
	for i in items:
		frappe.errprint(i)
		if i["bom"]:
			bom_list = frappe.get_all("BOM", {"name": i["bom"]},["*"])
			for bom in bom_list:
				items_list = frappe.get_all("BOM Item", {"parent": bom.name}, ["*"])
				for b in items_list:
					material_req.append('items',{
						"item_code":b.item_code,
						"rate":b.rate,
						"amount":b.amount * i["pending_qty"],
						"item_name":b.item_name,
						"qty":b.qty * i["pending_qty"],
						"schedule_date":today(),
						"sales_order":sales_order
					})
		else:
			material_req.append('items', {
				"item_code": i['item_code'],
				"qty": i['pending_qty'],
				"rate":i["rate"],
				"amount":i["amount"] ,
				"schedule_date": today(),
				"sales_order":sales_order

			})
	material_req.save()
	return material_req
@frappe.whitelist()
def inactive_employee(doc,method):
	if doc.status=="Active":
		if doc.relieving_date:
			throw(_("Please remove the relieving date for the Active Employee."))

# @frappe.whitelist()
# def update_amount(employee,ot,wh):
# 	basic = frappe.db.get_value("Employee",{'employee_number':employee},[['basic']])
# 	one_day_amount = basic / 26
# 	wh = one_day_amount * float(wh)
# 	ot = wh * ot
# 	return ot

@frappe.whitelist()
def update_emp_value(employee):
	value=frappe.db.get_value("Employee",{'employee_number':employee},['employee_name'])
	designation = frappe.db.get_value("Employee",{'employee_number':employee},['designation'])
	grade = frappe.db.get_value("Employee",{'employee_number':employee},['grade'])
	return value,designation,grade

# @frappe.whitelist()
# def create_entry():
# 	employee = '629'
# 	leave_type = 'Annual Leave'
# 	leaves = -33
# 	from_date = '2023-01-15'
# 	to_date = '2023-02-16'
# 	transaction_type = 'Leave Application'
# 	transaction_name = 'HR-LAP-2023-00009'
# 	entry = frappe.new_doc('Leave Ledger Entry')
# 	entry.employee = employee
# 	entry.leave_type = leave_type
# 	entry.leaves = leaves
# 	entry.from_date = from_date
# 	entry.to_date = to_date
# 	entry.leave_type = leave_type
# 	entry.transaction_type = transaction_type
# 	entry.transaction_name = transaction_name
# 	entry.insert()
# 	return _("Leave Ledger Entry created successfully.")


@frappe.whitelist()
def update_lareei():
	frappe.db.sql("""update `tabAttendance` set docstatus = 0 where attendance_date between "2023-11-01" and "2023-11-30" and company = "Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)" """,as_dict = True)
	
	# frappe.db.sql("""delete from `tabLeave Ledger Entry` where name = '2a43efd06b' """,as_dict = True)
	# frappe.db.sql("""delete from `tabRejoining Form` where name = 'ELE/HRA/04/0093' """,as_dict = True)
				
@frappe.whitelist()
def update_employee_no(name,employee_number):
	emp = frappe.get_doc("Employee",name)
	emps=frappe.get_all("Employee",{"status":"Active"},['*'])
	for i in emps:
		if emp.employee_number == employee_number:
			pass
		elif i.employee_number == employee_number:
			frappe.throw(f"Employee Number already exists for {i.name}")
		else:
			frappe.db.set_value("Employee",name,"employee_number",employee_number)
			frappe.rename_doc("Employee", name, employee_number, force=1)
			return employee_number


@frappe.whitelist()
def get_expected_dates(expect):
	exp_date = ''
	if expect == "In 15 Days":
		exp_date = add_days(nowdate(), 15)
		frappe.errprint(exp_date)
		
	elif expect == "In 30 Days":
		exp_date = add_days(nowdate(), 30)
	
	elif expect == "In 45 Days":
		exp_date = add_days(nowdate(), 45)
	
	elif expect == "In 60 Days":
		exp_date = add_days(nowdate(), 60)
	
	elif expect == "End of next Month":
		exp_date = get_last_day(add_months(nowdate(), 1))

	return exp_date

@frappe.whitelist()
def get_due_dates(payment,bill):
	due_date = ''
	if payment == "Due on receipt":
		due_date = bill

	elif payment == "Due end of next month":
		due_date = get_last_day(add_months(nowdate(), 1))

	elif payment == "Net 15":
		due_date = add_days(nowdate(), 15)

	elif payment == "Net 30":
		due_date = add_days(nowdate(), 30)

	elif payment == "Net 60":
		due_date = add_days(nowdate(), 60)

	elif payment == "Due end of the month":
		due_date = get_last_day(nowdate())

	return due_date

@frappe.whitelist()
def return_item_values(name,item_code):
	item_value=frappe.get_all("Sales Invoice Item",{'parent':name,'item_code':item_code},['qty','amount','base_amount','rate','base_rate','net_rate','base_net_rate','net_amount','base_net_amount'])
	for i in item_value:
		return i.qty,i.amount,i.base_amount,i.rate,i.base_rate,i.net_rate,i.base_net_rate,i.net_amount,i.base_net_amount
	
		
@frappe.whitelist()
def get_single_trip(sale):
	order = frappe.get_doc("Sales Order",sale)
	
	if order.work_end_date:
		new_doc = frappe.new_doc("Trip")
		new_doc.customer = order.customer
		new_doc.work_order_no = sale
		new_doc.distance_map = order.distance_map
		new_doc.billing = order.billing
		new_doc.company = order.company
		new_doc.rate_per_trip = order.rate_per_trip
		new_doc.total_trip1 = order.total_trip
		new_doc.total_amount = order.total_amount
		new_doc.from_location = order.destination[0].location_place
		new_doc.to_location = order.destination[-1].location_place
		for i in order.destination:
			new_doc.append('destination', {
				'location_place': i.location_place,
				'latitude_longitude':i.latitude_longitude,
				'point':i.point
			})

		for j in order.items:
			new_doc.append('trip_item', {
				'item_code': j.item_code,
				'customer_item_code':j.customer_item_code,
				'item_name':j.item_name,
				'delivery_date':j.delivery_date,
				'item_group':j.item_group,
				'description':j.description,
				'qty':j.qty,
				'uom':j.uom,
				'rate':j.rate,
				'amount':j.amount,
				'base_rate':j.base_rate,
				'base_amount':j.base_amount,
				'net_rate':j.net_rate,
				'net_amount':j.net_amount,
				'base_net_rate':j.base_net_rate,
				'base_net_amount':j.base_net_amount,
				'valuation_rate':j.valuation_rate,
				'warehouse':j.warehouse,
				'conversion_factor':j.conversion_factor,
				'prevdoc_docname':j.prevdoc_docname,
	
			})
			
		new_doc.save(ignore_permissions=True)
	return "ok"


@frappe.whitelist()
def create_multi(items, sale):
	order = frappe.get_doc("Sales Order", sale)
	item = int(items)
	frappe.errprint(type(item))
	for k in range(item):
		if order.work_end_date:
			new_doc = frappe.new_doc("Trip")
			new_doc.customer = order.customer
			new_doc.work_order_no = sale
			new_doc.distance_map = order.distance_map
			new_doc.billing = order.billing
			new_doc.company = order.company
			new_doc.rate_per_trip = order.rate_per_trip
			new_doc.total_trip1 = order.total_trip
			new_doc.total_amount = order.total_amount
			new_doc.from_location = order.destination[0].location_place
			new_doc.to_location = order.destination[-1].location_place
			for i in order.destination:
				new_doc.append('destination', {
					'location_place': i.location_place,
					'latitude_longitude': i.latitude_longitude,
					'point': i.point
				})

			for j in order.items:
				new_doc.append('trip_item', {
					'item_code': j.item_code,
					'customer_item_code':j.customer_item_code,
					'item_name':j.item_name,
					'item_group':j.item_group,
					'description':j.description,
					'uom':j.uom,
					'rate':j.rate,
					'base_net_rate':j.base_net_rate,
					'valuation_rate':j.valuation_rate,
					'warehouse':j.warehouse,
					'conversion_factor':j.conversion_factor,
					'prevdoc_docname':j.prevdoc_docname,
		
				})
			
			new_doc.insert(ignore_permissions=True)
	return "ok"


from electra.utils import get_series

@frappe.whitelist()
def get_si_doc(sales):
	trip = frappe.get_doc("Trip", sales)
	if trip.trip_item:
		si = frappe.new_doc("Sales Invoice")
		si.customer = trip.customer
		si.company = "KINGFISHER - TRANSPORTATION"
		si.naming_series = get_series("KINGFISHER - TRANSPORTATION", "Sales Invoice")
		for j in trip.trip_item:
			si.append('items', {
				'item_code': j.item_code,
				'customer_item_code': j.customer_item_code,
				'item_name': j.item_name,
				'delivery_date': j.delivery_date,
				'item_group': j.item_group,
				'description': j.description,
				'qty': j.qty,
				'uom': j.uom,
				'rate': j.rate,
				'amount': j.amount,
				'base_rate': j.base_rate,
				'base_amount': j.base_amount,
				'net_rate': j.net_rate,
				'net_amount': j.net_amount,
				'base_net_rate': j.base_net_rate,
				'base_net_amount': j.base_net_amount,
				'valuation_rate': j.valuation_rate,
				'warehouse': j.warehouse,
				'conversion_factor': j.conversion_factor,
				'prevdoc_docname': j.prevdoc_docname,
			})
		si.save(ignore_permissions=True)
		frappe.db.commit()
	return "ok"

@frappe.whitelist()
def get_child_si(trip):
	dict_list = []
	trip_new = frappe.get_doc("Trip",trip)
	for i in trip_new.trip_item:
		dict_list.append(frappe._dict({"item_code":i.item_code,"qty":i.qty,"item_name":i.item_name,"item_group":i.item_group,"description": i.description,"uom":i.uom,"rate":i.rate,"amount":i.amount,"valuation_rate":i.valuation_rate,"base_rate":i.base_rate,"base_amount":i.base_amount,"net_rate":i.net_rate,"net_amount":i.net_amount,"base_net_rate":i.base_net_rate,"base_net_amount":i.base_net_amount,"warehouse":i.warehouse}))
	return dict_list

@frappe.whitelist()
def get_hod_values():
	hod_users = frappe.get_all('User',filters={'enabled': 1},fields=['name', 'full_name', 'email'])
	hod_values_list = []
	for user in hod_users:
		if 'HOD' in frappe.get_roles(user['name']):
			hod_values_list.append({
				'full_name': user['full_name'],
			})
	for i in hod_values_list:
		emp_name = frappe.get_all()
		print(i['full_name'])



@frappe.whitelist()
def create_journal_for_retention(doc,method):
	if doc.ret_amount > 0:
		jv = frappe.new_doc("Journal Entry")
		jv.voucher_type = "Journal Entry"
		jv.company = doc.company
		jv.posting_date = nowdate()
		jv.append("accounts", {
			"account": frappe.db.get_value("Account",filters={'name': ['like', '%Retention -%'],'company':doc.company}),
			"party_type": "Customer",
			"party": doc.customer,
			"debit_in_account_currency": doc.ret_amount,
			"cost_center": erpnext.get_default_cost_center(doc.company),
		})

		jv.append("accounts", {
			"account": frappe.db.get_value("Account",filters={'name': ['like', '%4110 - Sales -%'],'company':doc.company}),
			"credit_in_account_currency": doc.ret_amount,
		})
		jv.save(ignore_permissions=True)

@frappe.whitelist()
def get_hod_values(doc,method):
	frappe.errprint("Hii")
	data = ''
	data += 'Dear Sir,<br><br>Kindly Find the List of Documents Moved To Pending for HOD<br>'
	data += '<table class="table table-bordered"><tr><th>Document Name</th></tr>'
	hod_users = frappe.get_all(
		'User',
		filters={'enabled': 1},
		fields=['name', 'full_name', 'email'],
	)
	hod_values_list = []
	for user in hod_users:
		if 'HOD' in frappe.get_roles(user['name']):
			hod_values_list.append({
				'email': user['email'],
			})
	for i in hod_values_list:
		company = frappe.get_all(
			"User Permission", {'user': i['email'], 'allow': 'Company'}, ['for_value'])
		for j in company:
			mr_list = frappe.get_all(
				"Material Request", {'workflow_state': 'Pending for HOD', 'company': j["for_value"]}, ['name'])
			for mr in mr_list:
				data += '<tr><td>%s</td></tr>' % (mr['name'])
	data += '</table>'
	frappe.sendmail(
		recipients=['jenisha.p@groupteampro.com',i['email']],
		subject=('Documents Moved to Pending for HOD'),
		message=data
	)

@frappe.whitelist()
def update_company():
	company = frappe.get_all("Stock Confirmation",['name','source_company'])
	for i in company:
		frappe.db.set_value("Stock Confirmation",i.name,"from__company",i.source_company)

@frappe.whitelist()
def update_workflow():
	value = frappe.get_all("Leave Application",{"status":"Cancelled"},["name"])
	for i in value:
		frappe.db.set_value("Leave Application",i.name,"workflow_state","Cancelled")

@frappe.whitelist()
def update_return_doc(doc, method):
    if doc.return_against:      
       frappe.db.set_value("Sales Invoice",doc.return_against,"return_document",doc.name)

@frappe.whitelist()
def update_return_documents():
	document = frappe.get_all("Sales Invoice",['return_against','name'])
	for i in document:
		if i.return_against:   
			frappe.db.set_value("Sales Invoice",i.return_against,"return_document",i.name)
	
@frappe.whitelist()
def update_ret_out(doc,method):
	if doc.order_type == "Project":
		outstanding_without_retention = doc.outstanding_amount - doc.ret_amount
		doc.outstanding_amount__without_retention = outstanding_without_retention


@frappe.whitelist(allow_guest=True)
def total_wh_hrs(in_time,out_time):
    inti = frappe.utils.get_datetime(in_time)
    out_ti = frappe.utils.get_datetime(out_time)
    frappe.errprint(type(out_ti))
    if inti and out_ti:
        wh = time_diff_in_hours(out_ti,inti)
        frappe.errprint(wh)
        return wh