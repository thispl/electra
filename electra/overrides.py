import frappe
from frappe import _
from erpnext.hr.doctype.employee.employee import Employee
# from erpnext.accounts.report.accounts_recievable.accounts_recievable import ReceivablePayableReport
from frappe.utils import add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words, formatdate, get_first_day
from erpnext.hr.utils import validate_dates, validate_overlap, get_leave_period, \
    get_holidays_for_employee, create_additional_leave_ledger_entry

# class CustomReceivablePayableReport(ReceivablePayableReport):
#     def add_common_filters(self, conditions, values, party_type_field):
#         if self.filters.company:
#             conditions.append("company='STEEL DIVISION - ELECTRA'")
#             values.append(self.filters.company)

#         if self.filters.finance_book:
#             conditions.append("ifnull(finance_book, '') in (%s, '')")
#             values.append(self.filters.finance_book)

#         if self.filters.get(party_type_field):
#             conditions.append("party=%s")
#             values.append(self.filters.get(party_type_field))

#         # get GL with "receivable" or "payable" account_type
#         account_type = "Receivable" if self.party_type == "Customer" else "Payable"
#         accounts = [d.name for d in frappe.get_all("Account",
#             filters={"account_type": account_type, "company": self.filters.company})]

#         if accounts:
#             conditions.append("account in (%s)" % ','.join(['%s'] *len(accounts)))
#             values += accounts

# class CustomEmployee(Employee):
#     def autoname(self):
#         emp = frappe.db.sql(""" select employee_number from `tabEmployee` order by name """,as_dict = 1)[-1]
#         last = emp.employee_number
#         las = int(last)
#         new = las + 1
#         # frappe.errprint(type(new))
#         frappe.errprint(type(new))
#         self.employee_number = new
#         # self.name = new