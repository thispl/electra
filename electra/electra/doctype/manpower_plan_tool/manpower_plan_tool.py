# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ManpowerplanTool(Document):
    @frappe.whitelist()
    def create_manpower_plan(self):
        counts = [self.month_1,self.month_2,self.month_3,self.month_4,self.month_5,self.month_6]
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        idx = months.index(self.month)
        for c in counts:
            idx += 1
            doc = frappe.new_doc('Manpower planning')
            doc.department = self.department
            doc.date = self.date
            doc.year = self.year
            doc.month = months[idx]
            doc.manpower_required = c
            doc.designation = self.designation
            doc.available_manpower = self.available_manpower
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            if idx == 11:
                idx = -1

@frappe.whitelist()
def designation_filter(designation):
    count=frappe.db.count('Employee',{'designation':designation})
    return count