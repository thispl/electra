# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import erpnext

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Company") + ":Data/:450",
		_("Invoice QAR Value") + ":Float/:150",
		_("Overhead Cost") + ":Float/:150",
		_("Total Purchase") + ":Float/:150",
	]
	return columns

def get_data(filters):
    data = []
    row_data = {}

    purchase_invoice = frappe.db.get_all(
        "Purchase Invoice",
        {
            "posting_date": ('between', (filters.from_date, filters.to_date)),
            "stock_confirmation": ('not in',("Stock Confirmation")),
            "status": ('not in', ["Cancelled", "Draft"])
        },
        ['*']
    )

    for i in purchase_invoice:
        company = i.company
        if company not in row_data:
            row_data[company] = {
                "Invoice QAR Value": 0,
                "Overhead Cost": 0,
                "Total Purchase": 0,
            }

        gt = frappe.get_doc("Purchase Invoice", i.name)
        for j in gt.items[:1]:
            lc = frappe.db.sql(
                """select sum(`tabLanded Cost Item`.applicable_charges) as pd from `tabLanded Cost Voucher`
                left join `tabLanded Cost Item` on `tabLanded Cost Voucher`.name = `tabLanded Cost Item`.parent
                where `tabLanded Cost Item`.receipt_document = '%s' and `tabLanded Cost Voucher`.docstatus =1 """ % (
                    j.purchase_receipt), as_dict=True)

            if lc:
                for l in lc:
                    if l.pd:
                        p = l.pd
                    else:
                        p = 0
            else:
                p = 0
            tot = round((i.base_net_total + (p)), 3)
            row_data[company]["Invoice QAR Value"] += round(i.base_net_total, 3)
            row_data[company]["Overhead Cost"] += round(p, 3)
            row_data[company]["Total Purchase"] += round(tot, 3)
    for company, values in row_data.items():
        row = [company, round(values["Invoice QAR Value"],2), round(values["Overhead Cost"],2), round(values["Total Purchase"],2)]
        data.append(row)

    return data
