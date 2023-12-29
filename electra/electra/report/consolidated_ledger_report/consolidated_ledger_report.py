# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
import erpnext


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = []
	columns += [
		_("Company") + ":Link/Company:300",
		_("Opening Debit") + ":Currency/:120",
		_("Opening Credit") + ":Currency/:120",
		_("Movement Debit") + ":Currency/:150",
		_("Movement Credit") + ":Currency/:150",
		_("Closing Debit") + ":Currency/:150",
		_("Closing Credit") + ":Currency/:150",
	]
	return columns

def get_data(filters):
	data = []
	row = []
	acct = filters.account
	if acct is not None:
		acct_parts = acct.split(' - ')
		if len(acct_parts) == 2:
			acc = acct_parts[0]
		elif len(acct_parts) == 3:
			acc = acct_parts[1]
		else:
			acc = None
		ac = '%' + acc + '%'
		op_credit = 0
		op_debit = 0
		li = []
		company = frappe.db.sql(""" select name from `tabCompany` where is_group = 1""",as_dict=1)
		for com in company:
			li.append(com.name)
			comp = frappe.db.get_list("Company",{"parent_company":com.name},['name'])
			for j in comp:
				li.append(j.name)
		for c in li:
			gle = frappe.db.sql("""select account, sum(debit) as opening_debit, sum(credit) as opening_credit from `tabGL Entry` where company = '%s'	and (posting_date < '%s' or (ifnull(is_opening, 'No') = 'Yes' and posting_date >= '%s')) and account like '%s' and is_cancelled = 0  """%(c,filters.from_date,filters.to_date,ac),as_dict=True)
			for g in gle:
				if g.opening_debit is None:
					g.opening_debit = 0
				if g.opening_credit is None:  
					g.opening_credit = 0
				sq = frappe.db.sql(""" select company,sum(debit_in_account_currency) as debit,sum(credit_in_account_currency) as credit from `tabGL Entry` where company = '%s' and account like '%s' and posting_date between '%s' and '%s' and is_opening = 'No' and is_cancelled = 0 """%(c,ac,filters.from_date,filters.to_date),as_dict=True)
				for i in sq:
					if not i.debit:
						i.debit = 0
					if not i.credit:
						i.credit = 0
					op_credit = g.opening_credit + i.credit
					op_debit = g.opening_debit + i.debit
				row = [c,g.opening_debit,g.opening_credit,i.debit,i.credit,op_debit,op_credit]
				data.append(row)
	return data
				
				