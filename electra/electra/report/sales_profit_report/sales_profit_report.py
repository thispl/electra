# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext



def execute(filters=None):
    columns =[]
    data = []
    columns += [
        _("Sales Invoice") + ":Link/Sales Invoice:200",
        _("Date") + ":Date/:95",
        _("Customer") + ":Link/Customer:200",
        _("Sales Person") + ":Link/Sales Person:200",
        _("Discount Amount") + ":Currency/:100",
        _("Net Amount") + ":Currency/:100",
        _("Cost") + ":Currency/:100",
		_("Profit") + ":Currency/:100" ,
		_("Percentage") + ":Percentage/:100",
		_("Invoice Type") + ":Data/:100",
        _("Status") + ":Data/:100",
        _("Prepared By") + ":Data/:200"
    ]
    data = get_invoice_data(filters)
    return columns, data

def get_invoice_data(filters):
    data =[]
    total_calc = 0
    dis_amount = 0
    total_add = 0
    grand_total = 0
    total_percentage = 0
    count = 0
    conditions = build_conditions(filters)
    query = """SELECT * FROM `tabSales Invoice` WHERE {conditions} and stock_transfer != 'Stock Transfer' AND is_internal_customer = 0 """.format(conditions=conditions)
    sales = frappe.db.sql(query, as_dict=True)
    for i in sales:
        if i.docstatus ==1:
            emp_name = frappe.db.get_value("User",i.prepared_by,['full_name'])
            dn = frappe.get_doc("Sales Invoice",i.name)
            add = 0
            prof = 0
            pro = 0
            cal =0
            for child in dn.items:
                add += child.qty * child.valuation_rate
            calc = i.base_grand_total - add
            # if calc >=0 :
            cal =calc
            total_calc += cal
            if i.base_grand_total > 0:
                prof = (calc / i.base_grand_total) * 100
                # if prof >= 0:
                pro = prof
            row = [i.name,i.posting_date,i.customer,i.sales_person_user,round(i.discount_amount,2),round(i.base_grand_total,2),round(add,2),round(cal,2),round(pro,2),i.invoice_type,i.status,emp_name]
            if i.customer != "Miscellaneous Customer (SAMPLE)":
                count +=1
                total_percentage +=prof
                total_add += add
                grand_total += i.base_grand_total
                dis_amount += i.discount_amount
            data.append(row)
    if count !=0:
        prc = (total_calc/grand_total)*100
    else:
        prc=0
    to = ["TOTAL","","","",round(dis_amount,2),round(grand_total,2),round(total_add,2),round(total_calc,2),round(prc,2),"","",""]
    data.append(to)
    return data

def build_conditions(filters):
    conditions = []
    if filters.get('company'):
        conditions.append("company = '{company}'".format(company=filters.get('company')))
    if filters.get('from_date') and filters.get('to_date'):
        conditions.append("posting_date BETWEEN '{from_date}' AND '{to_date}'".format(from_date=filters.get('from_date'), to_date=filters.get('to_date')))    
    return " AND ".join(conditions)

