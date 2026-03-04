# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class ConsolidatedPaymentRequest(Document):
	def on_submit(self):
		from collections import defaultdict
		from frappe.utils import now
		con = frappe.db.sql("""SELECT * FROM `tabPurchase Invoice List` WHERE parent = '%s' """ % (self.name), as_dict=True)

		def calculate_outstanding_payment_difference(child_table):
			amounts_by_company = defaultdict(float)
			total = 0.0

			for row in child_table:
				company = row.get("company", "")
				outstanding_amount = row.get("outstanding_amount", 0.0)
				payment_amount = row.get("payment_amount", 0.0)
				amounts_by_company[company] += payment_amount
				total += payment_amount

			result = []

			for company, difference in amounts_by_company.items():
				result.append({"company": company, "value": difference})

			for k in result:
				pay = frappe.new_doc("Payment Entry")
				pay.payment_type = "Pay"
				for i in self.purchase_invoice_list:
					if i.company == k['company']:
						pay.append("references",{
							"reference_doctype":i.type,
							"reference_name":i.name1,
							"allocated_amount":i.payment_amount,
							"total_amount": i.grand_total,
							"allocated_amount": i.payment_amount,
							"outstanding_amount": i.outstanding_amount,
						})
				pay.posting_date = now()
				pay.company = k['company']
				pay.mode_of_payment = self.mode_of_payment
				pay.party = self.supplier
				pay.party_name = self.supplier
				pay.party_type = "Supplier"
				acc = frappe.db.get_list("Account",{"company":k['company'],"account_number":"1211"},["name","account_currency"])
				for ac in acc:
					pay.paid_from = ac.name
					pay.paid_from_account_currency = ac.account_currency

				co = [{"company":"KINGFISHER TRADING AND CONTRACTING COMPANY","name":"Creditors - KTCC"},
						{"company":"KINGFISHER - TRANSPORTATION","name":"Creditors - KT"},
						{"company":"KINGFISHER - SHOWROOM","name":"Creditors - KS"}]
				for company_info in co:
					if k['company'] == company_info['company']:
						pay_acc = frappe.db.get_list("Account",{"name":company_info['name']},["name","account_currency"])
					else:
						pay_acc = frappe.db.get_list("Account",{"company":k['company'],"account_number":"2110"},["name","account_currency"])
				for ac_pay in pay_acc:
					pay.paid_to = ac_pay.name
					pay.paid_to_account_currency = ac_pay.account_currency
				pay.paid_amount = k['value']
				pay.received_amount = k['value']
				# pay.reference_no = i.reference_no
				pay.consolidated_payment_request = self.name
				# pay.reference_date = i.reference_date
				pay.flags.ignore_mandatory = True
				pay.flags.ignore_validate = True
				pay.save(ignore_permissions = True)

		child_table = con
		amounts_difference_by_company = calculate_outstanding_payment_difference(child_table)
		return amounts_difference_by_company