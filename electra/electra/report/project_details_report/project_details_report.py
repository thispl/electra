# # Copyright (c) 2023, Abdulla and contributors
# # For license information, please see license.txt

import frappe
# from frappe import _
# from frappe.utils import flt, getdate
# import erpnext

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
        _("Customer") + ":Link/Customer:200",
        _("Order Reference") + ":Link/Sales Order:200",
        _("Project Reference") + ":Link/Project:200",
        _("Order Value") + ":Float/:160",
        _("Invoice Value Till Date") + ":Float/:180",
        _("Cost Till Date") + ":Float/:160",
        _("Gross Profit") + ":Float/:160",
        _("% Of G.P") + ":Percentage/:100",
        _("Balance to Invoice") + ":Float/:170",
        _("Total Collection") + ":Float/:160",
        _("O/S Receipts") + ":Float/:160",
        
    ]
    return columns

def get_conditions(filters):
    conditions = ""
    if filters.get("company"):
        conditions += " company = %(company)s"
    if filters.get("sales_order"):
        conditions += "and sales_order = %(sales_order)s"
    return conditions, filters
    

def get_data(filters):
    data = []
    conditions, filters = get_conditions(filters)
    pb = frappe.db.sql("""
        SELECT * FROM `tabProject Budget`
        WHERE docstatus = 1 and %s
        """ % conditions, filters, as_dict=True)
    
    for i in pb:
        lead_customer = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation, 'docstatus': 1},['lead_customer'])
        
        sales = frappe.db.get_value("Project",{'budgeting':i.name},['sales_order'])
        
        if filters.project_no:
            project = frappe.db.get_value("Project",{'budgeting':i.name,'name':filters.project_no},['name'])
        elif filters.status:
            project = frappe.db.get_value("Project",{'budgeting':i.name,'status':filters.status},['name'])
        elif filters.from_date and filters.to_date:
            project = frappe.db.get_value("Project",{'budgeting':i.name,'creation':('between',(filters.from_date,filters.to_date))},['name'])
        elif filters.from_date and filters.to_date and filters.status:
            project = frappe.db.get_value("Project",{'budgeting':i.name,'status':filters.status,'creation':('between',(filters.from_date,filters.to_date))},['name'])
        
        else:
            project = frappe.db.get_value("Project",{'budgeting':i.name},['name'])
        if project:
            sales_ord = frappe.db.sql("""select grand_total as grand_total from `tabSales Order` where project = '%s' and docstatus = 1 """%(project),as_dict = True)[0]			
            if not sales_ord["grand_total"]:
                sales_ord["grand_total"] = 0
                
            sales_in = frappe.db.sql(""" select sum(grand_total) as total from `tabSales Invoice` where project = '%s' and docstatus = 1 """%(project),as_dict=True)[0]
            if not sales_in["total"]:
                sales_in["total"] = 0
                # frappe.errprint(type(sales_in["total"]))
                # frappe.errprint(sales_in["total"])
            prev_revenue = frappe.db.sql(""" select sum(paid_amount) as amt from `tabPayment Entry` where project = '%s' and docstatus = 1 """%(project),as_dict=True)[0]
            if not prev_revenue["amt"]:
                prev_revenue["amt"] = 0
            # frappe.errprint(type(prev_revenue["amt"]))
            # frappe.errprint(prev_revenue["amt"])
            tot = 0
            
            dn_list = frappe.db.get_list("Delivery Note",{'project':project, 'docstatus': 1})
            if dn_list:
                for d_list in dn_list:
                    dn = frappe.get_doc("Delivery Note",d_list.name)
                    for d in dn.items:
                        w_house = frappe.db.get_value("Warehouse",{'company':dn.company,'default_for_stock_transfer':1},['name'])
                        val = frappe.db.get_value("Bin",{"item_code":d.item_code,"warehouse":w_house},['valuation_rate'])
                        if val is not None:
                            total = val * d.qty
                            tot+=total
            gross_profit_amount=sales_in["total"]-tot
            if gross_profit_amount>0:
                gross_profit_per=(gross_profit_amount/sales_in["total"])*100
            else:
                gross_profit_per=0
            row = [lead_customer,sales,project,format_decimals(sales_ord["grand_total"]),format_decimals(sales_in["total"]),format_decimals(tot),format_decimals(gross_profit_amount),format_decimals(gross_profit_per),format_decimals(sales_ord["grand_total"] - sales_in["total"]),format_decimals(prev_revenue["amt"]),format_decimals(sales_in["total"] - prev_revenue["amt"])]
            data.append(row)
    return data                       
    
def format_decimals(value):
    result = round(value, 2)
    return result   