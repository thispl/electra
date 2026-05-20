# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe,erpnext
from frappe.model.document import Document
import datetime
from datetime import datetime
from frappe.utils import date_diff, add_months,today,add_days,add_years,nowdate,flt
from electra.utils import get_last_valuation_rate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_mode_of_payment_info


class StockConfirmation(Document):
    def validate(self):
        if not self.confirmed_by:
            self.confirmed_by = frappe.session.user

    def before_submit(self):
        if self.workflow_state == 'Material Recieved':
            if not self.confirmed_date:
                
                self.confirmed_date = nowdate()

    
    def on_submit(self):
        from electra.utils import get_series
        source_company = frappe.get_value("Stock Request",self.ic_material_transfer_request,"source_company")
        mpinfo = get_mode_of_payment_info("Bank Transfer - CBQ-4020",self.target_company)

        default_account = ''
        if len(mpinfo) > 0:
            default_account = mpinfo[0]['default_account']
        if self.workflow_state == 'Material Recieved':
            pi = frappe.new_doc("Purchase Invoice")
            pi.stock_confirmation = "Stock Confirmation"
            pi.custom_stock_confirmation_date = self.confirmed_date
            pi.supplier = source_company
            naming_series = get_series(self.target_company,"Purchase Invoice")
            nam = naming_series.split('-')
            pi.naming_series = nam[0]+'-'+nam[1]+'-'+'STC-'+nam[2]+'-'
            pi.company = self.target_company
            pi.cost_center = erpnext.get_default_cost_center(self.target_company)
            pi.update_stock = 1
            pi.confirmation_number = self.name
            # pi.is_paid = 1
            pi.mode_of_payment = "Bank Transfer - CBQ-4020"
            pi.paid_amount = pi.rounded_total
            pi.cash_bank_account = default_account
            if self.project:
                warehouse =frappe.db.sql("""select name from `tabWarehouse` where warehouse_name like %s""",(f"%{self.project}%",),as_dict=True)
                self.project_warehouse = warehouse[0].name
                for item in self.items:
                    if item.rate:
                        lvr = item.rate
                    else:
                        lvr = get_last_valuation_rate(item.item_code,source_company)
                    pi.append("items",{
                        "item_code" : item.item_code,
                        "qty" : item.qty,
                        "rate": lvr,
                        "price_list_rate":lvr,
                        "warehouse": warehouse[0].name,
                        "expense_account": frappe.get_cached_value('Company',  self.target_company, 'default_inventory_account'),
                        "project":item.project,
                        "cost_center": erpnext.get_default_cost_center(self.target_company)

                    })
            else:
                for item in self.items:
                    if item.rate:
                        lvr = item.rate
                    else:
                        lvr = get_last_valuation_rate(item.item_code,source_company)
                    pi.append("items",{
                        "item_code" : item.item_code,
                        "qty" : item.qty,
                        "rate": lvr,
                        "price_list_rate":lvr,
                        "warehouse": item.t_warehouse,
                        "expense_account": frappe.get_cached_value('Company',  self.target_company, 'default_inventory_account'),
                        "project":item.project,
                        "cost_center": erpnext.get_default_cost_center(self.target_company)

                    })
            pi.save(ignore_permissions=True)
            pi.submit()
            # self.internal_purchase_invoice = pi.name
            self.save(ignore_permissions=True)
            frappe.db.commit()

def on_cancel(self):
    if self.internal_purchase_invoice:
        pi = frappe.get_doc('Purchase Invoice',self.internal_purchase_invoice)
        pi.cancel()
        frappe.db.commit()
    
def update_purchase_invoice_date(doc, method):
    """
    This function is used to update the posting date of the purchase invoice 
    created from stock confirmation to the confirmed date of the stock confirmation.
    """
    if doc.custom_stock_confirmation_date:
        doc.posting_date = doc.custom_stock_confirmation_date
        
def test_check():
    stock_confirmations = frappe.db.get_all("Stock Confirmation", filters={"workflow_state": "Material Recieved", "creation": [">=", "2026-04-01"]}, fields=["name", "confirmed_date"])
    print(len(stock_confirmations))
    for sc in stock_confirmations:
        pi = frappe.db.get_value("Purchase Invoice", {"confirmation_number": sc.name}, ["name", "posting_date"], as_dict=True)
        if pi and pi.posting_date != sc.confirmed_date:
            print(f"Stock Confirmation: {sc.name}, Confirmed Date: {sc.confirmed_date}, Purchase Invoice: {pi.name}, Posting Date: {pi.posting_date}")

@frappe.whitelist()     
def create_purchase_invoice(stock_confirmation, confirmed_date):
    if frappe.db.exists("Purchase Invoice", {"confirmation_number": stock_confirmation, "posting_date": confirmed_date}):
        frappe.throw("Purchase Invoice for this Stock Confirmation and Date already exists")
        
    from electra.utils import get_series
    
    self = frappe.get_doc("Stock Confirmation", stock_confirmation)
    source_company = frappe.get_value("Stock Request",self.ic_material_transfer_request,"source_company")
    mpinfo = get_mode_of_payment_info("Bank Transfer - CBQ-4020",self.target_company)

    default_account = ''
    if len(mpinfo) > 0:
        default_account = mpinfo[0]['default_account']
    if self.workflow_state == 'Material Recieved':
        pi = frappe.new_doc("Purchase Invoice")
        pi.stock_confirmation = "Stock Confirmation"
        pi.custom_stock_confirmation_date = self.confirmed_date
        pi.supplier = source_company
        naming_series = get_series(self.target_company,"Purchase Invoice")
        nam = naming_series.split('-')
        pi.naming_series = nam[0]+'-'+nam[1]+'-'+'STC-'+nam[2]+'-'
        pi.company = self.target_company
        pi.cost_center = erpnext.get_default_cost_center(self.target_company)
        pi.update_stock = 1
        pi.confirmation_number = self.name
        # pi.is_paid = 1
        pi.mode_of_payment = "Bank Transfer - CBQ-4020"
        pi.paid_amount = pi.rounded_total
        pi.cash_bank_account = default_account
        if self.project:
            warehouse =frappe.db.sql("""select name from `tabWarehouse` where warehouse_name like %s""",(f"%{self.project}%",),as_dict=True)
            self.project_warehouse = warehouse[0].name
            for item in self.items:
                if item.rate:
                    lvr = item.rate
                else:
                    lvr = get_last_valuation_rate(item.item_code,source_company)
                pi.append("items",{
                    "item_code" : item.item_code,
                    "qty" : item.qty,
                    "rate": lvr,
                    "price_list_rate":lvr,
                    "warehouse": warehouse[0].name,
                    "expense_account": frappe.get_cached_value('Company',  self.target_company, 'default_inventory_account'),
                    "project":item.project,
                    "cost_center": erpnext.get_default_cost_center(self.target_company)

                })
        else:
            for item in self.items:
                if item.rate:
                    lvr = item.rate
                else:
                    lvr = get_last_valuation_rate(item.item_code,source_company)
                pi.append("items",{
                    "item_code" : item.item_code,
                    "qty" : item.qty,
                    "rate": lvr,
                    "price_list_rate":lvr,
                    "warehouse": item.t_warehouse,
                    "expense_account": frappe.get_cached_value('Company',  self.target_company, 'default_inventory_account'),
                    "project":item.project,
                    "cost_center": erpnext.get_default_cost_center(self.target_company)

                })
        pi.save(ignore_permissions=True)
        pi.submit()
        # self.internal_purchase_invoice = pi.name
        self.save(ignore_permissions=True)
        frappe.db.commit()