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
        _("Delivery Note") + ":Link/Delivery Note:200",
        _("Against Sales Order") + ":Link/Sales Order:200",
        _("Date") + ":Date/:110",
        _("Customer") + ":Link/Customer:300",
        _("Address") + ":Data/:150",
        _("Phone No") + ":Data/:150",
        _("Customer's PO No.") + ":Data/:230",
        _("Sales Person") + ":Data/:230",
        _("Discount Amount") + ":Currency/:100",
        _("Net Amount") + ":Currency/:100",
        _("Status") + ":Data/:200",
        _("Prepared By") + ":Data/:170"
    ]
    return columns

def get_data(filters):
    data = []
    conditions, filters = get_conditions(filters)

    delivery_notes = frappe.db.sql(
        f"""SELECT name, docstatus FROM `tabDelivery Note` WHERE {conditions}""",
        filters,
        as_dict=True,
    )

    for dn_record in delivery_notes:
        # Skip cancelled delivery notes
        if dn_record.docstatus == 2:
            continue

        dn = frappe.get_doc("Delivery Note", dn_record.name)
        for item in dn.items:
            row = [
                dn.name,
                item.against_sales_order,
                dn.posting_date,
                dn.customer,
                dn.address_display,
                dn.contact_mobile,
                dn.po_no,
                dn.sales_person_user,
                dn.discount_amount,
                dn.base_net_total,
                dn.status,
                dn.prepared_by_username
            ]
        data.append(row)
    return data

def get_conditions(filters):
    conditions = "1=1"  # start with true condition
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("company"):
        conditions += " AND company = %(company)s"
    if filters.get("docstatus"):
        conditions += " AND status = %(docstatus)s"
    if filters.get("dummy_dn"):
        conditions += " AND dummy_dn = %(dummy_dn)s"
    return conditions, filters
