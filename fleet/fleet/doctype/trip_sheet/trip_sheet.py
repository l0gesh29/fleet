# Copyright (c) 2021, Shivansh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
import json

class TripSheet(Document):
	pass

@frappe.whitelist()
def get_price(from_dest, to_dest):
	
	data = frappe.db.get_list('Fleet Price List', filters={
		'from_location': ['=', from_dest],
		'to_location': ['=', to_dest]
		},
		fields=['name', 'price', 'return_trip_price'],
	)

	if data == []:
		return 0
	else:	
		return data

@frappe.whitelist()
def insert_sales_invoice(cur_doc):
	check_invoice = frappe.db.get_list('Sales Invoice', filters={
		'trip_sheet_ref': ['=', cur_doc]
		},
		fields=['name']
		)
	if check_invoice == []:
		doc = frappe.get_doc('Trip Sheet', cur_doc)
		description = "From Destination: " + doc.get("loading_point_c") + " - To Destination: " + doc.get("destination_c")
		sales_invoice = frappe.new_doc("Sales Invoice")
		sales_invoice.customer = doc.get("consignor_c")
		sales_invoice.posting_date = nowdate()
		sales_invoice.payment_due = nowdate()
		sales_invoice.trip_vehicle_no = doc.get("vehicle_no_c")
		sales_invoice.trip_sheet_ref = doc.get("name")
		sales_invoice.append('items', {
			'item': frappe.get_single('Trip Setting').item,
			'item_name': frappe.get_single('Trip Setting').item,
			'unit': 1,
			'description': description,
			'qty': 1,
			'conversion_factor': 1,
			'rate': doc.get("price"),
			'uom': 'Nos',
			'amount': doc.get("price"),
			'income_account': 'Sales - A'
		})
		sales_invoice.grand_total = doc.get("price")

		sales_invoice.save()
		return 'success' 

	return 'not found'  

@frappe.whitelist()
def insert_Payment(cur_doc, price):
	doc = frappe.get_doc('Trip Sheet', cur_doc)

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = 'Receive'
	# pe.company = doc.company
	# pe.cost_center = doc.get("cost_center")
	pe.posting_date = nowdate()
	pe.mode_of_payment = 'Cash'
	pe.party_type = 'Customer'
	pe.party = doc.get("consignor_c")
	pe.paid_from = 'Debtors - A'
	pe.received_amount = price
	pe.paid_amount = price
	# pe.received_amount_after_tax = price
	pe.target_exchange_rate = 1
	pe.paid_to = 'Cash - A'
	pe.paid_to_account_currency = 'INR'
	# pe.contact_person = doc.get("contact_person")
	# pe.contact_email = doc.get("contact_email")
	pe.save()

	return pe.name