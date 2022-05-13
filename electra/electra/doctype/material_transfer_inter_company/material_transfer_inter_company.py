# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import json
import frappe,erpnext
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.utils import get_fetch_values



class MaterialTransferInterCompany(Document):
    def on_update(self):
        if self.workflow_state == 'Transfer Approved':
            si = frappe.new_doc("Sales Invoice")
            si.customer = self.target_company
            si.company = self.source_company
            si.cost_center = erpnext.get_default_cost_center(self.source_company)
            si.update_stock = 1
            for item in self.items:
                si.append("items",{
                    "item_code" : item.item_code,
                    "qty" : item.qty,
                    "rate": 0.0,
                    "price_list_rate":0.0,
                    "warehouse": item.s_warehouse,
                    "project":item.project,
                    "cost_center": erpnext.get_default_cost_center(self.source_company)

                })
            si.save(ignore_permissions=True)
            si.submit()

        if self.workflow_state == 'Material Recieved':
            ste = frappe.new_doc("Stock Entry")
            ste.stock_entry_type = "Material Receipt"
            ste.company = self.target_company
            ste.material_transfer = self.name
            for item in self.items:
                ste.append("items",{
                    "item_code" : item.item_code,
                    "qty" : item.qty,
                    "t_warehouse": item.t_warehouse,
                    "cost_center": frappe.db.get_value('Company', self.target_company, 'cost_center'),
                    "project":item.project
                })
            ste.save(ignore_permissions=True)
            ste.submit()

@frappe.whitelist()
def get_item_availability(item_code,source_warehouse):
    data = []
    item_name = frappe.get_value('Item',{'name':item_code},"item_name")
    query = """select actual_qty,warehouse,stock_uom,stock_value from tabBin
        where item_code = '%s' and warehouse = '%s' """ % (item_code,source_warehouse)
    
    stock = frappe.db.sql(query,as_dict=True)
    if stock:
        return stock[0]
    else:
        return 0

@frappe.whitelist()
def get_material_transfer_warehouse(company):
    warehouses = frappe.get_list("Warehouse",{'company':company,'default_for_stock_transfer':1},['name'],ignore_permissions=True)
    wh_list = []
    for wh in warehouses:
        wh_list.append(wh['name'])
    return wh_list[0]
