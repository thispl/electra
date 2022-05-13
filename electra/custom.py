from __future__ import unicode_literals
import frappe,erpnext
from frappe.utils import cint
import json
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
from frappe.model.mapper import get_mapped_doc
from frappe.utils.file_manager import get_file
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
import datetime
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import openpyxl
import xlrd
import re
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import GradientFill, PatternFill
from six import BytesIO, string_types
import pandas as pd



@frappe.whitelist()
def get_leave_details(name,from_date,to_date,leave):
    doc = frappe.get_doc('Leave Application',name)
    leave_type = doc.leave_type
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
    rdoj = to_date
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
        <td>Leave Status</td>
        </tr>
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

                            
def rejoin_form_creation(doc,method):
    rj=frappe.new_doc("Re Joining From Leave")
    rj.emp_no = doc.employee
    rj.employee_name = doc.employee_name
    rj.designation = doc.designation1
    rj.department = doc.department
    rj.date_of_joining = doc.date_of_joining0
    rj.resident_id_number = doc.resident_id_number
    rj.start = doc.from_date
    rj.end = doc.to_date
    rj.nature_of_leave = doc.leave_type
    rj.total_leave_in_days =doc.total_leave_days
    rj.save(ignore_permissions = True)
    frappe.db.commit()

@frappe.whitelist()
def get_stock_balance_from_wh(item_code,warehouse):
    actual_qty = 0
    try:
        actual_qty = frappe.db.sql("""select actual_qty from tabBin
            where item_code = '%s' and warehouse = '%s' """%(item_code,warehouse),as_dict=True)
    except:
        pass
    return actual_qty[0]

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
    doc = frappe.get_doc("Quotation",source_name)
    cost_estimation = doc.cost_estimation
    doclist = get_mapped_doc("Quotation", source_name, {
        "Quotation": {
            "doctype": "Project Budget",
            "field_map": {
                "title_of_project": "title_of_project",
                "name": "quotation",
                "party_name":"customer",
                "cost_estimation" : "cost_estimation"
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

@frappe.whitelist()
def stock_popup(item_code):
    item = frappe.get_value('Item',{'item_code':item_code},'item_code')
    data = ''
    stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
        where item_code = '%s' """%(item),as_dict=True)
    data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black" colspan=6><center>Stock Availability</center></th></tr>'
    data += '<tr><td style="padding:1px;border: 1px solid black"><b>Item Code</b></td><td style="padding:1px;border: 1px solid black"><b>Item Name</b></td><td style="padding:1px;border: 1px solid black"><b>Warehouse</b></td><td style="padding:1px;border: 1px solid black"><b>QTY</b></td><td style="padding:1px;border: 1px solid black"><b>UOM</b></td></tr>'
    i = 0
    for stock in stocks:
        if stock.actual_qty > 0:
            data += '<tr><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td><td style="padding:1px;border: 1px solid black">%s</td></tr>'%(item,frappe.db.get_value('Item',item,'item_name'),stock.warehouse,stock.actual_qty,stock.stock_uom)
            i += 1
    data += '</table>'
    if i > 0:
        return data


@frappe.whitelist()
def po_popup(item):
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
        for so_wt in so.so_work_title_item:
            task_name = so_wt.item_name
            task = frappe.new_doc("Task")
            task.update({
                "subject": task_name,
                "project": doc.name,
                "is_group": 1
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

@frappe.whitelist()
def employee_conversion():
    employee=frappe.get_all('Employee',{'employment_type':'Probation'},['date_of_joining','grade','employee_name','employee_number'])
    day = datetime.strptime(str(today()),"%Y-%m-%d").date()   
    for emp in employee:
        date = emp.date_of_joining
        worker = emp.grade
        staff = emp.grade
        if worker:
            six = add_months(date,5)
            if six== day:
                frappe.sendmail(
					recipients = ["karthikeyan.s@groupteampro.com"],
					subject = 'probation period of employee ',
					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,6))
				)

            fifteen_days = add_days(six,15)
            if fifteen_days== day:
                frappe.sendmail(
					recipients = ["karthikeyan.s@groupteampro.com"],
					subject = 'probation period ends ',
					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,6))
				)

            seven_days = add_days(fifteen_days,8)
            if seven_days== day:
                frappe.sendmail(
					recipients = ["karthikeyan.s@groupteampro.com"],
					subject = 'probation period ends ',
					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,6))
				)
        if staff:
            three = add_months(date,2)
            if three == day:
                print(day)
                frappe.sendmail(
					recipients = ["karthikeyan.s@groupteampro.com"],
					subject = 'probation period ends ',
					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,3))
				)

            fifteen_days_ = add_days(three,15)
            if fifteen_days_== day:
                frappe.sendmail(
					recipients = ["karthikeyan.s@groupteampro.com"],
					sender = sender['email'],
					subject = 'probation period of employee ',
					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,3))
				)

            seven_days_ = add_days(fifteen_days_,8)
            if seven_days_== day:
                frappe.sendmail(
					recipients = ["karthikeyan.s@groupteampro.com"],
					sender = sender['email'],
					subject = 'probation period  ',
					message = 'Dear Sir / Mam <br> Probation period end for %s (%s) in %s'%(emp.employee_name,emp.employee_number,add_months(date,3))
				)
    
           
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

@frappe.whitelist()
def alert_to_substitute(doc,method):
    frappe.sendmail(
        recipients='karthikeyan.s@groupteampro.com',
        subject=('ASSIGNED AS SUBSTITUTE'),
        header=(''),
        message="""
            Dear %s,<br>
            %s %s %s is going for vacation %s to %s so you assigned as substitute<br>
            and getting into trainee to probation.<br>
            """%(doc.sub_employee_id,doc.employee_name,doc.employee,doc.department,doc.from_date,doc.to_date)
    )

@frappe.whitelist()
def grade(name,grade):
    doc = frappe.get_doc('Employee Grade',name)
    ticket = doc.air_ticket_allowance_
    print(ticket)

@frappe.whitelist()
def create_contact(name,email,designation,customer_name):
    # values = json.loads(values)
    customer = frappe.new_doc("Contact")
    customer.first_name = name
    customer.designation = designation
    customer.contact_person_email_id_ = email
    customer.append('email_ids',{
    'email_id':email,
    'is_primary':True,
    })
    # customer.append('phone_nos',{
    # 'phone': contact_no,
    # 'is_primary_phone':True,
    # 'is_primary_mobile_no':True,
    # })
    customer.append('links',{
    'link_doctype':"Customer",
    'link_name':customer_name,
    })
    customer.save(ignore_permissions=True)
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
    basic,doj = frappe.db.get_value('Employee',employee,['basic','date_of_joining'])
    current_yoe_days = date_diff(nowdate(),doj)
    current_yoe = round((current_yoe_days / 365),1)
    # yoe = add_years(doc[1],5)
    if current_yoe < 5:
        gratuity_per_year = (basic/30) * 21
        total_gratuity = current_yoe * gratuity_per_year
        return total_gratuity
    if current_yoe >= 5:
        total_yoe = current_yoe
        first_five_yr = ((basic/30) * 21) * 5
        total_yoe -= 5
        rest_of_yrs = ((basic/30) * 30) * total_yoe
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

@frappe.whitelist()
def get_dn_list_sales_invoice(doc,method):
    frappe.errprint('hii')
    sii = doc.items
    dn_list = []
    for i in sii:
        dn_list.append(i.delivery_note)
    si = frappe.get_doc("Sales Invoice",doc.name)
    si.delivery_note_list = str(dn_list)
    frappe.errprint(dn_list)
    frappe.errprint(si.delivery_note_list)
    si.save(ignore_permissions=True)
    frappe.db.commit()  


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



