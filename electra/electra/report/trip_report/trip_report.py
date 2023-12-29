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
        _("Trip") + ":Link/Trip:120",
        _("Customer") + ":Link/Customer:120",
        _("Delivery Date") + ":Date/:120",
        _("Item") + ":Link/Item:120",
        _("Item Name") + ":Data:120",
        _("Qty") + ":Int:100",
        _("Rate") + ":Currency/:110",
        _("Amount") + ":Currency/:110",
        _("UOM") + ":Link/UOM:110",
        _("Sales Order") + ":Link/Sales Order:140",
        _("Driver") + ":Link/Employee:120",
        _("Driver Name") + ":Data:120",
        _("Vehicle Number") + ":Link/Vehicle:120",
        _("From Location") + ":Data:180",
        _("To Location") + ":Data:180",
        
    ]
    return columns

def get_data(filters):
    data = []
    if filters.item_code:
        trips = frappe.db.sql("""SELECT * FROM `tabTrip` trip INNER JOIN `tabTrip Item` item ON trip.name = item.parent WHERE trip.docstatus != 2 and item.item_code = %s """,(filters.item_code),as_dict=True)
    elif filters.driver_name:
        trips = frappe.db.sql("""SELECT * FROM `tabTrip` trip INNER JOIN `tabTrip Item` item ON trip.name = item.parent WHERE trip.docstatus != 2 and trip.driver_name = %s """, (filters.driver_name),as_dict=True)
    elif filters.customer:
        trips = frappe.db.sql("""SELECT * FROM `tabTrip` trip INNER JOIN `tabTrip Item` item ON trip.name = item.parent WHERE trip.docstatus != 2 and trip.customer = %s """, (filters.customer),as_dict=True)
    elif filters.sales_order:
        trips = frappe.db.sql("""SELECT * FROM `tabTrip` trip INNER JOIN `tabTrip Item` item ON trip.name = item.parent WHERE trip.docstatus != 2 and trip.work_order_no = %s """, (filters.sales_order),as_dict=True)
    elif filters.status:
        trips = frappe.db.sql("""SELECT * FROM `tabTrip` trip INNER JOIN `tabTrip Item` item ON trip.name = item.parent WHERE trip.docstatus != 2 and trip.docstatus = %s """, (filters.status),as_dict=True)
    elif filters.from_date and filters.to_date:
        trips = frappe.db.sql("""SELECT * FROM `tabTrip` trip INNER JOIN `tabTrip Item` item ON trip.name = item.parent WHERE trip.docstatus != 2 and trip.delivery_date between  %s and %s """, (filters.from_date,filters.to_date),as_dict=True)
    else:
        trips = frappe.db.sql("""SELECT * FROM `tabTrip` trip INNER JOIN `tabTrip Item` item ON trip.name = item.parent WHERE trip.docstatus != 2 """, as_dict=True)

    for j in trips:
        row = [j.parent,j.customer,j.delivery_date,j.item_code,j.item_name,j.qty,j.rate,j.amount,j.uom,j.work_order_no,j.driver_name,j.driver,j.vehicle_number,j.from_location,j.to_location]
        data.append(row)
    return data 