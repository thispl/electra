# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CESOW(Document):
    @frappe.whitelist()
    def copy_ce_items(self):
        total_cost = 0
        ce = frappe.get_doc("Cost Estimation",self.cost_estimation)
        if ce:
            try:
                if self.design:
                    ce.a_design = 1
                    ce.design_calculation = []
                    total_design_cost = 0
                    for c in self.design:
                        total_design_cost += c.amount
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
                    ce.total_design_calculation = total_design_cost
            except:
                pass
            
            try:
                if self.materials:
                    ce.b_materials = 1
                    ce.materials = []
                    total_materials_cost = 0
                    for c in self.materials:
                        total_materials_cost += c.amount
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
                    ce.total_material_calculation = total_materials_cost
            except:
                pass
            
            try:
                if self.finishing_work:
                    ce.c_finishing_work = 1
                    ce.finishing_work = []
                    total_finishing_work_cost = 0
                    for c in self.finishing_work:
                        total_finishing_work_cost += c.amount
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
                    ce.total_finishing_work_calculation = total_finishing_work_cost
            except:
                pass
            
            try:
                if self.bolts_accessories:
                    ce.d_accessories = 1
                    ce.bolts_accessories = []
                    total_bolts_accessories_cost = 0
                    for c in self.bolts_accessories:
                        total_bolts_accessories_cost += c.amount
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
                    ce.total_bolts_accessories_calculation = total_bolts_accessories_cost
            except:
                pass
            
            try:
                if self.installation:
                    ce.e_installationmanpower = 1
                    ce.installation_cost = []
                    total_installation_cost = 0
                    for c in self.installation:
                        total_installation_cost += c.amount
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
                    ce.total_installation_cost = total_installation_cost
            except:
                pass
            
            try:
                if self.manpower:
                    ce.i_manpower = 1
                    ce.manpower_cost = []
                    total_manpower_cost = 0
                    for c in self.manpower:
                        total_manpower_cost += c.amount
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
                    ce.total_manpower_cost = total_manpower_cost
            except:
                pass
            
            try:
                if self.heavy_equipments:
                    ce.f_tools__equipment__transport = 1
                    ce.heavy_equipments = []
                    total_heavy_equipments_cost = 0
                    for c in self.heavy_equipments:
                        total_heavy_equipments_cost += c.amount
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
                    ce.total_heavy_equipments_calculation = total_heavy_equipments_cost
            except:
                pass
            
            try:
                if self.others:
                    ce.g_others = 1
                    ce.manpower_subcontract = []
                    total_others_cost = 0
                    for c in self.others:
                        total_others_cost += c.amount
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
                    ce.total_manpower_subcontract_calculation = total_others_cost
            except:
                pass
            ce.save(ignore_permissions=True)
            frappe.db.commit()
                # ce.reload()
            return 'ok'

