# Copyright (c) 2022, Abdulla and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request


class GeneralPaymentRequest(Document):
	def on_submit(self):
		pr = make_payment_request(party_type=self.party_type, party=self.party, dt="General Payment Request",
					dn=self.name,bank_account=self.bank_account,payment_request_type=self.payment_request_type,
					company=self.company,mode_of_payment=self.mode_of_payment,transaction_date=self.transaction_date,
					currency=self.currency,submit_doc=False, use_dummy_message=True)
		self.payment_request = pr.name
