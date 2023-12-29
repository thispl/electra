# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe,erpnext
from frappe.model.document import Document
from frappe.utils import today, random_string
from frappe.utils import nowdate, get_last_day, getdate, add_days, add_years

class StockRequest(Document):
    def validate(self):
        self.transfer_incharge_user = frappe.get_value('Company',self.source_company,'sales_coordinator')

    def on_update(self):
        from electra.utils import get_series
        if self.workflow_state == 'Transfer Requested':
            target_warehouse = frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company':self.company}, ["name"])
            icmtc = frappe.new_doc("Stock Transfer")
            icmtc.update({
                "naming_series":get_series(self.source_company,"Stock Transfer"),
                "requested_date": self.requested_date,
                "transferred_date":nowdate(),
                "raised_by":self.raised_by,
                "project":self.project,
                "sales_order":self.sales_order,
                "target_company": self.company,
                "to__company":self.company,
                "source_company":self.source_company,
                "ic_material_transfer_request":self.name
            })
            for item in self.items:
                icmtc.append("items",{
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "qty": item.qty,
                    "uom": item.uom,
                    "project": item.project,
                    "description": item.description,
                    "item_group": item.item_group,
                    "s_warehouse": item.s_warehouse,
                    "t_warehouse": target_warehouse

                })
            icmtc.flags.ignore_permissions = True
            icmtc.flags.ignore_mandatory = True
            icmtc.flags.ignore_validate = True
            icmtc.flags.ignore_links = True
            icmtc.insert()
            # icmtc.save(ignore_permissions=True)

            
    def on_cancel(self):
        if frappe.db.exists("Stock Transfer",{"ic_material_transfer_request":self.name}):
            si = frappe.get_doc('Stock Transfer',{"ic_material_transfer_request":self.name})
            si.delete(ignore_permissions=True)
