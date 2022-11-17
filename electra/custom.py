from __future__ import unicode_literals
import frappe,erpnext
from frappe.utils import cint
import json
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
from frappe.model.mapper import get_mapped_doc
from frappe.utils.file_manager import get_file
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
import datetime
from datetime import datetime,timedelta
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

@frappe.whitelist()
def stock_popup(item_code):
    item = frappe.get_value('Item',{'item_code':item_code},'item_code')
    # item_price= frappe.get_value('Item Price',{item:'item_code'},'price_list_rate')
    data = ''
    stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
        where item_code = '%s' """%(item),as_dict=True)
    # frappe.errprint(stocks)
    # pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.amount as amount,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.company as company,`tabPurchase Order`.name as po from `tabPurchase Order`
    # left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
    # where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 1   order by amount desc limit 1"""%(item),as_dict=True)
    
   

    pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,`tabPurchase Order Item`.qty as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
    left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
    where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by rate asc limit 1""" % (item), as_dict=True)
    frappe.errprint(pos)
    data += '<table class="table table-bordered"><tr><th style="padding:1px;border: 1px solid black;color:white;background-color:orange" colspan=4><center>Stock Availability</center></th></tr>'
    data += '''
    <tr><td style="padding:1px;border: 1px solid black;width:300px" ><b>Item Code</b></td>
    <td style="padding:1px;border: 1px solid black;width:200px" colspan =3>%s</td></tr>
    <tr><td style="padding:1px;border: 1px solid black" ><b>Item Name</b></td>
    <td style="padding:1px;border: 1px solid black" colspan =3>%s</td></tr>
    <tr>
    <td style="padding:1px;border: 1px solid black;"  ><b>Warehouse</b></td>
    <td style="padding:1px;border: 1px solid black;max-width:50px"  ><b>QTY</b></td>
    <td style="padding:1px;border: 1px solid black;max-width:50px;" colspan ='1' ><b>Previous Purchase Order</b></td>
    <td style="padding:1px;border: 1px solid black;max-width:50px;" colspan ='1' ><b>PPQ</b></td></tr>'''%(item,frappe.db.get_value('Item',item,'item_name'))
   
    i = 0
    for po in pos:
        for stock in stocks:
            if stock.actual_qty > 0:
                if pos:
                    frappe.errprint(po.qty)
                    data += '''<tr>
                    <td style="padding:1px;border: 1px solid black" colspan =1>%s</td><td style="padding:1px;border: 1px solid black" colspan=1>%s</td>
                    <td style="padding:1px;border: 1px solid black" colspan=1>%s</td><td style="padding:1px;border: 1px solid black" colspan=1>%s</td></tr>'''%(stock.warehouse,stock.actual_qty,po.rate,po.qty)
                i += 1
    
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


# bundle = frappe.db.sql("""select `tabProduct Bundle Item`.item_code as item_code,`tabProduct Bundle Item`.description as description,
    #                         `tabProduct Bundle Item`.qty as qty from `tabProduct Bundle` left join `tabProduct Bundle Item` 
    #                         on `tabProduct Bundle`.name = `tabProduct Bundle Item`.parent where `tabProduct Bundle`.name ='%s' """%(item_code),as_dict=True)[0]
    
    # for bb in bundle:
    #     frappe.errprint(bb.item_code)
    #     doc.append("packed_items",{
    #         "item_code": bb.item_code,
    #         "description": bb.description,
    #         "qty": bb.qty * bun.qty,
    #         "parent_item":bun.item_code
    #     })




                   




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
def cancel_ce(doc,method):
    frappe.errprint("Cancelling CE")
    if doc.cost_estimation:
        cost_estimation = frappe.get_doc("Cost Estimation",{'quotation':doc.name})
        cost_estimation.cancel()

# @frappe.whitelist()
# def cancel_pb(doc,method):
#     frappe.errprint("Cancelling PB")
#     project_bud = frappe.get_doc("Project Budget",{'sales_order':doc.name})
#     project_bud.cancel()

@frappe.whitelist()
def amend_ce(doc,method):
    frappe.errprint("Amending CE")
    if doc.amended_from:
        ce_sow = frappe.get_all("CE SOW",{'cost_estimation':doc.amended_from},['name','cost_estimation'])
        for ce in ce_sow:
            ces = frappe.get_doc("CE SOW",{'name':ce.name,'cost_estimation':ce.cost_estimation})
            ces.cost_estimation = doc.name
            ces.save(ignore_permissions=True)

            
# @frappe.whitelist()
# def amend_pb(doc,method):
#     frappe.errprint("Amending PB")
#     if doc.amended_from:
#         pb_sow = frappe.get_all("PB SOW",{'project_budget':doc.amended_from},['name','project_budget'])
#         # frappe.errprint(pb_sow)
#         for pb in pb_sow:
#             pbs = frappe.get_doc("PB SOW",{'name':pb.name,'project_budget':pb.project_budget})
#             pbs.cost_estimation = doc.name
#             # frappe.errprint(pbs)
#             pbs.save(ignore_permissions=True)


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
    doc.employee_number = new
    doc.name = new
    # frappe.db.set_value('Job Offer',doc.name,'employee_number',new)
    # frappe.errprint(new)


@frappe.whitelist()
def record(name):
    maintenance = frappe.db.exists("Vehicle Maintenance Check List",{'name':name})
    if maintenance:
        main = frappe.db.get_all("Vehicle Maintenance Check List",{'name':name},['complaint','employee_id','vehicle_handover_date','garage_name'])[0]

    accident = frappe.db.exists("Vehicle Accident Report",{'plate_no':name})
    if accident:
        acc = frappe.db.get_all("Vehicle Accident Report",{'plate_no':name},['name','emp_id','date_of_accident','remarks'])[0]

        return main,acc

