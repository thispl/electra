import frappe
from frappe import _
from frappe.utils import flt
import erpnext

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	columns = [_("Sales Person") + ":Data/:190"]
	if filters.order_type == "Monthly":
		columns += [_(month) + ":Currency/:150" for month in months]
	elif filters.order_type == "Quarter":
		if filters.quarter == "Quarter 1":
			columns += [_(month) + ":Currency/:150" for month in months[:3]]
		elif filters.quarter == "Quarter 2":
			columns += [_(month) + ":Currency/:150" for month in months[3:6]]
		elif filters.quarter == "Quarter 3":
			columns += [_(month) + ":Currency/:150" for month in months[6:9]]
		elif filters.quarter == "Quarter 4":
			columns += [_(month) + ":Currency/:150" for month in months[9:]]
	elif filters.order_type == "Half Yearly":
		if filters.half_yearly == "First Half":
			columns += [_(month) + ":Currency/:150" for month in months[:6]]
		elif filters.half_yearly == "Second Half":
			columns += [_(month) + ":Currency/:150" for month in months[7:]]
	columns.append(_("Total") + ":Currency/:150")
	return columns

def get_data(filters):
	data = []
	year = filters.year
	sale = frappe.db.get_all("Sales Person", ['name'])
	for sa in sale:
		row = [sa.name]
		total = 0
		start_month = 0
		end_month = 0
		condition = " "
		if filters.order_type == "Monthly":
			start_month = 1
			end_month = 12
		elif filters.order_type == "Quarter":
			if filters.quarter == "Quarter 1":
				start_month = 1
				end_month = 3
			elif filters.quarter == "Quarter 2":
				start_month = 4
				end_month = 6
			elif filters.quarter == "Quarter 3":
				start_month = 7
				end_month = 9
			elif filters.quarter == "Quarter 4":
				start_month = 10
				end_month = 12
		elif filters.order_type == "Half Yearly":
			if filters.half_yearly == "First Half":
				start_month = 1
				end_month = 6
			elif filters.half_yearly == "Second Half":
				start_month = 7
				end_month = 12
		for i in range(start_month, end_month + 1):
			month = str(i).zfill(2)
			start_date = f"{year}-{month}-01"
			end_date = f"{year}-{month}-31"
			if filters.type == "Sales Order":
				if filters.order_type == "Monthly":
					table = "tabSales Order"
					condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
				elif filters.order_type == "Quarter":
					if filters.quarter == "Quarter 1":
						table = "tabSales Order"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
					elif filters.quarter == "Quarter 2":
						table = "tabSales Order"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
					elif filters.quarter == "Quarter 3":
						table = "tabSales Order"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
					elif filters.quarter == "Quarter 4":
						table = "tabSales Order"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
				elif filters.order_type == "Half Yearly":
					if filters.half_yearly == "First Half":
						table = "tabSales Order"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
					elif filters.half_yearly == "Second Half":
						table = "tabSales Order"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
			elif filters.type == "Sales Invoice":
				if filters.order_type == "Monthly":
					table = "tabSales Invoice"
					condition = f"posting_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
				elif filters.order_type == "Quarter":
					if filters.quarter == "Quarter 1":
						table = "tabSales Invoice"
						condition = f"posting_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
					elif filters.quarter == "Quarter 2":
						table = "tabSales Invoice"
						condition = f"posting_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
					elif filters.quarter == "Quarter 3":
						table = "tabSales Invoice"
						condition = f"posting_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
					elif filters.quarter == "Quarter 4":
						table = "tabSales Invoice"
						condition = f"posting_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
				elif filters.order_type == "Half Yearly":
					if filters.half_yearly == "First Half":
						table = "tabSales Invoice"
						condition = f"posting_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
					elif filters.half_yearly == "Second Half":
						table = "tabSales Invoice"
						condition = f"posting_date between '{start_date}' and '{end_date}' and docstatus != 2 and sales_person_user = '{sa.name}'"
			elif filters.type == "Quotation":
				if filters.order_type == "Monthly":
					table = "tabQuotation"
					condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and converted_by = '{sa.name}'"
				elif filters.order_type == "Quarter":
					if filters.quarter == "Quarter 1":
						table = "tabQuotation"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and converted_by = '{sa.name}'"
					elif filters.quarter == "Quarter 2":
						table = "tabQuotation"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and converted_by = '{sa.name}'"
					elif filters.quarter == "Quarter 3":
						table = "tabQuotation"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and converted_by = '{sa.name}'"
					elif filters.quarter == "Quarter 4":
						table = "tabQuotation"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and converted_by = '{sa.name}'"
				elif filters.order_type == "Half Yearly":
					if filters.half_yearly == "First Half":
						table = "tabQuotation"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and converted_by = '{sa.name}'"
					elif filters.half_yearly == "Second Half":
						table = "tabQuotation"
						condition = f"transaction_date between '{start_date}' and '{end_date}' and docstatus != 2 and converted_by = '{sa.name}'"
			result = frappe.db.sql(f"select sum(grand_total) as total from `{table}` where {condition}", as_dict=True)
			frappe.errprint(result)
			month_total = (result[0].get("total"))or 0
			total += month_total
			row.append(month_total)
		row.append(total)
		data.append(row)
	return data
