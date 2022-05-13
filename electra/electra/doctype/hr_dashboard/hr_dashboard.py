# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, add_months,today,add_days,nowdate
import datetime

class HRDashboard(Document):
    pass

@frappe.whitelist()
def legal_compliance():
    next_due_month= add_months(today(),2)
    lcm = frappe.db.sql("""select custodian_name,custodian,name,next_due from `tabLegal Compliance Monitor` where next_due between '%s' and '%s' """  %(today(),next_due_month), as_dict=1)
    return lcm

@frappe.whitelist()
def visa_renewal():
    visa_expiry= add_months(today(),2)
    vr = frappe.db.sql("""select visa_application_no,nationality,name,visa_expiry_date from `tabVisa Approval Monitor` where visa_expiry_date between '%s' and '%s' """  %(today(),visa_expiry), as_dict=1)
    return vr

@frappe.whitelist()
def vehicle_renewal(): 
    vehicle_expiry = add_months(today(),2)
    vehicle = frappe.db.sql(""" select name,employee,name,expiry_of_istimara from `tabVehicle` where expiry_of_istimara between '%s' and '%s' """ %(today(),vehicle_expiry), as_dict=1)
    return vehicle

@frappe.whitelist()
def staff_arrival(): 
    arrival = add_months(today(),2)
    staff = frappe.db.sql(""" select employee_name,end from `tabRe Joining From Leave` where end between '%s' and '%s' """ %(today(),arrival), as_dict=1)
    return staff

@frappe.whitelist()
def staff_vaccation(): 
    vacation = add_months(today(),2)
    emp = frappe.db.sql(""" select employee_name,from_date from `tabLeave Application` where end between '%s' and '%s' """ %(today(),vactaion), as_dict=1)
    return emp