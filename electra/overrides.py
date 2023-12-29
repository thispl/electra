import frappe
from frappe import _
from frappe.utils import nowdate, unique, add_days, cint, cstr, flt, getdate, rounded, date_diff, money_in_words, formatdate, get_first_day
from frappe.desk.reportview import get_filters_cond, get_match_cond
from hrms.hr.doctype.employee_separation.employee_separation import EmployeeSeparation

class CustomEmployeeSeparation(EmployeeSeparation):
	def on_submit(self):
		frappe.log_error(title='EmployeeSeparation',message='on_submit')


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