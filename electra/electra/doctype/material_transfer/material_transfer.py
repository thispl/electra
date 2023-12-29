# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MaterialTransfer(Document):
    def on_submit(self):
        doc = frappe.new_doc("Stock Entry")
        doc.stock_entry_type = "Material Transfer"
        doc.company = self.company
        doc.posting_date = self.requested_date
        doc.to_warehouse = self.to_warehouse
        doc.from_warehouse = self.source_company
        doc.material_transfer = self.name
        for item in self.items:
            doc.append("items",{
                's_warehouse': self.source_company,
                't_warehouse': self.to_warehouse,
                'item_code' : item.item_code,
                'qty' : item.qty,
                'uom' : item.uom,
            })
        doc.save(ignore_permissions=True)
        doc.submit()
        
    
    
