# Copyright (c) 2013, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns, data = [], []
    columns = get_columns()
    po_list = get_po_list()
    data.append(po_list)
    return columns, data

def get_columns():
    columns = []

    columns += [ _("PO No") + ":Link/Purchase Order:120",_("Date") + ":Date:120",_("Supplier") + ":Data:120",
                 _("Div") + ":Data:120",_("IN/LC") + ":Data:120",_("PRQ") + ":Data:120",
                 _("Proj/Stock") + ":PI:120",_("Shipment Type") + ":Category:120",_("Currency") + ":Data:120",
                 _("PO Value") + ":Data:120",_("Value QR") + ":Currency:120",_("Payment Status") + ":Data:120",_("Production Finish") + ":Data:120",
                 _("Shipment Departure Date") + ":Date:120",_("DOC") + ":Data:120",_("Shipment Arrival Date") + ":Date:120",
                 _("Goods Reciept") + ":Data:120",_("Purchase Entry No") + ":Data:120",_("Purchase Entry Date") + ":Date:120",_("Completed/LIVE") + ":Data:120"
                  ]

    return columns

def get_po_list():
    po_list = []
    pos = frappe.get_all('Purchase Order',['name','transaction_date'])
    for po in pos:
        po_list += [po.name,po.transaction_date]
    return po_list