# Copyright (c) 2013, Abdulla and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import date_diff, flt, cint
from six import iteritems
# from erpnext.stock.doctype.serial_no.serial_no import get_serial_nos

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	columns = []
	columns += [
	    _("Purchase Invoice Date") +':Data/:200',
		_("Supplier Name")+':Data/:100',
		_("Supplier ID")+':Data/:100',
		_("PI Entry Number")+':Data/:200',
		_("Amount")+':Data/:100',
		_("Landing Cost")+':Data/:200',
		_("PO Number ")+':Data/:200'
		
        
	]
	return columns

def get_data(filters):
	data=[]
	
	po = frappe.db.get_all("Purchase Invoice",{"posting_date": ("between",(filters.from_date,filters.to_date))},['*'])
	for p in po:
		pi = frappe.db.get_all("Purchase Invoice",['*'])
		frappe.errprint(pi)
		piu = frappe.db.sql(""" select purchase_order,purchase_receipt from `tabPurchase Invoice` left join `tabPurchase Invoice Item` on 
		`tabPurchase Invoice`.name = `tabPurchase Invoice Item`.parent where `tabPurchase Invoice`.name ='%s' """ %(p.name),as_dict=True)
		for pin in piu[:1]:
			frappe.errprint(pin)
			ping = frappe.db.sql(""" select total_taxes_and_charges from `tabLanded Cost Voucher` left join `tabLanded Cost Purchase Receipt` on 
			`tabLanded Cost Purchase Receipt`.parent =`tabLanded Cost Voucher`.name where `tabLanded Cost Purchase Receipt`.receipt_document ='%s' """  %(pin.purchase_receipt),as_dict=True)
			for pop in ping:
				
				frappe.errprint(pop)
				row = [p.posting_date,p.supplier_name,p.supplier,p.name,p.grand_total,pop.total_taxes_and_charges,pin.purchase_order]
				data.append(row)
	return data
