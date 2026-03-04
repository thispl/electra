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
    columns = [
        _("Sl No.Date") + ":Date:200",
        _("Stock Confirmation No") + ":Link/Stock Confirmation:200",
        _("Stock Transfer No") + ":Link/Stock Transfer:200",
        _("Stock Request No") + ":Link/Stock Request:200",
        _("Transfer From") + ":Data:200",
        _("Transfer To") + ":Link/Company:200",
        _("Status") + ":Data:200",
         _("Amount") + ":Currency:200",
        _("Remarks") + ":Small Text:100"
       
    ]
    return columns

def get_data(filters):
    data = []
    conditions = []
    
    if filters.is_checked == 1:
        if filters.target_company:
            conditions.append("target_company = '%s'" % filters.target_company)
    if filters.source_company:
        conditions.append("source_company = '%s'" % filters.source_company)
    if filters.target_company:
            conditions.append("target_company = '%s'" % filters.target_company)
    if filters.from_date and filters.to_date:
        conditions.append("confirmed_date BETWEEN '%s' AND '%s'" % (filters.from_date, filters.to_date))

    query = "SELECT * FROM `tabStock Confirmation` WHERE docstatus != 2"
    if conditions:
        query += " AND " + " AND ".join(conditions)

    sa = frappe.db.sql(query, as_dict=True)

    for i in sa:
        sb = frappe.get_value('Purchase Invoice', {"Confirmation_number": i.name,'docstatus':1}, ['grand_total'])
        row = [
            i.confirmed_date, 
            i.name, 
            i.ic_material_transfer_confirmation, 
            i.ic_material_transfer_request,
            i.source_company, 
            i.target_company,
            i.workflow_state, 
            round(flt(sb),2),
            i.remarks
        ]
        data.append(row)

    return data
