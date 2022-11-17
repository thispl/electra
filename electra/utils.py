from __future__ import unicode_literals
import json
from re import S
from unicodedata import name
from datetime import datetime
from datetime import date, timedelta
import calendar
from erpnext.stock.get_item_details import get_item_price
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.selling.doctype.customer.customer import get_customer_outstanding, get_credit_limit
from erpnext.stock.get_item_details import get_valuation_rate
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
def fetch_credit_limit(company,customer):
    customer_list = get_details(company,customer)
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
            result = """
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
            """ %( credit_limit, outstanding_amt, bal,bypass_credit_limit_check,is_frozen,disabled )
        else:
            result = "Empty"
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
def get_last_valuation_rate(item_code):
    valuation_rate = 0
    latest_vr = frappe.db.sql("""
                SELECT valuation_rate as vr FROM `tabStock Ledger Entry` WHERE item_code = %s AND valuation_rate > 0
                ORDER BY posting_date DESC, posting_time DESC, creation DESC LIMIT 1
                """, (item_code),as_dict=True)
    if len(latest_vr) > 0:
        valuation_rate = latest_vr[0]
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
def make_dn(name):
    frappe.errprint(name)
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
    employees = frappe.get_list("Employee",{'user_id':user},['employee_name','designation','cell_number'],ignore_permissions=True)
    employee_list = frappe._dict()
    for e in employees:
        employee_list.update({
            'employee_name': e.employee_name,
            'designation': e.designation,
            'cell_number': e.cell_number
        })
    frappe.errprint(employee_list)
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
        qno = frappe.get_value('Cost Estimation',doc.cost_estimation,'quotation')
        if not qno:
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
def item_default_wh(doc,method):
    item_default_set = frappe.get_value('Item',doc.item_code,'item_default_set')
    if not item_default_set:
        companies = [
            {"company":"KINGFISHER - TRANSPORTATION","default_warehouse":"Kingfisher Transportation Warehouse - KT", "buying_cost_center" : "Main - KT", "selling_cost_center" : "Main - KT","expense_account": "Expenses Included In Valuation - KT","income_account":"Cost of Goods Sold - KT"},
            {"company":"STEEL DIVISION - ELECTRA","default_warehouse":"Steel Warehouse - SDE", "buying_cost_center" : "Main - SDE", "selling_cost_center" : "Main - SDE","expense_account": "5118 - Expenses Included In Valuation - SDE","income_account":"5111 - Cost of Goods Sold - SDE"},
            {"company":"MARAZEEM SECURITY SERVICES - HO","default_warehouse":"Marazeem HO Warehouse - MSSHO", "buying_cost_center" : "Main - MSSHO", "selling_cost_center" : "Main - MSSHO","expense_account": "5118 - Expenses Included In Valuation - MSSHO","income_account":"5111 - Cost of Goods Sold - MSSHO"},
            {"company":"TRADING DIVISION - ELECTRA","default_warehouse":"Electra Trading Warehouse - TDE", "buying_cost_center" : "Main - TDE", "selling_cost_center" : "Main - TDE","expense_account": "5118 - Expenses Included In Valuation - TDE","income_account":"5111 - Cost of Goods Sold - TDE"},
            {"company":"MEP DIVISION - ELECTRA","default_warehouse":"Electra MEP Warehouse - MEP", "buying_cost_center" : "Main - MEP", "selling_cost_center" : "Main - MEP","expense_account": "5118 - Expenses Included In Valuation - MEP","income_account":"5111 - Cost of Goods Sold - MEP"},
            {"company":"ELECTRA - BINOMRAN SHOWROOM","default_warehouse":"Electra Binomran Showroom Warehouse - EBO", "buying_cost_center" : "Main - EBO", "selling_cost_center" : "Main - EBO","expense_account": "5118 - Expenses Included In Valuation - EBO","income_account":"5111 - Cost of Goods Sold - EBO"},
            {"company":"KINGFISHER TRADING AND CONTRACTING COMPANY","default_warehouse":"Kingfisher Warehouse - KTCC", "buying_cost_center" : "Main - KTCC", "selling_cost_center" : "Main - KTCC","expense_account": "Expenses Included In Valuation - KTCC","income_account":"Cost of Goods Sold - KTCC"},
            {"company":"KINGFISHER - SHOWROOM","default_warehouse":"Kingfisher Showroom Warehouse - KS", "buying_cost_center" : "Main - KS", "selling_cost_center" : "Main - KS","expense_account": "Expenses Included In Valuation - KS","income_account":"Cost of Goods Sold - KS"},
            {"company":"MARAZEEM SECURITY SERVICES - SHOWROOM","default_warehouse":"Marazeem Showroom - MSSS", "buying_cost_center" : "Main - MSSS", "selling_cost_center" : "Main - MSSS","expense_account": "5118 - Expenses Included In Valuation - MSSS","income_account":"5111 - Cost of Goods Sold - MSSS"},
            {"company":"MARAZEEM SECURITY SERVICES","default_warehouse":"Marazeem Warehouse - MSS", "buying_cost_center" : "Main - MSS", "selling_cost_center" : "Main - MSS","expense_account": "5118 - Expenses Included In Valuation - MSS","income_account":"5111 - Cost of Goods Sold - MSS"},
            {"company":"ELECTRA - BARWA SHOWROOM","default_warehouse":"Barwa Showroom  - EBS", "buying_cost_center" : "Main - EBS", "selling_cost_center" : "Main - EBS","expense_account": "5118 - Expenses Included In Valuation - EBS","income_account":"5111 - Cost of Goods Sold - EBS"},
            {"company":"ELECTRICAL DIVISION - ELECTRA","default_warehouse":"Electra Electrical Warehouse - EDE", "buying_cost_center" : "Main - EDE", "selling_cost_center" : "Main - EDE","expense_account": "5118 - Expenses Included In Valuation - EDE","income_account":"5111 - Cost of Goods Sold - EDE"},
            {"company":"ENGINEERING DIVISION - ELECTRA","default_warehouse":"Electra Engineering Warehouse - EED", "buying_cost_center" : "Main - EED", "selling_cost_center" : "Main - EED","expense_account": "5118 - Expenses Included In Valuation - EED","income_account":"5111 - Cost of Goods Sold - EED"},
            {"company": "INTERIOR DIVISION - ELECTRA","default_warehouse":"Electra Interior Warehouse - INE", "buying_cost_center" : "Main - INE", "selling_cost_center" : "Main - INE","expense_account": "5118 - Expenses Included In Valuation - INE","income_account":"5111 - Cost of Goods Sold - INE"},
            {"company" :"Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)","default_warehouse":"Electra Warehouse - ASTCC", "buying_cost_center" : "Main - ASTCC", "selling_cost_center" : "Main - ASTCC","expense_account": "5118 - Expenses Included In Valuation - ASTCC","income_account":"5111 - Cost of Goods Sold - ASTCC"}
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
                frappe.errprint(company['default_warehouse'])
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
            {"company":"KINGFISHER - TRANSPORTATION","default_warehouse":"Kingfisher Transportation Warehouse - KT", "buying_cost_center" : "Main - KT", "selling_cost_center" : "Main - KT","expense_account": "Expenses Included In Valuation - KT","income_account":"Cost of Goods Sold - KT"},
            {"company":"STEEL DIVISION - ELECTRA","default_warehouse":"Steel Warehouse - SDE", "buying_cost_center" : "Main - SDE", "selling_cost_center" : "Main - SDE","expense_account": "5118 - Expenses Included In Valuation - SDE","income_account":"5111 - Cost of Goods Sold - SDE"},
            {"company":"MARAZEEM SECURITY SERVICES - HO","default_warehouse":"Marazeem HO Warehouse - MSSHO", "buying_cost_center" : "Main - MSSHO", "selling_cost_center" : "Main - MSSHO","expense_account": "5118 - Expenses Included In Valuation - MSSHO","income_account":"5111 - Cost of Goods Sold - MSSHO"},
            {"company":"TRADING DIVISION - ELECTRA","default_warehouse":"Electra Trading Warehouse - TDE", "buying_cost_center" : "Main - TDE", "selling_cost_center" : "Main - TDE","expense_account": "5118 - Expenses Included In Valuation - TDE","income_account":"5111 - Cost of Goods Sold - TDE"},
            {"company":"MEP DIVISION - ELECTRA","default_warehouse":"Electra MEP Warehouse - MDE", "buying_cost_center" : "Main - MDE", "selling_cost_center" : "Main - MDE","expense_account": "5118 - Expenses Included In Valuation - MDE","income_account":"5111 - Cost of Goods Sold - MDE"},
            {"company":"ELECTRA - BINOMRAN SHOWROOM","default_warehouse":"Electra Binomran Showroom Warehouse - EBO", "buying_cost_center" : "Main - EBO", "selling_cost_center" : "Main - EBO","expense_account": "5118 - Expenses Included In Valuation - EBO","income_account":"5111 - Cost of Goods Sold - EBO"},
            {"company":"KINGFISHER TRADING AND CONTRACTING COMPANY","default_warehouse":"Kingfisher Warehouse - KTCC", "buying_cost_center" : "Main - KTCC", "selling_cost_center" : "Main - KTCC","expense_account": "Expenses Included In Valuation - KTCC","income_account":"Cost of Goods Sold - KTCC"},
            {"company":"KINGFISHER - SHOWROOM","default_warehouse":"Kingfisher Showroom Warehouse - KS", "buying_cost_center" : "Main - KS", "selling_cost_center" : "Main - KS","expense_account": "Expenses Included In Valuation - KS","income_account":"Cost of Goods Sold - KS"},
            {"company":"MARAZEEM SECURITY SERVICES - SHOWROOM","default_warehouse":"Marazeem Showroom - MSSS", "buying_cost_center" : "Main - MSSS", "selling_cost_center" : "Main - MSSS","expense_account": "5118 - Expenses Included In Valuation - MSSS","income_account":"5111 - Cost of Goods Sold - MSSS"},
            {"company":"MARAZEEM SECURITY SERVICES","default_warehouse":"Marazeem Warehouse - MSS", "buying_cost_center" : "Main - MSS", "selling_cost_center" : "Main - MSS","expense_account": "5118 - Expenses Included In Valuation - MSS","income_account":"5111 - Cost of Goods Sold - MSS"},
            {"company":"ELECTRA - BARWA SHOWROOM","default_warehouse":"Barwa Showroom  - EBS", "buying_cost_center" : "Main - EBS", "selling_cost_center" : "Main - EBS","expense_account": "5118 - Expenses Included In Valuation - EBS","income_account":"5111 - Cost of Goods Sold - EBS"},
            {"company":"ELECTRICAL DIVISION - ELECTRA","default_warehouse":"Electra Electrical Warehouse - EDE", "buying_cost_center" : "Main - EDE", "selling_cost_center" : "Main - EDE","expense_account": "5118 - Expenses Included In Valuation - EDE","income_account":"5111 - Cost of Goods Sold - EDE"},
            {"company":"ENGINEERING DIVISION - ELECTRA","default_warehouse":"Electra Engineering Warehouse - EED", "buying_cost_center" : "Main - EED", "selling_cost_center" : "Main - EED","expense_account": "5118 - Expenses Included In Valuation - EED","income_account":"5111 - Cost of Goods Sold - EED"},
            {"company": "INTERIOR DIVISION - ELECTRA","default_warehouse":"Electra Interior Warehouse - INE", "buying_cost_center" : "Main - INE", "selling_cost_center" : "Main - INE","expense_account": "5118 - Expenses Included In Valuation - INE","income_account":"5111 - Cost of Goods Sold - INE"},
            {"company" :"Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)","default_warehouse":"Electra Warehouse - ASTCC", "buying_cost_center" : "Main - ASTCC", "selling_cost_center" : "Main - ASTCC","expense_account": "5118 - Expenses Included In Valuation - ASTCC","income_account":"5111 - Cost of Goods Sold - ASTCC"}
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
            "warehouse_name" : doc.name,
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
    frappe.errprint(item_details)
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
    frappe.errprint(item_details)
    data = ''
    data += '<h4><center><b>STOCK DETAILS</b></center></h4>'

    for j in item_details:
        country = frappe.get_value("Company",{"name":company},["country"])

        warehouse_stock = frappe.db.sql("""
        select sum(b.actual_qty) as qty from `tabBin` b join `tabWarehouse` wh on wh.name = b.warehouse join `tabCompany` c on c.name = wh.company where c.country = '%s' and b.item_code = '%s'
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

        stocks = frappe.db.sql("""select actual_qty,warehouse,stock_uom,stock_value from tabBin
        where item_code = '%s' """%(j["item_code"]),as_dict=True)

        pos = frappe.db.sql("""select `tabPurchase Order Item`.item_code as item_code,`tabPurchase Order Item`.item_name as item_name,`tabPurchase Order`.supplier as supplier,sum(`tabPurchase Order Item`.qty) as qty,`tabPurchase Order Item`.rate as rate,`tabPurchase Order`.transaction_date as date,`tabPurchase Order`.name as po from `tabPurchase Order`
        left join `tabPurchase Order Item` on `tabPurchase Order`.name = `tabPurchase Order Item`.parent
        where `tabPurchase Order Item`.item_code = '%s' and `tabPurchase Order`.docstatus != 2 order by rate asc limit 1""" % (j["item_code"]), as_dict=True)
    
        i = 0
        for po in pos:
            
            if pos:
                frappe.errprint(po.qty)
                data += '<table class="table table-bordered">'
                data += '<tr>'
                data += '<td colspan=1 style="width:13%;padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>ITEM CODE</b><center></td>'
                data += '<td colspan=1 style="width:33%;padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>ITEM NAME</b><center></td>'
                for stock in stocks:
                    if stock.actual_qty > 0:
                        wh = stock.warehouse
                        x = wh.split('- ')
                        data += '<td colspan=1 style="padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>%s</b><center></td>'%(x[-1])
                data += '<td colspan=1 style="padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>IN TRANSIT</b><center></td>'
                data += '<td colspan=1 style="padding:1px;border:1px solid black;font-size:14px;font-size:12px;background-color:#e35310;color:white;"><center><b>AGAINST PO</b><center></td>'
                data += '</tr>'
                
                
                
                data +='<tr>'
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(j["item_code"])
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(j["item_name"])
                for stock in stocks:
                    if stock.actual_qty > 0:
                        data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(stock.actual_qty)
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(in_transit)
                data += '<td style="text-align:center;border: 1px solid black" colspan=1>%s</td>'%(po.qty)
                data += '</tr>'
            i += 1
        data += '</table>'
        
    #     data+='<tr><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s<center><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s<center><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s<center><center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td><td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td></tr>'%(j["item_code"],j["item_name"],warehouse_stock["qty"], in_transit,total)
    
    # data += '</table>'
    return data



@frappe.whitelist()
def get_item_margin(item_details,company):
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
    
    for i in item_details:
        total_selling_price =  (i["rate"] * i["qty"]) + total_selling_price
        frappe.errprint(total_selling_price)
        warehouse_stock = frappe.db.sql("""
        select valuation_rate as vr from `tabBin` b 
        join `tabWarehouse` wh on wh.name = b.warehouse
        join `tabCompany` c on c.name = wh.company
        where b.item_code = '%s'
        """ % (i["item_code"]),as_dict=True)[0]    
        if not warehouse_stock.vr :
            warehouse_stock.vr  = 0
        cost_amount = (warehouse_stock.vr  * i["qty"]) + cost_amount
        cost_amount_ = (warehouse_stock.vr * i["qty"])
        tot =  cost_amount - total_selling_price
        tot_diff =  cost_amount_ - i["base_amount"]
        tot_ = tot_diff/cost_amount_ *100
        data_4+='''<tr>
        <td colspan=1 style="border: 1px solid black;font-size:12px;">%s</td>
        <td colspan=1 style="border: 1px solid black;font-size:12px;">%s</td>
        <td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td>
        <td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td>
        <td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td>
        <td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td>
        <td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td>
        <td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td>
        <td colspan=1 style="border: 1px solid black;font-size:12px;"><center>%s</center></td>
        </tr>'''%(i["item_code"],i["description"],i["qty"],warehouse_stock.vr ,i["rate"],round(cost_amount_,2),i["base_amount"],round(-tot_diff,2),round(-tot_,2))
    data_5 = ''
    if cost_amount_ == 0:
        total_margin_internal = (total_selling_price - cost_amount_)/100
        frappe.errprint('total_margin_internal')

    else:
        total_margin_internal = (round(-tot_,2))
        frappe.errprint(total_margin_internal)
        frappe.errprint('oo')

        

    
    data_5 += '''<table class="table"><tr>
    <td style="padding:1px;font-size:12px"><center><b>Cost Amount</b></center></td>

    <td  style="padding:1px;font-size:12px;"><b><center>:%s</center></b></td>
    <td style="padding:1px;font-size:12px"><center><b>Profit Amount</b></center></td>

    <td  style="padding:1px;font-size:12px;"><b><center>:%s</center></b></td>
    <td style="padding:1px;font-size:12px"><center><b>Profit Percentage</b></center></td>
    <td  style="padding:1px;font-size:12px;"><b><center>:%s</center></b></td>
    
    
   
    </tr>'''%(round(cost_amount,2),round(-tot,2),round(total_margin_internal,2))
    data_5+='''</table>'''
# pro/cost 100
    
    return data_4,data_5

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
def get_current_month_date(employee):
    now = datetime.now()
    days = calendar.monthrange(now.year, now.month)[1]
    return(days)

@frappe.whitelist()
def calculate_attendance(employee):
    name_reg = frappe.db.sql(
        """select name,hods_relieving_date,actual_relieving_date from `tabResignation Form` where employee = %s """ % (employee), as_dict=True)[0]
    current_date = name_reg.actual_relieving_date
    first_day_of_month = current_date.replace(day=1)
    hod_date = str(first_day_of_month)
    app_date = str(name_reg.actual_relieving_date)
    frappe.errprint(hod_date)
    frappe.errprint(app_date)
    frappe.errprint(type(app_date))
    if name_reg:
        att = frappe.db.sql("""select count(*) as count from `tabAttendance` where attendance_date between '%s' and '%s' and status = 'Present'  and employee = %s""" %
                            (hod_date, app_date, employee), as_dict=True)[0]
        cal = att
        return cal, name_reg

@frappe.whitelist()
def get_reg_form(employee):
    frappe.errprint(employee)
    name_reg = frappe.db.sql(
        """select name,hods_relieving_date,actual_relieving_date from `tabResignation Form` where employee = %s """ % (employee), as_dict=True)[0]
    current_date = name_reg.actual_relieving_date
    first_day_of_month = current_date.replace(day=1)
    return name_reg.name, first_day_of_month, name_reg.actual_relieving_date

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
            frappe.errprint(emp)
            if emp.actual_relieving_date == datetime.strptime((today()), '%Y-%m-%d').date():
                emp_n = frappe.get_doc('Employee', emp.employee)
                emp_n.status = "Left"
                emp_n.relieving_date = emp.actual_relieving_date
                emp_n.save(ignore_permissions=True)
    