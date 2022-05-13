# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe,erpnext
from frappe.model.document import Document

class ICMaterialTransferRequest(Document):
    def on_update(self):
        if self.workflow_state == 'Transfer Requested':
            target_warehouse = frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company':self.company}, ["name"])
            icmtc = frappe.new_doc("IC Material Transfer Confirmation")
            icmtc.update({
                "requested_date": self.requested_date,
                "raised_by":self.raised_by,
                "project":self.project,
                "sales_order":self.sales_order,
                "target_company": self.company,
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
                    "t_warehouse": target_warehouse,

                })
            icmtc.flags.ignore_mandatory = True
            icmtc.insert()
            icmtc.save(ignore_permissions=True)
        

