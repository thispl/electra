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
        _("Project No.") + ":Link/Project:170",
        _("Project Reference") + ":Data/:200",
        _("Sales Order No") + ":Link/Sales Order:170",
        _("Project Description") + ":Data/:200",
        _("Contract Value") + ":Currency/:110",
        _("Revised Contract Value") + ":Currency/:110",
        _("Estimated cost to complete") + ":Currency/:110",
        _("Estimated Profit Margin") + ":Currency/:110",
        _("Actual Costs till Previous Year") + ":Currency/:110",
        _("Costs incurred during the year") + ":Currency/:110",
        _("Total Cost") + ":Currency/:110",
        _("Progress Bills Raised Previous Year") + ":Currency/:110",
        _("Progress Bills Raised Current Year") + ":Currency/:110",
        _("Revenue Recognised upto Previous Year") + ":Currency/:110",
        _("Revenue for the Current Year") + ":Currency/:110",
        _("Short/(Excess) Revenue Over Billings") + ":Currency/:110",
        _("Percentage to be Completed") + ":Percentage/:110",
        _("Value to be Executed") + ":Currency/:110",
        _("Delivery Note Percentage to be Completed") + ":Percentage/:110",
        _("Task Percentage to be Completed") + ":Percentage/:110",
        _("Project Costing Amount") + ":Currency/:110",
        _("Project Percentage to be Completed") + ":Percentage/:110",
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
        project_name,lead_customer = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['project_name','lead_customer'])
        if filters.project_no:
            project = frappe.db.get_value("Project",{'budgeting':i.name,'name':filters.project_no},['name'])
            task = frappe.db.count("Task",{"project":project},["name"])
            status = frappe.db.count("Task",{"project":project,"status":"Completed"},['name'])
            if task != 0:
                task_per = (status/task)*100
            else:
                task_per = 0
        else:
            project = frappe.db.get_value("Project",{'budgeting':i.name},['name'])
            task = frappe.db.count("Task",{"project":project},["name"])
            status = frappe.db.count("Task",{"project":project,"status":"Completed"},['name'])
            if task != 0:
                task_per = (status/task)*100
            else:
                task_per = 0
        sales = frappe.db.get_value("Project",{'budgeting':i.name},['sales_order'])
        dn_per = frappe.db.get_value("Sales Order",{"name":sales},['per_delivered'])
        dn_per = dn_per if dn_per is not None else 0
        task_per = task_per if task_per is not None else 0
        project_per = (dn_per + task_per) / 2
        project_cost = frappe.db.sql(""" select sum(costing_amount) as total from `tabTimesheet Detail` where project = '%s' """%(project),as_dict=True)[0]
        percent_total = frappe.db.get_value("Project",{'budgeting':i.name},['percent_complete'])
        if not percent_total:
            percent_total = 0
        total_costing_amount = frappe.db.get_value("Project",{'budgeting':i.name},['total_costing_amount'])
        if not total_costing_amount:
            total_costing_amount = 0
        total_purchase_cost = frappe.db.get_value("Project",{'budgeting':i.name},['total_purchase_cost'])
        if not total_purchase_cost:
            total_purchase_cost = 0
        purch_inv = total_purchase_cost + total_costing_amount
        ce = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['total_bidding_price'])
        per_to_complete = (100 - percent_total)
        perc = str(per_to_complete) + '%'
        to_complete = (per_to_complete/100) * i.total_bidding_price

        if project:			
            sales_in = frappe.db.sql(""" select sum(total) as total from `tabSales Invoice` where project = '%s'and `tabSales Invoice`.posting_date between '%s' and '%s'"""%(project,"2023-01-01","2023-12-31"),as_dict=True)[0]
            prev_sales_in = frappe.db.sql(""" select sum(total) as total from `tabSales Invoice` where project = '%s'and `tabSales Invoice`.posting_date between '%s' and '%s'"""%(project,"2022-01-01","2022-12-31"),as_dict=True)[0]
            revenue = frappe.db.sql(""" select sum(paid_amount) as amt from `tabPayment Entry` where project = '%s'and `tabPayment Entry`.posting_date between '%s' and '%s'"""%(project,"2023-01-01","2023-12-31"),as_dict=True)[0]
            prev_revenue = frappe.db.sql(""" select sum(paid_amount) as amt from `tabPayment Entry` where project = '%s'and `tabPayment Entry`.posting_date between '%s' and '%s'"""%(project,"2022-01-01","2022-12-31"),as_dict=True)[0]
            # prev_sales = frappe.db.sql(""" select sum(total) as total from `tabSales Invoice` where project = '%s'and `tabSales Invoice`.posting_date between '%s' and '%s'"""%(project,"2022-01-01","2022-12-31"),as_dict=True)[0]
            
            tot = 0
            dn_list = frappe.db.get_list("Delivery Note",{'project':project})
            if dn_list:
                for d_list in dn_list:
                    dn = frappe.get_doc("Delivery Note",d_list.name)
                    for d in dn.items:
                        w_house = frappe.db.get_value("Warehouse",{'company':dn.company,'default_for_stock_transfer':1},['name'])
                        val = frappe.db.get_value("Bin",{"item_code":d.item_code,"warehouse":w_house},['valuation_rate'])
                        if val:
                            total = val * d.qty
                            tot+=total
            
            row = [project,lead_customer,sales,project_name,ce,i.total_bidding_price,i.total_cost_of_the_project,i.net_profit_amount,'',tot,tot,prev_sales_in["total"],sales_in["total"],prev_revenue["amt"],revenue["amt"],'',perc,to_complete,dn_per,task_per,project_cost["total"],project_per]
            data.append(row)
    return data	