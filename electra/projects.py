# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import json
from typing import Literal

import frappe
import frappe.utils
from frappe import _, qb
from frappe.contacts.doctype.address.address import get_company_address
from frappe.desk.notifications import clear_doctype_notifications
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values
from frappe.query_builder.functions import Sum
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html

from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	unlink_inter_company_doc,
	update_linked_doc,
	validate_inter_company_party,
)
from erpnext.accounts.party import get_party_account
from erpnext.controllers.selling_controller import SellingController
from erpnext.manufacturing.doctype.blanket_order.blanket_order import (
	validate_against_blanket_order,
)
from erpnext.manufacturing.doctype.production_plan.production_plan import (
	get_items_for_material_requests,
)
from erpnext.selling.doctype.customer.customer import check_credit_limit
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
	get_sre_reserved_qty_details_for_voucher,
	has_reserved_stock,
)
from erpnext.stock.get_item_details import get_default_bom, get_price_list_rate
from erpnext.stock.stock_balance import get_reserved_qty, update_bin_qty

@frappe.whitelist()
def make_delivery_note_wip(source_name, target_doc=None, kwargs=None):
	from erpnext.stock.doctype.packed_item.packed_item import make_packing_list
	from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
		get_sre_details_for_voucher,
		get_sre_reserved_qty_details_for_voucher,
		get_ssb_bundle_for_voucher,
	)

	if not kwargs:
		kwargs = {
			"for_reserved_stock": frappe.flags.args and frappe.flags.args.for_reserved_stock,
			"skip_item_mapping": frappe.flags.args and frappe.flags.args.skip_item_mapping,
		}

	kwargs = frappe._dict(kwargs)

	sre_details = {}
	if kwargs.for_reserved_stock:
		pb = frappe.db.get_value("Sales Order",source_name,'project_budget')
		sre_details = get_sre_reserved_qty_details_for_voucher("Project Budget", pb)

	mapper = {
		# "Project Budget": {"doctype": "Delivery Note WIP", "validation": {"docstatus": ["=", 1]}},
		"Project Budget": {"doctype": "Delivery Note WIP"},
		"Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
		"Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
	}

	def set_missing_values(source, target):
		target.run_method("set_missing_values")
		target.run_method("set_po_nos")
		target.run_method("calculate_taxes_and_totals")
		target.update({"project_budget":source.name})
		project = frappe.get_value("Sales Order",{'project_budget':source.name},['project'])
		customer = frappe.get_value("Sales Order",{'project_budget':source.name},['customer'])
		title_of_project=frappe.get_value("Sales Order",{'project_budget':source.name},['title_of_project'])
		po_no=frappe.get_value("Sales Order",{'project_budget':source.name},['po_no'])
		po_date=frappe.get_value("Sales Order",{'project_budget':source.name},['po_date'])
		sales_person_user=frappe.get_value("Sales Order",{'project_budget':source.name},['sales_person_user'])
		sales_person_username=frappe.get_value("Sales Order",{'project_budget':source.name},['sales_person_username'])
		sales_person_designation=frappe.get_value("Sales Order",{'project_budget':source.name},['sales_person_designation'])
		sales_person_mobile=frappe.get_value("Sales Order",{'project_budget':source.name},['sales_person_mobile'])
		
		if project:
			target.update({"project": project})
		if customer:
			target.update({"customer": customer})
		if title_of_project:
			target.update({"title_of_project": title_of_project})
		if po_no:
			target.update({'po_no':po_no})
		if po_date:
			target.update({'po_date':po_date})
		if sales_person_user:
			target.update({'sales_person_user':sales_person_user})
		if sales_person_username:
			target.update({'sales_person_username':sales_person_username})
		if sales_person_designation:
			target.update({'sales_person_designation':sales_person_designation})
		if sales_person_mobile:
			target.update({'sales_person_mobile':sales_person_mobile})
		# else:
		# 	# set company address
		# 	target.update(get_company_address(target.company))

		# if target.company_address:
		# 	target.update(get_fetch_values("Delivery Note", "company_address", target.company_address))

		# if invoked in bulk creation, validations are ignored and thus this method is nerver invoked
		if frappe.flags.bulk_transaction:
			# set target items names to ensure proper linking with packed_items
			target.set_new_name()

		# make_packing_list(target)

	def condition(doc):
		if doc.name in sre_details:
			del sre_details[doc.name]
			return False

		# make_mapped_doc sets js `args` into `frappe.flags.args`
		if frappe.flags.args and frappe.flags.args.delivery_dates:
			if cstr(doc.delivery_date) not in frappe.flags.args.delivery_dates:
				return False

		return abs(doc.delivered_qty) < abs(doc.qty)

	def update_item(source, target, source_parent):
		target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.unit_price)
		target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.unit_price)
		target.qty = flt(source.qty) - flt(source.delivered_qty)

		item = get_item_defaults(target.item_code, source_parent.company)
		item_group = get_item_group_defaults(target.item_code, source_parent.company)

		# if item:
		# 	target.cost_center = (
		# 		frappe.db.get_value("Project", source_parent.project, "cost_center")
		# 		or item.get("buying_cost_center")
		# 		or item_group.get("buying_cost_center")
		# 	)
	sales = frappe.get_doc("Sales Order",source_name)
	if not kwargs.skip_item_mapping:
		mapper["Project Budget Items"] = {
			"doctype": "Delivery Note Item",
			"field_map": {
				"item":"item_code",
				"unit":"uom",
				"unit_price": "rate",
				"name": "custom_against_pb_item",
				"parent": "custom_against_pb",
				"docname": "custom_against_pbsow",
				"pb_doctype": "custom_against_pbsow_doctype",
			},
			"condition": condition,
			"postprocess": update_item,
		}

	pb = frappe.db.get_value("Sales Order",source_name,'project_budget')
	so = frappe.get_doc("Project Budget", pb)
	target_doc = get_mapped_doc("Project Budget", so.name, mapper, target_doc)

	if not kwargs.skip_item_mapping and kwargs.for_reserved_stock:
		pb = frappe.db.get_value("Sales Order",source_name,'project_budget')
		sre_list = get_sre_details_for_voucher("Project Budget", pb)

		if sre_list:

			def update_dn_item(source, target, source_parent):
				update_item(source, target, so)

			so_items = {d.name: d for d in so.item_table if d.stock_reserved_qty}

			for sre in sre_list:
				if not condition(so_items[sre.voucher_detail_no]):
					continue
				dn_item = get_mapped_doc(
					"Project Budget Items",
					sre.voucher_detail_no,
					{
						"Project Budget Items": {
							"doctype": "Delivery Note Item",
							"field_map": {
								"item":"item_code",
								"unit":"uom",
								"unit_price": "rate",
								"name": "custom_against_pb_item",
								"parent": "custom_against_pb",
								"docname": "custom_against_pbsow",
								"pb_doctype": "custom_against_pbsow_doctype"
							},
							"postprocess": update_dn_item,
						}
					},
					ignore_permissions=True,
				)
				dn_item.qty = flt(sre.reserved_qty) * flt(dn_item.get("conversion_factor", 1))

				if sre.reservation_based_on == "Serial and Batch" and (sre.has_serial_no or sre.has_batch_no):
					dn_item.serial_and_batch_bundle = get_ssb_bundle_for_voucher(sre)

				target_doc.append("items", dn_item)
			else:
				# Correct rows index.
				for idx, item in enumerate(target_doc.items):
					item.idx = idx + 1

	# Should be called after mapping items.
	set_missing_values(so, target_doc)

	return target_doc
