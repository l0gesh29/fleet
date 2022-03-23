# Copyright (c) 2022, Shivansh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display
from frappe.contacts.doctype.contact.contact import get_contact_details
from frappe.contacts.address_and_contact import (
	delete_contact_and_address,
	load_address_and_contact)

class Consignor(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)

	def on_trash(self):
		delete_contact_and_address('Consignor', self.name)

