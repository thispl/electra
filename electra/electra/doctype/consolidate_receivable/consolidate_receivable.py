# Copyright (c) 2023, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class ConsolidatedReceivable(Document):
	def on_submit(self):
		for i in self.order_invoice_list:
			pay = frappe.new_doc("Payment Entry")
			pay.payment_type = "Pay"
			pay.append("references",{
				"reference_doctype":i.type,
				"reference_name":i.name1,
				"allocated_amount":i.receivable_amount,
				"total_amount": i.grand_total,
				"allocated_amount": i.receivable_amount,
				"outstanding_amount": i.outstanding_amount,
			})
			pay.posting_date = now()
			pay.company = i.company
			pay.mode_of_payment = self.mode_of_payment
			pay.party = i.customer
			pay.party_name = i.customer
			pay.party_type = "Customer"
			acc = frappe.db.get_list("Account",{"company":i.company,"account_number":"1211"},["name","account_currency"])
			for ac in acc:
				pay.paid_from = ac.name
				pay.paid_from_account_currency = ac.account_currency
			pay_acc = frappe.db.get_list("Account",{"company":i.company,"account_number":"2110"},["name","account_currency"])
			for ac_pay in pay_acc:
				pay.paid_to = ac_pay.name
				pay.paid_to_account_currency = ac_pay.account_currency
			pay.paid_amount = i.receivable_amount
			pay.received_amount = i.receivable_amount
			pay.reference_no = i.chequereference_no
			pay.consolidate_receivable = self.name
			pay.reference_date = i.chequereference_date
			pay.flags.ignore_mandatory = True
			pay.flags.ignore_validate = True
			pay.save(ignore_permissions = True)



