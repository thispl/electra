# Copyright (c) 2013, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import msgprint, _

def execute(filters=None):
	columns, data = [], []
	row = []
	columns = get_columns()
	purchase_orders = frappe.get_all('Purchase Order',['*'])
	for po in purchase_orders:
		row = [
		po.name,po.transaction_date,po.supplier,po.division,po.in_lc,
		po.name,po.warehouse_type,po.proforma_invoice,po.shipment_type,
		po.category,po.currency,po.total,po.base_total,po.payment_status,po.production_finish_,
		po.shipment_departure_date,po.doc__,po.shipment__arrival_date,po.goods_receipt,
		po.purchase_entry_no,po.purchase_entry_date,po.completed_status,po.remarks]
		data.append(row)
	return columns, data

def get_columns():
	columns = []
	columns += [
		_("PO No") + ":Link/Purchase Order:120", 
		_("Date") + ":Date/:120",
		_("Supplier") + ":Link/Supplier:120", _("Div") + ":Data/:120",
		_("IN/LC") + ":Data:120", _("PRQ") + ":Link/Material Request:120",_("Proj / Stock") + ":Data:120", 
		_("PI") + ":Data:120", _("Shipment Type") + ":Data/:120",
		_("Category") + ":Data:120", _("Currency") + ":Data/:120",
		_("PO Value") + ":Data:120", _(" Value QAR ") + ":Data/:120",
		_("Payment Status") + ":Data:120", _("Production Finish") + ":Date/:120",
		_("Shipment Departure Date") + ":Data:120", _("DOC") + ":Data/:120",
		_("Shipment Arrival Date") + ":Date:120", _("Goods Reciept") + ":Data/:120",
		_("Purchase Entry No") + ":Data:120", _("Purchase Entry Date") + ":Date/:120",
		_("Completed/LIVE") + ":Data:120", _("Remarks") + ":Data/:120"
	]
	return columns