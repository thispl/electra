# Copyright (c) 2024, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data

def get_columns(filters):
    columns = [
        _("Plant") + ":Data/:100",
        _("Equipment") + ":Data/:200",
        _("Make") + ":Data/:100",
        _("Total (nos)") + ":Int/:100",
        _("Working (nos)") + ":Int/:100",
        _("Repire Required (nos)") + ":Int/:100",
        _("Idle (nos)") + ":Int/:100",
        _("Subair Tool Box (nos)") + ":Int/:100",
        _("Status") + ":Data/:200",
    ]
    return columns

def get_data(filters):    
    data = []
    filter_conditions = {}

    if filters.get("equipment"):
        filter_conditions["equipment"] = filters.get("equipment")
    
    if filters.get("make"):
        filter_conditions["make"] = filters.get("make")
	
    if filters.get("plant"):
        filter_conditions["plant"] = filters.get("plant")
	
    if filters.get("status"):
        filter_conditions["status"] = filters.get("status")
        
    plants = frappe.db.get_all("Plant and Equipment", filters=filter_conditions, fields=["name", "plant", "equipment", "make", "total", "working", "repire_required", "idle", "subair_tool_box", "status"])

    for plant in plants:
        row = [
            plant.plant,
            plant.equipment,
            plant.make,
            plant.total,
            plant.working,
            plant.repair_required,
            plant.idle,
            plant.subair_tool_box,
            plant.status,
        ]
        data.append(row)
    
    return data
