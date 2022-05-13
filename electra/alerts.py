import frappe
from frappe.utils import nowdate
from datetime import date

@frappe.whitelist()
def update_lcm_due_status():
    lcm = frappe.get_all("Legal Compliance Monitor",fields=['name','possibility_status','next_due'])
    for lc in lcm:
        if lc['possibility_status'] == 'Renewable':
            next_renewal_date = lc['next_due']
            days_left = (next_renewal_date - date.today()).days
            frappe.set_value('Legal Compliance Monitor',lc['name'],"days_left",days_left)
            if days_left <= 30:
                status = "Due for Renewal"
            else:
                status = "Valid"
            frappe.set_value('Legal Compliance Monitor',lc['name'],"status",status)
