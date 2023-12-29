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
        _("Customer") + ":Link/Customer:170",
        _("Order Reference") + ":Link/Sales Order:170",
        _("Project Reference") + ":Link/Project:170",
        _("Order Value") + ":Currency/:110",
        _("Invoice Value Till Date") + ":Currency/:110",
        _("Cost Till Date") + ":Currency/:110",
        _("Gross Profit") + ":Currency/:110",
        _("% Of G.P") + ":Percentage/:110",
        _("Balance to Invoice") + ":Currency/:110",
        _("Total Collection") + ":Currency/:110",
        _("O/S Receipts") + ":Currency/:110",
        
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
        lead_customer = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['lead_customer'])
        
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
            sales_ord = frappe.db.sql("""select grand_total as grand_total from `tabSales Order` where project = '%s' """%(project),as_dict = True)[0]			
            if not sales_ord["grand_total"]:
                sales_ord["grand_total"] = 0
                
            sales_in = frappe.db.sql(""" select sum(total) as total from `tabSales Invoice` where project = '%s' """%(project),as_dict=True)[0]
            if not sales_in["total"]:
                sales_in["total"] = 0
                frappe.errprint(type(sales_in["total"]))
                frappe.errprint(sales_in["total"])
            prev_revenue = frappe.db.sql(""" select sum(paid_amount) as amt from `tabPayment Entry` where project = '%s' """%(project),as_dict=True)[0]
            if not prev_revenue["amt"]:
                prev_revenue["amt"] = 0
            frappe.errprint(type(prev_revenue["amt"]))
            frappe.errprint(prev_revenue["amt"])
            tot = 0
            dn_list = frappe.db.get_list("Delivery Note",{'project':project})
            if dn_list:
                for d_list in dn_list:
                    dn = frappe.get_doc("Delivery Note",d_list.name)
                    for d in dn.items:
                        w_house = frappe.db.get_value("Warehouse",{'company':dn.company,'default_for_stock_transfer':1},['name'])
                        val = frappe.db.get_value("Bin",{"item_code":d.item_code,"warehouse":w_house},['valuation_rate'])
                        if val is not None:
                            total = val * d.qty
                            tot+=total
            row = [lead_customer,sales,project,sales_ord["grand_total"],sales_in["total"],tot,i.gross_profit_amount,i.gross_profit_percent,(sales_ord["grand_total"] - sales_in["total"]),prev_revenue["amt"],(sales_in["total"] - prev_revenue["amt"])]
            data.append(row)
    return data                       
    