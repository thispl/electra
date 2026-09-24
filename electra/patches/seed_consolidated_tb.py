import json
import os

import frappe


def execute():
	"""Seed Consolidated TB Bucket + Company Map from the mapping derived
	from the accountant's consolidated trial balance workbook."""
	path = os.path.join(os.path.dirname(__file__), "consolidated_tb_seed.json")
	with open(path) as f:
		seed = json.load(f)

	for cm in seed.get("company_map", []):
		if frappe.db.exists("Consolidated TB Company Map", cm["company"]):
			continue
		if not frappe.db.exists("Company", cm["company"]):
			continue
		frappe.get_doc(
			{
				"doctype": "Consolidated TB Company Map",
				"company": cm["company"],
				"division": cm["division"],
				"cr_group": cm["cr_group"],
				"sort_order": cm["sort_order"],
			}
		).insert(ignore_permissions=True)

	for b in seed.get("buckets", []):
		if frappe.db.exists("Consolidated TB Bucket", b["bucket"]):
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Consolidated TB Bucket",
				"bucket": b["bucket"],
				"account_head": b["account_head"],
				"tb_group": b["tb_group"],
				"sort_order": b["sort_order"],
			}
		)
		for a in b.get("accounts", []):
			doc.append(
				"accounts",
				{
					"account_number": a.get("account_number") or "",
					"account_name": a.get("account_name") or "",
					"company": a.get("company") or None,
				},
			)
		doc.insert(ignore_permissions=True)
