# Copyright (c) 2021, Shivansh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
import json

class TripSheet(Document):
	def on_submit(self):
		doc=frappe.new_doc("Trip Allocation")
		doc.consignor_c=self.consignor_c
		doc.branch_c=self.branch
		#doc.consignee_c=self.consignee_c
		doc.date_c=self.date_c
		doc.loading_point_c=self.loading_point_c
		doc.destination_c=self.destination_c
		doc.one_way=self.one_way
		doc.two_way=self.two_way
		doc.lorry_hire=self.price
		doc.linked_trip_order_c=self.name
		doc.vehicle_type_c=self.vehicle_type_c
		address = frappe.db.get_value("Dynamic Link",{"link_doctype":"Consignor","link_name":self.consignor_c},"parent")
	#	doc.consignor_address_display = get_address_display(address)
		doc.save()
		doc_name=frappe.db.get_value("Trip Allocation",{"linked_trip_order_c":self.name},"name")
		link="/app/trip-allocation/"+doc_name
		frappe.msgprint("Trip Allocation Created <a href="+link+">"+doc_name+"</a>")
	#@frappe.whitelist()
	def before_submit(self):
		#args=json.loads(args)
		l_lh=frappe.db.get_value("LH Master",{"consignor_c":self.consignor_c,'from': ["<=", self.date_c ],'to': [">=", self.date_c ]},"name")
		frappe.errprint(l_lh)
		res=0
		if l_lh:
			doc=frappe.get_doc("LH Master",l_lh)
			for row in doc.lh_master_table:
				if row.loading_point_c == self.loading_point_c and row.destination_c == self.destination_c:
					if self.one_way:
						#frappe.errprint(row.one_way_c)
						res=row.one_way_c
					elif self.two_way:
						res=row.two_way_c
		#if not res:
		#	frappe.throw("No Price in LH Master for this route")
		#else:
#			frappe.errprint(res)
			self.price=res

	#else:
	#	frappe.throw("No LH Master for this date "f'{date_c}')

#@frappe.whitelist()
#def get_price(from_dest, to_dest):
#	
#	data = frappe.db.get_list('Fleet Price List', filters={
#		'from_location': ['=', from_dest],
#		'to_location': ['=', to_dest]
#		},
#		fields=['name', 'price', 'return_trip_price'],
#	)
#
#	if data == []:
#		return 0
#	else:	
#		return data

@frappe.whitelist()
def vehicle_type(consignor):
	v_t = frappe.db.get_list("Vehicle Type Table",{"parent":consignor},"vehicle_type")
	if v_t:
		v = []
		for row in v_t:
			v.append(row.vehicle_type)
		return v
	else:
		return v_t
@frappe.whitelist()
def branch(branch):
	b = frappe.db.get_list("Destination Table",{"parent":branch},"destination")
	if b:
		b_l = []
		for row in b:
			b_l.append(row.destination)
		return b_l
	else:
		return b
@frappe.whitelist()
def insert_sales_invoice(cur_doc):
	company = frappe.db.get_value("Global Defaults",None,"default_company")
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
			'income_account': frappe.db.get_value("Company",company,"default_income_account")
		})
		sales_invoice.grand_total = doc.get("price")

		sales_invoice.save()
		return 'success' 

	return 'not found'  

@frappe.whitelist()
def insert_Payment(cur_doc, price):
	company = frappe.db.get_value("Global Defaults",None,"default_company")
	doc = frappe.get_doc('Trip Sheet', cur_doc)

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = 'Receive'
	# pe.company = doc.company
	# pe.cost_center = doc.get("cost_center")
	pe.posting_date = nowdate()
	pe.mode_of_payment = 'Cash'
	pe.party_type = 'Customer'
	pe.party = doc.get("consignor_c")
	pe.paid_from = frappe.db.get_value("Company",company,"default_receivable_account")
	pe.received_amount = float(price)
	pe.paid_amount = float(price)
	# pe.received_amount_after_tax = price
	pe.target_exchange_rate = 1
	pe.paid_to = frappe.db.get_value("Company",company,"default_cash_account")
	pe.paid_to_account_currency = frappe.db.get_value("Company",company,"default_currency")
	# pe.contact_person = doc.get("contact_person")
	# pe.contact_email = doc.get("contact_email")
	pe.save()

	return pe.name
