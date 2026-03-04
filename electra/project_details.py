import frappe
from frappe import _
from babel.numbers import format_decimal
from frappe.utils import cstr, add_days, date_diff, getdate, format_date
import frappe
from frappe.utils import fmt_money
from frappe import _
from frappe.utils import flt
from datetime import date
# Budgeted vs Actual Report
# Method to calculate the Prject's Cost Till Date

@frappe.whitelist()
def cost_till_date(name):
	today = date.today()
	current_year_start = f"{today.year}-01-01"
	current_year_end = f"{today.year}-12-31"
	previous_year_start = f"{today.year - 1}-01-01"
	previous_year_end = f"{today.year - 1}-12-31"
	so = frappe.get_value("Sales Order", {"project": name}, ["name"])
	total_cost = get_dn_from_stock_ledger(so, current_year_start, current_year_end) + get_dn_from_stock_ledger(so, previous_year_start, previous_year_end)
	return total_cost

def get_dn_from_stock_ledger(so, from_date, to_date):
	dn_wip = frappe.get_all("Delivery Note WIP", {"sales_order": so, "docstatus": 1, "posting_date": ["between", [from_date, to_date]]})
	total = 0
	wip_count = 0
	for dnwip in dn_wip:
		# if frappe.db.exists("Stock Entry", {"reference_number": dnwip.name}):
		se = frappe.get_doc("Stock Entry", {"reference_number": dnwip.name})
		wip_count += 1
		for i in se.items:
			total += i.qty * i.valuation_rate
   
	delivery_note = frappe.db.get_all('Delivery Note Item', {'against_sales_order': so},['parent'], distinct=True)
 
	for dn in delivery_note:
		d_note = frappe.db.get_value("Delivery Note", {"name": dn['parent'], "docstatus": 1, "posting_date": ["between", [from_date, to_date]]}, ["name"])
		
		if d_note:
			stock_entries = frappe.get_all("Stock Ledger Entry", filters={"voucher_no": d_note}, fields=["actual_qty", "valuation_rate"])
			for se in stock_entries:
				total += -(se['actual_qty']) * se['valuation_rate']

	return total

@frappe.whitelist()
def project_cost_till_date(name, from_date=None, to_date=None):
	project = name
	total = (total_dn_cost(project, from_date, to_date) + 
			 total_dnwip_cost(project, from_date, to_date) + 
			 total_jl_cost(project, from_date, to_date) + 
			 total_cost_by_timesheet(project, from_date, to_date))
	return total

def total_dn_cost(project, from_date, to_date):
	if from_date and to_date:
		delivery_note = frappe.db.sql("""
			SELECT SUM(grand_total) AS cost 
			FROM `tabDelivery Note` 
			WHERE project = %s AND docstatus = 1 AND posting_date BETWEEN %s AND %s
			GROUP BY project
		""", (project,from_date,to_date), as_dict=True)
	else:
		delivery_note = frappe.db.sql("""
			SELECT SUM(grand_total) AS cost 
			FROM `tabDelivery Note` 
			WHERE project = %s AND docstatus = 1 
			GROUP BY project
		""", (project,), as_dict=True)
	return round(delivery_note[0].cost, 2) if delivery_note else 0

def total_dnwip_cost(project, from_date, to_date):
	if from_date and to_date:
		sales_order = frappe.db.get_value("Sales Order", {"project": project}, "name")
		pb_name = frappe.db.get_value("Project", project, "budgeting")
		pb = frappe.get_doc("Project Budget", pb_name)
		amount = 0
		for child in pb.item_table:
			dn_wip_list = frappe.get_all("Delivery Note WIP", {"sales_order": sales_order, "is_return": 0, "posting_date": ["Between", [from_date, to_date]]})
			for dn_wip in dn_wip_list:
				stock_entry_exist = frappe.db.exists("Stock Entry", {"stock_entry_type": "Material Transfer", "reference_number": dn_wip.name, "docstatus": 1})
				if stock_entry_exist:
					se = frappe.get_doc("Stock Entry", {"stock_entry_type": "Material Transfer", "reference_number": dn_wip.name, "docstatus": 1})
					for row in se.items:
						if row.item_code == child.item:
							amount += row.qty * child.unit_price
		return amount or 0
		
	else:
		sales_order = frappe.db.get_value("Sales Order", {"project": project}, "name")
		
		pb_name = frappe.db.get_value("Project", project, "budgeting")
		pb = frappe.get_doc("Project Budget", pb_name)
		amount = 0
		for child in pb.item_table:
			dn_wip_list = frappe.get_all("Delivery Note WIP", {"sales_order": sales_order, "is_return": 0})
			for dn_wip in dn_wip_list:
				stock_entry_exist = frappe.db.exists("Stock Entry", {"stock_entry_type": "Material Transfer", "reference_number": dn_wip.name, "docstatus": 1})
				if stock_entry_exist:
					se = frappe.get_doc("Stock Entry", {"stock_entry_type": "Material Transfer", "reference_number": dn_wip.name, "docstatus": 1})
					for row in se.items:
						if row.item_code == child.item:
							amount += row.qty * child.unit_price
		return amount or 0

def total_jl_cost(project, from_date=None, to_date=None):
	if from_date and to_date:
		journal_entry = frappe.db.sql("""
			SELECT SUM(c.debit_in_account_currency) AS cost 
			FROM `tabJournal Entry` jl 
			INNER JOIN `tabJournal Entry Account` c ON c.parent = jl.name 
			WHERE c.project = %s AND jl.docstatus = 1 AND posting_date BETWEEN %s AND %s
			GROUP BY c.project
		""", (project,from_date,to_date), as_dict=True)
	else:
		journal_entry = frappe.db.sql("""
			SELECT SUM(c.debit_in_account_currency) AS cost 
			FROM `tabJournal Entry` jl 
			INNER JOIN `tabJournal Entry Account` c ON c.parent = jl.name 
			WHERE c.project = %s AND jl.docstatus = 1 
			GROUP BY c.project
		""", (project,), as_dict=True)
	return round(journal_entry[0].cost, 2) if journal_entry else 0 

def total_cost_by_timesheet(project, from_date, to_date):
	if from_date and to_date:
		timesheet = frappe.db.sql("""
		SELECT SUM(c.costing_amount) AS cost 
		FROM `tabTimesheet` p 
		INNER JOIN `tabTimesheet Detail` c ON c.parent = p.name 
		WHERE c.project = %s AND p.docstatus = 1 AND start_date BETWEEN %s AND %s
		GROUP BY c.project
	""", (project,from_date,to_date), as_dict=True)
	else:
		timesheet = frappe.db.sql("""
			SELECT SUM(c.costing_amount) AS cost 
			FROM `tabTimesheet` p 
			INNER JOIN `tabTimesheet Detail` c ON c.parent = p.name 
			WHERE c.project = %s AND p.docstatus = 1 
			GROUP BY c.project
		""", (project,), as_dict=True)
	return round(timesheet[0].cost, 2) if timesheet else 0


# PROJECT Overview

@frappe.whitelist()
def overview_report(overview):
	report_data = []
	total_amount_expense = 0  # Initialize total cost
	other_expenses = 0
	total_expense = 0
	expense = 0
	total_income = 0  # Rename 'total' to 'total_income' for clarity

	# Calculate costs from functions
	cost = project_cost_till_date(overview)  # Material and installation cost
	other = other_report_total(overview)  # Other expenses

	# Fetch the project details
	projects = frappe.db.get_all('Project', filters={'docstatus': ['!=', 2], 'name': overview}, fields=["*"])

	for project in projects:
		advance_received = 0
		advance_adjusted_amount = 0
		retention_amount = 0
		total_amount_received = 0

		# Fetch advance invoices
		advance_invoices = frappe.db.get_all('Advance Invoice', filters={'docstatus': ['!=', 2], 'project': project.name}, fields=["advance_amount", 'name'])
		for invoice in advance_invoices:
			advance_received += invoice.advance_amount

		# Fetch sales invoices
		sales_invoices = frappe.db.get_all('Sales Invoice', filters={'docstatus': ['!=', 2], 'project': project.name}, fields=["*"])
		for sales_invoice in sales_invoices:
			sales_invoice_doc = frappe.get_doc('Sales Invoice', sales_invoice.name)
			advance_adjusted_amount += sales_invoice_doc.adv_amount or 0
			retention_amount += sales_invoice_doc.ret_amount or 0
			total_amount_received += sales_invoice_doc.outstanding_amount or 0

		# Accumulate expenses
		total_amount_expense += int(cost)
		other_expenses += other

		# Calculate total income
		total_income += advance_received + advance_adjusted_amount + retention_amount + total_amount_received

		# Append project data to report_data
		report_data.append({
			'project_name': project.name,
			'advance_received': round(advance_received, 2),
			'adv_amount': round(advance_adjusted_amount, 2),
			'ret_amount': round(retention_amount, 2),
			'outstanding_amount': round(total_amount_received, 2),
			'total': round(cost, 2),
			'total_amount': round(other, 2),
		})

	# Calculate total and net expenses
	total_expense = total_amount_expense + other_expenses
	expense = total_income - total_expense   # "Expense - Income" calculation

	# CSS for styling
	css_styles = """
	<style>
		.container {
			display: flex;
			flex-wrap: wrap;
		}
		.report-overview, .Other-Expense, .Amount-to-be-invoiced {
			box-sizing: border-box;
			padding: 60px;
			margin: 20px 0;
			background-color: #f9f9f9;
			border: 3px solid #ddd;
		}
		.table-responsive table {
			width: 100%;
			border-collapse: collapse;
		}
		.table-responsive table, th, td {
			border: 2px solid #ddd;
		}
		th, td {
			padding: 15px;
			text-align: left;
		}
		th {
			background-color: #FFA500;
			color: white;
		}
		@media screen and (max-width: 800px) {
			.report-overview, .Other-Expense, .Amount-to-be-invoiced {
				padding: 30px;
			}
		}
	</style>
	"""

	# Project Overview Section HTML
	html_output = """
	<div class="report-overview col-4">
		<h2 style="color: black; font-weight: bold;">Project Overview Report</h2>
		<p><strong>Total Advance Received:</strong> {total_advance_received}</p>
		<p><strong>Total Amount Adjusted:</strong> {total_adjusted_amount}</p>
		<p><strong>Total Retention Amount:</strong> {total_retention_amount}</p>
		<p><strong>Total Amount Received:</strong> {total_received_amount}</p><br><br>
		<p><strong>Total Income:</strong> {total_income}</p>
	</div>
	""".format(
		total_advance_received=round(sum(row['advance_received'] for row in report_data), 2),
		total_adjusted_amount=round(sum(row['adv_amount'] for row in report_data), 2),
		total_retention_amount=round(sum(row['ret_amount'] for row in report_data), 2),
		total_received_amount=round(sum(row['outstanding_amount'] for row in report_data), 2),
		total_income=round(total_income, 2)
	)

	# Overall Expense Section HTML
	html_expense = """
	<div class="Other-Expense col-4 ml-auto">
		<h2 style="color: black; font-weight: bold;">Overall Expense</h2>
		<p><strong>Total Material & Installation:</strong> {total_amount_expense}</p>
		<p><strong>Total Other Expenses:</strong> {other_expenses}</p><br><br>
		<p><strong style="background-color: white; color: black;">Total Expense:</strong> {total_expense}</p>
	</div>
	""".format(
		total_amount_expense=round(total_amount_expense, 2),
		other_expenses=round(other_expenses, 2),
		total_expense=round(total_expense, 2)
	)

	# Amount to be invoiced section
	html_invoice = """
	<div class="Amount-to-be-invoiced col-4 ml-auto">
		<h2 style="color: black; font-weight: bold;">Amount to be Invoiced :</h2>
		<p><strong style="background-color: white; color: black; text-align: center;">Total:</strong> {expense}</p>
	</div>
	""".format(expense=round(expense, 2))

	# Combine all sections into the final HTML output
	return css_styles + "<div class='container'>" + html_output + html_expense + html_invoice + "</div>"



# Project Module Code
@frappe.whitelist()
def material_report(project_name):
	# Begin building the HTML table with inline CSS for responsiveness
	table = '''<style>
		/* Bootstrap styles for responsiveness */
		.material-report-table {
			width: 100%;
			border-collapse: collapse;
			margin: 20px 0;
			font-size: 16px;
		}

		.material-report-table th, .material-report-table td {
			padding: 10px;
			text-align: left;
			border: 1px solid #ddd;
		}

		/* Header styles */
		.material-report-table th {
			background-color: orange; /* Set header background to orange */
			color: white; /* White text */
		}

		/* Row styles */
		.material-report-table tr:nth-child(even) {
			background-color: #f2f2f2; /* Light gray for even rows */
		}

		/* Hover effect for rows */
		.material-report-table tr:hover {
			background-color: #ddd; /* Darker gray on hover */
		}

		/* Ensure table contents are centered */
		.material-report-table td {
			text-align: center; /* Center-align table data */
		}
	</style>
	<table class="table table-bordered table-striped material-report-table">
		<thead>
			<tr>
				<th>S.NO</th>
				<th>Project Budget Name</th>
				<th>Part Number</th>
				<th>Description</th>
				<th>Quantity</th>
				<th>Unit</th>
				<th>Rate</th>
				<th>Amount</th>
			</tr>
		</thead>
		<tbody>'''

	# Fetch budget items relevant to the specific project
	budget_items = frappe.db.sql(""" 
		SELECT p.name AS project_name, pb.name AS budget_name, pbi.item, 
			   pbi.qty, pbi.unit, pbi.rate_with_overheads, pbi.amount_with_overheads, pbi.item_name
		FROM `tabProject` p
		JOIN `tabProject Budget` pb ON p.budgeting = pb.name
		JOIN `tabProject Budget Items` pbi ON pbi.parent = pb.name
		WHERE p.budgeting IS NOT NULL  -- Ensure budgeting field is set
		AND p.name = %s  -- Filter by project name
	""", (project_name,), as_dict=True)

	# Check if budget items exist
	if not budget_items:
		table += f'<tr><td colspan="8" style="text-align:center;">No budget items for this project</td></tr>'
	else:
		# Iterate over each budget item and append data to the table
		for index, item in enumerate(budget_items, start=1):
			table += f'''
				<tr>
					<td>{index}</td>
					<td>{item['budget_name']}</td>
					<td>{item['item']}</td>
					<td>{item['item_name']}</td>
					<td>{round(item['qty'])}</td>
					<td>{item['unit']}</td>
					<td>{round(item['rate_with_overheads'], 2)}</td>
					<td>{round(item['amount_with_overheads'], 2)}</td>
				</tr>'''

	# Close the table
	table += '</tbody></table>'

	# Return the generated HTML table
	return table


 # Other Expense Project
@frappe.whitelist()
def other_report(project):
	# Prepare the initial HTML table structure with styles
	table = '''<style>
		/* Bootstrap styles for responsiveness */
		.material-report-table {
			width: 100%;
			border-collapse: collapse;
			margin: 20px 0;
			font-size: 16px;
		}

		.material-report-table th, .material-report-table td {
			padding: 10px;
			text-align: left;
			border: 1px solid #ddd;
		}

		/* Header styles */
		.material-report-table th {
			background-color: orange; /* Set header background to orange */
			color: white; /* White text */
		}

		/* Row styles */
		.material-report-table tr:nth-child(even) {
			background-color: #f2f2f2; /* Light gray for even rows */
		}

		/* Hover effect for rows */
		.material-report-table tr:hover {
			background-color: #ddd; /* Darker gray on hover */
		}

		/* Ensure table contents are centered */
		.material-report-table td {
			text-align: center; /* Center-align table data */
		}
	</style>
	<table class="table table-bordered table-striped material-report-table">
		<thead>
			<tr>
				<th>S.NO</th>
				<th>Project Name</th>
				<th>Voucher Name</th>
				<th>Voucher Type</th>
				<th>Expense For</th>
				<th>Amount</th>
			</tr>
		</thead>
		<tbody>'''

	serial_no = 1  # Initialize serial number for table rows
	total_amount = 0  # Initialize total amount accumulator

	# SQL Query to fetch project and journal entry data from the child table (Journal Entry Account)
	other_items = frappe.db.sql("""
		SELECT p.name AS project_name, pb.name AS budget_name, pb.voucher_type, pbi.account, pbi.debit, pbi.credit
		FROM `tabProject` p
		JOIN `tabJournal Entry Account` pbi ON p.name = pbi.project
		JOIN `tabJournal Entry` pb ON pbi.parent = pb.name
		WHERE pbi.project = %s
		  AND pb.voucher_type = 'Journal Entry' AND pb.docstatus = 1
	""", (project,), as_dict=True)

	# Check if no data is returned
	if not other_items:
		# If no data, display a message inside the table
		table += '''
			<tr>
				<td colspan="6">No data available for the selected project.</td>
			</tr>'''
	else:
		# If data exists, iterate through the fetched data and build the table rows
		for item in other_items:
			# Determine whether to use debit or credit for the amount
			amount = item['debit'] if item['debit'] else item['credit']
			# Accumulate total amount
			total_amount += amount
		

			# Populate table rows with data
			table += f'''
				<tr>
					<td>{serial_no}</td>
					<td>{item['project_name']}</td>  <!-- Project Name from Journal Entry Account -->
					<td>{item['budget_name']}</td>   <!-- Voucher Name -->
					<td>{item['voucher_type']}</td>  <!-- Voucher Type -->
					<td>{item['account']}</td>       <!-- Expense For (Account) -->
					<td>{amount}</td>                <!-- Debit or Credit -->
				</tr>'''
			serial_no += 1  # Increment serial number

		# Add a final row for the overall total
		table += f'''
			<tr>
				<td colspan="5" style="text-align: right; font-weight: bold;">Total Amount</td>
				<td>{total_amount}</td>
			</tr>'''

	# Close the table body and table tags
	table += '''</tbody>
	</table>'''

	# Return the complete HTML table
	return table
@frappe.whitelist()
def other_report_total(project):
	# Prepare the initial HTML table structure with styles
	table = '''<style>
		/* Bootstrap styles for responsiveness */
		.material-report-table {
			width: 100%;
			border-collapse: collapse;
			margin: 20px 0;
			font-size: 16px;
		}

		.material-report-table th, .material-report-table td {
			padding: 10px;
			text-align: left;
			border: 1px solid #ddd;
		}

		/* Header styles */
		.material-report-table th {
			background-color: orange; /* Set header background to orange */
			color: white; /* White text */
		}

		/* Row styles */
		.material-report-table tr:nth-child(even) {
			background-color: #f2f2f2; /* Light gray for even rows */
		}

		/* Hover effect for rows */
		.material-report-table tr:hover {
			background-color: #ddd; /* Darker gray on hover */
		}

		/* Ensure table contents are centered */
		.material-report-table td {
			text-align: center; /* Center-align table data */
		}
	</style>
	<table class="table table-bordered table-striped material-report-table">
		<thead>
			<tr>
				<th>S.NO</th>
				<th>Project Name</th>
				<th>Voucher Name</th>
				<th>Voucher Type</th>
				<th>Expense For</th>
				<th>Amount</th>
			</tr>
		</thead>
		<tbody>'''

	serial_no = 1  # Initialize serial number for table rows
	total_amount = 0  # Initialize total amount accumulator

	# SQL Query to fetch project and journal entry data from the child table (Journal Entry Account)
	other_items = frappe.db.sql("""
		SELECT p.name AS project_name, pb.name AS budget_name, pb.voucher_type, pbi.account, pbi.debit, pbi.credit
		FROM `tabProject` p
		JOIN `tabJournal Entry Account` pbi ON p.name = pbi.project
		JOIN `tabJournal Entry` pb ON pbi.parent = pb.name
		WHERE pbi.project = %s
		  AND pb.voucher_type = 'Journal Entry' AND pb.docstatus = 1
	""", (project,), as_dict=True)

	# Check if no data is returned
	if not other_items:
		# If no data, display a message inside the table
		table += '''
			<tr>
				<td colspan="6">No data available for the selected project.</td>
			</tr>'''
	else:
		# If data exists, iterate through the fetched data and build the table rows
		for item in other_items:
			# Determine whether to use debit or credit for the amount
			amount = item['debit'] if item['debit'] else item['credit']
			# Accumulate total amount
			total_amount += amount
		

			# Populate table rows with data
			table += f'''
				<tr>
					<td>{serial_no}</td>
					<td>{item['project_name']}</td>  <!-- Project Name from Journal Entry Account -->
					<td>{item['budget_name']}</td>   <!-- Voucher Name -->
					<td>{item['voucher_type']}</td>  <!-- Voucher Type -->
					<td>{item['account']}</td>       <!-- Expense For (Account) -->
					<td>{amount}</td>                <!-- Debit or Credit -->
				</tr>'''
			serial_no += 1  # Increment serial number

		# Add a final row for the overall total
		table += f'''
			<tr>
				<td colspan="5" style="text-align: right; font-weight: bold;">Total Amount</td>
				<td>{total_amount}</td>
			</tr>'''

	# Close the table body and table tags
	table += '''</tbody>
	</table>'''

	# Return the complete HTML table
	return total_amount




 # Invoice Collection
@frappe.whitelist()
def invoice_report(invoice):
	# Prepare the initial HTML table structure with styles
	table = '''<style>
		/* Bootstrap styles for responsiveness */
		.material-report-table {
			width: 100%;
			border-collapse: collapse;
			margin: 20px 0; /* Reduced margin size */
			font-size: 14px; /* Reduced font size */
		}

		.material-report-table th, .material-report-table td {
			padding: 8px; /* Reduced padding for smaller rows */
			text-align: center; /* Center-align table data */
			border: 1px solid #ddd;
			white-space: nowrap; /* Prevent text wrapping */
		}

		/* Header styles */
		.material-report-table th {
			background-color: orange; /* Set header background to orange */
			color: white; /* White text */
		}

		/* Row styles */
		.material-report-table tr:nth-child(even) {
			background-color: #f2f2f2; /* Light gray for even rows */
		}

		/* Hover effect for rows */
		.material-report-table tr:hover {
			background-color: #ddd; /* Darker gray on hover */
		}

		/* Styles for total row */
		.total-row {
			font-weight: bold; 
			background-color: #ffcc99; /* Light orange for total row */
		}
	</style>
	<table class="table table-bordered table-striped material-report-table">
		<thead>
			<tr>
				<th>S.NO</th>
				<th>Project Name</th>
				<th>Invoice NO</th>
				<th>Date</th>
				<th>Amount</th>
				<th>Discount Amount</th>
				<th>Advance Amount</th>
				<th>Retention Amount</th>  <!-- Added Retention Amount column -->
				<th>Received Amount</th>
			</tr>
		</thead>
		<tbody>'''

	serial_no = 1  # Initialize serial number for table rows
	total_grand_total = 0  # Initialize total grand total accumulator
	total_discount_amount = 0  # Initialize total discount amount accumulator
	total_adv_amount = 0  # Initialize total advance amount accumulator
	total_retention_amount = 0  # Initialize total retention amount accumulator
	total_tax_amount = 0  # Initialize total tax amount accumulator
	total_outstanding_amount = 0  # Initialize total outstanding amount accumulator

	# SQL Query to fetch grouped project and invoice data
	invoice_items = frappe.db.sql("""
		SELECT p.name AS project_name, 
			   pb.name AS voucher_name, 
			   pb.posting_date,pb.status, 
			   SUM(pb.grand_total) AS total_grand_total,
			   SUM(pb.discount_amount) AS total_discount_amount,
			   SUM(pb.adv_amount) AS total_adv_amount,
			   SUM(pbi.tax_amount) AS total_tax_amount,
			   SUM(pb.outstanding_amount) AS total_outstanding_amount,
			   SUM(pb.ret_amount) AS total_retention_amount
		FROM `tabProject` p
		JOIN `tabSales Invoice` pb ON p.name = pb.project
		LEFT JOIN `tabSales Taxes and Charges` pbi ON pb.name = pbi.parent
		WHERE pb.project = %s AND pb.status !='Cancelled'
		GROUP BY p.name, pb.name
	""", (invoice,), as_dict=True)

	# Check if no data is returned
	if not invoice_items:
		# If no data, display a message inside the table
		table += '''
			<tr>
				<td colspan="9">No data available for the selected project.</td>
			</tr>'''
	else:
		# If data exists, iterate through the fetched data and build the table rows
		for item in invoice_items:
			# Safely retrieve amounts or set to 0 if null
			grand_total = item['total_grand_total'] or 0
			discount_amount = item['total_discount_amount'] or 0
			adv_amount = item['total_adv_amount'] or 0
			retention_amount = item['total_retention_amount'] or 0
			tax_amount = item['total_tax_amount'] or 0
			outstanding_amount = item['total_outstanding_amount'] or 0

			# Accumulate totals for overall summary
			total_grand_total += grand_total
			total_discount_amount += discount_amount
			total_adv_amount += adv_amount
			total_retention_amount += retention_amount
			total_tax_amount += tax_amount
			total_outstanding_amount += outstanding_amount

			# Populate table rows with data
			table += f'''
			<tr>
				<td>{serial_no}</td>
				<td>{item['project_name']}</td>  
				<td>{item['voucher_name']}</td>   
				<td>{item['posting_date']}</td>  
				<td>{grand_total:.2f}</td>                
				<td>{discount_amount:.2f}</td>                
				<td>{adv_amount:.2f}</td>                
				<td>{retention_amount:.2f}</td>  <!-- Show Retention Amount -->
				<td>{outstanding_amount:.2f}</td>                
			</tr>'''
			serial_no += 1  # Increment serial number

		# Add a separate row for the overall total
		table += f'''
			<tr class="total-row">
				<td colspan="4" style="text-align: right;">Total</td>
				<td>{total_grand_total:.2f}</td>
				<td>{total_discount_amount:.2f}</td>
				<td>{total_adv_amount:.2f}</td>
				<td>{total_retention_amount:.2f}</td>  <!-- Show Total Retention Amount -->
				<td>{total_outstanding_amount:.2f}</td>
			</tr>'''

	# Close the table body and table tags
	table += '''</tbody>
	</table>'''

	# Return the complete HTML table
	return table

@frappe.whitelist()
def test_check():
	query = f"""
		SELECT pb.*, so.project
		FROM `tabProject Budget` pb
		JOIN `tabSales Order` so ON pb.sales_order = so.name
		WHERE pb.docstatus = 1 AND so.docstatus = 1
		AND so.status != 'Closed' 
		AND pb.company = "ENGINEERING DIVISION - ELECTRA"
	"""


	project_budgets = frappe.db.sql(query, as_dict=True)

	for pb in project_budgets:
		project = pb.project
		sales_order = frappe.db.get_value("Sales Order", {"project_budget": pb.name}, "name")
		project_name = frappe.db.get_value("Cost Estimation",{'name':pb.cost_estimation, "docstatus": 1},['project_name'])
		
		print([pb.project, sales_order, project_name])
		
