from __future__ import unicode_literals
import json
import requests
from re import S
from unicodedata import name
from datetime import datetime
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
from datetime import date, timedelta
import calendar
from erpnext.stock.get_item_details import get_item_price
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.selling.doctype.customer.customer import get_customer_outstanding, get_credit_limit
from erpnext.stock.get_item_details import get_valuation_rate
from erpnext.setup.utils import get_exchange_rate
from frappe.utils.background_jobs import enqueue
from frappe.utils import (
    add_days,
    add_months,
    cint,
    date_diff,
    flt,
    get_first_day,
    get_last_day,
    get_link_to_form,
    getdate,
    rounded,
    today,
)
import json
from frappe.core.doctype.session_default_settings.session_default_settings import (
    clear_session_defaults,
    set_session_default_values,
)
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


@frappe.whitelist()
def update_outstanding_without_retention(doc,method):
    if doc.order_type == 'Project':
        doc.outstanding_amount__without_retention = doc.outstanding_amount
        
@frappe.whitelist()
def add_company_to_session_defaults(doc):
    default_company = frappe.get_value('User Permission',{'user':frappe.session.user,'allow':'Company','is_default':1},'for_value')
    if default_company:
        frappe.defaults.set_user_default("company", default_company)

@frappe.whitelist()
def set_cluster(sales_person):
    doc = frappe.get_value("Cluster",{"user":sales_person})
    if doc:
        return doc

@frappe.whitelist()
def get_dns(doc):
    dn = []
    sales_order = frappe.db.sql("""select sales_order as so from `tabSales Invoice Item` where parent = '%s' """ % doc,as_dict=1)
    if sales_order:
        for item in sales_order: 
            if item.so not in dn:
                if item.so:
                    dn.append(item)
    if len(dn) > 0:
        return dn
    else:
        return ''


@frappe.whitelist()
def get_sos(doc):
    dn = []
    sales_order = frappe.db.sql("""select delivery_note as dn from `tabSales Invoice Item` where parent = '%s' """ % doc,as_dict=1)
    if sales_order:
        for item in sales_order: 
            if item.dn not in dn:
                if item.dn:
                    dn.append(item.dn)
    if len(dn) > 0:
        return dn
    else:
        return ''

@frappe.whitelist()
def get_so_list():
    doc = "ITD-CRD-2023-00106"
    dn = []
    sales_order = frappe.db.sql("""select delivery_note as dn from `tabSales Invoice Item` where parent = '%s' """ % doc,as_dict=1)
    if sales_order:
        for item in sales_order: 
            if item.dn not in dn:
                if item.dn:
                    dn.append(item.dn)
    if len(dn) > 0:
        return dn
    else:
        return ''

    # frappe.log_error(title='dn_list',message=dn[0])
            
    # return sales_order


@frappe.whitelist()
def reset_general_entry_purchase_rate():
    last_purchase_rate = frappe.get_value('Item','001','last_purchase_rate')
    if last_purchase_rate:
        frappe.db.set_value('Item','001','last_purchase_rate',0.0)
        frappe.db.commit()

@frappe.whitelist()
def get_item_details(item_group=None,brand=None,item=None):
    if item_group and brand:
        filters = { 'item_group' : item_group,'brand' : brand }
    if brand:
        filters = { 'brand' : brand }
    if item_group:
        filters = { 'item_group' : item_group }
    if item:
        filters = {'item_code':item}  

    

    items = frappe.get_all("Item",fields=['item_code','stock_uom','item_name',],filters=filters)
    item_details = []
    for item in items:
        selling_price = 0.0
        item_price_args = {
                "item_code": item['item_code'],
                "price_list": "Standard Selling",
                "uom": item['stock_uom'],
                "batch_no": ""
                
        }
        item_code = item['item_code']
        item_price_list = frappe.db.get_value('Item Price',{'item_code':item_code},['name'])
        item_price = get_item_price(item_price_args,item_code,)
        if item_price:
            selling_price = item_price[0][1]
        item_detail = {
                "item_code": item['item_code'],
                "item_name": item['item_name'],
                "selling_price": selling_price,
                'item_marked':item_price_list
        }
        item_details.append(item_detail)
    return item_details


@frappe.whitelist()
def update_selling_price(update_selling_price,percentage):
    items = json.loads(update_selling_price)
    for i in items:
        if percentage:
            percent_calculate = i['selling_price']
            percent_value = percent_calculate * (1 +(int(percentage)/100))
            frappe.db.set_value("Item Price",i['item_marked'],'price_list_rate',percent_value)
            frappe.msgprint('Item Price Rate was updated')
        else:
            frappe.db.set_value('Item Price',i['item_marked'],'price_list_rate',i['selling_price'])
            frappe.msgprint(_('Item Price Rate was updated'))

       
    
@frappe.whitelist()
def fetch_credit_limit(company,customer,doctype):
    result = ""
    customer_type = frappe.db.get_value("Customer",customer,['customer_type'])
    customer_list = get_details(company,customer)
    if not customer_list and customer_type == "Company" and doctype != "Quotation":
        frappe.throw(_("Kindly Set the Credit Limit in Customer"))
    bypass_credit_limit_check = is_frozen = disabled = "No"
    customer_naming_type = frappe.db.get_value("Selling Settings", None, "cust_master_name")
    for d in customer_list:
        outstanding_amt = get_customer_outstanding(d.name, company,
                ignore_outstanding_sales_order=d.bypass_credit_limit_check_at_sales_order)
        credit_limit = get_credit_limit(d.name, company)
        bal = flt(credit_limit) - flt(outstanding_amt)
        if d.bypass_credit_limit_check:
            bypass_credit_limit_check = "Yes"
        if d.is_frozen:
            is_frozen = "Yes"
        if d.disabled:
            disabled = "Yes"
        if credit_limit and bal:
            result = '''
            <table class="table table-bordered">
            <tr>
                <td>Credit Limit</td>
                <td>Outstanding Amount</td>
                <td>Balance</td>
                <td>Bypassing Credit Limit Enabled ?</td>
                <td>Frozen ?</td>
                <td>Disabled ?</td>
            </tr>
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            
            </table>
            ''' %( credit_limit, outstanding_amt, bal,bypass_credit_limit_check,is_frozen,disabled )
        # else:
        #     result = "Empty"
        return result

def get_details(company,customer):
    sql_query = """SELECT
                        c.name, c.customer_name,
                        ccl.bypass_credit_limit_check,
                        c.is_frozen, c.disabled
                    FROM    `tabCustomer` c, `tabCustomer Credit Limit` ccl
                    WHERE
                        c.name = ccl.parent
                        AND ccl.company = '%s' AND c.name = '%s' """ % (company,customer)

    return frappe.db.sql(sql_query, as_dict=1)

@frappe.whitelist()
def get_wh(company):
    warehouses = frappe.get_list("Warehouse",{'company':company},['name'],ignore_permissions=True)
    wh_list = []
    for wh in warehouses:
        wh_list.append(wh['name'])
    return wh_list

@frappe.whitelist()
def get_last_valuation_rate(item_code,source_company):
    valuation_rate = 0
    source_warehouse = frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company': source_company }, ["name"])
    latest_vr = frappe.db.sql("""select valuation_rate as vr from tabBin
            where item_code = '%s' and warehouse = '%s' """%(item_code,source_warehouse),as_dict=True)
    # latest_vr = frappe.db.sql("""
    #             SELECT valuation_rate as vr FROM `tabStock Ledger Entry` WHERE item_code = %s AND company=%s AND valuation_rate > 0
    #             ORDER BY posting_date DESC, posting_time DESC, creation DESC LIMIT 1
    #             """, (item_code,source_warehouse),as_dict=True)
    if latest_vr:
        valuation_rate = latest_vr[0]["vr"]
    else:
        val_rate = []
        l_vr = frappe.db.sql("""select valuation_rate as vr from tabBin
                where item_code = '%s' """%(item_code),as_dict=True)
        for item in l_vr: 
            if item not in val_rate: 
                val_rate.append(item.vr)
        if len(val_rate) > 1 :
            valuation_rate = max(val_rate)
    return valuation_rate

@frappe.whitelist()
def make_sales_order(name):
    prepared_by,converted_by = frappe.db.get_value("Quotation",{'name':name},['user_id','converted_by']) 

    user_list=frappe._dict()
    user_list.update({
        "converted_by":converted_by,
        "prepared_by":prepared_by
    })
    return user_list

@frappe.whitelist()
def make_dnote(name):
    prepared_by,sales_person_user = frappe.db.get_value("Sales Order",{'name':name},['prepared_by','sales_person_user']) 

    user_list=frappe._dict()
    user_list.update({
        "sales_person_user":sales_person_user,
        "prepared_by":prepared_by
    })
    return user_list

@frappe.whitelist()
def make_dn(name):
    name =frappe.db.get_value("Sales Order",{'name':name},['name'])
    return name
# @frappe.whitelist()
# def get_dn_names(so_name):
#     name,sales_order =frappe.get_list("Delivery Invoice",{'name':name},['name','sales_order'])
#     frappe.errprint(name)
#     frappe.errprint(sales_order)
#     refer_list = frappe._dict()
#     refer_list.update({
#         'sales_invoice':name,
#         'dn':sales_order
#     })
#     return refer_list

# @frappe.whitelist()
# def make_qn(name):
#     frappe.errprint(name)
#     name = frappe.db.get_value('Opportunity',{'name':name},name)
#     return name



@frappe.whitelist()
def get_user_details(user):
    employee = frappe.get_value("Sales Person",user,['user_id'])
    employees = frappe.get_list("Employee",{'user_id':employee},['user_id','designation','cell_number'],ignore_permissions=True)
    employee_list = frappe._dict()
    for e in employees:
        employee_list.update({
            'user_id': e.user_id,
            'designation': e.designation,
            'cell_number': e.cell_number
        })
    return employee_list


@frappe.whitelist()
def get_user_detail(user):
    employees = frappe.get_list("Employee",{'user_id':user},['employee_name','designation','cell_number'],ignore_permissions=True)
    employee_list = frappe._dict()
    for e in employees:
        employee_list.update({
            'employee_name': e.employee_name,
            'designation': e.designation,
            'cell_number': e.cell_number
        })
    return employee_list

@frappe.whitelist()
def get_ce_msow(cost_estimation):
    return frappe.get_all("CE Master Scope of Work",{'parent':cost_estimation},['*'])


@frappe.whitelist()
def get_transfer(employee_transfer_id):
    return frappe.get_all("Employee Property History",{'parent':employee_transfer_id},['*'])

@frappe.whitelist()
def get_evaluation_period():
    return frappe.get_all("External Provider Evaluation",['*'])

@frappe.whitelist()
def get_evaluation_date(supplier):
    epef = frappe.get_all("External Provider Evaluation Form",{'external_provider':supplier},['max(re_evaluation_date) as re_evaluation_date'])[0]
    return epef['re_evaluation_date']


@frappe.whitelist()
def show_valuation_rate(items,company):
    import json
    items = json.loads(items)
    data = ''
    data += """<table class="table table-bordered">
                <tr><th style="padding:1px;border: 1px solid black" colspan=6><center>Itemwise Valuation Rate</center></th></tr>
                <tr>
                    <td style="padding:1px;border: 1px solid black"><b>Item Code</b></td>
                    <td style="padding:1px;border: 1px solid black"><b>Item Name</b></td>
                    <td style="padding:1px;border: 1px solid black"><b>Valuation Rate</b></td>
                </tr>"""
    for item in items:
        gvr = get_valuation_rate(item['item_code'], company)
        last_valuation_rate = frappe.db.sql("""
                SELECT valuation_rate FROM `tabStock Ledger Entry` WHERE item_code = %s AND valuation_rate > 0
                ORDER BY posting_date DESC, posting_time DESC, creation DESC LIMIT 1
                """, (item['item_code']))
        data += """
        <tr>
        <td style="padding:1px;border: 1px solid black">%s</td>
        <td style="padding:1px;border: 1px solid black">%s</td>
        <td style="padding:1px;border: 1px solid black">%s</td>
        </tr>""" % (item['item_code'],item['item_name'],last_valuation_rate[0][0])
    data += """</table>"""
    if items:
        return data

@frappe.whitelist()
def validate_sow(doc,method):
    sows = doc.scope_of_work
    if sows:
        for sow in sows:
            if sow.msow:
                if frappe.db.exists('Master Scope of Work',sow.msow):
                    msow_id = frappe.get_doc("Master Scope of Work",sow.msow)
                else:
                    msow_id = frappe.new_doc("Master Scope of Work")
                msow_id.scope_of_work = sow.msow
                msow_id.desc = sow.msow_desc
                msow_id.is_group = 1
                msow_id.save(ignore_permissions=True)
            # if sow.ssow:
            #     if frappe.db.exists('Sub Scope of Work',{"name":sow.ssow,"parent_scope_of_work":sow.msow}):
            #         ssow_id = frappe.get_doc("Sub Scope of Work",sow.ssow)
            #     else:	
            #         ssow_id = frappe.new_doc("Sub Scope of Work")
            #     ssow_id.scope_of_work = sow.ssow
            #     ssow_id.desc = sow.ssow_desc
            #     ssow_id.parent_scope_of_work = sow.msow
            #     ssow_id.save(ignore_permissions=True)

@frappe.whitelist()
def get_series(company,doctype):
    company_series = frappe.db.get_value("Company Series",{'company':company,'document_type':doctype},'series')
    return company_series

@frappe.whitelist()
def get_so_sow(sales_order,msow):
    so_sow = frappe.get_all("SO Scope of Work",{'parent':sales_order,'msow':msow},['*'])
    return so_sow

@frappe.whitelist()
def get_ce_sow(cost_estimation,msow):
    ce_sow = frappe.get_all("CE Master Scope of Work",{'parent':cost_estimation,'msow':msow},['*'])
    return ce_sow

    

@frappe.whitelist()
def add_quotation_ce(doc,method):
    if doc.cost_estimation:
        frappe.db.set_value('Cost Estimation',doc.cost_estimation,'quotation',doc.name)
        frappe.db.commit()

        
@frappe.whitelist()
def validate_opportunity_sow(doc,method):
    sows = doc.scope_of_work
    for sow in sows:
        if sow.msow:
            if frappe.db.exists('Master Scope of Work',sow.msow):
                msow_id = frappe.get_doc("Master Scope of Work",sow.msow)
            else:
                msow_id = frappe.new_doc("Master Scope of Work")
            msow_id.master_scope_of_work = sow.msow
            msow_id.desc = sow.msow_desc
            msow_id.save(ignore_permissions=True)

@frappe.whitelist()
def set_income_account(doc,method):
    if doc.invoice_type == 'Cash':
        short_code = frappe.get_value('Company',doc.company,'abbr')
        for it in doc.items:
            it.income_account = 'Sales - Cash - '+short_code

@frappe.whitelist()
def item_default_wh(doc,method):
    item_default_set = frappe.get_value('Item',doc.item_code,'item_default_set')
    if not item_default_set:
        companies = [
            {"company":"KINGFISHER - TRANSPORTATION","default_warehouse":"Kingfisher Transportation Warehouse - KT", "buying_cost_center" : "Main - KT", "selling_cost_center" : "Main - KT","expense_account": "Cost of Goods Sold - KT","income_account":"Sales - Credit - KT"},
            {"company":"STEEL DIVISION - ELECTRA","default_warehouse":"Steel Warehouse - SDE", "buying_cost_center" : "Main - SDE", "selling_cost_center" : "Main - SDE","expense_account": "5111 - Cost of Goods Sold - SDE","income_account":"Sales - Credit - SDE"},
            {"company":"MARAZEEM SECURITY SERVICES - HO","default_warehouse":"Marazeem HO Warehouse - MSSHO", "buying_cost_center" : "Main - MSSHO", "selling_cost_center" : "Main - MSSHO","expense_account": "5111 - Cost of Goods Sold - MSSHO","income_account":"Sales - Credit - MSSHO"},
            {"company":"TRADING DIVISION - ELECTRA","default_warehouse":"Electra Trading Warehouse - TDE", "buying_cost_center" : "Main - TDE", "selling_cost_center" : "Main - TDE","expense_account": "5111 - Cost of Goods Sold - TDE","income_account":"Sales - Credit - TDE"},
            {"company":"MEP DIVISION - ELECTRA","default_warehouse":"Electra MEP Warehouse - MEP", "buying_cost_center" : "Main - MEP", "selling_cost_center" : "Main - MEP","expense_account": "5111 - Cost of Goods Sold - MEP","income_account":"Sales - Credit - MEP"},
            {"company":"ELECTRA - BINOMRAN SHOWROOM","default_warehouse":"Electra Binomran Showroom Warehouse - EBO", "buying_cost_center" : "Main - EBO", "selling_cost_center" : "Main - EBO","expense_account": "5111 - Cost of Goods Sold - EBO","income_account":"Sales - Credit - EBO"},
            {"company":"KINGFISHER TRADING AND CONTRACTING COMPANY","default_warehouse":"Kingfisher Warehouse - KTCC", "buying_cost_center" : "Main - KTCC", "selling_cost_center" : "Main - KTCC","expense_account": "Cost of Goods Sold - KTCC","income_account":"Sales - Credit - KTCC"},
            {"company":"KINGFISHER - SHOWROOM","default_warehouse":"Kingfisher Showroom Warehouse - KS", "buying_cost_center" : "Main - KS", "selling_cost_center" : "Main - KS","expense_account": "Cost of Goods Sold - KS","income_account":"Sales - Credit - KS"},
            {"company":"MARAZEEM SECURITY SERVICES - SHOWROOM","default_warehouse":"Marazeem Showroom - MSSS", "buying_cost_center" : "Main - MSSS", "selling_cost_center" : "Main - MSSS","expense_account": "5111 - Cost of Goods Sold - MSSS","income_account":"Sales - Credit - MSSS"},
            {"company":"MARAZEEM SECURITY SERVICES","default_warehouse":"Marazeem Warehouse - MSS", "buying_cost_center" : "Main - MSS", "selling_cost_center" : "Main - MSS","expense_account": "5111 - Cost of Goods Sold - MSS","income_account":"Sales - Credit - MSS"},
            {"company":"ELECTRA - BARWA SHOWROOM","default_warehouse":"Barwa Showroom  - EBS", "buying_cost_center" : "Main - EBS", "selling_cost_center" : "Main - EBS","expense_account": "5111 - Cost of Goods Sold - EBS","income_account":"Sales - Credit - EBS"},
            {"company":"ELECTRA  - NAJMA SHOWROOM","default_warehouse":"Electra Najma Showroom Warehouse - ENS", "buying_cost_center" : "Main - ENS", "selling_cost_center" : "Main - ENS","expense_account": "5111 - Cost of Goods Sold - ENS","income_account":"Sales - Credit - ENS"},
            {"company":"ELECTRA - ALKHOR SHOWROOM","default_warehouse":"Alkhor Showroom Warehouse - EAS", "buying_cost_center" : "Main - EAS", "selling_cost_center" : "Main - EAS","expense_account": "5111 - Cost of Goods Sold - EAS","income_account":"Sales - Credit - EAS"},
            {"company":"INDUSTRIAL TOOLS DIVISION","default_warehouse":"Electra Industrial Tools Warehouse - ITD", "buying_cost_center" : "Main - ITD", "selling_cost_center" : "Main - ITD","expense_account": "5111 - Cost of Goods Sold - ITD","income_account":"Sales - Credit - ITD"},
            {"company":"ELECTRICAL DIVISION - ELECTRA","default_warehouse":"Electra Electrical Warehouse - EDE", "buying_cost_center" : "Main - EDE", "selling_cost_center" : "Main - EDE","expense_account": "5111 - Cost of Goods Sold - EDE","income_account":"Sales - Credit - EDE"},
            {"company":"ENGINEERING DIVISION - ELECTRA","default_warehouse":"Electra Engineering Warehouse - EED", "buying_cost_center" : "Main - EED", "selling_cost_center" : "Main - EED","expense_account": "5111 - Cost of Goods Sold - EED","income_account":"Sales - Credit - EED"},
            {"company": "INTERIOR DIVISION - ELECTRA","default_warehouse":"Electra Interior Warehouse - INE", "buying_cost_center" : "Main - INE", "selling_cost_center" : "Main - INE","expense_account": "5111 - Cost of Goods Sold - INE","income_account":"Sales - Credit - INE"},
            {"company" :"Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)","default_warehouse":"Electra Warehouse - ASTCC", "buying_cost_center" : "Main - ASTCC", "selling_cost_center" : "Main - ASTCC","expense_account": "5111 - Cost of Goods Sold - ASTCC","income_account":"Sales - Credit - ASTCC"}
                    ]
        for company in companies:
            item_default = frappe.db.exists('Item Default',{'parent':doc.item_code,'company':company['company']},'parent')
            if not item_default:
                itemid = frappe.get_doc("Item",doc.item_code)
                itemid.item_default_set = 1
                itemid.append('item_defaults',{
                    'company':company['company'],
                    'default_warehouse':company['default_warehouse'],
                    'buying_cost_center':company['buying_cost_center'],
                    'selling_cost_center':company['selling_cost_center'],
                    'expense_account':company['expense_account'],
                    'income_account':company['income_account'],
                })
                itemid.save(ignore_permissions=True)
            else:
                frappe.db.set_value('Item Default',{'parent':itemid.name,'company':company['company']},'default_warehouse',company['default_warehouse'])
                frappe.db.set_value('Item Default',{'parent':itemid.name,'company':company['company']},'buying_cost_center',company['buying_cost_center'])
                frappe.db.set_value('Item Default',{'parent':itemid.name,'company':company['company']},'selling_cost_center',company['selling_cost_center'])
                frappe.db.set_value('Item Default',{'parent':itemid.name,'company':company['company']},'expense_account',company['expense_account'])
                frappe.db.set_value('Item Default',{'parent':itemid.name,'company':company['company']},'income_account',company['income_account'])
        frappe.db.set_value('Item',doc.item_code,"item_default_set",1)
        
@frappe.whitelist()
def enqueue_default_wh():
    enqueue(method=mark_default_wh, queue='long', timeout=9000, is_async=True)

@frappe.whitelist()
def mark_default_wh():
    frappe.db.auto_commit_on_many_writes = 1
    # item_default = frappe.new_doc("Item Default")
    companies = [
            {"company":"KINGFISHER - TRANSPORTATION","default_warehouse":"Kingfisher Transportation Warehouse - KT", "buying_cost_center" : "Main - KT", "selling_cost_center" : "Main - KT","expense_account": "Cost of Goods Sold - KT","income_account":"Sales - Credit - KT"},
            {"company":"STEEL DIVISION - ELECTRA","default_warehouse":"Steel Warehouse - SDE", "buying_cost_center" : "Main - SDE", "selling_cost_center" : "Main - SDE","expense_account": "5111 - Cost of Goods Sold - SDE","income_account":"Sales - Credit - SDE"},
            {"company":"MARAZEEM SECURITY SERVICES - HO","default_warehouse":"Marazeem HO Warehouse - MSSHO", "buying_cost_center" : "Main - MSSHO", "selling_cost_center" : "Main - MSSHO","expense_account": "5111 - Cost of Goods Sold - MSSHO","income_account":"Sales - Credit - MSSHO"},
            {"company":"TRADING DIVISION - ELECTRA","default_warehouse":"Electra Trading Warehouse - TDE", "buying_cost_center" : "Main - TDE", "selling_cost_center" : "Main - TDE","expense_account": "5111 - Cost of Goods Sold - TDE","income_account":"Sales - Credit - TDE"},
            {"company":"MEP DIVISION - ELECTRA","default_warehouse":"Electra MEP Warehouse - MEP", "buying_cost_center" : "Main - MEP", "selling_cost_center" : "Main - MEP","expense_account": "5111 - Cost of Goods Sold - MEP","income_account":"Sales - Credit - MEP"},
            {"company":"ELECTRA - BINOMRAN SHOWROOM","default_warehouse":"Electra Binomran Showroom Warehouse - EBO", "buying_cost_center" : "Main - EBO", "selling_cost_center" : "Main - EBO","expense_account": "5111 - Cost of Goods Sold - EBO","income_account":"Sales - Credit - EBO"},
            {"company":"KINGFISHER TRADING AND CONTRACTING COMPANY","default_warehouse":"Kingfisher Warehouse - KTCC", "buying_cost_center" : "Main - KTCC", "selling_cost_center" : "Main - KTCC","expense_account": "Cost of Goods Sold - KTCC","income_account":"Sales - Credit - KTCC"},
            {"company":"KINGFISHER - SHOWROOM","default_warehouse":"Kingfisher Showroom Warehouse - KS", "buying_cost_center" : "Main - KS", "selling_cost_center" : "Main - KS","expense_account": "Cost of Goods Sold - KS","income_account":"Sales - Credit - KS"},
            {"company":"MARAZEEM SECURITY SERVICES - SHOWROOM","default_warehouse":"Marazeem Showroom - MSSS", "buying_cost_center" : "Main - MSSS", "selling_cost_center" : "Main - MSSS","expense_account": "5111 - Cost of Goods Sold - MSSS","income_account":"Sales - Credit - MSSS"},
            {"company":"MARAZEEM SECURITY SERVICES","default_warehouse":"Marazeem Warehouse - MSS", "buying_cost_center" : "Main - MSS", "selling_cost_center" : "Main - MSS","expense_account": "5111 - Cost of Goods Sold - MSS","income_account":"Sales - Credit - MSS"},
            {"company":"ELECTRA - BARWA SHOWROOM","default_warehouse":"Barwa Showroom  - EBS", "buying_cost_center" : "Main - EBS", "selling_cost_center" : "Main - EBS","expense_account": "5111 - Cost of Goods Sold - EBS","income_account":"Sales - Credit - EBS"},
            {"company":"ELECTRA  - NAJMA SHOWROOM","default_warehouse":"Electra Najma Showroom Warehouse - ENS", "buying_cost_center" : "Main - ENS", "selling_cost_center" : "Main - ENS","expense_account": "5111 - Cost of Goods Sold - ENS","income_account":"Sales - Credit - ENS"},
            {"company":"ELECTRA - ALKHOR SHOWROOM","default_warehouse":"Alkhor Showroom Warehouse - EAS", "buying_cost_center" : "Main - EAS", "selling_cost_center" : "Main - EAS","expense_account": "5111 - Cost of Goods Sold - EAS","income_account":"Sales - Credit - EAS"},
            {"company":"INDUSTRIAL TOOLS DIVISION","default_warehouse":"Electra Industrial Tools Warehouse - ITD", "buying_cost_center" : "Main - ITD", "selling_cost_center" : "Main - ITD","expense_account": "5111 - Cost of Goods Sold - ITD","income_account":"Sales - Credit - ITD"},
            {"company":"ELECTRICAL DIVISION - ELECTRA","default_warehouse":"Electra Electrical Warehouse - EDE", "buying_cost_center" : "Main - EDE", "selling_cost_center" : "Main - EDE","expense_account": "5111 - Cost of Goods Sold - EDE","income_account":"Sales - Credit - EDE"},
            {"company":"ENGINEERING DIVISION - ELECTRA","default_warehouse":"Electra Engineering Warehouse - EED", "buying_cost_center" : "Main - EED", "selling_cost_center" : "Main - EED","expense_account": "5111 - Cost of Goods Sold - EED","income_account":"Sales - Credit - EED"},
            {"company": "INTERIOR DIVISION - ELECTRA","default_warehouse":"Electra Interior Warehouse - INE", "buying_cost_center" : "Main - INE", "selling_cost_center" : "Main - INE","expense_account": "5111 - Cost of Goods Sold - INE","income_account":"Sales - Credit - INE"},
            {"company" :"Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)","default_warehouse":"Electra Warehouse - ASTCC", "buying_cost_center" : "Main - ASTCC", "selling_cost_center" : "Main - ASTCC","expense_account": "5111 - Cost of Goods Sold - ASTCC","income_account":"Sales - Credit - ASTCC"}
                    ]

    items = frappe.get_all('Item')
    for item in items:
        print(item)
        for company in companies:
            item_default = frappe.db.exists('Item Default',{'parent':item.name,'company':company['company']},'parent')
            if not item_default:
                itemid = frappe.get_doc("Item",item.name)
                itemid.shelf_life_in_days = 0
                itemid.append('item_defaults',{
                    'company':company['company'],
                    'default_warehouse':company['default_warehouse'],
                    'buying_cost_center':company['buying_cost_center'],
                    'selling_cost_center':company['selling_cost_center'],
                    'expense_account':company['expense_account'],
                    'income_account':company['income_account']
                })
                itemid.flags.ignore_mandatory = True
                itemid.save(ignore_permissions=True)
                frappe.db.commit()
            else:
                frappe.db.set_value('Item Default',{'parent':item.name,'company':company['company']},'default_warehouse',company['default_warehouse'])
                frappe.db.set_value('Item Default',{'parent':item.name,'company':company['company']},'buying_cost_center',company['buying_cost_center'])
                frappe.db.set_value('Item Default',{'parent':item.name,'company':company['company']},'selling_cost_center',company['selling_cost_center'])
                frappe.db.set_value('Item Default',{'parent':item.name,'company':company['company']},'expense_account',company['expense_account'])
                frappe.db.set_value('Item Default',{'parent':item.name,'company':company['company']},'income_account',company['income_account'])
                frappe.db.commit()
        # frappe.db.set_value('Item',item.name,"item_default_set",1)
    frappe.db.auto_commit_on_many_writes = 0

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_company_users(doctype, txt, searchfield, start, page_len, filters):
    cond = ''
    if filters and filters.get('company'):
        parent_company = frappe.db.get_value('Company',{'name': filters.get('company')}, 'parent_company')
    query = frappe.db.sql(
        """select u.name from `tabUser` u inner join `tabEmployee` e on e.user_id = u.name 
            and e.company in ('%s','%s') """ %(filters.get('company'),parent_company)
                    )
    return query

@frappe.whitelist()
def create_project_warehouse(doc,method):
    parent_warehouse = frappe.get_value("Warehouse",{"company":doc.company,"is_group": 1})
    if not frappe.db.exists('Warehouse',doc.name):
        wh = frappe.new_doc("Warehouse")
        wh.update({
            "warehouse_name" : doc.name +" - "+ doc.project_name,
            "project_name":doc.name,
            "company": doc.company,
            "parent_warehouse": parent_warehouse
        })
        wh.save(ignore_permissions=True)

@frappe.whitelist()
def manpower_avg_cost_calculation(doc,method):
    designation = doc.designation
    if designation:
        avg_phc = 0
        total_per_hour_cost = frappe.get_all("Employee",{'status': 'Active','designation':designation},['sum(per_hour_cost) as phc'])
        employees = frappe.db.count("Employee",{'status': 'Active','designation':designation},['name'])
        if employees:
            avg_phc = total_per_hour_cost[0]['phc'] / employees
        frappe.db.set_value("Designation",designation,"per_hour_cost",avg_phc)
        frappe.db.commit()


@frappe.whitelist()
def bulk_manpower_avg_cost_calculation():
    designations = frappe.get_all('Designation')
    for designation in designations:
        designation = designation['name']
        if designation:
            avg_phc = 0
            total_per_hour_cost = frappe.get_all("Employee",{'status': 'Active','designation':designation},['sum(per_hour_cost) as phc'])
            employees = frappe.db.count("Employee",{'status': 'Active','designation':designation},['name'])
            if employees:
                avg_phc = total_per_hour_cost[0]['phc'] / employees
            frappe.db.set_value("Designation",designation,"per_hour_cost",avg_phc)
            frappe.db.commit()

@frappe.whitelist()
def create_project_from_so(doc,method):
    if doc.order_type == 'Project':
        series = get_series(doc.company,"Project")
        project = frappe.new_doc("Project")
        project.update({
            "company": doc.company,
            "naming_series": get_series(doc.company,"Project"),
            "project_name": doc.title_of_project,
            "customer":doc.customer,
            "sales_order":doc.name,
            "budgeting": frappe.get_value("Project Budget",{"sales_order":doc.name},"name")
        })
        project.save(ignore_permissions=True)
        frappe.db.commit()
        bom = frappe.db.get_list("BOM",{"project_budget":doc.project_budget},["name"])
        if bom:
            for i in bom:
                bo = frappe.get_doc("BOM",i.name)
                bo.project = project.name
                bo.save(ignore_permissions=True) 

@frappe.whitelist(allow_guest=True)
def ping():
    return 'Pong'


@frappe.whitelist()
def submit_dummy_dn(doc,method):
    if doc.grand_total <= 0 and doc.dummy_dn == 0 and not doc.is_return:
        frappe.throw("Cannot deliver with zero rate unless it is a dummy DN")

# @frappe.whitelist()
# def stockpopup(item_code):
#     item = frappe.get_value('Item',{'item_code':item_code},'item_code')
#     stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
#         where item_code = '%s' """%(item),as_dict=True)
#     frappe.errprint(stocks[8])
#     data = ''
#     data += '<table class="table table-bordered"><tr><th style="padding:1px;border:1px solid black;font-size:14px;background-color:#e35310;color:white;" colspan=8><center><b>STOCK DETAILS</b></center></th></tr>'
#     data += '<tr><td colspan=1 style="border: 1px solid black;font-size:12px;"><center><b>ITEM CODE</b><center></td></tr>'
#     data += '<tr><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s<center><center></td></tr>'%(stocks[2])
#     data += '</table>'
#     return item

@frappe.whitelist()
def get_stock_details(item_details,company):
    item_details = json.loads(item_details)
    data = ''
    data += '<table class="table table-bordered"><tr><th style="padding:1px;border:1px solid black;font-size:14px;background-color:#e35310;color:white;" colspan=8><center><b>STOCK DETAILS</b></center></th></tr>'
    data +='<tr><td colspan=1 style="border: 1px solid black;font-size:12px;"><center><b>ITEM CODE</b><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center><b>ITEM NAME</b><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center><b>IN WAREHOUSE</b><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center><b>IN TRANSIT</b><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center><b>TOTAL</b><center></td></tr>'
    
    for j in item_details:
        country = frappe.get_value("Company",{"name":company},["country"])
        warehouse_stock = frappe.db.sql("""
        select sum(b.actual_qty) as qty from `tabBin` b 
        join `tabWarehouse` wh on wh.name = b.warehouse
        join `tabCompany` c on c.name = wh.company
        where c.country = '%s' and b.item_code = '%s'
        """ % (country,j["item_code"]),as_dict=True)[0]
        if not warehouse_stock["qty"]:
            warehouse_stock["qty"] = 0
        purchase_order = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty from `tabPurchase Order`
                left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
                where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 """%(j["item_code"]),as_dict=True)[0] or 0 
        if not purchase_order["qty"]:
            purchase_order["qty"] = 0
        purchase_receipt = frappe.db.sql("""select sum(`tabPurchase Receipt Item`.qty) as qty from `tabPurchase Receipt`
                left join `tabPurchase Receipt Item` on `tabPurchase Receipt`.name = `tabPurchase Receipt Item`.parent
                where `tabPurchase Receipt Item`.item_code = '%s' and `tabPurchase Receipt`.docstatus = 1 """%(j["item_code"]),as_dict=True)[0] or 0 
        if not purchase_receipt["qty"]:
            purchase_receipt["qty"] = 0
        in_transit = purchase_order["qty"] - purchase_receipt["qty"]
        total = warehouse_stock["qty"] + in_transit
        data+='<tr><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s<center><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s<center><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s<center><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td></tr>'%(j["item_code"],j["item_name"],warehouse_stock["qty"], in_transit,total)
    
    data += '</table>'
    return data

@frappe.whitelist()
def getstock_detail(item_details,company):
    item_details = json.loads(item_details)
    data = ''
    data += '<h4><center><b>STOCK DETAILS</b></center></h4>'
    data += '<h6>Note:</h6>'
    data += '<table style = font-size:10px width=100% ><tr><td>Electra Interior Warehouse - <b>INE</b></td><td>Kingfisher Transportation Warehouse - <b>KT</b></td><td>Steel Warehouse - <b>SDE</b></td><td>Marazeem HO Warehouse - <b>MSSHO</b></td><td>Electra Trading Warehouse - <b>TDE</b></td></tr>'
    data += '<tr><td>Electra Warehouse - <b>ASTCC</b></td><td>Electra Binomran Showroom Warehouse - <b>EBO</b></td><td>Kingfisher Warehouse - <b>KTCC</b></td><td>Kingfisher Showroom Warehouse - <b>KS</b></td><td>Marazeem Showroom - <b>MSSS</b></td></tr>'
    data += '<tr><td>Electra Najma Showroom Warehouse - <b> ENS</b></td><td>Marazeem Warehouse - <b>MSS</b></td><td>Barwa Showroom  - <b>EBS</b></td><td>Electra Electrical Warehouse - <b>EDE</b></td><td>Electra Engineering Warehouse - <b>EED</b></td></tr>'
    data += '</table>'
    for j in item_details:
        country = frappe.get_value("Company",{"name":company},["country"])

        warehouse_stock = frappe.db.sql("""
        select sum(b.actual_qty) as qty from `tabBin` b join `tabWarehouse` wh on wh.name = b.warehouse join `tabCompany` c on c.name = wh.company where c.country = '%s' and b.item_code = '%s'
        """ % (country,j["item_code"]),as_dict=True)[0]

        if not warehouse_stock["qty"]:
            warehouse_stock["qty"] = 0
        
        
        new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order` 
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (j["item_code"]), as_dict=True)[0]
        if not new_po['qty']:
            new_po['qty'] = 0
        if not new_po['d_qty']:
            new_po['d_qty'] = 0
        in_transit = new_po['qty'] - new_po['d_qty']


        
        total = warehouse_stock["qty"] + in_transit

        stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
        where item_code = '%s' """%(j["item_code"]),as_dict=True)

        pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,sum(`tabPurchase Order Item`.qty) as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by rate asc limit 1""" % (j["item_code"]), as_dict=True)
    
        new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
        left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
        where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1  """ % (j["item_code"]), as_dict=True)[0]
        if not new_so['qty']:
            new_so['qty'] = 0
        if not new_so['d_qty']:
            new_so['d_qty'] = 0
        del_total = new_so['qty'] - new_so['d_qty']
            
        
        i = 0
        for po in pos:
            if pos:
                data += '<table class="table table-bordered">'
                data += '<tr>'
                data += '<td colspan=1 style="width:13%;padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>ITEM CODE</b><center></td>'
                data += '<td colspan=1 style="width:33%;padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>ITEM NAME</b><center></td>'
                data += '<td colspan=1 style="width:70px;padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>STOCK</b><center></td>'

                for stock in stocks:
                    if stock.actual_qty > 0:
                        wh = stock.warehouse
                        x = wh.split('- ')
                        data += '<td colspan=1 style="width:70px;padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>%s</b><center></td>'%(x[-1])
                data += '<td colspan=1 style="padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>PENDING TO RECEIVE</b><center></td>'
                data += '<td colspan=1 style="padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>PENDING TO SELL</b><center></td>'
                data += '</tr>'
                
                
                
                data +='<tr>'
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(j["item_code"])
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(j["item_name"])
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(warehouse_stock['qty'] or 0)
                for stock in stocks:
                    if stock.actual_qty > 0:
                        data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(stock.actual_qty)
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(in_transit or 0)
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(del_total or 0)
                data += '</tr>'
            i += 1
        data += '</table>'
            
    return data


@frappe.whitelist()
def detail_stock(item_details, company):
    item_details = json.loads(item_details)
    frappe.errprint(item_details)
    data = ''
    data += '<h4><center><b>STOCK DETAILS</b></center></h4>'
    data += '<h6>Note:</h6>'
    

    data += '<table style = font-size:10px width=100% ><tr><td>Electra Warehouse - <b>ASTCC</b></td><td>Electra Trading Warehouse - <b>TDE</b></td><td>Electra Interior Warehouse - <b>INE</b></td><td>Steel Warehouse - <b>SDE</b></td><td>Electra Electrical Warehouse - <b>EDE</b></td></tr>'
    data += '<tr><td>Electra Engineering Warehouse - <b>EED</b></td><td>Barwa Showroom  - <b>EBS</b></td><td>Electra Najma Showroom Warehouse - <b> ENS</b></td><td>Electra Binomran Showroom Warehouse - <b>EBO</b></td><td>Alkhor Showroom Warehouse - <b>EAS</b></td></tr>'
    data += '<tr><td>Electra Industrial Tools Warehouse - <b> ITD</b></td><td>Kingfisher Showroom Warehouse - <b>KS</b></td><td>Kingfisher Transportation Warehouse - <b>KT</b></td><td>Kingfisher Warehouse - <b>KTCC</b></td><td>Marazeem HO Warehouse - <b>MSSHO</b></td></tr>'
    data += '<tr><td>Marazeem Warehouse - <b>MSS</b></td><td>Marazeem Showroom - <b>MSSS</b></td></tr>'


    
    data += '</table>'
    data += '<table class="table table-bordered" style = font-size:10px>'
    data += '<td colspan=1 style="width:12%;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>ITEM CODE</b></center></td>'
    data += '<td colspan=1 style="width:20%;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>ITEM NAME</b></center></td>'
    data += '<td colspan=1 style="width:70px;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>STOCK</b></center></td>'
    comp = frappe.db.get_list("Company","name")
    for co in comp:
        st = 0
        ware = frappe.db.get_list("Warehouse",{"company":co.name,"default_for_stock_transfer":1},['name'])
        for w in ware:
            frappe.errprint(w)

            data += '<td colspan=1 style="width:70px;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>%s</b></center></td>'%(w.name.split("-")[-1]) 
    data += '<td colspan=1 style="width:180px;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>TO RECEIVE</b></center></td>'
    data += '<td colspan=1 style="width:180px;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>TO SELL</b></center></td>'
    warehouses = []  
    for j in item_details:
        country = frappe.get_value("Company",{"name":company},["country"])

        warehouse_stock = frappe.db.sql("""
        select sum(b.actual_qty) as qty from `tabBin` b join `tabWarehouse` wh on wh.name = b.warehouse join `tabCompany` c on c.name = wh.company where c.country = '%s' and b.item_code = '%s'
        """ % (country,j["item_code"]),as_dict=True)[0]

        if not warehouse_stock["qty"]:
            warehouse_stock["qty"] = 0
        
        
        new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order` 
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (j["item_code"]), as_dict=True)[0]
        if not new_po['qty']:
            new_po['qty'] = 0
        if not new_po['d_qty']:
            new_po['d_qty'] = 0
        in_transit = new_po['qty'] - new_po['d_qty']


        
        total = warehouse_stock["qty"] + in_transit

        stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
        where item_code = '%s' """%(j["item_code"]),as_dict=True)

        pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,sum(`tabPurchase Order Item`.qty) as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by rate asc limit 1""" % (j["item_code"]), as_dict=True)
    
        new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
        left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
        where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1  """ % (j["item_code"]), as_dict=True)[0]
        if not new_so['qty']:
            new_so['qty'] = 0
        if not new_so['d_qty']:
            new_so['d_qty'] = 0
        del_total = new_so['qty'] - new_so['d_qty']
        i = 0
        for po in pos:
            data += '<tr>'
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (j["item_code"])
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (j["item_name"])
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (warehouse_stock['qty'] or 0)
            comp = frappe.db.get_list("Company","name")
            for co in comp:
                st = 0
                ware = frappe.db.get_list("Warehouse",{"company":co.name,"default_for_stock_transfer":1},['name'])
                for w in ware:
                    sto = frappe.db.get_value("Bin",{"item_code":j["item_code"],"warehouse":w.name},['actual_qty'])
                    if not sto:
                        sto = 0
                    st += sto
                    data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' %(st)
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(in_transit or 0)
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(del_total or 0)
            data += '</tr>'
        i += 1
    data += '</tr>'
    data += '</table>'
    return data




@frappe.whitelist()
def get_item_margin(item_details,company,discount_amount):
    item_details = json.loads(item_details)
    data_4 = ''
    data_4 += '''<table class="table">
    <tr>
    <th style="padding:1px;border: 1px solid black;font-size:14px;background-color:#FF4500;color:white;" colspan =9 ><center><b>MARGIN</b></center></th>
    </tr>'''

    data_4+='''<tr>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b>ITEM</b></td>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b>ITEM NAME</b></td>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>QTY</center></b></td>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Cost</center></b></td>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Rate</center></b></td>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Cost Amount</center></b></td>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Selling Amount</center></b></td>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Profit Amount</center></b></td>
    <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Profit %</center></b></td>
    </tr>'''
    cost_amount = 0
    total_selling_price = 0
    rate = 0
    cost = 0
    selling_amount = 0
    profit_amount_ = 0
    selling_amount_ = 0
    qty_tot = 0
    tot_per = 0
    no_item = 0
    for i in item_details:
        qty_tot += i["qty"]
        rate += i["base_net_rate"]
        selling_amount += i["base_net_amount"]
        total_selling_price =  (i["base_net_rate"] * i["qty"]) + total_selling_price
        warehouse_stock = frappe.db.sql("""
        select valuation_rate as vr from `tabBin` b 
        join `tabWarehouse` wh on wh.name = b.warehouse
        join `tabCompany` c on c.name = wh.company
        where b.item_code = '%s'
        """ % (i["item_code"]),as_dict=True)[0]
        cost += warehouse_stock.vr 
        if not warehouse_stock.vr :
            warehouse_stock.vr  = 0
        cost_amount = (warehouse_stock.vr  * i["qty"]) + cost_amount
        cost_amount_ = (warehouse_stock.vr * i["qty"])
        
        tot =  cost_amount - total_selling_price
        tot_diff =  cost_amount_ - i["base_net_amount"]
        
        if cost_amount_ > 0:
            tot_ = tot_diff/cost_amount_ *100
            tot_per += tot_
            data_4+='''<tr>
            <td colspan=1 style="border: 1px solid black;font-size:12px;">%s</td>
            <td colspan=1 style="border: 1px solid black;font-size:12px;">%s</td>
            <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
            <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
            <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
            <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
            <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
            <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
            <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
            </tr>'''%(i["item_code"],i["description"],i["qty"],round(warehouse_stock.vr,2) ,round(i["base_net_rate"],2),round(cost_amount_,2),round(i["base_net_amount"],2),round(-tot_diff,2),round(-tot_,2))
    
    if cost_amount_ == 0:
        total_margin_internal = (total_selling_price - cost_amount_)/100

    else:
        total_margin_internal = (-tot / cost_amount)*100

        data_4 += '''<tr>
        <td colspan=2 style="border: 1px solid black;padding:1px;font-size:14px;text-align: right"><b>Total </b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        </tr>'''%(qty_tot,round(cost,2),round(rate,2),round(cost_amount,2),round(selling_amount,2),round(-tot,2),round(total_margin_internal,2))
        
        total_amount = float(discount_amount) + float(selling_amount)
        data_4+= '''<tr>
        <td colspan=2 style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>Before Applying Discount</b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        <td colspan=2 style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>Discount Amount </b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        <td colspan=2 style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>After Applying Discount</b></td>
        <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        </tr>'''%(total_amount,discount_amount,selling_amount)
        
    
    return data_4



# @frappe.whitelist()
# def get_item_margin_percentage_calculation(item_details,company,profit):
#     profit_per = int(profit)
#     item_details = json.loads(item_details)
#     data_4 = ''
#     data_4 += '''<table class="table">
#     <tr>
#     <th style="padding:1px;border: 1px solid black;font-size:14px;background-color:#FF4500;color:white;" colspan =9 ><center><b>MARGIN</b></center></th>
#     </tr>'''

#     data_4+='''<tr>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b>ITEM</b></td>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b>ITEM NAME</b></td>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>QTY</center></b></td>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Cost</center></b></td>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Rate</center></b></td>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Cost Amount</center></b></td>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Selling Amount</center></b></td>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Profit Amount</center></b></td>
#     <td colspan=1 style="border: 1px solid black;font-size:12px;"><b><center>Profit %</center></b></td>
#     </tr>'''
#     cost_amount = 0
#     total_selling_price = 0
#     rate = 0
#     cost = 0
#     selling_amount = 0
#     profit_amount_ = 0
#     selling_amount_ = 0
#     qty_tot = 0
#     for i in item_details:
#         qty_tot += i["qty"]
#         rate += i["rate"]
#         selling_amount += i["base_amount"]
#         total_selling_price =  (i["rate"] * i["qty"]) + total_selling_price
#         frappe.errprint(total_selling_price)
#         warehouse_stock = frappe.db.sql("""
#         select valuation_rate as vr from `tabBin` b 
#         join `tabWarehouse` wh on wh.name = b.warehouse
#         join `tabCompany` c on c.name = wh.company
#         where b.item_code = '%s'
#         """ % (i["item_code"]),as_dict=True)[0]
#         cost += warehouse_stock.vr 
#         if not warehouse_stock.vr :
#             warehouse_stock.vr  = 0
#         cost_amount = (warehouse_stock.vr  * i["qty"]) + cost_amount
#         cost_amount_ = (warehouse_stock.vr * i["qty"])
        
#         tot =  cost_amount - total_selling_price
#         tot_diff =  cost_amount_ - i["base_amount"]
        
#         if profit_per > 0:
#             profit_amount_calc = (cost_amount_ * profit_per)/100
#             selling_amount_calc = profit_amount_calc + cost_amount_
#             profit_amount_ += profit_amount_calc
#             selling_amount_ += selling_amount_calc
#         if cost_amount_ > 0:
#             tot_ = tot_diff/cost_amount_ *100
#         if profit_per == 0:
#             data_4+='''<tr>
#             <td colspan=1 style="border: 1px solid black;font-size:12px;">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px;">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             </tr>'''%(i["item_code"],i["description"],i["qty"],round(warehouse_stock.vr,2) ,round(i["rate"],2),round(cost_amount_,2),round(i["base_amount"],2),round(-tot_diff,2),round(-tot_,2))
#         elif profit_per > 0:
#             data_4+='''<tr>
#             <td colspan=1 style="border: 1px solid black;font-size:12px;">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px;">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             <td colspan=1 style="border: 1px solid black;font-size:12px; text-align: right">%s</td>
#             </tr>
#             '''%(i["item_code"],i["description"],i["qty"],round(warehouse_stock.vr,2) ,round(i["rate"],2),round(cost_amount_,2),round(selling_amount_calc,2),round(profit_amount_calc,2),round(profit_per,2))
    
    
    
#     # data_5 = ''
#     if cost_amount_ == 0:
#         total_margin_internal = (total_selling_price - cost_amount_)/100
#         frappe.errprint('total_margin_internal')

#     else:
#         total_margin_internal = (round(-tot_,2))
#         frappe.errprint(total_margin_internal)
#         frappe.errprint('oo')

        

#     if profit_per == 0:
#         data_4 += '''<tr>
#         <td colspan=2 style="border: 1px solid black;padding:1px;font-size:14px;text-align: right"><b>Total </b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         </tr>'''%(qty_tot,round(cost,2),round(rate,2),round(cost_amount,2),round(selling_amount,2),round(-tot,2),round(total_margin_internal,2))
#         data_4+='''</table>'''
#     elif profit_per > 0:

#         data_4 += '''<tr>
#         <td colspan=2 style="border: 1px solid black;padding:1px;font-size:14px;text-align: right"><b>Total </b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
#         <td style="border: 1px solid black;padding:1px;font-size:12px;text-align: right"><b>%s</b></td>
        
#         </tr>'''%(qty_tot,round(cost,2),round(rate,2),round(cost_amount,2),round(selling_amount_,2),round(profit_amount_,2),round(profit_per,2))
#         data_4+='''</table>'''
# # pro/cost 100
    
#     return data_4

@frappe.whitelist()
def get_invoice_summary(project):
    # data = ''
    # data += '<table class="table table-bordered"><tr><th style="padding:1px;border:1px solid black;font-size:14px;background-color:#e35310;color:white;" colspan=8><center><b>INVOICE SUMMARY</b></center></th></tr>'
    # data +='<tr><td colspan=1 style="border: 1px solid black;font-size:12px;"><center><b>INVOICE LIST</b><center></td></tr>'
   
    invoice = frappe.get_all('Sales Invoice',{"project":project},["*"])
    for i in invoice:
        frappe.errprint(i.name)
    
    # data+='<tr><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s<center><center></td></tr>'%(invoice)
    
    # data += '</table>'
    # return 

@frappe.whitelist()
def get_dates(boarding_begins_on,last__days):
    no_of_days = date_diff(add_days(last__days, 1), boarding_begins_on)
    dates = [add_days(boarding_begins_on, i) for i in range(0, no_of_days)]
    return dates

# @frappe.whitelist()
# def calculate_attendance(employee):
#     name_reg = frappe.db.sql(
#         """select name,hods_relieving_date,actual_relieving_date from `tabResignation Form` where employee = %s """ % (employee), as_dict=True)[0]
#     current_date = name_reg.actual_relieving_date
#     first_day_of_month = current_date.replace(day=1)
#     hod_date = str(first_day_of_month)
#     app_date = str(name_reg.actual_relieving_date)
#     if name_reg:
#         att = frappe.db.sql("""select count(*) as count from `tabAttendance` where attendance_date between '%s' and '%s' and status = 'Present'  and employee = %s""" %
#                             (hod_date, app_date, employee), as_dict=True)[0]
#         cal = att
#         return cal, name_reg

# @frappe.whitelist()
# def get_reg_form(employee):
#     name_reg = frappe.db.sql(
#         """select name,hods_relieving_date,actual_relieving_date from `tabResignation Form` where employee = %s """ % (employee), as_dict=True)[0]
#     current_date = name_reg.actual_relieving_date
#     first_day_of_month = current_date.replace(day=1)
#     return name_reg.name, first_day_of_month, name_reg.actual_relieving_date

@frappe.whitelist()
def get_gratuity(employee):
    from datetime import datetime
    from dateutil import relativedelta
    date_2 = datetime.now()
    emp = frappe.get_doc('Employee', employee)
    # Get the interval between two dates
    diff = relativedelta.relativedelta(date_2, emp.date_of_joining)

    exp_years = diff.years
    exp_month = diff.months
    exp_days = diff.days

    basic_salary = frappe.db.get_value(
        'Employee', emp.employee_number, 'basic')

    per_day_basic = basic_salary / 30

    if emp.grade == 'Office Staff':
        gratuity_per_year = per_day_basic * 30
    else:
        gratuity_per_year = per_day_basic * 21

    gratuity_per_month = gratuity_per_year / 12
    gratuity_per_day = gratuity_per_month / 30
    earned_gpy = gratuity_per_year * exp_years
    earned_gpm = gratuity_per_month * exp_month
    earned_gpd = gratuity_per_day * exp_days
    total_gratuity = earned_gpy + earned_gpm + earned_gpd

    return total_gratuity

@frappe.whitelist()
def update_employee_status(doc,method):
    reg = frappe.db.sql(
        """select * from `tabResignation Form` where docstatus = 1""", as_dict=1)
    if reg:
        for emp in reg:
            if emp.actual_relieving_date == datetime.strptime((today()), '%Y-%m-%d').date():
                emp_n = frappe.get_doc('Employee', emp.employee)
                emp_n.status = "Left"
                emp_n.relieving_date = emp.actual_relieving_date
                emp_n.save(ignore_permissions=True)

@frappe.whitelist(allow_guest=True)
def bluetooth_print_format():
    a = []
    b = {}
    b['type'] = 0
    b['content'] = 'My Title'	
    # b.bold = 1
    # b.align = 1
    b['format'] = 0; # 0 if normal, 1 if double Height, 2 if double Height + Width, 3 if double Width, 4 if small
    a.append(b)
 
    # Dictionary to JSON Object using dumps() method
    # Return JSON Object
    return json.dumps(a)

@frappe.whitelist()
# def enqueue_delete_items():
#     enqueue(method=delete_items, queue="long", timeout=6000, is_async=True)

def delete_items():
    items_list = frappe.get_all('Item',['name'])
    for it in items_list:
        item = frappe.get_doc('Item',it['name'])
        item.is_stock_item = 1
        item.flags.ignore_links = True
        item.save(ignore_permissions=True)

def delete_linked():
    linked_doctypes = [
            "Quotation Item",
            "Opportunity Item"
            
        ]

    for lin in linked_doctypes:
        dle = '`tab%s`' % lin
        frappe.db.sql("""delete from %s """ %dle)

@frappe.whitelist()
def get_pay_terms(payment):
    pay = frappe.get_doc("Payment Terms Template",payment)
    return pay.terms

@frappe.whitelist()
def get_currency_exchange(currency):
    conversion = get_exchange_rate(currency, "QAR")
    return conversion


@frappe.whitelist(allow_guest=True)
def get_norden_item(item):
    url = "https://erp.nordencommunication.com/api/method/norden.custom.get_electra_details?item=%s" % (item)
    headers = { 'Content-Type': 'application/json','Authorization': 'token 28a1f5da5dffd46:812f4d4d2671af2'}
    # params = {"limit_start": 0,"limit_page_length": 20000}

    response = requests.request('GET',url,headers=headers)
    res = json.loads(response.text)
    return res
    
@frappe.whitelist()
def get_stock_av(item_code,abbr):
    item = frappe.db.get_value("Item",item_code,abbr)
    return item

@frappe.whitelist()
def get_default_letter_head(company):
    letter_head = frappe.db.get_value("Company",company,['default_letter_head'])
    return letter_head

@frappe.whitelist()
def get_sales_invoice_series(company,doctype):
    frappe.errprint("hi")
    frappe.errprint(company)
    frappe.errprint(doctype)
    company_series = frappe.db.get_value("Company Series",{'company':company,'document_type':doctype},['series'])
    frappe.errprint(company_series)
    series = company_series.split('-')
    ser = series[0]+"-"+ "STI" +"-"+ series[2]+ "-"
    return ser

@frappe.whitelist()
def get_user_role(user):
    user_roles = frappe.get_roles(user)
    return user_roles
    
@frappe.whitelist()
def get_dn_return_series(company,doctype):
    company_series = frappe.db.get_value("Company Series",{'company':company,'document_type':doctype},'series')
    series = company_series.split('-')
    ser = series[0]+"-"+ "DNR" +"-"+ series[2]+ "-"
    return ser


@frappe.whitelist()
def restrict_general_item_so(doc,method):
    if doc.items:
        for item in doc.items:
            if item.item_code == "001":
                frappe.throw("Not Allowed to Make Sales Order in General Entry")


@frappe.whitelist()
def restrict_general_item_si(doc,method):
    if doc.items:
        for item in doc.items:
            if item.item_code == "001":
                frappe.throw("Not Allowed to Make Sales Invoice in General Entry")

@frappe.whitelist()
def restrict_general_item_dn(doc,method):
    if doc.items:
        for item in doc.items:
            if item.item_code == "001":
                frappe.throw("Not Allowed to Make Delivery Note in General Entry")

# def setup_hooks():
#     from frappe.model import DocType
#     if "Sales Order" in DocType:
#         DocType["Sales Order"].before_save.append(restrict_general_item)

# # Execute the setup_hooks function
# setup_hooks()


from frappe.utils import fmt_money

@frappe.whitelist()
def actual_vs_budgeted(name):
    crea = frappe.db.sql("""select creation from `tabProject` where name ='%s' """ % (name), as_dict=True)[0]
    project_budget, p_name = frappe.db.get_value("Project", {'name': name}, ['budgeting', 'project_name'])
    pb = frappe.get_doc("Project Budget", project_budget)
    data = '<table width = 100%>'
    data += '<tr><td><b>Date</b></td><td>%s</td><td><b>Refer No</b></td><td></td></tr>' % (
        format_date(crea["creation"].date()))
    data += '<tr><td><b>Project Code</b></td><td>%s</td><td><b>Project</b></td><td>%s</td></tr>' % (name, p_name)
    data += '<tr><td><b>Client</b></td><td>%s</td><td><b>Order Ref No.</b></td><td>%s</td></tr>' % (
        pb.lead_customer_name, pb.sales_order)
    data += '</table><br>'
    grand = frappe.db.get_value("Sales Order", {'project': name}, ['grand_total'])
    sales_in = frappe.db.sql(
        """ SELECT SUM(grand_total) as total FROM `tabSales Invoice` WHERE project = %s""",
        (name,),
        as_dict=True)[0]
    if not sales_in["total"]:
        sales_in["total"] = 0
    bal = grand - sales_in["total"]
    revenue = frappe.db.sql(
        """ SELECT SUM(paid_amount) as amt FROM `tabPayment Entry` WHERE project = %s""",
        (name,),
        as_dict=True)[0]
    if not revenue["amt"]:
        revenue["amt"] = 0
    out = grand - revenue["amt"]
    tot = 0
    dn_list = frappe.db.get_list("Delivery Note", {'project': name})
    if dn_list:
        for d_list in dn_list:
            dn = frappe.get_doc("Delivery Note", d_list.name)
            for d in dn.items:
                w_house = frappe.db.get_value("Warehouse",
                                              {'company': dn.company, 'default_for_stock_transfer': 1},
                                              ['name'])
                val = frappe.db.get_value("Bin", {"item_code": d.item_code, "warehouse": w_house}, ['valuation_rate'])
                total = val * d.qty
                tot += total
    prof = grand - tot
    gp = (prof / grand) * 100
    data += '<h3>Project Details</h3>'
    data += '<table border=1px solid black width=100%>'
    data += '<tr style="background-color:#ABB2B9;text-align:center"><td><b>Order Value</b></td><td><b>Invoice Value till Date</b></td><td><b>Cost Till Date</b></td><td><b>Gross Profit</b></td><td><b>Gross Profit %</b></td><td><b>Balance To Invoice</b></td><td><b>Total Collection</b></td><td><b>O/S Receipts</b></td></tr>'
    data += '<tr style="text-align:right"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
        fmt_money(grand, 2), fmt_money(sales_in["total"] or 0, 2), fmt_money(round(tot, 2), 2),
        fmt_money(round(prof, 2), 2), fmt_money(round(gp, 2), 2), fmt_money(round(bal, 2), 2),
        fmt_money(round(revenue["amt"], 2) or 0, 2), fmt_money(round(out, 2), 2))
    data += '</table><br>'
    data += '<table border=1px solid black width=100%>'
    data += '<tr style="background-color:#ABB2B9"><td colspan=4></td><td colspan=3 style="text-align:center"><b>Budgeted</b></td><td colspan=2 style="text-align:center"><b>Actual</b></td><td style="text-align:center" colspan=2><b>Variance</b></td><tr>'
    data += '<tr style="background-color:#D5D8DC"><td colspan=1><b>Budget Code</b></td><td colspan=1><b>Part Number</b></td><td colspan=1><b>Description</b></td><td colspan=1><b>Unit</b></td><td colspan=1><b>Qty</b></td><td colspan=1><b>Rate</b></td><td colspan=1><b>Amount</b></td><td colspan=1><b>Qty</b></td><td colspan=1><b>Amount</b></td><td colspan=1><b>Qty</b></td><td colspan=1><b>Amount</b></td><tr>'
    dic_items = []
    dic = [{"name": "Supply Materials", "table": pb.materials},
           {"name": "Accessories", "table": pb.bolts_accessories},
           {"name": "Installation", "table": pb.installation},
           {"name": "Subcontract", "table": pb.others},
           {"name": "Design", "table": pb.design},
           {"name": "Finishing Work", "table": pb.finishing_work},
           {"name": "Tools / Equipment / Transport / Others", "table": pb.heavy_equipments},
           {"name": "Finished Goods", "table": pb.finished_goods}]
    for j in dic:
        if j["table"]:
            data += '<tr><td style="background-color:#EBEDEF;text-align:center" colspan=11><b>%s</b></td><tr>' % (
                j["name"])
            amt = 0
            total_amt = 0
            a_amt = 0
            total_a_amt = 0
            v_amt = 0
            total_v_amt = 0
            for i in j["table"]:
                dn = frappe.db.sql(
                    """select `tabDelivery Note Item`.item_code as item_code, `tabDelivery Note Item`.qty as qty, `tabDelivery Note Item`.amount as amount from `tabDelivery Note`
                    left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
                    where `tabDelivery Note Item`.item_code = %s and `tabDelivery Note`.project = %s""",
                    (i.item, name),
                    as_dict=True) or 0
                if dn:
                    d = dn[0]['qty']
                    d_amt = dn[0]['amount']
                else:
                    d = 0
                    d_amt = 0
                data += '<tr><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><tr>' % (
                    project_budget, i.item, i.description, i.unit, i.qty, fmt_money(round(i.rate_with_overheads, 2), 2),
                    fmt_money(round(i.amount_with_overheads, 2), 2), d, fmt_money(round(d_amt, 2), 2),
                    i.qty - d, fmt_money(round(i.amount_with_overheads, 2) - round(d_amt, 2), 2))
                amt += round(i.amount_with_overheads, 2)
                a_amt += round(d_amt, 2)
                v_amt += round(i.amount_with_overheads, 2) - round(d_amt, 2)
                total_amt += amt
                total_a_amt += a_amt
                total_v_amt += v_amt
            data += '<tr><td colspan=6></td><td style="text-align:right" colspan=1>%s</td><td style="text-align:right" colspan=1></td><td style="text-align:right" colspan=1>%s</td><td style="text-align:right" colspan=1></td><td style="text-align:right" colspan=1>%s</td><tr>' % (
                fmt_money(round(amt, 2), 2), fmt_money(round(a_amt, 2), 2), fmt_money(round(v_amt, 2), 2))
    manpower = [{"name": "Manpower", "table": pb.manpower}]
    for j in manpower:
        if j["table"]:
            data += '<tr><td style="background-color:#EBEDEF;text-align:center" colspan=11><b>%s</b></td><tr>' % (
                j["name"])
            for i in j["table"]:
                man = frappe.db.sql(
                    """select sum(`tabTimesheet`.total_costing_amount) as amt from `tabTimesheet`
                    left join `tabTimesheet Detail` on `tabTimesheet`.name = `tabTimesheet Detail`.parent
                    where `tabTimesheet Detail`.project = %s""",
                    (name,),
                    as_dict=True) or 0
                if man:
                    m = man[0]['amt']
                else:
                    m = 0
                data += '<tr><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><tr>' % (
                    project_budget, i.worker, i.worker, "Nos", i.total_workers,
                    fmt_money(round(i.rate_with_overheads, 2), 2),
                    fmt_money(round(i.amount_with_overheads, 2), 2), i.total_workers,
                    fmt_money((m or 0), 2), i.total_workers,
                    fmt_money(((i.amount_with_overheads) - (m or 0)), 2))
    data += '</table>'
    return data


@frappe.whitelist()
def work_order_detailed_report(name):
    crea = frappe.db.sql("""select creation from `tabProject` where name ='%s' """ % (name), as_dict=True)[0]
    project_budget,p_name = frappe.db.get_value("Project",{'name':name},['budgeting','project_name'])
    pb = frappe.get_doc("Project Budget",project_budget)
    data = '<table width = 100%>'
    data += '<tr><td><b>Date</b></td><td>%s</td><td><b>Refer No</b></td><td></td></tr>'%(format_date(crea["creation"].date()))
    data += '<tr><td><b>Project Code</b></td><td>%s</td><td><b>Project</b></td><td>%s</td></tr>'%(name,p_name)
    data += '<tr><td><b>Client</b></td><td>%s</td><td><b>Order Ref No.</b></td><td>%s</td></tr>'%(pb.lead_customer_name,pb.sales_order)
    data += '</table><br>'

    grand = frappe.db.get_value("Sales Order",{'project':name},['grand_total'])
    sales_in = frappe.db.sql(""" select sum(grand_total) as total from `tabSales Invoice` where project = '%s' """%(name),as_dict=True)[0]
    if not sales_in["total"]:
        sales_in["total"] = 0
    bal = grand - sales_in["total"]
    revenue = frappe.db.sql(""" select sum(paid_amount) as amt from `tabPayment Entry` where project = '%s' """%(name),as_dict=True)[0]
    if not revenue["amt"]:
        revenue["amt"] = 0
    out = grand - revenue["amt"]
    tot = 0
    val = 0
    dn_list = frappe.db.get_list("Delivery Note",{'project':name})
    if dn_list:
        for d_list in dn_list:
            dn = frappe.get_doc("Delivery Note",d_list.name)
            for d in dn.items:
                w_house = frappe.db.get_value("Warehouse",{'company':dn.company,'default_for_stock_transfer':1},['name'])
                val = frappe.db.get_value("Bin",{"item_code":d.item_code,"warehouse":w_house},['valuation_rate']) or 0
                if not d.qty:
                    d.qty = 0
                total = val * d.qty
                tot+=total
    prof = grand - tot
    gp = (prof / grand)*100
    data += '<h3>Project Details</h3>'
    data += '<table border= 1px solid black width = 100%>'
    data += '<tr style = "background-color:#ABB2B9;text-align:center"><td><b>Order Value</b></td><td><b>Invoice Value till Date</b></td><td><b>Cost Till Date</b></td><td><b>Gross Profit</b></td><td><b>Gross Profit %</b></td><td><b>Balance To Invoice</b></td><td><b>Total Collection</b></td><td><b>O/S Receipts</b></td></tr>'
    data += '<tr style = "text-align:right"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'%(grand,sales_in["total"] or 0,round(tot,2),round(prof,2),round(gp,2),round(bal,2),round(revenue["amt"],2) or 0,round(out,2))
    data += '</table><br>'

    data += '<table border= 1px solid black width = 100%>'
    dic = [{"name":"Supply Materials","table":pb.materials},{"name":"Accessories","table":pb.bolts_accessories},{"name":"Installation","table":pb.installation},{"name":"Subcontract","table":pb.others},{"name":"Design","table":pb.design},{"name":"Finishing Work","table":pb.finishing_work},{"name":"Tools / Equipment / Transport / Others","table":pb.heavy_equipments}]
    for j in dic:
        if j["table"]:
            data += '<tr><td style ="background-color:#EBEDEF;text-align:center" colspan = 13><b>%s</b></td><tr>'%(j["name"])          
            data +='<table border= 1px width = 100%>'
            data += '<tr style= "background-color:#D5D8DC"><td colspan = 1><b>Budget Code</b></td><td colspan = 1><b>Part Number</b></td><td colspan = 1><b>Description</b></td><td colspan = 1><b>Unit</b></td><td colspan = 1><b>Qty</b></td><td colspan = 1><b>Rate</b></td><td colspan = 1><b>Amount</b></td><td colspan = 1><b>Stock Qty</b></td><td colspan = 1><b>MR Qty</b></td><td colspan = 1><b>MR Rate</b></td><td colspan = 1><b>MR Amount</b></td><td colspan = 1><b>DN Rate</b></td><td colspan = 1><b>DN Amount</b></td><tr>'
            
            for i in j["table"]:     
                dn = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code, `tabDelivery Note Item`.qty as qty, `tabDelivery Note Item`.amount as amount from `tabDelivery Note`
                left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
                where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.project = '%s' """ % (i.item,name), as_dict=True) or 0
                if dn:
                    d = dn[0]['qty']
                    d_amt = dn[0]['amount']
                else:
                    d = 0
                    d_amt = 0
                mr_amount = 0
                mr_qty = 0
                mr_rate = 0
                parent = frappe.db.sql("""select `tabMaterial Request`.name as name from `tabMaterial Request`
                left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus != 2 and `tabMaterial Request Item`.project = '%s'"""%(i.item,name),as_dict=True)
                company = frappe.db.get_value("Project",{'name':name},['company'])
                w_house = frappe.db.get_value("Warehouse",{'company':company,'default_for_stock_transfer':1},['name'])
                stocks = frappe.db.sql("""select actual_qty from tabBin where item_code = '%s' and warehouse = '%s' """%(i.item,w_house),as_dict=True)
                if not stocks:
                    stock = 0
                else:
                    stock = stocks[0]["actual_qty"]
                    wo_amt = 0
                data += '<tr><td  style = "text-align:left;width:18%% " colspan = 1>%s</td><td  style = "text-align:left;width:22%%" colspan = 1>%s</td><td  style = "text-align:left;width:28%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td></tr>'%(project_budget,i.item,i.description,i.unit,i.qty,round(i.rate_with_overheads,2),round(i.amount_with_overheads,2),stock,mr_qty,mr_rate,mr_amount,d,round(d_amt,2))

    fg = [{"name":"Finished Goods","table":pb.finished_goods}]
    for j in fg:
        if j["table"]:
            data += '<tr><td style ="background-color:#EBEDEF;text-align:center" colspan = 13><b>%s</b></td><tr>'%(j["name"])          
            amt = 0
            total_amt = 0
            a_amt = 0 
            total_a_amt = 0 
            v_amt = 0
            total_v_amt = 0
            for i in j["table"]:     
                dn = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code, `tabDelivery Note Item`.qty as qty, `tabDelivery Note Item`.amount as amount from `tabDelivery Note`
                left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
                where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.project = '%s' """ % (i.item,name), as_dict=True) or 0
                if dn:
                    d = dn[0]['qty']
                    d_amt = dn[0]['amount']
                else:
                    d = 0
                    d_amt = 0
                mr_amount = 0
                if i.bom:
                    bom = frappe.get_doc("BOM",i.bom)
                    for it in bom.items:
                        parent = frappe.db.sql("""select `tabMaterial Request`.name as name from `tabMaterial Request`
                        left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                        where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus != 2 and `tabMaterial Request Item`.project = '%s'"""%(it.item_code,name),as_dict=True) or ''
                        
                        if parent:
                            
                            mr = frappe.get_doc("Material Request",parent[0]["name"])
                            for m in mr.items:
                                if m.item_code == it.item_code:
                                    mr_amount += m.amount
                wo_amt = 0
                if i.bom:
                    wor = frappe.db.exists("Work Order",{'bom_no':i.bom})
                    if wor:
                        work_order = frappe.get_doc("Work Order",{'bom_no':i.bom})
                        if work_order:
                            for wo in work_order.required_items:
                                wo_amt += wo.amount
         
                data +='<table border= 1px width = 100%>'
                data += '<tr style= "background-color:#D5D8DC"><td colspan = 1><b>Budget Code</b></td><td colspan = 1><b>Part Number</b></td><td colspan = 1><b>Description</b></td><td colspan = 1><b>Unit</b></td><td colspan = 1><b>Qty</b></td><td colspan = 1><b>Rate</b></td><td colspan = 1><b>Amount</b></td><td colspan = 1><b>MR Amount</b></td><td colspan = 1><b>WO Amount</b></td><tr>'
                data += '<tr><td  style = "text-align:left;width:18%% " colspan = 1>%s</td><td  style = "text-align:left;width:22%%" colspan = 1>%s</td><td  style = "text-align:left;width:28%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td></tr>'%(project_budget,i.item,i.description,i.unit,i.qty,round(i.rate_with_overheads,2),round(i.amount_with_overheads,2),round(mr_amount,2),round(wo_amt,2))

                data += '<tr style= "background-color:#D5D8DC"><td style = "text-align:center"  colspan = 3></td><td style = "text-align:center"  colspan = 3><b>Material Request Details</b></td><td style = "text-align:center"  colspan = 3><b>Work Order Details</b></td></tr>'
                data +='<tr style ="background-color:#EBEDEF"><td style = "text-align:center;width: 25%" colspan = 1><b>Item Code</b></td><td  style = "text-align:center;width: 35%" colspan = 1><b>Item Name</b></td><td  style = "text-align:center;width: 25%" colspan = 1><b>Stock Qty</b></td><td  style = "text-align:center;width: 25%" colspan = 1><b>Qty</b></td><td  style = "text-align:center;width: 25%" colspan = 1><b>Rate</b></td><td  style = "text-align:center;width: 25%" colspan = 1><b>Amount</b></td><td  style = "text-align:center;width: 25%" colspan = 1><b>Qty</b></td><td  style = "text-align:center;width: 25%" colspan = 1><b>Rate</b></td><td  style = "text-align:center;width: 25%" colspan = 2><b>Amount</b></td><tr>'
                

                if i.bom:                    
                    bom = frappe.get_doc("BOM",i.bom)
                    for it in bom.items:
                        company = frappe.db.get_value("Project",{'name':name},['company'])
                        w_house = frappe.db.get_value("Warehouse",{'company':company,'default_for_stock_transfer':1},['name'])
                        stocks = frappe.db.sql("""select actual_qty from tabBin where item_code = '%s' and warehouse = '%s' """%(it.item_code,w_house),as_dict=True)
                        parent = frappe.db.sql("""select `tabMaterial Request`.name as name from `tabMaterial Request`
                        left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                        where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus != 2 and `tabMaterial Request Item`.project = '%s'"""%(it.item_code,name),as_dict=True) or ''
                        
                        if parent:
                            
                            mr = frappe.get_doc("Material Request",parent[0]["name"])
                            for m in mr.items:                                                            
                                if m.item_code == it.item_code:    
                                    pos = frappe.db.sql("""select `tabWork Order Item`.rate as rate,`tabWork Order Item`.amount as amount,`tabWork Order Item`.consumed_qty as consumed_qty from `tabWork Order`
                                    left join `tabWork Order Item` on `tabWork Order`.name = `tabWork Order Item`.parent
                                    where `tabWork Order Item`.item_code = '%s' and `tabWork Order`.docstatus != 2 and `tabWork Order`.bom_no ='%s' """%(m.item_code,i.bom),as_dict=True)                                                         
                                    data += '<tr><td  style = "text-align:left" colspan = 1>%s</td><td  style = "text-align:left" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td></tr>'%(m.item_code,m.item_name or '',round(stocks[0]["actual_qty"],2) or 0,m.qty or '',m.rate or '',m.amount or '',round(pos[0]["consumed_qty"],2) or '',round(pos[0]["rate"],2) or '',round(pos[0]["amount"],2) or '')
                        else:
                            workorder = frappe.db.sql("""select `tabWork Order`.name as name from `tabWork Order`
                            left join `tabWork Order Item` on `tabWork Order`.name = `tabWork Order Item`.parent
                            where `tabWork Order Item`.item_code = '%s' and `tabWork Order`.docstatus != 2 and `tabWork Order`.bom_no ='%s' """%(it.item_code,i.bom),as_dict=True) or ''
                            
                            if workorder:
                                work_order = frappe.get_doc("Work Order",workorder[0]["name"])
                        
                            pos = frappe.db.sql("""select `tabWork Order Item`.rate as rate,`tabWork Order Item`.amount as amount,`tabWork Order Item`.consumed_qty as consumed_qty,`tabWork Order Item`.required_qty as required_qty from `tabWork Order`
                            left join `tabWork Order Item` on `tabWork Order`.name = `tabWork Order Item`.parent
                            where `tabWork Order Item`.item_code = '%s' and `tabWork Order`.docstatus != 2 and `tabWork Order`.bom_no ='%s' """%(it.item_code,i.bom),as_dict=True)
                            if pos:
                                data += '<tr><td  style = "text-align:left" colspan = 1>%s</td><td  style = "text-align:left" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 1>%s</td><td  style = "text-align:right" colspan = 2>%s</td></tr>'%(it.item_code,it.item_name,round(stocks[0]["actual_qty"],2) or 0, 0,0,0,round(pos[0]["consumed_qty"],2) or round(pos[0]["required_qty"],2),round(pos[0]["rate"],2) or '',round(pos[0]["amount"],2) or '')

                data +='</table>'
                amt += round(i.amount_with_overheads,2)
                a_amt += round(d_amt,2)
                v_amt += round(i.amount_with_overheads,2) - round(d_amt,2)
                total_amt += amt
                total_a_amt += a_amt
                total_v_amt += v_amt
          
    return data



@frappe.whitelist()
def work_order_brief_report(name):
    crea = frappe.db.sql("""select creation from `tabProject` where name ='%s' """ % (name), as_dict=True)[0]
    project_budget,p_name = frappe.db.get_value("Project",{'name':name},['budgeting','project_name'])
    pb = frappe.get_doc("Project Budget",project_budget)
    data = '<table width = 100%>'
    data += '<tr><td><b>Date</b></td><td>%s</td><td><b>Refer No</b></td><td></td></tr>'%(format_date(crea["creation"].date()))
    data += '<tr><td><b>Project Code</b></td><td>%s</td><td><b>Project</b></td><td>%s</td></tr>'%(name,p_name)
    data += '<tr><td><b>Client</b></td><td>%s</td><td><b>Order Ref No.</b></td><td>%s</td></tr>'%(pb.lead_customer_name,pb.sales_order)
    data += '</table><br>'

    grand = frappe.db.get_value("Sales Order",{'project':name},['grand_total'])
    sales_in = frappe.db.sql(""" select sum(grand_total) as total from `tabSales Invoice` where project = '%s' """%(name),as_dict=True)[0]
    if not sales_in["total"]:
        sales_in["total"] = 0
    bal = grand - sales_in["total"]
    revenue = frappe.db.sql(""" select sum(paid_amount) as amt from `tabPayment Entry` where project = '%s' """%(name),as_dict=True)[0]
    if not revenue["amt"]:
        revenue["amt"] = 0
    out = grand - revenue["amt"]
    tot = 0
    val = 0
    dn_list = frappe.db.get_list("Delivery Note",{'project':name})
    if dn_list:
        for d_list in dn_list:
            dn = frappe.get_doc("Delivery Note",d_list.name)
            for d in dn.items:
                w_house = frappe.db.get_value("Warehouse",{'company':dn.company,'default_for_stock_transfer':1},['name'])
                val = frappe.db.get_value("Bin",{"item_code":d.item_code,"warehouse":w_house},['valuation_rate']) or 0
                if not d.qty:
                    d.qty = 0
                total = val * d.qty
                tot+=total
    prof = grand - tot
    gp = (prof / grand)*100
    data += '<h3>Project Details</h3>'
    data += '<table border= 1px solid black width = 100%>'
    data += '<tr style = "background-color:#ABB2B9;text-align:center"><td><b>Order Value</b></td><td><b>Invoice Value till Date</b></td><td><b>Cost Till Date</b></td><td><b>Gross Profit</b></td><td><b>Gross Profit %</b></td><td><b>Balance To Invoice</b></td><td><b>Total Collection</b></td><td><b>O/S Receipts</b></td></tr>'
    data += '<tr style = "text-align:right"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'%(grand,sales_in["total"] or 0,round(tot,2),round(prof,2),round(gp,2),round(bal,2),round(revenue["amt"],2) or 0,round(out,2))
    data += '</table><br>'

    data += '<table border= 1px solid black width = 100%>'
    dic = [{"name":"Supply Materials","table":pb.materials},{"name":"Accessories","table":pb.bolts_accessories},{"name":"Installation","table":pb.installation},{"name":"Subcontract","table":pb.others},{"name":"Design","table":pb.design},{"name":"Finishing Work","table":pb.finishing_work},{"name":"Tools / Equipment / Transport / Others","table":pb.heavy_equipments}]
    for j in dic:
        if j["table"]:
            data += '<tr><td style ="background-color:#EBEDEF;text-align:center" colspan = 13><b>%s</b></td><tr>'%(j["name"])          
            data +='<table border= 1px width = 100%>'
            data += '<tr style= "background-color:#D5D8DC"><td colspan = 1><b>Budget Code</b></td><td colspan = 1><b>Part Number</b></td><td colspan = 1><b>Description</b></td><td colspan = 1><b>Unit</b></td><td colspan = 1><b>Qty</b></td><td colspan = 1><b>Rate</b></td><td colspan = 1><b>Amount</b></td><td colspan = 1><b>Stock Qty</b></td><td colspan = 1><b>MR Amount</b></td><td colspan = 1><b>DN Amount</b></td><tr>'
            
            for i in j["table"]:     
                dn = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code, `tabDelivery Note Item`.qty as qty, `tabDelivery Note Item`.amount as amount from `tabDelivery Note`
                left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
                where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.project = '%s' """ % (i.item,name), as_dict=True) or 0
                if dn:
                    d = dn[0]['qty']
                    d_amt = dn[0]['amount']
                else:
                    d = 0
                    d_amt = 0
                mr_amount = 0
                mr_qty = 0
                mr_rate = 0
                parent = frappe.db.sql("""select `tabMaterial Request`.name as name from `tabMaterial Request`
                left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus != 2 and `tabMaterial Request Item`.project = '%s'"""%(i.item,name),as_dict=True)
                company = frappe.db.get_value("Project",{'name':name},['company'])
                w_house = frappe.db.get_value("Warehouse",{'company':company,'default_for_stock_transfer':1},['name'])
                stocks = frappe.db.sql("""select actual_qty from tabBin where item_code = '%s' and warehouse = '%s' """%(i.item,w_house),as_dict=True)
                if not stocks:
                    stock = 0
                else:
                    stock = stocks[0]["actual_qty"]
                    wo_amt = 0
                data += '<tr><td  style = "text-align:left;width:18%% " colspan = 1>%s</td><td  style = "text-align:left;width:22%%" colspan = 1>%s</td><td  style = "text-align:left;width:28%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td></tr>'%(project_budget,i.item,i.description,i.unit,i.qty,round(i.rate_with_overheads,2),round(i.amount_with_overheads,2),stock,mr_amount,round(d_amt,2))

    fg = [{"name":"Finished Goods","table":pb.finished_goods}]
    for j in fg:
        if j["table"]:
            data += '<tr><td style ="background-color:#EBEDEF;text-align:center" colspan = 13><b>%s</b></td><tr>'%(j["name"])
            data +='<table border= 1px width = 100%>'
            data += '<tr style= "background-color:#D5D8DC"><td colspan = 1><b>Budget Code</b></td><td colspan = 1><b>Part Number</b></td><td colspan = 1><b>Description</b></td><td colspan = 1><b>Unit</b></td><td colspan = 1><b>Qty</b></td><td colspan = 1><b>Rate</b></td><td colspan = 1><b>Amount</b></td><td colspan = 1><b>MR Amount</b></td><td colspan = 1><b>WO Amount</b></td><tr>'
                     
            amt = 0
            total_amt = 0
            a_amt = 0 
            total_a_amt = 0 
            v_amt = 0
            total_v_amt = 0
            for i in j["table"]:     
                dn = frappe.db.sql("""select `tabDelivery Note Item`.item_code as item_code, `tabDelivery Note Item`.qty as qty, `tabDelivery Note Item`.amount as amount from `tabDelivery Note`
                left join `tabDelivery Note Item` on `tabDelivery Note`.name = `tabDelivery Note Item`.parent
                where `tabDelivery Note Item`.item_code = '%s' and `tabDelivery Note`.project = '%s' """ % (i.item,name), as_dict=True) or 0
                if dn:
                    d = dn[0]['qty']
                    d_amt = dn[0]['amount']
                else:
                    d = 0
                    d_amt = 0
                mr_amount = 0
                if i.bom:
                    bom = frappe.get_doc("BOM",i.bom)
                    for it in bom.items:
                        parent = frappe.db.sql("""select `tabMaterial Request`.name as name from `tabMaterial Request`
                        left join `tabMaterial Request Item` on `tabMaterial Request`.name = `tabMaterial Request Item`.parent
                        where `tabMaterial Request Item`.item_code = '%s' and `tabMaterial Request`.docstatus != 2 and `tabMaterial Request Item`.project = '%s'"""%(it.item_code,name),as_dict=True) or ''
                        
                        if parent:
                            
                            mr = frappe.get_doc("Material Request",parent[0]["name"])
                            for m in mr.items:
                                if m.item_code == it.item_code:
                                    mr_amount += m.amount
                wo_amt = 0
                if i.bom:
                    wor = frappe.db.exists("Work Order",{'bom_no':i.bom})
                    if wor:
                        work_order = frappe.get_doc("Work Order",{'bom_no':i.bom})
                        if work_order:
                            for wo in work_order.required_items:
                                wo_amt += wo.amount
         
                data += '<tr><td  style = "text-align:left;width:18%% " colspan = 1>%s</td><td  style = "text-align:left;width:22%%" colspan = 1>%s</td><td  style = "text-align:left;width:28%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td><td  style = "text-align:right;width:3%%" colspan = 1>%s</td></tr>'%(project_budget,i.item,i.description,i.unit,i.qty,round(i.rate_with_overheads,2),round(i.amount_with_overheads,2),round(mr_amount,2),round(wo_amt,2))

               
                amt += round(i.amount_with_overheads,2)
                a_amt += round(d_amt,2)
                v_amt += round(i.amount_with_overheads,2) - round(d_amt,2)
                total_amt += amt
                total_a_amt += a_amt
                total_v_amt += v_amt
          
    return data

@frappe.whitelist()
def make_item_sheet():
    args = frappe.local.form_dict
    filename = args.name
    test = build_xlsx_response(filename)

def make_xlsx(data,sheet_name=None, wb=None, column_widths=None):
    args = frappe.local.form_dict
    company = args.company
    column_widths = column_widths or []
    if wb is None:
        wb = openpyxl.Workbook()
    ws = wb.create_sheet(sheet_name, 0)
    warehouse = []
    comp = frappe.db.sql("""select name from `tabCompany`""",as_dict=1)
    for co in comp:
        st = 0
        ware = frappe.db.sql("""select name from `tabWarehouse` where company = '%s' and default_for_stock_transfer = 1 """%(co.name),as_dict=1)
        for w in ware:
            warehouse.append(w.get('name')) 
    ws.append(['Item Code']+['Item Name']+['Stock']+warehouse+['TO RECEIVE']+['TO SELL'])
    doc = frappe.get_doc(args.doctype,args.name)
    for j in doc.items:
        country = frappe.get_value("Company",{"name":company},["country"])

        warehouse_stock = frappe.db.sql("""
        select sum(b.actual_qty) as qty from `tabBin` b join `tabWarehouse` wh on wh.name = b.warehouse join `tabCompany` c on c.name = wh.company where c.country = '%s' and b.item_code = '%s'
        """ % (country,j.item_code),as_dict=True)[0]

        if not warehouse_stock["qty"]:
            warehouse_stock["qty"] = 0
    
        new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order` 
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (j.item_code), as_dict=True)[0]
        if not new_po['qty']:
            new_po['qty'] = 0
        if not new_po['d_qty']:
            new_po['d_qty'] = 0
        in_transit = new_po['qty'] - new_po['d_qty']
        pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,sum(`tabPurchase Order Item`.qty) as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
            left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
            where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by rate asc limit 1""" % (j.item_code), as_dict=True)
        
        new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
            left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
            where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1  """ % (j.item_code), as_dict=True)[0]
        

        if not new_so['qty']:
            new_so['qty'] = 0
        if not new_so['d_qty']:
            new_so['d_qty'] = 0
        del_total = new_so['qty'] - new_so['d_qty']
        
        i= 0
        st = 0
        amt = []
        comp = frappe.db.sql("""select name from `tabCompany`""",as_dict=1)
        for co in comp:
            ware = frappe.db.sql("""select name from `tabWarehouse` where company = '%s' and default_for_stock_transfer = 1 """%(co.name),as_dict=1)
            for w in ware:
                sto = frappe.db.get_value("Bin", {"item_code": j.item_code, "warehouse": w.name}, ['actual_qty'])
                if not sto:
                    sto = 0
                st += sto
                amt.append(sto)
        ws.append([j.item_code,j.item_name,st]+amt + [int(in_transit or 0), int(del_total or 0)])
        i += 1
    xlsx_file = BytesIO()
    wb.save(xlsx_file)
    return xlsx_file

def build_xlsx_response(filename):
    xlsx_file = make_xlsx(filename)
    frappe.response['filename'] = filename + '.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary' 	

@frappe.whitelist()
def update_detail_stock(item_details, company):
    item_details = json.loads(item_details)
    frappe.errprint(item_details)
    data = ''
    data += '<h4><center><b>STOCK DETAILS</b></center></h4>'
    data += '<h6>Note:</h6>'
    data += '<table style = font-size:10px width=100% ><tr><td>Electra Interior Warehouse - <b>INE</b></td><td>Kingfisher Transportation Warehouse - <b>KT</b></td><td>Steel Warehouse - <b>SDE</b></td><td>Marazeem HO Warehouse - <b>MSSHO</b></td><td>Electra Trading Warehouse - <b>TDE</b></td></tr>'
    data += '<tr><td>Electra Warehouse - <b>ASTCC</b></td><td>Electra Binomran Showroom Warehouse - <b>EBO</b></td><td>Kingfisher Warehouse - <b>KTCC</b></td><td>Kingfisher Showroom Warehouse - <b>KS</b></td><td>Marazeem Showroom - <b>MSSS</b></td></tr>'
    data += '<tr><td>Electra Najma Showroom Warehouse - <b> ENS</b></td><td>Marazeem Warehouse - <b>MSS</b></td><td>Barwa Showroom  - <b>EBS</b></td><td>Electra Electrical Warehouse - <b>EDE</b></td><td>Electra Engineering Warehouse - <b>EED</b></td></tr>'
    data += '</table>'
    data += '<table class="table table-bordered" style = font-size:10px>'
    data += '<td colspan=1 style="width:12%;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>ITEM CODE</b></center></td>'
    data += '<td colspan=1 style="width:20%;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>ITEM NAME</b></center></td>'
    data += '<td colspan=1 style="width:70px;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>STOCK</b></center></td>'
    # comp = frappe.db.get_list("Company","name")
    comp = frappe.db.sql("""select name from `tabCompany`""",as_dict=1)
    for co in comp:
        st = 0
        ware = frappe.db.sql("""select name from `tabWarehouse` where company = '%s' and default_for_stock_transfer = 1 """%(co.name),as_dict=1)
        # ware = frappe.db.get_list("Warehouse",{"company":co.name,"default_for_stock_transfer":1},['name'])
        for w in ware:
            frappe.errprint(w)

            data += '<td colspan=1 style="width:70px;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>%s</b></center></td>'%(w.name.split("-")[-1]) 
    data += '<td colspan=1 style="width:180px;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>TO RECEIVE</b></center></td>'
    data += '<td colspan=1 style="width:180px;padding:1px;border:1px solid black;background-color:#e35310;color:white;"><center><b>TO SELL</b></center></td>'
    warehouses = []  
    for j in item_details:
        country = frappe.get_value("Company",{"name":company},["country"])

        warehouse_stock = frappe.db.sql("""
        select sum(b.actual_qty) as qty from `tabBin` b join `tabWarehouse` wh on wh.name = b.warehouse join `tabCompany` c on c.name = wh.company where c.country = '%s' and b.item_code = '%s'
        """ % (country,j["item_code"]),as_dict=True)[0]

        if not warehouse_stock["qty"]:
            warehouse_stock["qty"] = 0
        
        
        new_po = frappe.db.sql("""select sum(`tabPurchase Order Item`.qty) as qty,sum(`tabPurchase Order Item`.received_qty) as d_qty from `tabPurchase Order` 
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus = 1 """ % (j["item_code"]), as_dict=True)[0]
        if not new_po['qty']:
            new_po['qty'] = 0
        if not new_po['d_qty']:
            new_po['d_qty'] = 0
        in_transit = new_po['qty'] - new_po['d_qty']


        
        total = warehouse_stock["qty"] + in_transit

        stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
        where item_code = '%s' """%(j["item_code"]),as_dict=True)

        pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,sum(`tabPurchase Order Item`.qty) as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by rate asc limit 1""" % (j["item_code"]), as_dict=True)
    
        new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order`
        left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent
        where `tabSales Order Item`.item_code = '%s' and `tabSales Order`.docstatus = 1  """ % (j["item_code"]), as_dict=True)[0]
        if not new_so['qty']:
            new_so['qty'] = 0
        if not new_so['d_qty']:
            new_so['d_qty'] = 0
        del_total = new_so['qty'] - new_so['d_qty']
        i = 0
        for po in pos:
            data += '<tr>'
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (j["item_code"])
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (j["item_name"])
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' % (warehouse_stock['qty'] or 0				)
            comp = frappe.db.sql("""select name from `tabCompany`""",as_dict=1)
            for co in comp:
                st = 0
                ware = frappe.db.sql("""select name from `tabWarehouse` where company = '%s' and default_for_stock_transfer = 1 """%(co.name),as_dict=1)
                for w in ware:
                    sto = frappe.db.get_value("Bin",{"item_code":j["item_code"],"warehouse":w.name},['actual_qty'])
                    if not sto:
                        sto = 0
                    st += sto
                    data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>' %(st)
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(in_transit or 0)
            data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(del_total or 0)
            data += '</tr>'
        i += 1
    data += '</tr>'
    data += '</table>'
    return data

# @frappe.whitelist()
# def update_child_table():
# 	emp = frappe.get_all("Employee",{"status":"Active"},["*"])
# 	for i in emp:
# 		if i.history:
# 			print("yes")
# 		else:
# 			print("no")
# 			e = frappe.get_doc("Employee",i.name)
# 			e.append("history", {
# 			'date':'2023-09-01',
# 			'basic':i.basic,
# 			'hra':i.hra,
# 			'other_allowance':i._other_allowance,
# 			'transport_allowance':i.transportation,
# 			'medical_allowance':i.medical_allowance_,
# 			'air_ticket_allowance':i.air_ticket_allowance_,
# 			'mobile_allowance':i.mobile_allowance,
# 			'visa_cost':i.visa_cost_,
# 			'accommodation':i.accommodation,
# 			'leave_salary':i.leave_salary,
# 			'qid_cost':i.qid_cost,
# 			'medical_renewal':i.medical_renewal,
# 			'compensation':i.compensationemployee_insurence,
# 			'remark':'Salary on September-01'
# 			})
# 			e.save(ignore_permissions = True)


@frappe.whitelist()
def returnall():
    k = 0
    leave = frappe.db.get_list("Leave Application",{'docstatus':1},['name','company','creation','leave_type','status'])
    for i in leave:
        doc = frappe.db.exists("Leave Ledger Entry",{'transaction_name':i.name})
        if not doc:
            # if i.leave_type == "Casual Leave" and i.status != "Rejected":
            print(i.name)
    #             k = k + 1
    # print(k)

# @frappe.whitelist()
# def return_leave():
#     doc = frappe.db.sql(""" select employee_name,sum(total_leave_days) as total from `tabLeave Application` where leave_type = 'Casual Leave' and status = 'Approved' and docstatus = 1 group by employee """,as_dict=1)
#     for i in doc:
#         print(i.employee_name)
#         print(i.total)
