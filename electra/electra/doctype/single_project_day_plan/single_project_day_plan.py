# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class SingleProjectDayPlan(Document):
    # pass
    def validate(self):
        #  if self.employee_multiselect or self.employee_table:
        #     if self.day_schedule:
        #         worker_count = 0
        #         staff_count= 0
        #         supervisor_count = 0
        #         for i in self.employee_multiselect:
        #             frappe.errprint(i.employee)
        #             grade = frappe.get_value("Employee",{'name':i.employee},['grade'])
        #             if grade == "WORKER":
        #                 worker_count = worker_count + 1
        #             if grade == "STAFF":
        #                 staff_count = staff_count + 1
        #             if grade == "SUPERVISOR": 
        #                 supervisor_count = supervisor_count + 1
        #         if self.staff == staff_count and self.supervisor == supervisor_count and self.worker == worker_count:
        #             pass
        #         else:
        #             frappe.throw("Employee Count not matched against day schedule")
        # else:
        #     frappe.throw("Atleast one Employee should be selected")
        if self.worker_multiselect or self.employee_table:
            if self.day_schedule:
                if self.worker == len(self.worker_multiselect):
                    pass
                else:
                    frappe.throw("Worker Count not matched against day schedule")
                # worker_count = 0
                # for i in self.worker_multiselect:
                #     grade = frappe.get_value("NON STAFF",{'name':i.non_staff},['name'])
                #     # if grade == "WORKER":
                #     worker_count = worker_count + 1
                # if self.worker == worker_count:
                #     pass
                # else:
                #     frappe.throw("Employee Count not matched against day schedule")
 
        if self.staff_multiselect or self.employee_table:
            if self.day_schedule:
                if self.staff == len(self.staff_multiselect):
                    pass
                else:
                    frappe.throw("Staff Count not matched against day schedule")
                # staff_count = 0
                # for i in self.staff_multiselect:
                #     grade = frappe.get_value("STAFF",{'name':i.staff},['name'])
                #     # if grade == "WORKER":
                #     staff_count = staff_count + 1
                # if self.staff == staff_count:
                #     pass
                # else:
                #     frappe.throw("Employee Count not matched against day schedule")
        

        if self.supervisor_multiselect or self.employee_table:
            if self.day_schedule:
                if self.supervisor == len(self.supervisor_multiselect):
                    pass
                else:
                    frappe.throw("Supervisor Count not matched against day schedule")
                # supervisor_count = 0
                # for i in self.supervisor_multiselect:
                #     grade = frappe.get_value("SUPERVISOR",{'name':i.supervisor},['name'])
                #     # if grade == "WORKER":
                #     supervisor_count = supervisor_count + 1
                # if self.supervisor == supervisor_count:
                #     pass
                # else:
                #     frappe.throw("Employee Count not matched against day schedule")
        # else:
        #     frappe.throw("Atleast one Employee should be selected")


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
        
        # employee_multiselect = self.employee_multiselect
        # if employee_multiselect:
        #     for employee in employee_multiselect:
        #         dpe = frappe.db.exists('Day Plan Employee',{'planned_date':self.planned_date,'employee':employee.employee,'parent':('!=',self.name)})
        #         if dpe:
        #             frappe.throw("A Day Plan is Already Assigned for the  Employee : %s : %s" %(employee.employee,employee.employee_name))



@frappe.whitelist()
def make_single_project_day_plan(source_name, target_doc=None):
    # doc = frappe.get_("Cost Estimation",source_name)
    doclist = get_mapped_doc("Day Plan", source_name, {
        "Day Plan": {
            "doctype": "Day Plan Timesheet",
            "field_map": {
                "name": "single_project_day_plan",
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
