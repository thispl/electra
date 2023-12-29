# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

from optparse import Values
import frappe,erpnext
import datetime
from datetime import datetime
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
from frappe.model.document import Document
from electra.utils import get_last_valuation_rate,get_default_letter_head,get_sales_invoice_series
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_mode_of_payment_info

class StockTransfer(Document):
    def validate(self):
        if not self.transferred_by:
            self.transferred_by = frappe.session.user
    
    @frappe.whitelist()
    def before_submit(self):
        self.transferred_by = frappe.session.user
        
    
    @frappe.whitelist()
    def on_submit(self):
        from electra.utils import get_series
        source_company = frappe.get_value("Stock Request",self.ic_material_transfer_request,"source_company")
        sales_person = frappe.get_value("Sales Order",self.sales_order,"sales_person_user")
        mpinfo = get_mode_of_payment_info("Wire Transfer - CBQ-4020",source_company)
        default_account = ''
        if len(mpinfo) > 0:
            default_account = mpinfo[0]['default_account']
            
        if self.workflow_state == 'Transferred':
            self.transferred_date = nowdate()
            si = frappe.new_doc("Sales Invoice")
            si.naming_series = get_sales_invoice_series(source_company,"Sales Invoice")
            si.customer = self.target_company
            si.company = source_company
            si.cost_center = erpnext.get_default_cost_center(source_company)
            si.update_stock = 1
            si.stock_transfer_numner = self.name
            si.sales_person_user = sales_person
            si.stock_transfer = "Stock Transfer"
            # si.is_pos = 1
            # si.pos_profile = source_company
            for item in self.items:
                lvr = get_last_valuation_rate(item.item_code,source_company)
                frappe.errprint(lvr)
                si.append("items",{
                    "item_code" : item.item_code,
                    "income_account" : 'Sales - Stock Transfer - ' + frappe.get_value('Company',self.source_company,'abbr'),
                    "qty" : item.qty,
                    "rate": lvr,
                    "price_list_rate": lvr,
                    "warehouse": item.s_warehouse,
                    "project":item.project,
                    "cost_center": erpnext.get_default_cost_center(source_company),
                })
            si.insert(ignore_permissions=True)
            si.append("payments",{
                    "mode_of_payment" : "Wire Transfer - CBQ-4020",
                    "amount" : si.rounded_total,
                    "account" : default_account
                })
            si.paid_amount = si.rounded_total
            si.letter_head = get_default_letter_head(source_company)
            si.submit()
            self.internal_sales_invoice = si.name

            target_warehouse = frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company': self.target_company }, ["name"])
            icmta = frappe.new_doc("Stock Confirmation")
            from electra.utils import get_series
            
            icmta.update({
                "naming_series": get_series(self.target_company,"Stock Confirmation"),
                "requested_date": self.requested_date,
                "transferred_date" : self.transferred_date,
                "raised_by":self.raised_by,
                "transferred_by":self.transferred_by,
                "project":self.project,
                "sales_order":self.sales_order,
                "target_company": self.target_company,
                "source_company":self.source_company,
                "from__company":self.source_company,
                "ic_material_transfer_request":self.ic_material_transfer_request,
                "ic_material_transfer_confirmation":self.name
            })
            for item in self.items:
                icmta.append("items",{
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "qty": item.qty,
                    "uom": item.uom,
                    "project": item.project,
                    "description": item.description,
                    "item_group": item.item_group,
                    "s_warehouse": item.s_warehouse,
                    "t_warehouse": target_warehouse,

                })
            icmta.flags.ignore_permissions = True
            icmta.flags.ignore_mandatory = True
            icmta.insert()

def on_cancel(self):
    if self.internal_sales_invoice:
        si = frappe.get_doc('Sales Invoice',self.internal_sales_invoice)
        si.cancel()
        frappe.db.commit()

def cancel_stock_request():
    transfer_request = frappe.db.get_all('Stock Transfer',{'workflow_state':'Rejected'},['ic_material_transfer_request'])
    for t in transfer_request:
        sr=t.values()
    for stock_req in sr:
        frappe.db.set_value('Stock Request',stock_req,'workflow_state','Cancelled')
        print(stock_req)

# @frappe.whitelist()
# def temp_sc(id):
#         from electra.utils import get_series
#         doc = frappe.get_doc('Stock Transfer',id)
#         source_company = frappe.get_value("Stock Request",self.ic_material_transfer_request,"source_company")
#         sales_person = frappe.get_value("Sales Order",self.sales_order,"sales_person_user")
#         # frappe.errprint(source_company)
#         mpinfo = get_mode_of_payment_info("Wire Transfer - CBQ-4020",source_company)
#         # frappe.errprint(mpinfo)
#         if len(mpinfo) > 0:
#             default_account = mpinfo[0]['default_account']
#         if self.workflow_state == 'Transferred':
#             self.transferred_date = nowdate()
#             si = frappe.new_doc("Sales Invoice")
#             si.naming_series = get_series(source_company,"Sales Invoice")
#             si.customer = self.target_company
#             si.company = source_company
#             si.cost_center = erpnext.get_default_cost_center(source_company)
#             si.update_stock = 1
#             si.stock_transfer = "Stock Transfer"
#             si.sales_person_user = sales_person
#             si.stock_transfer_numner = self.name
#             # si.is_pos = 1
#             # si.pos_profile = source_company
#             for item in self.items:
#                 lvr = get_last_valuation_rate(item.item_code,source_company)
#                 si.append("items",{
#                     "item_code" : item.item_code,
#                     "qty" : item.qty,
#                     "rate": lvr,
#                     "price_list_rate": lvr,
#                     "warehouse": item.s_warehouse,
#                     "project":item.project,
#                     "cost_center": erpnext.get_default_cost_center(source_company),
#                 })
#             si.insert(ignore_permissions=True)
#             si.append("payments",{
#                     "mode_of_payment" : "Wire Transfer - CBQ-4020",
#                     "amount" : si.rounded_total,
#                     "account" : default_account
#                 })
#             si.paid_amount = si.rounded_total
#             si.letter_head = get_default_letter_head(source_company)
#             si.submit()
#             self.internal_sales_invoice = si.name

#             target_warehouse = frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company': self.target_company }, ["name"])
#             icmta = frappe.new_doc("Stock Confirmation")
#             from electra.utils import get_series
            
#             icmta.update({
#                 "naming_series": get_series(self.target_company,"Stock Confirmation"),
#                 "requested_date": self.requested_date,
#                 "transferred_date" : self.transferred_date,
#                 "raised_by":self.raised_by,
#                 "transferred_by":self.transferred_by,
#                 "project":self.project,
#                 "sales_order":self.sales_order,
#                 "target_company": self.target_company,
#                 "source_company":self.source_company,
#                 "ic_material_transfer_request":self.ic_material_transfer_request,
#                 "ic_material_transfer_confirmation":self.name
#             })
#             for item in self.items:
#                 icmta.append("items",{
#                     "item_code": item.item_code,
#                     "item_name": item.item_name,
#                     "qty": item.qty,
#                     "uom": item.uom,
#                     "project": item.project,
#                     "description": item.description,
#                     "item_group": item.item_group,
#                     "s_warehouse": item.s_warehouse,
#                     "t_warehouse": target_warehouse,

#                 })
#             icmta.flags.ignore_permissions = True
#             icmta.flags.ignore_mandatory = True
#             icmta.insert()


