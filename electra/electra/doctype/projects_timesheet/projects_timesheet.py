# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt,time_diff_in_hours,to_timedelta
import datetime

class ProjectsTimesheet(Document):
    def on_submit(self):
        # update task qty
        for tl in self.project_day_plan_employee:
            if tl.activity:
                task_id = frappe.get_doc("Task",tl.activity)
                if task_id.qty > 0:
                    task_id.pending_qty -= tl.qty
                    task_id.completed_qty += tl.qty
                    task_id.save(ignore_permissions=True)
                    frappe.db.commit()
            
        
        #create timesheet
        self.start_time = frappe.get_value("Day Plan",self.day_plan,"from_time")
        if self.start_time:
            start_time = self.start_time
        else:
            plan_date = datetime.datetime.strptime(str(self.plan_date),"%Y-%m-%d").date()
            start_time = datetime.datetime.combine(plan_date, datetime.time(hour=5))
        
        for tlog in self.project_day_plan_employee:
            query = """
                select * from `tabTimesheet` ts where '%s' between ts.start_date and ts.end_date and employee = '%s'
                            """ % (self.plan_date,tlog.employee)
            timesheet_id = frappe.db.sql(query,as_dict=True)
            
            if not timesheet_id:
                ts = frappe.new_doc('Timesheet')
                ts.project = tlog.project
                ts.employee = tlog.employee
                ot = ot_hours = total_working_hours = 0
                total_working_hours = time_diff_in_hours(tlog.to_time,tlog.from_time)
                if tlog.ot:
                    ot = to_timedelta(tlog.ot).total_seconds()
                    ot_hours = ot / 3600
                end_time = start_time + datetime.timedelta(hours=total_working_hours)
                basic = frappe.db.get_value('Employee',{'name':ts.employee},'basic')
                leave = frappe.db.get_value('Employee',{'name':ts.employee},'holiday_list')
                holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
                left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(leave,self.plan_date),as_dict=True)
                if holiday:
                    amt_1 = flt(((basic/26)/8)*1.50)
                    if total_working_hours and total_working_hours > 0:
                        
                        ts.append("time_logs", {
                        "activity_type" : "Regular Work",
                        "project":tlog.project,
                        "task": tlog.activity,
                        "from_time" : start_time,
                        "to_time" : end_time,
                        "hours": total_working_hours,
                        "is_billable" : 1,
                        "costing_rate": amt_1,
                        
                    })
                    if ot_hours and ot_hours > 0:
                        overtime = end_time + datetime.timedelta(hours=ot_hours)
                        ts.append("time_logs", {
                        "activity_type" : "Overtime",
                        "project":tlog.project,
                        "task": tlog.activity,
                        "from_time" : end_time,
                        "to_time" : overtime,
                        "hours": ot_hours,
                        "is_billable" : 1,
                        "costing_rate": amt_1,
                        
                    })
                else:
                    amt_2 = flt(((basic/26)/8)*1.25)
                    if total_working_hours and total_working_hours > 0:
                        ts.append("time_logs", {
                            "activity_type" : "Regular Work",
                            "project":tlog.project,
                            "task": tlog.activity,
                            "from_time" : start_time,
                            "to_time" : end_time,
                            "hours": total_working_hours,
                            "is_billable" : 1,
                            "costing_rate": flt((basic/26)/8),
                            
                        })
                    if ot_hours and ot_hours > 0:
                        overtime = end_time + datetime.timedelta(hours=ot_hours)
                        ts.append("time_logs", {
                        "activity_type" : "Overtime",
                        "project":tlog.project,
                        "task": tlog.activity,
                        "from_time" : end_time,
                        "to_time" : overtime,
                        "hours": ot_hours,
                        "is_billable" : 1,
                        "costing_rate":amt_2,
                        
                    })
                ts.save(ignore_permissions=True)
               
                # leave = frappe.db.get_value('Employee',{'name':ts.employee},'holiday_list')
                # holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
                # left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(leave,self.plan_date),as_dict=True)
                # if holiday:
                #     ts.total_billable_amount = flt(((basic/26)/8) * 1.50)
                # else:
                #     ts.total_billable_amount = flt(((basic/26)/8) * 1.25)
                # ts.save(ignore_permissions=True)
                ts.submit()
            else:
                frappe.throw("Timesheets has been already created for this Employee for the same period")
