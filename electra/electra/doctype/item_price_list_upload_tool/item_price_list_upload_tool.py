# Copyright (c) 2024, Abdulla and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class ItemPriceListUploadTool(Document):
# 	pass
# Copyright (c) 2024, Teampro and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from time import gmtime
import frappe
from frappe.model import workflow
from frappe.utils import cstr, add_days, date_diff, getdate,flt
from frappe import _
from frappe.utils.csvutils import UnicodeWriter, read_csv_content
from frappe.utils.file_manager import get_file
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from frappe.utils import get_first_day, get_last_day, format_datetime,get_url_to_form, format_date

class ItemPriceListUploadTool(Document):
    # pass
    def validate(self):
        if not self.upload:
            frappe.throw(_("Please upload a CSV file before submitting."))
        filepath = get_file(self.upload)
        if not filepath or not filepath[1]:
            frappe.throw(_("Could not retrieve file path. Ensure the file is properly uploaded."))
        pps = read_csv_content(filepath[1])
        headers = pps[0]
        item_code_index = headers.index("Item Code")
        currency_index = headers.index("Currency")
        price_columns = {}
        for index in range(item_code_index + 2, len(headers)):
            price_type = headers[index]
            price_columns[price_type] = index
        for pp in pps[1:]:
            
            item_code = pp[item_code_index]
            currency = pp[currency_index]

            if not frappe.db.exists("Item", {"name": item_code}):
                frappe.throw(_("Item Code '{0}' does not exist. Please check the item code in the file.").format(item_code))
            
            for price_type in price_columns.keys():
                if not frappe.db.exists("Price List", {"name": price_type}):
                    frappe.throw(_("Price list '{0}' does not exist. Please check the Price List in the file.").format(price_type))

    @frappe.whitelist()
    def on_submit(self):
        ss = self.name
        file = self.upload
        enqueue(self.enqueue_submit_price, queue='default', timeout=6000, event='enqueue_submit_price',
                ss=ss,file=file)

    @frappe.whitelist()
    def enqueue_submit_price(self, ss, file):
        filepath = get_file(file)
        if not filepath or not filepath[1]:
            frappe.throw(_("Could not retrieve file path. Ensure the file is properly uploaded."))
        pps = read_csv_content(filepath[1])
        headers = pps[0]
        item_code_index = headers.index("Item Code")
        currency_index = headers.index("Currency")
        price_columns = {}
        for index in range(item_code_index + 2, len(headers)):
            price_type = headers[index]
            price_columns[price_type] = index
        for pp in pps[1:]:
            item_code = pp[item_code_index]
            currency = pp[currency_index]

            for price_type, price_index in price_columns.items():
                price = pp[price_index]
                if price:
                    if frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_type, "currency": currency}):
                        frappe.db.set_value("Item Price", {"item_code": str(item_code), "price_list": str(price_type), "currency": str(currency)}, "price_list_rate", flt(price))

                    elif not frappe.db.exists("Item Price", {"item_code": item_code, "price_list": price_type, "currency": currency}):

                        doc = frappe.new_doc("Item Price")
                        doc.price_list = str(price_type)
                        doc.currency = str(currency)
                        doc.item_code = str(item_code)
                        doc.price_list_rate = flt(price)
                        # doc.valid_from="2022-01-01"
                        doc.save(ignore_permissions=True)
        frappe.db.commit()


@frappe.whitelist()
def get_template():
    args = frappe.local.form_dict

    w = UnicodeWriter()
    currencies = get_currency(args)
    # currency_row = [_("Item Code")]+[_("Currency")]+currencies
    currency_row = [_("Item Code")]+[_("Currency")]+[_("Cut Off Price")]+[_("Standard Selling")]+[_("Cost")]
    w.writerow(currency_row)
    frappe.response['result'] = cstr(w.getvalue())
    frappe.response['type'] = 'csv'
    frappe.response['doctype'] = "Item Price List"

@frappe.whitelist()
def add_data(w, args):
    data = get_data(args)
    writedata(w, data)
    return w

@frappe.whitelist()
def get_data(args):
    currency_data = get_currency(args)
    data = []
    for i in currency_data:
        row = [
            i
        ]
        data.append(row)
    return data

@frappe.whitelist()
def writedata(w, data):
    for row in data:
        w.writerow(row)

@frappe.whitelist()
def get_currency(args):
    data = []
    currency_data = frappe.db.get_all("Price List", filters={"currency": args["currency"]}, fields=["*"],order_by="custom_index asc")
    for i in currency_data:
        data.append(i.name)
    return data
