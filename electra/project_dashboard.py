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
import json


@frappe.whitelist()
def get_project_dashboard(doc):
    project = json.loads(doc)
    so = project['sales_order']
    name = project['name']
    project_budget = project["budgeting"]
    val = frappe.db.get_value("Sales Order",project['sales_order'],['grand_total'])
    deliver = frappe.db.get_value("Sales Order",project['sales_order'],['per_delivered'])

    pb = frappe.db.sql(""" select * from `tabProject Budget` where name = '%s' and docstatus = 1 """%(project['budgeting']),as_dict=True)
    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    
    # pb = frappe.db.sql(""" select * from `tabProject Budget` where company = '%s' and docstatus = 1 """%(project['company']),as_dict=True)
    for i in pb:
        project_name,lead_customer = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['project_name','lead_customer'])
        project = frappe.db.get_value("Project",{'budgeting':i.name},['name'])
        percent_complete = frappe.db.get_value("Project",{'budgeting':i.name},['percent_complete'])
        if not percent_complete:
            percent_complete = 0
        total_costing_amount = frappe.db.get_value("Project",{'budgeting':i.name},['total_costing_amount'])
        if not total_costing_amount:
            total_costing_amount = 0
        total_purchase_cost = frappe.db.get_value("Project",{'budgeting':i.name},['total_purchase_cost'])
        if not total_purchase_cost:
            total_purchase_cost = 0
        purch_inv = total_purchase_cost + total_costing_amount
        ce = frappe.db.get_value("Cost Estimation",{'name':i.cost_estimation},['total_bidding_price'])
        per_to_complete = (100 - percent_complete)
        per_complete = str(percent_complete) + '%'
        perc = str(per_to_complete) + '%'
        to_complete = (per_to_complete/100) * i.total_bidding_price
        if project:
            new_so = frappe.db.sql("""select sum(`tabSales Order Item`.qty) as qty,sum(`tabSales Order Item`.delivered_qty) as d_qty from `tabSales Order` left join `tabSales Order Item` on `tabSales Order`.name = `tabSales Order Item`.parent	where `tabSales Order`.name = '%s' """ % (so), as_dict=True)[0]
            if not new_so['qty']:
                new_so['qty'] = 0
            if not new_so['d_qty']:
                new_so['d_qty'] = 0
            del_total = new_so['qty'] - new_so['d_qty']
            pending_task_qty = frappe.db.sql("""select sum(`tabTask`.pending_qty) as qty from `tabTask` where `tabTask`.project = '%s' """ % (name),
            as_dict=True)[0]
            
            task_complete = frappe.db.sql("""select  sum(`tabTask`.qty) as qty ,sum(`tabTask`.completed_qty) as completed_qty  from `tabTask` where `tabTask`.project = '%s' """ %(name),as_dict=True)[0]
            frappe.errprint(task_complete)
            if task_complete['qty']:
                total_qty = task_complete["qty"]
                total_completed_qty = task_complete["completed_qty"]
                complete_qty = (total_completed_qty / total_qty) * 100
                not_complete = 100 - complete_qty
            else:
                total_qty = 0
                total_completed_qty = 0
                complete_qty = 0
                not_complete = 0
        
                        
        html = frappe.render_template(
            "templates/pages/project_dashboard.html",
            {
                "doc": doc,
                "so":so,
                "name":name,
                "val":round(val,2),
                "project_budget":project_budget,
                
                "total_cost":round(i.total_cost_of_the_project,2),
                "bid":round(i.total_bidding_price,2),
                "ce":ce,
                "to_complete":round(to_complete,2),
                "net_profit_amount":round(i.net_profit_amount,2),
                "percent_complete":per_complete,
                "perc":perc,
                "deliver":round(deliver,2),
                "cost_estimation":i.cost_estimation,
                "to_supply":del_total,
                "pending_task_qty":pending_task_qty['qty'],
                "complete_qty":complete_qty,
                "not_complete":not_complete,
                'gross_profit':i.gross_profit_amount,
                'profit':round(i.gross_profit_percent)
            },
        )
        return html