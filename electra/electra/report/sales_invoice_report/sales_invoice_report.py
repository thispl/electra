# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext



def execute(filters=None):
    columns = []
    data = []
    
    # Base columns
    columns += [
        _("Sales Invoice") + ":Link/Sales Invoice:200",
    ]
    if filters.get("company") == "MEP DIVISION - ELECTRA":
        columns += [
        _("Return Against") + ":Link/Sales Invoice:200",
    ]
    if filters.get("order_type") and filters.get("order_type") == "Project":
        columns += [
            _("Project") + ":Link/Project:200",
            _("Title of Project") + ":Data:250",
        ]
    
    # Continue with the remaining columns
    columns += [
        _("Sales Order") + ":Link/Sales Order:200",
        _("Customer's PO No") + ":Data:200",
        _("Date") + ":Date:110",
        _("Customer") + ":Link/Customer:250",
        _("Sales Person") + ":Link/Sales Person:150",
        _("Total Amount") + ":Currency:150",
        _("Net Amount") + ":Currency:150",
        _("Discount Amount") + ":Currency:150",
    ]
    
    if filters.get("order_type") and filters.get("order_type") == "Project":
        columns += [
            _("Advance Amount") + ":Currency:150",
            _("Retention Amount") + ":Currency:150",
        ]

    columns += [		
        _("Invoice Type") + ":Data:150",
        _("Status") + ":Data:100",
        _("Prepared By") + ":Data:300",
    ]

    # Get data
    data = get_invoice_data(filters)
    
    return columns, data


def get_invoice_data(filters):
    data = []
    conditions = build_conditions(filters)
    
    if filters.get("status"):
        query = f"""SELECT * FROM `tabSales Invoice` WHERE {conditions}"""
    else:
        query = f"""SELECT * FROM `tabSales Invoice` WHERE docstatus = 1 AND {conditions}"""
    
    sales = frappe.db.sql(query, as_dict=True)

    for i in sales:
        # if i.docstatus == 1:
        emp_name = frappe.db.get_value("User",i.prepared_by,['full_name'])
        si = frappe.get_doc("Sales Invoice",i.name)
        if si.stock_transfer != "Stock Transfer":
            for child in si.items:
                if si.order_type == "Project":
                    if i.is_return ==1:
                        total = round(i.total,2)
                    else:
                        total = round(si.custom_total_invoice_amount,2)
                else:
                    total = round(i.total,2)
                sales_order=frappe.db.get_value("Sales Invoice Item",{'parent':i.name},['sales_order'])
                project = frappe.db.get_value('Project',{'sales_order':sales_order},['name']) or ""
                so = frappe.db.get_value("Sales Invoice Item",{"parent":i.name},["sales_order"]) 
                if filters.get("company") == "MEP DIVISION - ELECTRA":
                    if filters.get("order_type") == "Project":
                        if i.is_return ==1:
                            
                            row = [i.name,i.return_against,project,i.title_of_project,so,i.po_no,i.posting_date,i.customer,i.sales_person_user,round(i.total,2),round(i.net_total_project,2),round(i.discount_amount,2),round(i.adv_amount,2) or 0,round(i.ret_amount,2) or 0,round(i.discount_amount,2),i.invoice_type,i.status,i.prepared_by]
                        else:
                            row = [i.name,i.return_against,project,i.title_of_project,so,i.po_no,i.posting_date,i.customer,i.sales_person_user,total,round(total-i.adv_amount-i.ret_amount-i.discount_amount,2),round(i.discount_amount,2),round(i.adv_amount,2) or 0,round(i.ret_amount,2) or 0,round(i.discount_amount,2),i.invoice_type,i.status,i.prepared_by]
                    else:
                        if i.is_return ==1 and si.order_type == "Project":
                            row = [i.name,i.return_against,so,i.po_no,i.posting_date,i.customer,i.sales_person_user,total,round(i.net_total_project,2),round(i.discount_amount,2),i.invoice_type,i.status,i.prepared_by,emp_name]    
                        else:
                            row = [i.name,i.return_against,so,i.po_no,i.posting_date,i.customer,i.sales_person_user,total,round(total-i.adv_amount-i.ret_amount-i.discount_amount,2),round(i.discount_amount,2),i.invoice_type,i.status,i.prepared_by,emp_name]    
                else:
                    if filters.get("order_type") == "Project":
                        if i.is_return ==1:
                            
                            row = [i.name,project,i.title_of_project,so,i.po_no,i.posting_date,i.customer,i.sales_person_user,round(i.total,2),round(i.net_total_project,2),round(i.discount_amount,2),round(i.adv_amount,2) or 0,round(i.ret_amount,2) or 0,round(i.discount_amount,2),i.invoice_type,i.status,i.prepared_by]
                        else:
                            row = [i.name,project,i.title_of_project,so,i.po_no,i.posting_date,i.customer,i.sales_person_user,total,round(total-i.adv_amount-i.ret_amount-i.discount_amount,2),round(i.discount_amount,2),round(i.adv_amount,2) or 0,round(i.ret_amount,2) or 0,round(i.discount_amount,2),i.invoice_type,i.status,i.prepared_by]
                    else:
                        if i.is_return ==1 and si.order_type == "Project":
                            row = [i.name,so,i.po_no,i.posting_date,i.customer,i.sales_person_user,total,round(i.net_total_project,2),round(i.discount_amount,2),i.invoice_type,i.status,i.prepared_by,emp_name]    
                        else:
                            row = [i.name,so,i.po_no,i.posting_date,i.customer,i.sales_person_user,total,round(total-i.adv_amount-i.ret_amount-i.discount_amount,2),round(i.discount_amount,2),i.invoice_type,i.status,i.prepared_by,emp_name]    
            data.append(row)
    return data

def build_conditions(filters):
    conditions = []
    if filters.get('sales_person_user'):
        conditions.append("sales_person_user = '{sales_person_user}'".format(sales_person_user=filters.get('sales_person_user')))
    if filters.get('company'):
        conditions.append("company = '{company}'".format(company=filters.get('company')))
    if filters.get('customer'):
        conditions.append("customer = '{customer}'".format(customer=filters.get('customer')))
    if filters.get('status'):
        conditions.append("status = '{status}'".format(status=filters.get('status')))
    if filters.get('from_date') and filters.get('to_date'):
        conditions.append("posting_date BETWEEN '{from_date}' AND '{to_date}'".format(from_date=filters.get('from_date'), to_date=filters.get('to_date')))    
    if filters.get('invoice_type'):
        conditions.append("invoice_type = '{invoice_type}'".format(invoice_type=filters.get('invoice_type')))
    if filters.get('order_type'):
        conditions.append("order_type = '{order_type}'".format(order_type=filters.get('order_type')))
    
    # conditions.append("docstatus = 1")  # Filter for approved invoices
    # conditions.append("docstatus != 2") 
    return " AND ".join(conditions)

