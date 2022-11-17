# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class DayPlan(Document):
    def validate(self):
        if self.employee_multiselect:
            if self.day_schedule:
                worker_count = 0
                staff_count= 0
                supervisor_count = 0
                for i in self.employee_multiselect:
                    frappe.errprint(i.employee)
                    emp = frappe.get_value("Employee",{'name':i.employee},['grade'])
                    if emp == "WORKER":
                        worker_count = worker_count + 1
                    if emp == "STAFF":
                        staff_count = staff_count + 1
                    if emp == "SUPERVISOR": 
                        supervisor_count = supervisor_count + 1
                if self.staff == staff_count and self.supervisor == supervisor_count  and self.worker == worker_count:
                    pass
                else:
                    frappe.throw("Employee Count not matched against day schedule")
        else:
            frappe.throw("Atleast one Employee should be selected")


        # if not self.employee_table and not self.employee_multiselect:
        #     frappe.throw("Employee Allocation is Mandatory")

        employees_table = self.employee_table    
        if employees_table:
            # frappe.errprint(employees_table)

            for employee in employees_table:
                frappe.errprint(employee)

                dpe = frappe.db.exists('Day Plan Employee',{'planned_date':self.planned_date,'employee':employee.employee,'parent':('!=',self.name)})
                frappe.errprint(dpe)
                if dpe:
                    frappe.throw("A Day Plan is Already Assigned for the  Employee : %s : %s" %(employee.employee,employee.employee_name))
        
        employee_multiselect = self.employee_multiselect
        if employee_multiselect:
            for employee in employee_multiselect:
                dpe = frappe.db.exists('Day Plan Employee',{'planned_date':self.planned_date,'employee':employee.employee,'parent':('!=',self.name)})
                if dpe:
                    frappe.throw("A Day Plan is Already Assigned for the  Employee : %s : %s" %(employee.employee,employee.employee_name))



@frappe.whitelist()
def make_day_plan(source_name, target_doc=None):
    # doc = frappe.get_("Cost Estimation",source_name)
    doclist = get_mapped_doc("Day Plan", source_name, {
        "Day Plan": {
            "doctype": "Day Plan Timesheet",
            "field_map": {
                "name": "day_plan",
                "project":"project",
                "planned_date":"worked_date"
            }
        },
        "Day Plan Employee": {
            "doctype": "Day Plan Time Log",
            "field_map": {
                "employee": "employee",
                "from_time" : "from_time",
                "to_time" : "to_time"
            }
        }
    }, target_doc)
    return doclist
