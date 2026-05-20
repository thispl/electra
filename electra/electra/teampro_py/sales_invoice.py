import frappe
from frappe import _, bold

def update_return_document_in_sales_invoice_before_rename(doc, method, old_name, new_name, merge=False):
	"""
		Before rename, update the new name to the return document from the return against document
	"""
	if doc.docstatus == 1 and doc.is_return == 1:
		frappe.db.set_value("Sales Invoice", {"name": doc.return_against, "docstatus": ["!=", 2]}, "return_document", new_name)
  
def validate_on_save(doc, method):
	"""
		If there is no active Project Budget, do allow to save the invoice if it is Project
	"""
	
	if doc.order_type == "Project":
		# If no active Project Budget
		if doc.so_no:
			if not frappe.db.exists("Project Budget", {"sales_order": doc.so_no, "docstatus": 1}):
				msg = f"For the Sales Order {bold(doc.so_no)}, there is no active Project Budget"
				frappe.throw(msg, title=_("No Active Project Budget"))
	