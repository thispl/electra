# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class Trip(Document):
    pass
#    def after_insert(self):
#        frappe.errprint("hi")
#        if self.destination:
#             self.from_location = self.destination[0].location_place
#             self.to_location = self.destination[-1].location_place