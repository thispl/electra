# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe,erpnext
from frappe.model.document import Document
from electra.utils import get_last_valuation_rate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_mode_of_payment_info


class StockConfirmation(Document):
    def validate(self):
        if not self.confirmed_by:
            self.confirmed_by = frappe.session.user

    def on_submit(self):
        source_company = frappe.get_value("Stock Request",self.ic_material_transfer_request,"source_company")
        mpinfo = get_mode_of_payment_info("Wire Transfer",self.target_company)
        if len(mpinfo) > 0:
            default_account = mpinfo[0]['default_account']
        if self.workflow_state == 'Material Recieved':
            pi = frappe.new_doc("Purchase Invoice")
            pi.supplier = source_company
            pi.company = self.target_company
            pi.cost_center = erpnext.get_default_cost_center(self.target_company)
            pi.update_stock = 1
            pi.is_paid = 1
            pi.mode_of_payment = "Wire Transfer"
            pi.paid_amount = pi.rounded_total
            pi.cash_bank_account = default_account
            for item in self.items:
                lvr = get_last_valuation_rate(item.item_code)
                pi.append("items",{
                    "item_code" : item.item_code,
                    "qty" : item.qty,
                    "rate": lvr['vr'],
                    "price_list_rate":lvr['vr'],
                    "warehouse": item.t_warehouse,
                    "expense_account": frappe.get_cached_value('Company',  self.target_company, 'default_inventory_account'),
                    "project":item.project,
                    "cost_center": erpnext.get_default_cost_center(self.target_company)

                })
            pi.save(ignore_permissions=True)
            pi.submit()