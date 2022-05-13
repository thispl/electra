# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StaffSkillMappingForm(Document):
	pass

@frappe.whitelist()
def get_skill_set():
	ss = frappe.get_all("Skill Set",fields=["name"])
	return ss
