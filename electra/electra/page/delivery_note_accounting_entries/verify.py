import frappe


def verify():
	page = frappe.db.sql(
		"SELECT name, page_name, module, standard FROM tabPage WHERE name='delivery-note-wip-accounting'",
		as_dict=True,
	)
	print("Page in DB:")
	for p in page:
		print(f"  name={p['name']}  page_name={p['page_name']}  module={p['module']}  standard={p['standard']}")

	# Also check if the JS file is being served
	import os
	js_path = os.path.join(frappe.get_app_path("electra"), "electra", "page", "delivery_note_wip_accounting", "delivery_note_wip_accounting.js")
	print(f"\nJS file exists: {os.path.exists(js_path)}")
	print(f"JS path: {js_path}")
