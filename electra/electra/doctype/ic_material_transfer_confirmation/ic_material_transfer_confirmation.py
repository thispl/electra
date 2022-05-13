# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe,erpnext
from frappe.model.document import Document
from electra.utils import get_last_valuation_rate
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_mode_of_payment_info

class ICMaterialTransferConfirmation(Document):
    def on_submit(self):
        source_company = frappe.get_value("IC Material Transfer Request",self.ic_material_transfer_request,"source_company")
        mpinfo = get_mode_of_payment_info("Wire Transfer",source_company)
        if len(mpinfo) > 0:
            default_account = mpinfo[0]['default_account']
        if self.workflow_state == 'Transfer Confirmed':
            si = frappe.new_doc("Sales Invoice")
            si.customer = self.target_company
            si.company = source_company
            si.cost_center = erpnext.get_default_cost_center(source_company)
            si.update_stock = 1
            si.is_pos = 1
            si.pos_profile = source_company
            for item in self.items:
                lvr = get_last_valuation_rate(item.item_code)
                si.append("items",{
                    "item_code" : item.item_code,
                    "qty" : item.qty,
                    "rate": lvr['vr'],
                    "price_list_rate": lvr['vr'],
                    "warehouse": item.s_warehouse,
                    "project":item.project,
                    "cost_center": erpnext.get_default_cost_center(source_company),
                })
            si.insert()
            si.append("payments",{
                    "mode_of_payment" : "Wire Transfer",
                    "amount" : si.rounded_total,
                    "account" : default_account
                })
            si.paid_amount = si.rounded_total
            si.submit()

            target_warehouse = frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company': self.target_company }, ["name"])
            icmta = frappe.new_doc("IC Material Transfer Acknowledge")
            icmta.update({
                "requested_date": self.requested_date,
                "raised_by":self.raised_by,
                "project":self.project,
                "sales_order":self.sales_order,
                "target_company": self.target_company,
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
            icmta.flags.ignore_mandatory = True
            icmta.insert()
            icmta.save(ignore_permissions=True)