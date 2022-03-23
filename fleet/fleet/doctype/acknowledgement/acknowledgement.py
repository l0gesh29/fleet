# Copyright (c) 2022, Shivansh and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Acknowledgement(Document):
	def before_save(self):
		add = 0
		sub = 0
		amount=self.outstanding_amount
		if len(self.addition):
			for row in self.addition:
				add+=row.approval_amount
		if len(self.deduction):
			for row in self.deduction:
				sub+=row.approval_amount
		self.outstanding_amount=(amount+add)-sub
		self.total_addition = add
		self.total_deduction = sub

	#pass
