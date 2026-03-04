# Copyright (c) 2025, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, add_days, date_diff, getdate, format_date, fmt_money


class BudgetedvsActualTestReport(Document):
	pass

@frappe.whitelist()
def update_project_values(name):
	project_budget, p_name = frappe.db.get_value(
		"Project", {'name': name}, ['budgeting', 'project_name']
	)
	grand = frappe.db.get_value("Sales Order", {'project': name, 'docstatus': 1}, 'grand_total')
	sales_in = frappe.db.sql(
		""" SELECT SUM(custom_total_invoice_amount - discount_amount) as total FROM `tabSales Invoice` WHERE project = %s and docstatus = 1""",
		(name,),
		as_dict=True)[0]
	if not sales_in["total"]:
		sales_in["total"] = 0
	bal = grand - sales_in["total"]
	revenue = frappe.db.sql(
		""" SELECT SUM(paid_amount) as amt FROM `tabPayment Entry` WHERE project = %s and docstatus=1""",
		(name,),
		as_dict=True)[0]
	if not revenue["amt"]:
		revenue["amt"] = 0
	out = sales_in["total"] - revenue["amt"]
	cost_till_date = project_cost_till_date(name)
	# cost_till_date = 0

	gr_pr = sales_in["total"] - cost_till_date
	if sales_in["total"]>0:
		per_gp = (gr_pr / sales_in["total"] or 0) * 100
	else:
		per_gp=0
	
	pb = frappe.get_doc("Project Budget", project_budget)		
	categories = [
		{"name": "Supply Materials", "table": pb.materials, "custom_field": "custom_supply_materials"},
		{"name": "Accessories", "table": pb.bolts_accessories, "custom_field": "custom_accessories"},
		{"name": "Subcontract", "table": pb.others, "custom_field": "custom_subcontract"},
		{"name": "Design", "table": pb.design, "custom_field": "custom_design"},
		{"name": "Finishing Work", "table": pb.finishing_work, "custom_field": "custom_finishing_work"},
		{"name": "Tools / Equipment / Transport / Others", "table": pb.heavy_equipments, "custom_field": "custom_tools"},
		{"name": "Finished Goods", "table": pb.finished_goods, "custom_field": "custom_finished_goods"},
		{"name": "Manpower", "table": pb.manpower, "custom_field": "custom_manpower"},
		{"name": "Installation", "table": pb.installation, "custom_field": "custom_installation"},
	]
	frappe.publish_realtime(
		"project_update_progress",
		{"progress": 1.1, "description": f"Processing {1.1}%..."},
		user=frappe.session.user
	)
	project_doc=frappe.get_doc("Project",name)
	project_doc.custom_order_value=grand
	project_doc.custom_invoice_value_till_date=sales_in["total"]
	
	project_doc.custom_cost_till_date=cost_till_date
	project_doc.custom_gross_profit=gr_pr
	project_doc.custom_gross_profit_per=per_gp
	project_doc.custom_balance_to_invoice=bal
	project_doc.custom_total_collection=revenue["amt"]
	project_doc.custom_os_receipts=out
	


	# Reset custom fields in the project
	for field in [
		'custom_overall_summary_', 'custom_supply_materials', 'custom_accessories',
		'custom_subcontract', 'custom_design', 'custom_finishing_work',
		'custom_tools', 'custom_finished_goods', 'custom_manpower', 'custom_installation','custom_other_report'
	]:
		project_doc.set(field, [])
	total_material_cost=0
	total_operational_cost=0
	# Emit real-time progress updates
	total_steps = len(categories)
	for index, category in enumerate(categories):
		progress = round(((index + 1) / total_steps) * 100, 2)
		frappe.publish_realtime(
			"project_update_progress",
			{"progress": progress, "description": f"Processing {progress}%..."},
			user=frappe.session.user
		)

		if not category["table"]:
			continue

		if category["name"] == "Manpower":
			total_operational_cost,amt = process_manpower(category, project_doc, pb, name)
			project_doc.append('custom_overall_summary_', {
				'item': category["name"],
				'budgeted': amt,
				'actual': total_operational_cost
			})
		elif category["name"] == "Installation":
			total_operational_cost,amt = process_installation(category, project_doc, pb, name)
			project_doc.append('custom_overall_summary_', {
				'item': category["name"],
				'budgeted': amt,
				'actual': total_operational_cost
			})
		elif category["name"] == "Supply Materials":
			if pb.docname_updated_in_dn == 1:
				if pb.company == "MEP DIVISION - ELECTRA":
					total_material_cost,amt = process_mep_material_docname(category, project_doc, pb, name)
					project_doc.append('custom_overall_summary_', {
						'item': category["name"],
						'budgeted': amt,
						'actual': total_material_cost
					})
				else:
					total_material_cost,amt = process_category_docname(category, project_doc, pb, name)
					project_doc.append('custom_overall_summary_', {
						'item': category["name"],
						'budgeted': amt,
						'actual': total_material_cost
					})
			else:
				if pb.company == "MEP DIVISION - ELECTRA":
					total_material_cost,amt = process_mep_material(category, project_doc, pb, name)
					project_doc.append('custom_overall_summary_', {
						'item': category["name"],
						'budgeted': amt,
						'actual': total_material_cost
					})
				else:
					total_material_cost,amt = process_category(category, project_doc, pb, name)
					project_doc.append('custom_overall_summary_', {
						'item': category["name"],
						'budgeted': amt,
						'actual': total_material_cost
					})
		else:
			if pb.docname_updated_in_dn == 1:
				total_material_cost,amt = process_category_docname(category, project_doc, pb, name)
				project_doc.append('custom_overall_summary_', {
					'item': category["name"],
					'budgeted': amt,
					'actual': total_material_cost
				})
			else:
				total_material_cost,amt = process_category(category, project_doc, pb, name)
				project_doc.append('custom_overall_summary_', {
					'item': category["name"],
					'budgeted': amt,
					'actual': total_material_cost
				})
	# # Handle other expenses (if applicable)
	project_doc.custom_material_cost=total_material_cost
	project_doc.custom_operational_cost=total_operational_cost+process_other_expenses(name)
	project_doc.save(ignore_permissions=True)
	frappe.publish_realtime(
		"project_update_progress",
		{"progress": 100, "description": "Calculation complete!"},
		user=frappe.session.user
	)
	return True
@frappe.whitelist()
def process_manpower(category, project_doc, project_budget, project_name):
	"""Process manpower-related calculations."""
	budget = 0 
	timesheet = frappe.db.sql("""
		SELECT SUM(c.costing_amount) AS cost 
		FROM `tabTimesheet` p 
		INNER JOIN `tabTimesheet Detail` c ON c.parent = p.name 
		WHERE c.project = %s AND p.docstatus = 1 
		GROUP BY c.project
	""", (project_name,), as_dict=True)
	total_cost = round(timesheet[0].cost, 2) if timesheet else 0
	for item in category["table"]:
		project_doc.append(category["custom_field"], {
			'budget_code': item.msow,
			'part_number': item.worker,
			'description': item.worker,
			'unit': "Nos",
			'qty': item.total_workers,
			'rate': item.rate_with_overheads,
			'amount': item.amount_with_overheads,
			'del_qty': item.total_workers,
			'del_amount': total_cost,
			'bal_qty': item.total_workers,
			'amount_variance': total_cost,
			'docname': item.docname,
		})
		total_op_cost = total_cost
		budget += item.amount_with_overheads
	return total_op_cost, budget


@frappe.whitelist()
def process_installation(category, project_doc, project_budget, project_name):
	total_op_cost = 0
	budget = 0 
	"""Process installation-related calculations."""
	timesheet = frappe.db.sql("""
		SELECT SUM(c.costing_amount) AS cost 
		FROM `tabTimesheet` p 
		INNER JOIN `tabTimesheet Detail` c ON c.parent = p.name 
		WHERE c.project = %s AND p.docstatus = 1 
		GROUP BY c.project
	""", (project_name,), as_dict=True)
	total_cost = round(timesheet[0].cost, 2) if timesheet else 0
	for item in category["table"]:
		timesheet_data = frappe.db.sql("""
			SELECT 
				SUM(`tabTimesheet Detail`.costing_amount) AS total_cost,
				`tabTimesheet Detail`.task,
				`tabTask`.subject AS task_name
			FROM 
				`tabTimesheet`
			LEFT JOIN 
				`tabTimesheet Detail` ON `tabTimesheet`.name = `tabTimesheet Detail`.parent
			LEFT JOIN 
				`tabTask` ON `tabTimesheet Detail`.task = `tabTask`.name
			WHERE 
				`tabTimesheet Detail`.project = %s AND `tabTimesheet`.docstatus = 1 AND `tabTask`.subject = %s
			GROUP BY 
				`tabTimesheet Detail`.task
		""", (project_name, item.description), as_dict=True)

		if timesheet_data:
			completed_qty = frappe.db.get_value("Task", timesheet_data[0]['task'], 'completed_qty') or 0
			delivered_amount = round(timesheet_data[0]['total_cost'], 2)
		else:
			completed_qty = 0
			delivered_amount = 0
		if item.item:
			project_doc.append(category["custom_field"], {
				'budget_code': item.msow,
				'part_number': item.item,
				'description': item.description,
				'unit': item.unit,
				'qty': item.qty,
				'rate': item.rate_with_overheads,
				'amount': item.amount_with_overheads,
				'del_qty': completed_qty,
				'del_amount': delivered_amount,
				'bal_qty': item.qty - completed_qty,
				'amount_variance': item.amount_with_overheads - delivered_amount,
				'docname': item.docname
			})
			total_op_cost += delivered_amount
			budget += item.amount_with_overheads
	if delivered_amount == 0:
		total_op_cost = total_cost
	return total_op_cost, budget

@frappe.whitelist()
def process_category(category, project_doc, project_budget, project_name):
	total_material_cost = 0
	budget = 0 
	"""Process generic category calculations."""
	for item in category["table"]:
		dn, dn_amount = find_dn_qty_for_item(project_name, item.item)
		dn_wip,dn_wip_amount = find_dn_wip_qty_for_item(project_budget.sales_order, item.item, item.docname) or 0
		if dn and dn_wip:
			delivered_qty = dn + dn_wip
			delivered_amount = (dn_amount + dn_wip_amount) 
		elif dn:
			delivered_qty = dn
			delivered_amount = dn_amount
		elif dn_wip:
			delivered_qty = dn_wip
			delivered_amount = dn_wip_amount
		else:
			delivered_qty = 0
			delivered_amount = 0
		

		project_doc.append(category["custom_field"], {
			'budget_code': item.msow,
			'part_number': item.item,
			'description': item.description,
			'unit': item.unit,
			'qty': delivered_qty,
			'rate': item.unit_price,
			'amount': delivered_qty * item.unit_price,
			'del_qty': delivered_qty,
			'del_amount': delivered_amount,
			'bal_qty': 0,
			'amount_variance': (delivered_qty * item.unit_price) - delivered_amount,
			'docname': item.docname,
		})
		total_material_cost+=delivered_amount
		budget += item.amount
	return total_material_cost,budget

@frappe.whitelist()
def process_category_docname(category, project_doc, project_budget, project_name):
	total_material_cost = 0
	budget = 0 
	"""Process generic category calculations."""
	for item in category["table"]:
		dn, dn_amount = find_dn_qty_for_item(project_name, item.item, item.docname)
		dn_wip,dn_wip_amount = find_dn_wip_qty_for_item(project_budget.sales_order, item.item, item.docname) or 0
		if dn and dn_wip:
			delivered_qty = dn + dn_wip
			delivered_amount = (dn_amount + dn_wip_amount) 
		elif dn:
			delivered_qty = dn
			delivered_amount = dn_amount
		elif dn_wip:
			delivered_qty = dn_wip
			delivered_amount = dn_wip_amount
		else:
			delivered_qty = 0
			delivered_amount = 0

		project_doc.append(category["custom_field"], {
			'budget_code': item.msow,
			'part_number': item.item,
			'description': item.description,
			'unit': item.unit,
			'qty': delivered_qty,
			'rate': item.unit_price,
			'amount': delivered_qty * item.unit_price,
			'del_qty': delivered_qty,
			'del_amount': delivered_amount,
			'bal_qty': 0,
			'amount_variance': (delivered_qty * item.unit_price) - delivered_amount,
			'docname': item.docname,
		})
		total_material_cost+=delivered_amount
		budget += item.amount
	return total_material_cost,budget


@frappe.whitelist()
def process_other_expenses(project):
	journal_entry = frappe.db.sql("""
		SELECT SUM(c.debit_in_account_currency) AS cost 
		FROM `tabJournal Entry` jl 
		INNER JOIN `tabJournal Entry Account` c ON c.parent = jl.name 
		WHERE c.project = %s AND jl.docstatus = 1 
		GROUP BY c.project
	""", (project,), as_dict=True)
	
	return round(journal_entry[0].cost, 2) if journal_entry else 0

@frappe.whitelist()
def project_cost_till_date(name):
	project = name
	
	total = (total_dn_cost(project) + 
			 total_dnwip_cost(project) + 
			 total_jl_cost(project) + 
			 total_cost_by_timesheet(project))
	return total

@frappe.whitelist()
def total_dn_cost(project):
	project_budget = frappe.db.get_value("Project", project, "budgeting")
	pb = frappe.get_doc("Project Budget", project_budget)
 
	data = {}
	project_name = project
	
	if pb.docname_updated_in_dn == 1:
		for item in pb.item_table:
			dn_data = frappe.db.sql(
				"""
				SELECT 
					dni.item_code, 
					dni.qty,
					(
						SELECT sle.valuation_rate 
						FROM `tabStock Ledger Entry` sle 
						WHERE sle.item_code = dni.item_code 
						AND sle.voucher_no = dn.name 
						ORDER BY sle.creation DESC 
						LIMIT 1
					) AS valuation_rate
				FROM `tabDelivery Note` dn
				LEFT JOIN `tabDelivery Note Item` dni 
					ON dn.name = dni.parent
				WHERE dni.item_code = %s 
				AND dni.custom_docname = %s
				AND dn.project = %s 
				""",
				(item.item, item.docname, project_name),
				as_dict=True
			) or []

			# Process fetched data
			for i in dn_data:
				item_code = i.item_code
				qty = i.qty or 0
				valuation_rate = i.valuation_rate or 0
				amount = qty * valuation_rate

				# Store data in dictionary
				if item_code in data:
					data[item_code]["total_qty"] += qty
					data[item_code]["total_amount"] += amount
				else:
					data[item_code] = {
						"total_qty": qty,
						"total_amount": amount
					}

		total_amount = sum(d["total_amount"] for d in data.values())
	else:
		for item in pb.item_table:
			dn_data = frappe.db.sql(
				"""
				SELECT 
					dni.item_code, 
					dni.qty,
					(
						SELECT sle.valuation_rate 
						FROM `tabStock Ledger Entry` sle 
						WHERE sle.item_code = dni.item_code 
						AND sle.voucher_no = dn.name 
						ORDER BY sle.creation DESC 
						LIMIT 1
					) AS valuation_rate
				FROM `tabDelivery Note` dn
				LEFT JOIN `tabDelivery Note Item` dni 
					ON dn.name = dni.parent
				WHERE dni.item_code = %s 
				AND dn.project = %s 
				""",
				(item.item, project_name),
				as_dict=True
			) or []

			# Process fetched data
			for i in dn_data:
				item_code = i.item_code
				qty = i.qty or 0
				valuation_rate = i.valuation_rate or 0
				amount = qty * valuation_rate

				# Store data in dictionary
				if item_code in data:
					data[item_code]["total_qty"] += qty
					data[item_code]["total_amount"] += amount
				else:
					data[item_code] = {
						"total_qty": qty,
						"total_amount": amount
					}

		total_amount = sum(d["total_amount"] for d in data.values())
	return round(total_amount, 2)


@frappe.whitelist()
def total_jl_cost(project):
	journal_entry = frappe.db.sql("""
		SELECT SUM(c.debit_in_account_currency) AS cost 
		FROM `tabJournal Entry` jl 
		INNER JOIN `tabJournal Entry Account` c ON c.parent = jl.name 
		WHERE c.project = %s AND jl.docstatus = 1 
		GROUP BY c.project
	""", (project,), as_dict=True)
	
	return round(journal_entry[0].cost, 2) if journal_entry else 0

@frappe.whitelist()
def total_cost_by_timesheet(project):
	timesheet = frappe.db.sql("""
		SELECT SUM(c.costing_amount) AS cost 
		FROM `tabTimesheet` p 
		INNER JOIN `tabTimesheet Detail` c ON c.parent = p.name 
		WHERE c.project = %s AND p.docstatus = 1 
		GROUP BY c.project
	""", (project,), as_dict=True)
	return round(timesheet[0].cost, 2) if timesheet else 0

# @frappe.whitelist()
# def find_dn_wip_qty_for_item(sales_order, item, docname):
# 	dn_wip_list = frappe.get_all("Delivery Note WIP", {"sales_order": sales_order, "is_return": 0, "docstatus": 1})
	
# 	total_qty = 0
# 	total_amount = 0  # Accumulator for total valuation amount

# 	for dn_wip in dn_wip_list:
# 		del_wip = frappe.get_doc("Delivery Note WIP", dn_wip.name)
		
# 		stock_entry_exist = frappe.db.exists("Stock Entry", {"stock_entry_type": "Material Transfer", "reference_number": dn_wip.name, "docstatus": 1})
# 		if stock_entry_exist:
# 			se = frappe.get_doc("Stock Entry", {"stock_entry_type": "Material Transfer", "reference_number": dn_wip.name, "docstatus": 1})
			
# 			# Dictionary to store item rates by delivery note
# 			item_rate_map = {}
			
# 			for row in se.items:
# 				if row.item_code == item:
# 					item_rate_map[row.item_code] = row.basic_rate  # Store rate per item
			
# 			for i in del_wip.items:
# 				if i.item_code == item and i.custom_against_pbsow == docname:
# 					item_qty = i.qty
# 					rate = item_rate_map.get(item, 0)  # Get rate, default to 0 if not found

# 					total_qty += item_qty
# 					total_amount += item_qty * rate  # Accumulate weighted rate

# 	# Avoid division by zero
# 	average_rate = total_amount / total_qty if total_qty > 0 else 0

# 	return total_qty, total_amount

@frappe.whitelist()
def find_dn_wip_qty_for_item(sales_order, item, docname):
    dn_wip_names = frappe.get_all(
        "Delivery Note WIP",
        filters={"sales_order": sales_order, "is_return": 0, "docstatus": 1},
        pluck="name"
    )

    if not dn_wip_names:
        return 0, 0

    # Get all relevant stock entries in a single query
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={
            "stock_entry_type": "Material Transfer",
            "reference_number": ["in", dn_wip_names],
            "docstatus": 1
        },
        fields=["name", "reference_number"]
    )

    # Build a map: reference_number -> stock_entry_name
    ref_to_se = {se.reference_number: se.name for se in stock_entries}

    total_qty = 0
    total_amount = 0

    # Load all item rows from Stock Entries in one go
    stock_items = frappe.get_all(
        "Stock Entry Detail",
        filters={
            "parent": ["in", list(ref_to_se.values())],
            "item_code": item
        },
        fields=["parent", "item_code", "basic_rate"]
    )

    # Map of stock_entry -> rate
    se_rate_map = {row.parent: row.basic_rate for row in stock_items}

    for dn_name in dn_wip_names:
        del_wip = frappe.get_doc("Delivery Note WIP", dn_name)
        if dn_name not in ref_to_se:
            continue

        rate = se_rate_map.get(ref_to_se[dn_name], 0)

        for i in del_wip.items:
            if i.item_code == item and i.custom_against_pbsow == docname:
                total_qty += i.qty
                total_amount += i.qty * rate

    average_rate = total_amount / total_qty if total_qty else 0
    return total_qty, total_amount


@frappe.whitelist()
def actual_vs_budgeted(name):
	crea = frappe.db.sql("""select creation from `tabProject` where name ='%s' """ % (name), as_dict=True)[0]
	project = frappe.get_doc("Project",name)
	data = '''<style>
			.font-size {
				font-size: 10px;
			}
			.top-header {
				margin-top: 30px;
			}
			.page-break {
				page-break-before: always;
			}
			table {
				font-family: Soleto;
				border-collapse: collapse;
			}
			.orange {
				color: white;
				background-color: #e35310;
				font-weight: bold;
				border: 1px solid white;
				text-align: center;
			}
			.white-border {
				border: 1px solid white;
			}
			</style>
			'''
	data += '<table style="font-size: 14px;" class="top-header" width = 100%>'
	data += '<tr><td><b>Date</b></td><td>%s</td><td><b>Refer No</b></td><td></td></tr>' % (
		format_date(crea["creation"].date()))
	data += '<tr><td><b>Project Code</b></td><td>%s</td><td><b>Project</b></td><td>%s</td></tr>' % (name, project.project_name)
	data += '<tr><td><b>Client</b></td><td>%s</td><td><b>Order Ref No.</b></td><td>%s</td></tr>' % (
		project.customer, project.sales_order)
	data += '<tr><td><b></b></td><td></td><td><b>Budget Code</b></td><td>%s</td></tr>' % (
		project.budgeting)
	data += '</table><br>'
	
	data += '<h3>Project Details</h3>'
	data += '<table style="margin-10px" solid black width=100%>'
	data += '<tr style="background-color:#e35310;text-align:center;color: white;"><td class="orange" style="border-left-style: hidden;">Order Value</td><td class="orange">Invoice Value till Date</td><td class="orange">Cost Till Date</td><td class="orange">Gross Profit</td><td class="orange">Gross Profit %</td><td class="orange">Balance To Invoice</td><td class="orange">Total Collection</td><td class="orange" style="border-right-style: hidden;">O/S Receipts</td></tr>'
	data += '<tr style="text-align:right;background-color:#ffe5b4;"><td class="white-border">%s</td><td class="white-border">%s</td><td class="white-border">%s</td><td class="white-border">%s</td><td class="white-border">%s</td><td class="white-border">%s</td><td class="white-border">%s</td><td class="white-border">%s</td></tr>' % (
		fmt_money(project.custom_order_value, 2), fmt_money(project.custom_invoice_value_till_date, 2), fmt_money(project.custom_cost_till_date, 2),
		fmt_money(round(project.custom_gross_profit, 2), 2), fmt_money(round(project.custom_gross_profit_per, 2), 2), fmt_money(round(project.custom_balance_to_invoice, 2), 2),
		fmt_money(round(project.custom_total_collection, 2) or 0, 2), fmt_money(round(project.custom_os_receipts, 2), 2))
	data += '</table><br>'           
	
	data += '<h3>Overall Summary</h3>'
	data += '<table style="width:100%; border-collapse:collapse;">'
	data += '<tr style="background-color:#f8b878; text-align:center">'
	data += '<td class="orange" style="border-left-style:hidden;">S.NO</td>'
	data += '<td class="orange">Items</td>'
	data += '<td class="orange">Budgeted</td>'
	data += '<td class="orange">Actual</td>'
	data += '<td class="orange" style="border-right-style:hidden;">Variance</td></tr>'

	serial_no = 1
	total_budgeted = 0
	total_actual = 0
	total_variance = 0

	for j in project.custom_overall_summary_:
		row_color = "#f8b878" if serial_no % 2 == 0 else "#ffe5b4"

		data += '<tr style="text-align:right; background-color:{};">'.format(row_color)
		data += '<td class="white-border">%s</td>' % serial_no
		data += '<td class="white-border" style="text-align:left">%s</td>' % j.item
		data += '<td class="white-border">%s</td>' % fmt_money(round(j.budgeted, 2), 2)
		data += '<td class="white-border">%s</td>' % fmt_money(round(j.actual, 2), 2)

		diff = round(j.budgeted - j.actual, 2)
		if diff < 0:
			color = "red"
			display_value = fmt_money(diff, 2) 
		elif diff > 0:
			color = "green"
			display_value = "+ " + fmt_money(diff, 2)
		else:
			color = "black"
			display_value = fmt_money(diff, 2)

		data += '<td class="white-border" style="color:{};">{}</td>'.format(color, display_value)
		data += '</tr>'

		# accumulate totals
		total_budgeted += round(j.budgeted, 2)
		total_actual += round(j.actual, 2)
		total_variance += diff

		serial_no += 1

	# Petty Cash Row
	row_color = "#f8b878" if serial_no % 2 == 0 else "#ffe5b4"
	data += '<tr style="text-align:right; background-color:{};">'.format(row_color)
	data += '<td class="white-border">%s</td>' % serial_no
	data += '<td class="white-border" style="text-align:left">Petty Cash</td>'
	data += '<td class="white-border">-</td>'
	petty_cash_val = total_jl_cost(name)
	data += '<td class="white-border">%s</td>' % fmt_money(petty_cash_val, 2)
	data += '<td class="white-border">-</td>'
	data += '</tr>'

	# --- Totals Row ---
	row_color = "#f8b878" if (serial_no+1) % 2 == 0 else "#ffe5b4"
	data += '<tr style="text-align:right; background-color:{}; font-weight:bold">'.format(row_color)
	data += '<td class="white-border" colspan="2" style="text-align:center">Total</td>'
	data += '<td class="white-border">%s</td>' % fmt_money(total_budgeted, 2)
	data += '<td class="white-border">%s</td>' % fmt_money(total_actual + petty_cash_val, 2)  # include petty cash
	data += '<td class="white-border">%s</td>' % fmt_money(total_variance, 2)
	data += '</tr>'

	data += '</table>'




	serial_no_s = 1
	project_materials_sno = 1
	if project.custom_supply_materials:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Supply Materials</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '''
<tr style="background-color:#e35310">
	<td colspan=1 rowspan=2 class="orange" style="border-left-style: hidden;"><br>S.NO</td>
	<td colspan=1 rowspan=2 class="orange"><br>SOW ID</td>
	<td colspan=1 rowspan=2 class="orange"><br>Part Number</td>
	<td colspan=1 rowspan=2 class="orange"><br>Description</td>
	<td colspan=1 rowspan=2 class="orange"><br>Unit</td>
	<td colspan=1 rowspan=2 class="orange"><br>Tot. Qty</td>
	<td class="orange" colspan=3 style="text-align:center">Budgeted</td>
	<td class="orange" colspan=3 style="text-align:center">Actual</td>
	<td class="orange" style="text-align:center; border-right-style: hidden;" colspan=2>Variance</td>
</tr>
<tr style="background-color:#e35310;">
	<td class="orange" style="padding:8px;">Qty</td>
	<td class="orange" style="padding:8px;">Rate</td>
	<td class="orange" style="padding:8px;">Amount</td>
	<td class="orange" style="padding:8px;">Qty</td>
	<td class="orange" style="padding:8px;">Rate</td>
	<td class="orange" style="padding:8px;">Amount</td>
	<td class="orange" style="padding:8px;">Qty</td>
	<td class="orange" style="padding:8px;border-right-style: hidden;">Amount</td>
</tr>
'''

		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_supply_materials:
			del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else 0.00
			variance_amount = round(s.amount, 2) - round(s.del_amount, 2)
			if variance_amount < 0:
				color = "red"
				display_value = fmt_money(variance_amount, 2)
			elif variance_amount > 0:
				color = "green"
				display_value = "+" + fmt_money(variance_amount, 2)
			else:
				color = "black"
				display_value = fmt_money(variance_amount, 2)
			
			data_row_color = "#f8b878" if serial_no_s % 2 == 0 else "#ffe5b4"
			data += '''<tr style="background-color:{};">'''.format(data_row_color)
			data += '''<td class="white-border" style="text-align: right;">%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td>
						<td class="white-border" colspan=1 style="text-align: right;">%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right; font-weight: bold; color:%s;" colspan=1>%s</td>
					</tr>''' % (
						serial_no_s, s.budget_code, s.part_number, s.description, s.unit, 
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
						fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), 
						color, display_value
					)
			serial_no_s += 1
			amt += round(s.amount, 2)
			a_amt += round(s.del_amount, 2)
			v_amt += round(s.amount, 2) - round(s.del_amount, 2)
				
		data += f'''<tr style="font-weight: bold; background-color: #e35310;">
					<td class="white-border text-right" style="color: white;" colspan=6>Total Amount</td> <!-- 7 columns -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(amt, 2), 2)}</td> <!-- 1 column -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(a_amt, 2), 2)}</td> <!-- 3 columns -->
					<td colspan=2 class="white-border" style="text-align:right;color: white;">{fmt_money(round(v_amt, 2), 2)}</td> <!-- 3 columns -->
				<tr>'''
		data += '</table>'
	serial_no_a = 1
	if project.custom_accessories:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Accessories</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '<tr style="background-color:#e35310"><td colspan=1></td><td colspan=4></td><td><b>Budget</b></td><td colspan=3 style="text-align:center"><b>Budgeted</b></td><td colspan=3 style="text-align:center"><b>Actual</b></td><td style="text-align:center" colspan=2><b>Variance</b></td><tr>'
		data += '''
					<tr style="background-color:#D5D8DC;">
						<th padding:8px;">S.NO</th>
						<th padding:8px;">SOW ID</th>
						<th padding:8px;">Part Number</th>
						<th padding:8px;">Description</th>
						<th padding:8px;">Unit</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Rate</th>
						<th padding:8px;">Amount</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Rate</th>
						<th padding:8px;">Amount</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Amount</th>
					</tr>
				'''
		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_accessories:
			del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else "0.00"
			data += '<tr><td>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><tr>' % (
				serial_no_a,s.budget_code, s.part_number, s.description, s.unit, fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
				fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
				fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), fmt_money(round(s.amount, 2) - round(s.del_amount, 2), 2))
			serial_no_a += 1
			amt += round(s.amount, 2)
			a_amt += round(s.del_amount, 2)
			v_amt += round(s.amount, 2) - round(s.del_amount, 2)
				
		data += '<tr style="font-weight: bold;"><td colspan=7>Total Amount</td><td style="text-align:right" colspan=1>%s</td><td style="text-align:right" colspan=2></td><td style="text-align:right" colspan=1>%s</td><td style="text-align:right" colspan=2>%s</td><tr>' % (
			fmt_money(round(amt, 2), 2), fmt_money(round(a_amt, 2), 2), format_value(v_amt))
		data += '</table>'
	serial_no_sb = 1
	if project.custom_subcontract:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Subcontract</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '<tr style="background-color:#e35310"><td colspan=1></td><td colspan=4></td><td><b>Budget</b></td><td colspan=3 style="text-align:center"><b>Budgeted</b></td><td colspan=3 style="text-align:center"><b>Actual</b></td><td style="text-align:center" colspan=2><b>Variance</b></td><tr>'
		data += '''
					<tr style="background-color:#D5D8DC;">
						<th padding:8px;">S.NO</th>
						<th padding:8px;">SOW ID</th>
						<th padding:8px;">Part Number</th>
						<th padding:8px;">Description</th>
						<th padding:8px;">Unit</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Rate</th>
						<th padding:8px;">Amount</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Rate</th>
						<th padding:8px;">Amount</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Amount</th>
					</tr>
				'''
		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_subcontract:
			del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else "0.00"
			data += '<tr><td>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><tr>' % (
				serial_no_sb,s.budget_code, s.part_number, s.description, s.unit, fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
				fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
				fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), fmt_money(round(s.amount, 2) - round(s.del_amount, 2), 2))
			serial_no_sb += 1
			amt += round(s.amount, 2)
			a_amt += round(s.del_amount, 2)
			v_amt += round(s.amount, 2) - round(s.del_amount, 2)
				
		data += '<tr<tr style="font-weight: bold;"><td class="text-center" colspan=7></td><td style="text-align:right" colspan=1>%s</td><td style="text-align:right" colspan=2></td><td style="text-align:right" colspan=1>%s</td><td style="text-align:right" colspan=1></td><td style="text-align:right" colspan=1>%s</td><tr>' % (
			fmt_money(round(amt, 2), 2), fmt_money(round(a_amt, 2), 2), format_value(v_amt))
		data += '</table>'
	serial_no_d = 1
	if project.custom_design:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Design</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '<tr style="background-color:#e35310"><td colspan=1></td><td colspan=4></td><td><b>Budget</b></td><td colspan=3 style="text-align:center"><b>Budgeted</b></td><td colspan=3 style="text-align:center"><b>Actual</b></td><td style="text-align:center" colspan=2><b>Variance</b></td><tr>'
		data += '''
					<tr style="background-color:#D5D8DC;">
						<th padding:8px;">S.NO</th>
						<th padding:8px;">SOW ID</th>
						<th padding:8px;">Part Number</th>
						<th padding:8px;">Description</th>
						<th padding:8px;">Unit</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Rate</th>
						<th padding:8px;">Amount</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Rate</th>
						<th padding:8px;">Amount</th>
						<th padding:8px;">Qty</th>
						<th padding:8px;">Amount</th>
					</tr>
				'''
		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_design:
			del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else "0.00"
			data += '<tr><td>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><td  style="text-align:right" colspan=1>%s</td><tr>' % (
				serial_no_d,s.budget_code, s.part_number, s.description, s.unit, fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
				fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
				fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), fmt_money(round(s.amount, 2) - round(s.del_amount, 2), 2))
			serial_no_d += 1
			amt += round(s.amount, 2)
			a_amt += round(s.del_amount, 2)
			v_amt += round(s.amount, 2) - round(s.del_amount, 2)
				
		data += '<tr style="font-weight: bold;"><td class="text-center" colspan=7></td><td style="text-align:right" colspan=1>%s</td><td style="text-align:right" colspan=2></td><td style="text-align:right" colspan=1>%s</td><td style="text-align:right" colspan=1></td><td style="text-align:right" colspan=1>%s</td><tr>' % (
			fmt_money(round(amt, 2), 2), fmt_money(round(a_amt, 2), 2), format_value(v_amt))
		data += '</table>'
	serial_no_fw = 1
	if project.custom_finishing_work:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Finishing Work</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '''
			<tr style="background-color:#e35310">
				<td colspan=1 rowspan=2 class="orange" style="border-left-style: hidden;"><br>S.NO</td>
				<td colspan=1 rowspan=2 class="orange"><br>SOW ID</td>
				<td colspan=1 rowspan=2 class="orange"><br>Part Number</td>
				<td colspan=1 rowspan=2 class="orange"><br>Description</td>
				<td colspan=1 rowspan=2 class="orange"><br>Unit</td>
				<td colspan=1 rowspan=2 class="orange"><br>Tot. Qty</td>
				<td class="orange" colspan=3 style="text-align:center">Budgeted</td>
				<td class="orange" colspan=3 style="text-align:center">Actual</td>
				<td class="orange" style="text-align:center; border-right-style: hidden;" colspan=2>Variance</td>
			</tr>
			<tr style="background-color:#e35310;">
				<td class="orange" style="padding:8px;">Qty</td>
				<td class="orange" style="padding:8px;">Rate</td>
				<td class="orange" style="padding:8px;">Amount</td>
				<td class="orange" style="padding:8px;">Qty</td>
				<td class="orange" style="padding:8px;">Rate</td>
				<td class="orange" style="padding:8px;">Amount</td>
				<td class="orange" style="padding:8px;">Qty</td>
				<td class="orange" style="padding:8px;border-right-style: hidden;">Amount</td>
			</tr>
			'''
		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_finishing_work:
			del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else "0.00"
			variance_amount = round(s.amount, 2) - round(s.del_amount, 2)
			if variance_amount < 0:
				color = "red"
				display_value = fmt_money(variance_amount, 2)
			elif variance_amount > 0:
				color = "green"
				display_value = "+" + fmt_money(variance_amount, 2)
			else:
				color = "black"
				display_value = fmt_money(variance_amount, 2)
			
			data_row_color = "#f8b878" if serial_no_fw % 2 == 0 else "#ffe5b4"
			data += '''<tr style="background-color:{};">'''.format(data_row_color)
			data += '''<td class="white-border" style="text-align: right;">%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td>
						<td class="white-border" colspan=1 style="text-align: right;">%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right; font-weight: bold; color:%s;" colspan=1>%s</td>
					</tr>''' % (
						serial_no_fw, s.budget_code, s.part_number, s.description, s.unit, 
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
						fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), 
						color, display_value
					)
			serial_no_fw += 1
			amt += round(s.amount, 2)
			a_amt += round(s.del_amount, 2)
			v_amt += round(s.amount, 2) - round(s.del_amount, 2)
		data += f'''<tr style="font-weight: bold; background-color: #e35310;">
					<td class="white-border text-right" style="color: white;" colspan=6>Total Amount</td> <!-- 7 columns -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(amt, 2), 2)}</td> <!-- 1 column -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(a_amt, 2), 2)}</td> <!-- 3 columns -->
					<td colspan=2 class="white-border" style="text-align:right;color: white;">{fmt_money(round(v_amt, 2), 2)}</td> <!-- 3 columns -->
				<tr>'''
		data += '</table>'
	serial_no_t = 1
	if project.custom_tools:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Tools</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '''
			<tr style="background-color:#e35310">
			<td colspan=1 rowspan=2 class="orange" style="border-left-style: hidden;"><br>S.NO</td>
			<td colspan=1 rowspan=2 class="orange"><br>SOW ID</td>
			<td colspan=1 rowspan=2 class="orange"><br>Part Number</td>
			<td colspan=1 rowspan=2 class="orange"><br>Description</td>
			<td colspan=1 rowspan=2 class="orange"><br>Unit</td>
			<td colspan=1 rowspan=2 class="orange"><br>Tot. Qty</td>
			<td class="orange" colspan=3 style="text-align:center">Budgeted</td>
			<td class="orange" colspan=3 style="text-align:center">Actual</td>
			<td class="orange" style="text-align:center; border-right-style: hidden;" colspan=2>Variance</td>
			</tr>
			<tr style="background-color:#e35310;">
			<td class="orange" style="padding:8px;">Qty</td>
			<td class="orange" style="padding:8px;">Rate</td>
			<td class="orange" style="padding:8px;">Amount</td>
			<td class="orange" style="padding:8px;">Qty</td>
			<td class="orange" style="padding:8px;">Rate</td>
			<td class="orange" style="padding:8px;">Amount</td>
			<td class="orange" style="padding:8px;">Qty</td>
			<td class="orange" style="padding:8px;border-right-style: hidden;">Amount</td>
			</tr>
			'''
		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_tools:
			del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else "0.00"
			variance_amount = round(s.amount, 2) - round(s.del_amount, 2)
			if variance_amount < 0:
				color = "red"
				display_value = fmt_money(variance_amount, 2)
			elif variance_amount > 0:
				color = "green"
				display_value = "+" + fmt_money(variance_amount, 2)
			else:
				color = "black"
				display_value = fmt_money(variance_amount, 2)
			
			data_row_color = "#f8b878" if serial_no_t % 2 == 0 else "#ffe5b4"
			data += '''<tr style="background-color:{};">'''.format(data_row_color)
			data += '''<td class="white-border" style="text-align: right;">%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td>
						<td class="white-border" colspan=1 style="text-align: right;">%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right; font-weight: bold; color:%s;" colspan=1>%s</td>
					</tr>''' % (
						serial_no_t, s.budget_code, s.part_number, s.description, s.unit, 
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
						fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), 
						color, display_value
					)
			serial_no_t += 1
			amt += round(s.amount, 2)
			a_amt += round(s.del_amount, 2)
			v_amt += round(s.amount, 2) - round(s.del_amount, 2)
				
		data += f'''<tr style="font-weight: bold; background-color: #e35310;">
					<td class="white-border text-right" style="color: white;" colspan=6>Total Amount</td> <!-- 7 columns -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(amt, 2), 2)}</td> <!-- 1 column -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(a_amt, 2), 2)}</td> <!-- 3 columns -->
					<td colspan=2 class="white-border" style="text-align:right;color: white;">{fmt_money(round(v_amt, 2), 2)}</td> <!-- 3 columns -->
				<tr>'''
		data += '</table>'
	serial_no_fg = 1
	if project.custom_finished_goods:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Finished Goods</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '''
				<tr style="background-color:#e35310">
					<td colspan=1 rowspan=2 class="orange" style="border-left-style: hidden;"><br>S.NO</td>
					<td colspan=1 rowspan=2 class="orange"><br>SOW ID</td>
					<td colspan=1 rowspan=2 class="orange"><br>Part Number</td>
					<td colspan=1 rowspan=2 class="orange"><br>Description</td>
					<td colspan=1 rowspan=2 class="orange"><br>Unit</td>
					<td colspan=1 rowspan=2 class="orange"><br>Tot. Qty</td>
					<td class="orange" colspan=3 style="text-align:center">Budgeted</td>
					<td class="orange" colspan=3 style="text-align:center">Actual</td>
					<td class="orange" style="text-align:center; border-right-style: hidden;" colspan=2>Variance</td>
				</tr>
				<tr style="background-color:#e35310;">
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;">Rate</td>
					<td class="orange" style="padding:8px;">Amount</td>
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;">Rate</td>
					<td class="orange" style="padding:8px;">Amount</td>
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;border-right-style: hidden;">Amount</td>
				</tr>
				'''
		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_finished_goods:
			del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else "0.00"
			variance_amount = round(s.amount, 2) - round(s.del_amount, 2)
			if variance_amount < 0:
				color = "red"
				display_value = fmt_money(variance_amount, 2)
			elif variance_amount > 0:
				color = "green"
				display_value = "+" + fmt_money(variance_amount, 2)
			else:
				color = "black"
				display_value = fmt_money(variance_amount, 2)
			
			data_row_color = "#f8b878" if serial_no_fg % 2 == 0 else "#ffe5b4"
			data += '''<tr style="background-color:{};">'''.format(data_row_color)
			data += '''<td class="white-border" style="text-align: right;">%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td>
						<td class="white-border" colspan=1 style="text-align: right;">%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right; font-weight: bold; color:%s;" colspan=1>%s</td>
					</tr>''' % (
						serial_no_fg, s.budget_code, s.part_number, s.description, s.unit, 
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
						fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), 
						color, display_value
					)
			serial_no_fg += 1
			amt += round(s.amount, 2)
			a_amt += round(s.del_amount, 2)
			v_amt += round(s.amount, 2) - round(s.del_amount, 2)
				
		data += f'''<tr style="font-weight: bold; background-color: #e35310;">
					<td class="white-border text-right" style="color: white;" colspan=6>Total Amount</td> <!-- 7 columns -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(amt, 2), 2)}</td> <!-- 1 column -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(a_amt, 2), 2)}</td> <!-- 3 columns -->
					<td colspan=2 class="white-border" style="text-align:right;color: white;">{fmt_money(round(v_amt, 2), 2)}</td> <!-- 3 columns -->
				<tr>'''
		data += '</table>'
	serial_no_m = 1
	if project.custom_manpower:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Manpower</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '''
					<tr style="background-color:#e35310">
					<td colspan=1 rowspan=2 class="orange" style="border-left-style: hidden;"><br>S.NO</td>
					<td colspan=1 rowspan=2 class="orange"><br>SOW ID</td>
					<td colspan=1 rowspan=2 class="orange"><br>Part Number</td>
					<td colspan=1 rowspan=2 class="orange"><br>Description</td>
					<td colspan=1 rowspan=2 class="orange"><br>Unit</td>
					<td colspan=1 rowspan=2 class="orange"><br>Tot. Qty</td>
					<td class="orange" colspan=3 style="text-align:center">Budgeted</td>
					<td class="orange" colspan=3 style="text-align:center">Actual</td>
					<td class="orange" style="text-align:center; border-right-style: hidden;" colspan=2>Variance</td>
					</tr>
					<tr style="background-color:#e35310;">
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;">Rate</td>
					<td class="orange" style="padding:8px;">Amount</td>
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;">Rate</td>
					<td class="orange" style="padding:8px;">Amount</td>
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;border-right-style: hidden;">Amount</td>
					</tr>
				'''
		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_manpower:
			del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else "0.00"
			variance_amount = round(s.amount, 2) - round(s.del_amount, 2)
			if variance_amount < 0:
				color = "red"
				display_value = fmt_money(variance_amount, 2)
			elif variance_amount > 0:
				color = "green"
				display_value = "+" + fmt_money(variance_amount, 2)
			else:
				color = "black"
				display_value = fmt_money(variance_amount, 2)
			
			data_row_color = "#f8b878" if serial_no_m % 2 == 0 else "#ffe5b4"
			data += '''<tr style="background-color:{};">'''.format(data_row_color)
			data += '''<td class="white-border" style="text-align: right;">%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td>
						<td class="white-border" colspan=1 style="text-align: right;">%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right" colspan=1>%s</td>
						<td class="white-border" style="text-align:right; font-weight: bold; color:%s;" colspan=1>%s</td>
					</tr>''' % (
						serial_no_m, s.budget_code, s.part_number, s.description, s.unit, 
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
						fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
						fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), 
						color, display_value
					)
			serial_no_m += 1
			amt += round(s.amount, 2)
			a_amt = round(s.del_amount, 2)
			v_amt = amt - round(s.del_amount, 2)
				
		data += f'''<tr style="font-weight: bold; background-color: #e35310;">
					<td class="white-border text-right" style="color: white;" colspan=6>Total Amount</td> <!-- 7 columns -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(amt, 2), 2)}</td> <!-- 1 column -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(a_amt, 2), 2)}</td> <!-- 3 columns -->
					<td colspan=2 class="white-border" style="text-align:right;color: white;">{fmt_money(round(v_amt, 2), 2)}</td> <!-- 3 columns -->
				<tr>'''
		data += '</table>'
	serial_no_i = 1
	if project.custom_installation:
		data += '<div class="page-break"></div>'
		data += f'<h4>{project_materials_sno}. Installation</h4>'
		project_materials_sno += 1
		data += '<table class="font-size" border=1px solid black width=100%>'
		data += '''
					<tr style="background-color:#e35310">
					<td colspan=1 rowspan=2 class="orange" style="border-left-style: hidden;"><br>S.NO</td>
					<td colspan=1 rowspan=2 class="orange"><br>SOW ID</td>
					<td colspan=1 rowspan=2 class="orange"><br>Part Number</td>
					<td colspan=1 rowspan=2 class="orange"><br>Description</td>
					<td colspan=1 rowspan=2 class="orange"><br>Unit</td>
					<td colspan=1 rowspan=2 class="orange"><br>Tot. Qty</td>
					<td class="orange" colspan=3 style="text-align:center">Budgeted</td>
					<td class="orange" colspan=3 style="text-align:center">Actual</td>
					<td class="orange" style="text-align:center; border-right-style: hidden;" colspan=2>Variance</td>
					</tr>
					<tr style="background-color:#e35310;">
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;">Rate</td>
					<td class="orange" style="padding:8px;">Amount</td>
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;">Rate</td>
					<td class="orange" style="padding:8px;">Amount</td>
					<td class="orange" style="padding:8px;">Qty</td>
					<td class="orange" style="padding:8px;border-right-style: hidden;">Amount</td>
					</tr>
					'''
		amt = 0
		total_amt = 0
		a_amt = 0
		total_a_amt = 0
		v_amt = 0
		total_v_amt = 0
		for s in project.custom_installation:
			if s.part_number:
				del_rate = fmt_money(round(round(s.del_amount, 2) / s.del_qty, 2)) if s.del_qty else "0.00"
				variance_amount = round(s.amount, 2) - round(s.del_amount, 2)
				if variance_amount < 0:
					color = "red"
					display_value = fmt_money(variance_amount, 2)
				elif variance_amount > 0:
					color = "green"
					display_value = "+" + fmt_money(variance_amount, 2)
				else:
					color = "black"
					display_value = fmt_money(variance_amount, 2)
				
				data_row_color = "#f8b878" if serial_no_i % 2 == 0 else "#ffe5b4"
				data += '''<tr style="background-color:{};">'''.format(data_row_color)
				data += '''<td class="white-border" style="text-align: right;">%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td><td class="white-border" colspan=1>%s</td>
							<td class="white-border" colspan=1 style="text-align: right;">%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
							<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
							<td class="white-border" style="text-align:right" colspan=1>%s</td><td class="white-border" style="text-align:right" colspan=1>%s</td>
							<td class="white-border" style="text-align:right" colspan=1>%s</td>
							<td class="white-border" style="text-align:right" colspan=1>%s</td>
							<td class="white-border" style="text-align:right; font-weight: bold; color:%s;" colspan=1>%s</td>
						</tr>''' % (
							serial_no_i, s.budget_code, s.part_number, s.description, s.unit, 
							fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname),2),2), fmt_money(round(s.qty, 2),2), fmt_money(round(s.rate, 2), 2),
							fmt_money(round(s.amount, 2), 2), fmt_money(round(s.del_qty, 2),2), del_rate, fmt_money(round(s.del_amount, 2), 2),
							fmt_money(round(so_qty(project.budgeting, s.part_number, s.docname) - s.del_qty, 2), 2), 
							color, display_value
						)
				serial_no_i += 1
				amt += round(s.amount, 2)
				a_amt += round(s.del_amount, 2)
				v_amt += round(s.amount, 2) - round(s.del_amount, 2)
				
		data += f'''<tr style="font-weight: bold; background-color: #e35310;">
					<td class="white-border text-center" style="color: white;" colspan=7>Total Amount</td> <!-- 7 columns -->
					<td class="white-border" style="text-align:right; color: white;" colspan=1>{fmt_money(round(amt, 2), 2)}</td> <!-- 1 column -->
					<td class="white-border" style="text-align:right; color: white;" colspan=3>{fmt_money(round(a_amt, 2), 2)}</td> <!-- 3 columns -->
					<td colspan=3 class="white-border" style="text-align:right;color: white;">{fmt_money(round(v_amt, 2), 2)}</td> <!-- 3 columns -->
				<tr>'''
	

	data += '</table>'
	data += '<div class="page-break"></div>'
	data += f'<h4>{project_materials_sno}. Petty Cash</h4>'
	data += other_report(name)
	data += '<div class="page-break"></div>'
	data += f'<h4>Timesheet Details</h4>'
	data += get_timesheet_project(name)
	return data

@frappe.whitelist()
def other_report(project):
	# Prepare the initial HTML table structure with styles
	pro = frappe.get_doc("Project",project)
	

	# Check if no data is returned
	if  pro.custom_other_report:
		table = '''
		
		<table border=1px solid black width=100%>
			<tr style="background-color: #e35310; font-weight: bold;">
				<td class="white-border" style="color: white;">S.NO</td>
				<td class="white-border" style="color: white;">Project Name</td>
				<td class="white-border" style="color: white;">Voucher Name</td>
				<td class="white-border" style="color: white;">Voucher Type</td>
				<td class="white-border" style="color: white;">Expense For</td>
				<td class="white-border" style="color: white;">Amount</td>
			</tr>'''

		serial_no = 1  # Initialize serial number for table rows
		total_amount = 0  # Initialize total amount accumulator

	
	
		for item in pro.custom_other_report:
			# Determine whether to use debit or credit for the amount
			# Accumulate total amount
			total_amount += item.amount
		
			jl_color = "#ffe5b4" if serial_no % 2 == 1 else "#f8b878"
			# Populate table rows with data
			table += f'''
				<tr style="background-color: {jl_color};">
					<td style="text-align: right;" class="white-border">{serial_no}</td>
					<td style="" class="white-border">{item.project_name}</td>
					<td style="" class="white-border">{item.voucher_name}</td> 
					<td style="" class="white-border">{item.voucher_type}</td>
					<td style="" class="white-border">{item.expense_for}</td>
					<td style="text-align: right;" class="white-border">{fmt_money(round(item.amount, 2),2)}</td> 
				</tr>'''
			serial_no += 1

		# Add a final row for the overall total
		table += f'''
			<tr style="background-color: #e35310;">
				<td colspan="5" class="white-border" style="font-weight: bold; text-align: right; color: white;">Total Amount</td>
				<td style="font-weight: bold; text-align: right; color: white;" class="white-border">{fmt_money(round(total_amount, 2), 2)}</td>
			</tr>'''

	# Close the table body and table tags
		table += '''
		</table>'''

	# Return the complete HTML table
 
		return table
	else:
		return ''

@frappe.whitelist()
def get_timesheet_project(name):
	project_pos = frappe.db.sql("""
		SELECT
			SUM(`tabTimesheet Detail`.billing_hours) AS hours,
			SUM(`tabTimesheet Detail`.costing_amount) AS cost_amount,
			`tabTimesheet Detail`.project,
			`tabTimesheet Detail`.project_name,
			`tabTimesheet`.start_date,
			`tabTimesheet`.employee_name,
			`tabTimesheet`.employee
		FROM
			`tabTimesheet`
		LEFT JOIN
			`tabTimesheet Detail`
		ON
			`tabTimesheet`.name = `tabTimesheet Detail`.parent
		LEFT JOIN
			`tabProject`
		ON
			`tabTimesheet Detail`.project = `tabProject`.name
		WHERE
			`tabTimesheet`.docstatus != 2
			AND `tabTimesheet Detail`.project = %s
		Group by 
			`tabTimesheet`.employee					 
		ORDER BY
			`tabTimesheet Detail`.project, `tabTimesheet`.employee_name, `tabTimesheet`.start_date
		
	""", (name), as_dict=True)
	data = "<table class='table table-bordered'>"
	data += """<tr>
			<td style='text-align:center; color: white; border: 1px solid white;background-color:#e35310;font-weight:bold'>Sl.No.</td>
			<td style='text-align:center; color: white; border: 1px solid white;background-color:#e35310;font-weight:bold'>Employee</td>
			<td style='text-align:center; color: white; border: 1px solid white;background-color:#e35310;font-weight:bold'>Project Name</td>
			<td style='text-align:center; color: white; border: 1px solid white;background-color:#e35310;font-weight:bold'>Hours</td>
			<td style='text-align:center; color: white; border: 1px solid white;background-color:#e35310;font-weight:bold'>Total Cost</td>
			</tr>"""
	s_no = 1
	total_cost = 0
	total_hours = 0
	for i in project_pos:
		t_row_color = "#ffe5b4" if s_no % 2 == 0 else "#f8b878"
		data += f"""<tr>
			<td style='text-align:right;border: 1px solid white;background-color:{t_row_color};'>{s_no}</td>
			<td style='text-align:left;border: 1px solid white;background-color:{t_row_color};'>{i.employee} - {i.employee_name}</td>
			<td style='text-align:left;border: 1px solid white;background-color:{t_row_color};'>{i.project_name}</td>
			<td style='text-align:right;border: 1px solid white;background-color:{t_row_color};'>{fmt_money(round(i.hours,2),2)}</td>
			<td style='text-align:right;border: 1px solid white;background-color:{t_row_color};'>{fmt_money(round(i.cost_amount, 2), 2)}</td>
			</tr>"""
		total_cost += i.cost_amount
		total_hours += i.hours
		s_no += 1
	data += f"""<tr>
			<td colspan=3 style='text-align:right; color: white; border: 1px solid white;background-color:#e35310;font-weight:bold'>Total</td>
			<td style='text-align:right; color: white; border: 1px solid white;background-color:#e35310;font-weight:bold'>{fmt_money(round(total_hours, 2), 2)}</td>
			<td style='text-align:right; color: white; border: 1px solid white;background-color:#e35310;font-weight:bold'>{fmt_money(round(total_cost, 2), 2)}</td>
			</tr>"""
	data += "</table>"
	return data

@frappe.whitelist()
def so_qty(project_budget, item, docname):
	doc = frappe.get_doc("Project Budget", project_budget)
	for pb in doc.item_table:
		if pb.item.upper() == item.upper() and pb.docname == docname:
			return pb.qty

@frappe.whitelist()
def total_dnwip_cost(project):
	sales_order = frappe.db.get_value("Sales Order", {"project": project}, "name")
	pb_name = frappe.db.get_value("Project", project, "budgeting")
	pb = frappe.get_doc("Project Budget", pb_name)

	# Fetch all relevant Delivery Note WIP names in bulk
	dn_wip_list = frappe.get_all(
		"Delivery Note WIP",
		filters={"sales_order": sales_order, "is_return": 0, "docstatus": 1},
		pluck="name"
	)

	if not dn_wip_list:
		return 0

	# Fetch all relevant Delivery Note WIP items in bulk
	dn_wip_items = frappe.db.sql("""
		SELECT dni.parent AS dn_wip_name, dni.item_code, dni.qty, dni.custom_against_pbsow
		FROM `tabDelivery Note Item` dni
		WHERE dni.parent IN %(dn_wip_list)s
	""", {"dn_wip_list": dn_wip_list}, as_dict=True)

	# Group quantities by (dn_wip_name, item_code, custom_against_pbsow)
	item_qty_map = {}
	for i in dn_wip_items:
		key = (i.dn_wip_name, i.item_code, i.custom_against_pbsow)
		item_qty_map[key] = item_qty_map.get(key, 0) + i.qty

	# Fetch Stock Entry rates in bulk
	stock_entry_data = frappe.db.sql("""
		SELECT se.reference_number, sei.item_code, sei.basic_rate, sei.qty
		FROM `tabStock Entry` se
		JOIN `tabStock Entry Detail` sei ON se.name = sei.parent
		WHERE se.stock_entry_type = 'Material Transfer'
		AND se.docstatus = 1
		AND se.reference_number IN %(dn_wip_list)s
	""", {"dn_wip_list": dn_wip_list}, as_dict=True)

	# Store stock rates in a dictionary with weighted rate calculation
	stock_entries = {}
	for entry in stock_entry_data:
		key = (entry.reference_number, entry.item_code)
		if key in stock_entries:
			stock_entries[key]['total_value'] += entry.basic_rate * entry.qty
			stock_entries[key]['total_qty'] += entry.qty
		else:
			stock_entries[key] = {'total_value': entry.basic_rate * entry.qty, 'total_qty': entry.qty}

	# Calculate the correct weighted average rate
	stock_rates = {}
	for key, values in stock_entries.items():
		stock_rates[key] = values['total_value'] / values['total_qty'] if values['total_qty'] > 0 else 0

	amount = 0

	# Calculate total amount using correct stock rates
	for child in pb.item_table:
		total_item_qty = 0
		weighted_rate_sum = 0
		total_rate_qty = 0  # Used for calculating weighted avg

		for dn_wip in dn_wip_list:
			key = (dn_wip, child.item, child.docname)
			if key in item_qty_map:
				item_qty = item_qty_map[key]
				total_item_qty += item_qty

				if (dn_wip, child.item) in stock_rates:
					rate = stock_rates[(dn_wip, child.item)]
					weighted_rate_sum += rate * item_qty
					total_rate_qty += item_qty

		# Compute weighted average rate
		final_rate = weighted_rate_sum / total_rate_qty if total_rate_qty > 0 else 0

		amount += final_rate * total_item_qty

	return amount


def find_dn_qty_for_item(project, item, docname = None):
	data = {}
	project_name = project
	if docname:
		dn_data = frappe.db.sql(
			"""
			SELECT 
				dni.item_code, 
				dni.qty,
				(
					SELECT sle.valuation_rate 
					FROM `tabStock Ledger Entry` sle 
					WHERE sle.item_code = dni.item_code 
					AND sle.voucher_no = dn.name 
					ORDER BY sle.creation DESC 
					LIMIT 1
				) AS valuation_rate
			FROM `tabDelivery Note` dn
			LEFT JOIN `tabDelivery Note Item` dni 
				ON dn.name = dni.parent
			WHERE dni.item_code = %s 
			AND dni.custom_docname = %s
			AND dn.project = %s 
			""",
			(item, docname, project_name),
			as_dict=True
		) or []
	else:
		dn_data = frappe.db.sql(
			"""
			SELECT 
				dni.item_code, 
				dni.qty,
				(
					SELECT sle.valuation_rate 
					FROM `tabStock Ledger Entry` sle 
					WHERE sle.item_code = dni.item_code 
					AND sle.voucher_no = dn.name 
					ORDER BY sle.creation DESC 
					LIMIT 1
				) AS valuation_rate
			FROM `tabDelivery Note` dn
			LEFT JOIN `tabDelivery Note Item` dni 
				ON dn.name = dni.parent
			WHERE dni.item_code = %s 
			AND dn.project = %s 
			""",
			(item, project_name),
			as_dict=True
		) or []
		
	# Process fetched data
	for i in dn_data:
		item_code = i.item_code
		qty = i.qty or 0
		valuation_rate = i.valuation_rate or 0
		amount = qty * valuation_rate

		# Store data in dictionary
		if item_code in data:
			data[item_code]["total_qty"] += qty
			data[item_code]["total_amount"] += amount
		else:
			data[item_code] = {
				"total_qty": qty,
				"total_amount": amount
			}

	# Handle case when no data is found
	if item not in data:
		return 0, 0  # Return default values if the item is not found

	return data[item]["total_qty"], data[item]["total_amount"]




@frappe.whitelist()
def process_mep_material_docname(category,project_doc, project_budget, project_name):
	total_material_cost = 0
	budget = 0 
	"""Process generic category calculations."""
	for item in category["table"]:
		dn, dn_amount = find_dn_qty_for_item(project_name, item.item, item.docname)
		dn_wip,dn_wip_amount = find_dn_wip_qty_for_item(project_budget.sales_order, item.item, item.docname) or 0
		if dn and dn_wip:
			delivered_qty = dn + dn_wip
			delivered_amount = (dn_amount + dn_wip_amount) 
		elif dn:
			delivered_qty = dn
			delivered_amount = dn_amount
		elif dn_wip:
			delivered_qty = dn_wip
			delivered_amount = dn_wip_amount
		else:
			delivered_qty = 0
			delivered_amount = 0
		cost = get_cost_from_pbsow(item.item, item.msow, item.unit_price, project_doc) or 0
		project_doc.append(category["custom_field"], {
			'budget_code': item.msow,
			'part_number': item.item,
			'description': item.description,
			'unit': item.unit,
			'qty': delivered_qty,
			'rate': cost,
			'amount': delivered_qty * cost,
			'del_qty': delivered_qty,
			'del_amount': delivered_amount,
			'bal_qty': 0,
			'amount_variance': (delivered_qty * cost) - delivered_amount,
			'docname': item.docname,
		})
		total_material_cost+=delivered_amount
		budget += delivered_qty * cost
	return total_material_cost,budget


@frappe.whitelist()
def process_mep_material(category, project_doc, project_budget, project_name):
	total_material_cost = 0
	budget = 0 
	"""Process generic category calculations."""
	for item in category["table"]:
		dn, dn_amount = find_dn_qty_for_item(project_name, item.item)
		dn_wip,dn_wip_amount = find_dn_wip_qty_for_item(project_budget.sales_order, item.item, item.docname) or 0
		if dn and dn_wip:
			delivered_qty = dn + dn_wip
			delivered_amount = (dn_amount + dn_wip_amount) 
		elif dn:
			delivered_qty = dn
			delivered_amount = dn_amount
		elif dn_wip:
			delivered_qty = dn_wip
			delivered_amount = dn_wip_amount
		else:
			delivered_qty = 0
			delivered_amount = 0
		cost = get_cost_from_pbsow(item.item, item.msow, item.unit_price, project_doc) or 0
		project_doc.append(category["custom_field"], {
			'budget_code': item.msow,
			'part_number': item.item,
			'description': item.description,
			'unit': item.unit,
			'qty': delivered_qty,
			'rate': cost,
			'amount': delivered_qty * cost,
			'del_qty': delivered_qty,
			'del_amount': delivered_amount,
			'bal_qty': 0,
			'amount_variance': (delivered_qty * cost) - delivered_amount,
			'docname': item.docname,
		})
		total_material_cost+=delivered_amount
		budget += delivered_qty * cost
	return total_material_cost,budget

@frappe.whitelist()
def get_cost_from_pbsow(item, msow, unit_price, project_doc):
	project_budget = frappe.get_doc("Project Budget", project_doc.budgeting)
	pb_sow = frappe.get_doc("PB SOW", {"project_budget": project_budget.name, "sales_order": project_budget.sales_order})
	if pb_sow.company == "MEP DIVISION - ELECTRA":
		category = pb_sow.mep_materials
	else:
		category = pb_sow.materials
	for row in category:
		if row.item == item and row.msow == msow and row.unit_price == unit_price:
			return row.cost or 0

@frappe.whitelist()
def format_value(val):
	"""Format value with color and prefix for positive values."""
	if val < 0:
		color = "red"
		display_value = fmt_money(round(val, 2), 2)
	elif val > 0:
		color = "green"
		display_value = "+ " + fmt_money(round(val, 2), 2)
	else:
		color = "black"
		display_value = fmt_money(round(val, 2), 2)
	
	return '<td colspan=3 style="text-align:right; color:{};">{}</td>'.format(color, display_value)


@frappe.whitelist()
def update_project_values_name():
	name = 'ENG-PRO-2024-00112'
	project_budget, p_name = frappe.db.get_value(
		"Project", {'name': name}, ['budgeting', 'project_name']
	)
	grand = frappe.db.get_value("Sales Order", {'project': name, 'docstatus': 1}, 'grand_total')
	sales_in = frappe.db.sql(
		""" SELECT SUM(custom_total_invoice_amount - discount_amount) as total FROM `tabSales Invoice` WHERE project = %s and docstatus = 1""",
		(name,),
		as_dict=True)[0]
	if not sales_in["total"]:
		sales_in["total"] = 0
	bal = grand - sales_in["total"]
	revenue = frappe.db.sql(
		""" SELECT SUM(paid_amount) as amt FROM `tabPayment Entry` WHERE project = %s and docstatus=1""",
		(name,),
		as_dict=True)[0]
	if not revenue["amt"]:
		revenue["amt"] = 0
	out = sales_in["total"] - revenue["amt"]
	cost_till_date = project_cost_till_date(name)
	# cost_till_date = 0

	gr_pr = sales_in["total"] - cost_till_date
	if sales_in["total"]>0:
		per_gp = (gr_pr / sales_in["total"] or 0) * 100
	else:
		per_gp=0
	
	pb = frappe.get_doc("Project Budget", project_budget)		
	categories = [
		{"name": "Supply Materials", "table": pb.materials, "custom_field": "custom_supply_materials"},
		{"name": "Accessories", "table": pb.bolts_accessories, "custom_field": "custom_accessories"},
		{"name": "Subcontract", "table": pb.others, "custom_field": "custom_subcontract"},
		{"name": "Design", "table": pb.design, "custom_field": "custom_design"},
		{"name": "Finishing Work", "table": pb.finishing_work, "custom_field": "custom_finishing_work"},
		{"name": "Tools / Equipment / Transport / Others", "table": pb.heavy_equipments, "custom_field": "custom_tools"},
		{"name": "Finished Goods", "table": pb.finished_goods, "custom_field": "custom_finished_goods"},
		{"name": "Manpower", "table": pb.manpower, "custom_field": "custom_manpower"},
		{"name": "Installation", "table": pb.installation, "custom_field": "custom_installation"},
	]
	frappe.publish_realtime(
		"project_update_progress",
		{"progress": 1.1, "description": f"Processing {1.1}%..."},
		user=frappe.session.user
	)
	project_doc=frappe.get_doc("Project",name)
	project_doc.custom_order_value=grand
	project_doc.custom_invoice_value_till_date=sales_in["total"]
	
	project_doc.custom_cost_till_date=cost_till_date
	project_doc.custom_gross_profit=gr_pr
	project_doc.custom_gross_profit_per=per_gp
	project_doc.custom_balance_to_invoice=bal
	project_doc.custom_total_collection=revenue["amt"]
	project_doc.custom_os_receipts=out
	


	# Reset custom fields in the project
	for field in [
		'custom_overall_summary_', 'custom_supply_materials', 'custom_accessories',
		'custom_subcontract', 'custom_design', 'custom_finishing_work',
		'custom_tools', 'custom_finished_goods', 'custom_manpower', 'custom_installation','custom_other_report'
	]:
		project_doc.set(field, [])
	total_material_cost=0
	total_operational_cost=0
	# Emit real-time progress updates
	total_steps = len(categories)
	for index, category in enumerate(categories):
		progress = round(((index + 1) / total_steps) * 100, 2)
		frappe.publish_realtime(
			"project_update_progress",
			{"progress": progress, "description": f"Processing {progress}%..."},
			user=frappe.session.user
		)

		if not category["table"]:
			continue

		if category["name"] == "Manpower":
			total_operational_cost,amt = process_manpower(category, project_doc, pb, name)
			project_doc.append('custom_overall_summary_', {
				'item': category["name"],
				'budgeted': amt,
				'actual': total_operational_cost
			})
		elif category["name"] == "Installation":
			total_operational_cost,amt = process_installation(category, project_doc, pb, name)
			project_doc.append('custom_overall_summary_', {
				'item': category["name"],
				'budgeted': amt,
				'actual': total_operational_cost
			})
		elif category["name"] == "Supply Materials":
			if pb.docname_updated_in_dn == 1:
				if pb.company == "MEP DIVISION - ELECTRA":
					total_material_cost,amt = process_mep_material_docname(category, project_doc, pb, name)
					project_doc.append('custom_overall_summary_', {
						'item': category["name"],
						'budgeted': amt,
						'actual': total_material_cost
					})
				else:
					total_material_cost,amt = process_category_docname(category, project_doc, pb, name)
					project_doc.append('custom_overall_summary_', {
						'item': category["name"],
						'budgeted': amt,
						'actual': total_material_cost
					})
			else:
				if pb.company == "MEP DIVISION - ELECTRA":
					total_material_cost,amt = process_mep_material(category, project_doc, pb, name)
					project_doc.append('custom_overall_summary_', {
						'item': category["name"],
						'budgeted': amt,
						'actual': total_material_cost
					})
				else:
					total_material_cost,amt = process_category(category, project_doc, pb, name)
					project_doc.append('custom_overall_summary_', {
						'item': category["name"],
						'budgeted': amt,
						'actual': total_material_cost
					})
		else:
			if pb.docname_updated_in_dn == 1:
				total_material_cost,amt = process_category_docname(category, project_doc, pb, name)
				project_doc.append('custom_overall_summary_', {
					'item': category["name"],
					'budgeted': amt,
					'actual': total_material_cost
				})
			else:
				total_material_cost,amt = process_category(category, project_doc, pb, name)
				project_doc.append('custom_overall_summary_', {
					'item': category["name"],
					'budgeted': amt,
					'actual': total_material_cost
				})
	# # Handle other expenses (if applicable)
	project_doc.custom_material_cost=total_material_cost
	project_doc.custom_operational_cost=total_operational_cost+process_other_expenses(name)
	project_doc.save(ignore_permissions=True)
	frappe.publish_realtime(
		"project_update_progress",
		{"progress": 100, "description": "Calculation complete!"},
		user=frappe.session.user
	)
	return True
