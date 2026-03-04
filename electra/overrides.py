import frappe
from frappe import _
from datetime import date,datetime,timedelta
from frappe.utils import nowdate, unique, add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words, formatdate, get_first_day
from frappe.desk.reportview import get_filters_cond, get_match_cond
from hrms.hr.doctype.employee_separation.employee_separation import EmployeeSeparation
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
class CustomEmployeeSeparation(EmployeeSeparation):
    def on_submit(self):
        frappe.log_error(title='EmployeeSeparation',message='on_submit')

class CustomSalarySlip(SalarySlip):
    def get_date_details(self):
        emp=frappe.get_doc('Employee',self.employee) 
        basic=0
        hra=0
        other_allow=0
        transport=0
        if emp.history:
            # Filter only records before or on start_date
            valid_history = [i for i in emp.history if getdate(i.date) <= getdate(self.start_date)]

            if valid_history:
                # Get the record with the latest date
                last_record = max(valid_history, key=lambda x: getdate(x.date))

                basic = last_record.basic
                hra = last_record.hra
                other_allow = last_record.other_allowance
                transport = last_record.transport_allowance

        else:
            basic=emp.basic
            hra=emp.hra
            other_allow=emp._other_allowance
            transport=emp.transportation
        self.basic=basic
        self.hra=hra
        self._other_allowance=other_allow
        self.transportation=transport
        
    from datetime import datetime

    def before_save(self):
        current_year = datetime.now().year

        # Get all medical leaves in the year sorted by from_date
        leave_apps = frappe.get_all(
            "Leave Application",
            filters={
                "employee": self.employee,
                "leave_type": "Medical Leave",
                "from_date": [">=", f"{current_year}-01-01"],
                "to_date": ["<=", f"{current_year}-12-31"],
                "docstatus":1
            },
            fields=["from_date", "to_date", "total_leave_days"],
            order_by="from_date asc"
        )

        allowed_limit = 15
        running_total = 0
        extra_in_period = 0

        # Salary slip period
        start_date = datetime.strptime(str(self.start_date), "%Y-%m-%d").date()
        end_date = datetime.strptime(str(self.end_date), "%Y-%m-%d").date()

        for app in leave_apps:
            leave_start = datetime.strptime(str(app.get("from_date")), "%Y-%m-%d").date()
            leave_end = datetime.strptime(str(app.get("to_date")), "%Y-%m-%d").date()

            # Loop day by day through the leave period
            day = leave_start
            while day <= leave_end:
                running_total += 1
                # If over the allowed limit and inside salary slip period → count as extra
                if running_total > allowed_limit and start_date <= day <= end_date:
                    extra_in_period += 1
                day += timedelta(days=1)

        self.custom_medical_leave = extra_in_period/2


                    

@frappe.whitelist()
def get_project_emp():
    pass


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_delivery_notes_to_be_billed(doctype, txt, searchfield, start, page_len, filters, as_dict):
    doctype = "Delivery Note"
    fields = get_fields(doctype, ["name","posting_date","po_no"])

    return frappe.db.sql(
        """
        select %(fields)s
        from `tabDelivery Note`
        where `tabDelivery Note`.`%(key)s` like %(txt)s and
            `tabDelivery Note`.docstatus = 1
            and status not in ('Stopped', 'Closed') %(fcond)s
            and (
                (`tabDelivery Note`.is_return = 0 and `tabDelivery Note`.per_billed < 100)
                or (`tabDelivery Note`.grand_total = 0 and `tabDelivery Note`.per_billed < 100)
                or (
                    `tabDelivery Note`.is_return = 1
                    and return_against in (select name from `tabDelivery Note` where per_billed < 100)
                )
            )
            %(mcond)s order by `tabDelivery Note`.`%(key)s` asc limit %(page_len)s offset %(start)s
    """
        % {
            "fields": ", ".join(["`tabDelivery Note`.{0}".format(f) for f in fields]),
            "key": searchfield,
            "fcond": get_filters_cond(doctype, filters, []),
            "mcond": get_match_cond(doctype),
            "start": start,
            "page_len": page_len,
            "txt": "%(txt)s",
        },
        {"txt": ("%%%s%%" % txt)},
        as_dict=as_dict,
    )

def get_fields(doctype, fields=None):
    if fields is None:
        fields = []
    meta = frappe.get_meta(doctype)
    fields.extend(meta.get_search_fields())

    if meta.title_field and not meta.title_field.strip() in fields:
        fields.insert(1, meta.title_field.strip())

    return unique(fields)