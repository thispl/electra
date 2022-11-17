# Copyright (c) 2021, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
import datetime


class DayPlanTimesheet(Document):
    def validate(self):
        for tl in self.time_log:
            task_id = frappe.get_doc("Task",tl.activity)
            if task_id.qty > 0:
                task_id.pending_qty -= tl.qty
                task_id.completed_qty += tl.qty
                task_id.save(ignore_permissions=True)
                frappe.db.commit()
            
    #     self.start_time = frappe.get_value("Day Plan",self.day_plan,"from_time")

    def on_submit(self):
        # update task qty
        
        #create timesheet
        self.start_time = frappe.get_value("Day Plan",self.day_plan,"from_time")
        if self.start_time:
            start_time = self.start_time
        else:
            worked_date = datetime.datetime.strptime(str(self.worked_date),"%Y-%m-%d").date()
            start_time = datetime.datetime.combine(worked_date, datetime.time(hour=5))
        
        for tlog in self.time_log:
            query = """
                select * from `tabTimesheet` ts where '%s' between ts.start_date and ts.end_date and employee = '%s'
                            """ % (self.worked_date,tlog.employee)
            timesheet_id = frappe.db.sql(query,as_dict=True)
            
            if not timesheet_id:
                ts = frappe.new_doc('Timesheet')
                ts.customer = self.customer
                ts.project = self.project
                ts.employee = tlog.employee
                end_time = start_time + datetime.timedelta(hours=tlog.work_hours)
                basic = frappe.db.get_value('Employee',{'name':ts.employee},'basic')
                leave = frappe.db.get_value('Employee',{'name':ts.employee},'holiday_list')
                holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
                left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(leave,self.worked_date),as_dict=True)
                if holiday:
                    amt_1 = flt(((basic/26)/8)*1.50)
                    if tlog.overtime and tlog.overtime > 0:
                        overtime = end_time + datetime.timedelta(hours=tlog.overtime)
                        ts.append("time_logs", {
                        "activity_type" : "Overtime",
                        "task": tlog.activity,
                        "from_time" : end_time,
                        "to_time" : overtime,
                        "hours": tlog.overtime,
                        "is_billable" : 1,
                        "billing_rate": amt_1,
                        
                    })
                else:
                    amt_2 = flt(((basic/26)/8)*1.25)
                    if tlog.overtime and tlog.overtime > 0:
                        overtime = end_time + datetime.timedelta(hours=tlog.overtime)
                        ts.append("time_logs", {
                        "activity_type" : "Overtime",
                        "task": tlog.activity,
                        "from_time" : end_time,
                        "to_time" : overtime,
                        "hours": tlog.overtime,
                        "is_billable" : 1,
                        "billing_rate":amt_2,
                        
                    })
        
                ts.append("time_logs", {
                        "activity_type" : "Regular Work",
                        "task": tlog.activity,
                        "from_time" : start_time,
                        "to_time" : end_time,
                        "hours": tlog.work_hours
                    })
                ts.save(ignore_permissions=True)
               
                # leave = frappe.db.get_value('Employee',{'name':ts.employee},'holiday_list')
                # holiday = frappe.db.sql("""select `tabHoliday`.holiday_date,`tabHoliday`.weekly_off from `tabHoliday List` 
                # left join `tabHoliday` on `tabHoliday`.parent = `tabHoliday List`.name where `tabHoliday List`.name = '%s' and holiday_date = '%s' """%(leave,self.worked_date),as_dict=True)
                # if holiday:
                #     ts.total_billable_amount = flt(((basic/26)/8) * 1.50)
                # else:
                #     ts.total_billable_amount = flt(((basic/26)/8) * 1.25)
                # ts.save(ignore_permissions=True)
                ts.submit()
            else:
                frappe.throw("Timesheets has been already created for this Employee for the same period")
