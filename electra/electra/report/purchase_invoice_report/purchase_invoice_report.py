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
		_("Date") + ":Date/:95",
		_("Invoice No") + ":Data/:200",
		_("Purchase Invoice") + ":Link/Purchase Invoice:200",
		_("Supplier Name") + ":Data/:150",
		_("Currency") + ":Data/:70",
		_("Invoice Value") + ":Data/:100",
		_("Invoice QAR Value") + ":Data/:100",
		_("Overhead Cost") + ":Data/:150",
		_("Total Purchase") + ":Data/:150",
	]
	return columns

def get_data(filters):
	data = []
	purchase_invoice = frappe.db.get_all("Purchase Invoice",{'company':filters.company,"posting_date":('between',(filters.from_date,filters.to_date)),"stock_confirmation": ('not in',("Stock Confirmation")),"status":('not in',("Cancelled","Draft"))},['*'])
	for i in purchase_invoice:
		gt = frappe.get_doc("Purchase Invoice",i.name)
		for j in gt.items[:1]:
			# lc = frappe.db.sql("""select total_taxes_and_charges as pd from `tabLanded Cost Voucher`
			# left join `tabLanded Cost Purchase Receipt` on `tabLanded Cost Voucher`.name = `tabLanded Cost Purchase Receipt`.parent
			# where `tabLanded Cost Purchase Receipt`.receipt_document = '%s' and `tabLanded Cost Voucher`.docstatus =1 """%(j.purchase_receipt),as_dict=True)

			lc = frappe.db.sql("""select sum(`tabLanded Cost Item`.applicable_charges) as pd from `tabLanded Cost Voucher`
			left join `tabLanded Cost Item` on `tabLanded Cost Voucher`.name = `tabLanded Cost Item`.parent
			where `tabLanded Cost Item`.receipt_document = '%s' and `tabLanded Cost Voucher`.docstatus =1 """%(j.purchase_receipt),as_dict=True)
			if lc:
				for l in lc:
					if l.pd:
						p = l.pd
					else:
						p = 0
			else:
				p = 0
			tot = round((i.base_net_total+(p)),3)

			row = [i.posting_date,i.bill_no,i.name,i.supplier,i.currency,round(i.net_total,3),round(i.base_net_total,3),round((p),3),round(tot,3)]
			data.append(row)
	return data