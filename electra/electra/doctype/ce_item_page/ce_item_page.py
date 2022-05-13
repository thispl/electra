# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

from shutil import ignore_patterns
import frappe
from frappe.model.document import Document

class CEItemPage(Document):
    @frappe.whitelist()
    def copy_ce_items(self):
        ce = frappe.get_doc("Cost Estimation",self.cost_estimation)
        if ce:
            try:
                if self.design:
                     ce.a_design = 1
                for c in self.design:
                    ce.append("design_calculation",{
                        'msow': self.msow,
                        'ssow': self.ssow,
                        'item_group': c.item_group,
                        'item': c.item,
                        'item_name': c.item_name,
                        'description': c.description,
                        'unit': c.unit,
                        'qty': c.qty,
                        'unit_price': c.unit_price,
                        'amount': c.amount
                    })
            except:
                pass
            
            try:
                if self.materials:
                    ce.b_materials = 1
                for c in self.materials:
                    ce.append("materials",{
                        'msow': self.msow,
                        'ssow': self.ssow,
                        'item_group': c.item_group,
                        'item': c.item,
                        'item_name': c.item_name,
                        'description': c.description,
                        'unit': c.unit,
                        'qty': c.qty,
                        'unit_price': c.unit_price,
                        'amount': c.amount
                    })
            except:
                pass
            
            try:
                if self.finishing_work:
                    ce.c_finishing_work = 1
                for c in self.finishing_work:
                    ce.append("finishing_work",{
                        'msow': self.msow,
                        'ssow': self.ssow,
                        'item_group': c.item_group,
                        'item': c.item,
                        'item_name': c.item_name,
                        'description': c.description,
                        'unit': c.unit,
                        'qty': c.qty,
                        'unit_price': c.unit_price,
                        'amount': c.amount
                    })
            except:
                pass
            
            try:
                if self.bolts_accessories:
                    ce.d_accessories = 1
                for c in self.bolts_accessories:
                    ce.append("bolts_accessories",{
                        'msow': self.msow,
                        'ssow': self.ssow,
                        'item_group': c.item_group,
                        'item': c.item,
                        'item_name': c.item_name,
                        'description': c.description,
                        'unit': c.unit,
                        'qty': c.qty,
                        'unit_price': c.unit_price,
                        'amount': c.amount
                    })
            except:
                pass
            
            try:
                if self.installation:
                    ce.e_installationmanpower = 1
                for c in self.installation:
                    ce.append("installation_cost",{
                        'msow': self.msow,
                        'ssow': self.ssow,
                        'item_group': c.item_group,
                        'item': c.item,
                        'item_name': c.item_name,
                        'description': c.description,
                        'unit': c.unit,
                        'qty': c.qty,
                        'unit_price': c.unit_price,
                        'amount': c.amount
                    })
            except:
                pass
            
            try:
                if self.manpower:
                    ce.i_manpower = 1
                for c in self.manpower:
                    ce.append("manpower_cost",{
                        'msow': self.msow,
                        'ssow': self.ssow,
                        'worker': c.worker,
                        'total_workers': c.total_workers,
                        'unit_price': c.unit_price,
                        'working_hours': c.working_hours,
                        'days': c.days,
                        'amount': c.amount
                    })
            except:
                pass
            
            try:
                if self.heavy_equipments:
                    ce.f_tools__equipment__transport = 1
                for c in self.heavy_equipments:
                    ce.append("heavy_equipments",{
                        'msow': self.msow,
                        'ssow': self.ssow,
                        'item_group': c.item_group,
                        'item': c.item,
                        'item_name': c.item_name,
                        'description': c.description,
                        'unit': c.unit,
                        'qty': c.qty,
                        'unit_price': c.unit_price,
                        'amount': c.amount
                    })
            except:
                pass
            
            try:
                if self.others:
                    ce.g_others = 1
                for c in self.others:
                    ce.append("manpower_subcontract",{
                        'msow': self.msow,
                        'ssow': self.ssow,
                        'item_group': c.item_group,
                        'item': c.item,
                        'item_name': c.item_name,
                        'description': c.description,
                        'unit': c.unit,
                        'qty': c.qty,
                        'unit_price': c.unit_price,
                        'amount': c.amount
                    })
            except:
                pass
                ce.save(ignore_permissions=True)
                frappe.db.commit()
                # ce.reload()
            return 'ok'
