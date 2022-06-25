# Copyright (c) 2022, Shivansh and contributors
# For license information, please see license.txt

import frappe,json
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display

class TripAllocation(Document):
	def before_save(self):
		if self.vehicle_type=="Own Vehicle" and self.saved:
			if len(self.driver_mobile) > 10:
				frappe.throw("Mobile Number Exceed 10 digit")
			if len(self.driver_mobile) < 10:
				frappe.throw("Mobile Number Should be 10 digit")
		if self.vehicle_type=="Market Vehicle" and self.saved:
			if len(self.market_driver_mobile_c) > 10:
				frappe.throw("Mobile Number Exceed 10 digit")
			if len(self.market_driver_mobile_c) < 10:
				frappe.throw("Mobile Number Should be 10 digit")
		if self.saved and self.vehicle_type=="Own Vehicle":
			l_lh=frappe.db.get_value("LH Master",{"consignor_c":self.consignor_c,'from': ["<=", self.date_c] ,'to': [">=", self.date_c ]},"name")
			res=0
			if l_lh:
				doc=frappe.get_doc("LH Master",l_lh)
				for row in doc.lh_master_table:
					if row.loading_point_c == self.loading_point_c and row.destination_c == self.destination_c:
						if self.one_way:
							res=row.one_way_c
						elif self.two_way:
							res=row.two_way_c
				if res:
					self.lorry_hire= res
					self.total_lorry_hire = res+self.hamali+self.toll
				else:
					frappe.throw("No price for "+self.loading_point_c+" to "+self.destination_c+" in  LH Master")
		else:
			self.saved=1

	def on_submit(self):
		for row in self.dr_table_c:
			if self.vehicle_type == "Own Vehicle":
				doc=frappe.new_doc("Final Trip Sheet")
				doc.vehicle_type="Own Vehicle"
				doc.consignor_c=self.consignor_c
				doc.date_c=self.date_c
				#doc.consignee_c=self.consignee_c
				doc.loading_point_c = row.loading_point_c
				doc.destination_c = row.destination_c
				doc.vehicle_reg_no=self.vehicle_reg_no
				if row.idx != 1:
					doc.duplicate_entry = 1
				doc.customer=self.customer
				# adding supplier
				#		doc.supplier=self.supplier		
				doc.branch_c=self.branch_c
				doc.driver_mobile=self.driver_mobile
				doc.pan_no = self.pan_no_c
				doc.driver=self.driver
				doc.lorry_hire=self.total_lorry_hire
				doc.advance_amount=self.advance_amount
				doc.outstanding_amount = self.total_lorry_hire
				doc.vehicle_type_c=self.vehicle_type_c
				doc.one_way=self.one_way
				doc.two_way=self.two_way
				doc.linked_trip_allocation_c=self.name
				doc.rc_copy = self.rc_copy
				doc.pan_copy = self.pan_copy
				#doc.consignee_address=frappe.db.get_value("Dynamic Link",{"link_doctype":"Consignee","link_name":self.consignee_c},"parent")
				#doc.consignee_address_display=get_address_display(doc.consignee_address)
				doc.consignor_address=frappe.db.get_value("Dynamic Link",{"link_doctype":"Consignor","link_name":self.consignor_c},"parent")
				doc.consignor_address_display=get_address_display(doc.consignor_address)
				doc.save()
				row.fts = doc.name
				doc_name=frappe.db.get_value("Final Trip Sheet",{"linked_trip_allocation_c":self.name},"name")
				link="/app/final-trip-sheet/"+doc_name
				frappe.msgprint("Final Trip Sheet Created <a href="+link+">"+doc_name+"</a>")

			if self.vehicle_type == "Market Vehicle":
				doc=frappe.new_doc("Final Trip Sheet")
				doc.vehicle_type="Market Vehicle"
				doc.consignor_c=self.consignor_c
				doc.date_c=self.date_c
				#doc.consignee_c=self.consignee_c
				doc.loading_point_c=row.loading_point_c
				doc.destination_c=row.destination_c
				if row.idx != 1:
					doc.duplicate_entry = 1
				doc.market_vehicle_no_c=self.market_vehicle_no_c
				doc.supplier=self.supplier
				doc.branch_c=self.branch_c
				doc.rc_copy = self.rc_copy
				doc.pan_copy = self.pan_copy
				# adding supplier
				#               doc.supplier=self.supplier
				doc.market_driver_mobile_c=self.market_driver_mobile_c
				doc.market_driver_c=self.market_driver_c
				doc.market_lorry_hire=self.market_total_lorry_hire
				doc.market_advance_amount_c = self.market_advance_amount_c
				doc.outstanding_amount = self.market_total_lorry_hire
				doc.vehicle_type_c=self.vehicle_type_c
				doc.pan_no = self.pan_no_c
				doc.one_way=self.one_way
				doc.two_way=self.two_way
				doc.linked_trip_allocation_c=self.name
				#doc.consignee_address=frappe.db.get_value("Dynamic Link",{"link_doctype":"Consignee","link_name":self.consignee_c},"parent")
				#doc.consignee_address_display=get_address_display(doc.consignee_address)
				doc.consignor_address=frappe.db.get_value("Dynamic Link",{"link_doctype":"Consignor","link_name":self.consignor_c},"parent")
				doc.consignor_address_display=get_address_display(doc.consignor_address)
				doc.save()
				row.fts = doc.name
				doc_name=frappe.db.get_value("Final Trip Sheet",{"linked_trip_allocation_c":self.name},"name")
				link="/app/final-trip-sheet/"+doc_name
				frappe.msgprint("Final Trip Sheet Created <a href="+link+">"+doc_name+"</a>")



	def before_submit(self):
		if self.vehicle_type == "Own Vehicle":
			pe=frappe.new_doc("Payment Entry")
			pe.payment_type="Receive"
			pe.mode_of_payment="NEFT/RTGS/IMPS"
			pe.vehicle_no = self.vehicle_reg_no
			pe.party_type="Customer"
			pe.party=self.customer
			pe.party_name=self.customer
			pe.paid_amount=self.advance_amount
			pe.received_amount=self.advance_amount
			pe.target_exchange_rate=1
			pe.base_received_amount=self.advance_amount
			pe.paid_from="Debtors - SCC"
			pe.paid_to="Cash - SCC"
			pe.paid_from_account_currency="INR"
			pe.paid_to_account_currency="INR"
			pe.append("references",{"reference_doctype":"Trip Allocation","reference_name":self.name,"total_amount":self.total_lorry_hire,"outstanding_amount":self.total_lorry_hire,"allocated_amount":self.advance_amount})
			pe.linked_trip_allocation = self.name
			pe.save()
	#	pe.submit()
	#	self.outstanding_amount=self.lorry_hire-self.advance_amount
			doc_name=pe.name
			link="/app/payment-entry/"+doc_name
			frappe.msgprint("Advance Created <a href="+link+">"+doc_name+"</a>")



		if self.vehicle_type == "Market Vehicle":
			pe=frappe.new_doc("Payment Entry")
			pe.payment_type="Pay"
			pe.mode_of_payment="NEFT/RTGS/IMPS"
			pe.party_type="Supplier"
			pe.vehicle_no = self.market_vehicle_no_c
			pe.party=self.supplier
			pe.party_name=self.supplier
			pe.paid_amount=self.market_advance_amount_c
			pe.received_amount=self.market_advance_amount_c
			pe.target_exchange_rate=1
			pe.base_received_amount=self.market_advance_amount_c
			pe.paid_from="Cash - SCC"
			pe.paid_to="Creditors - SCC"
			pe.paid_from_account_currency="INR"
			pe.paid_to_account_currency="INR"
			pe.append("references",{"reference_doctype":"Trip Allocation","reference_name":self.name,"total_amount":self.market_advance_amount_c,"outstanding_amount":self.market_advance_amount_c,"allocated_amount":self.market_advance_amount_c})
			pe.linked_trip_allocation = self.name
			pe.save()
			doc_name=pe.name
			link="/app/payment-entry/"+doc_name
			frappe.msgprint("Advance Created <a href="+link+">"+doc_name+"</a>")











@frappe.whitelist()
def make_payment_entry(frm):
	val=json.loads(frm)
	if val['vehicle_type'] == "Own Vehicle":
		pe=frappe.new_doc("Payment Entry")
		pe.payment_type="Receive"
		pe.mode_of_payment="NEFT/RTGS/IMPS"
		pe.party_type="Customer"
		pe.party=val['customer']
		pe.party_name=val['customer']
		pe.vehicle_no = val['vehicle_reg_no']
		pe.paid_amount = val['outstanding_amount']
		pe.received_amount = val['outstanding_amount']
		pe.target_exchange_rate = 1
		pe.base_received_amount = val['outstanding_amount']
		pe.paid_from = "Debtors - SCC"
		pe.paid_to = "Cash - SCC"
		pe.paid_from_account_currency = "INR"
		pe.paid_to_account_currency = "INR"
		pe.append("references",{"reference_doctype":"Acknowledgement","reference_name":val['name'],"total_amount":val['outstanding_amount'],"outstanding_amount":val['outstanding_amount'],"allocated_amount":val['outstanding_amount']})
		pe.save()
#       pe.submit()
#       val['outstanding_amount=val['lorry_hire-val['advance_amount
		doc_name=pe.name
		link="/app/payment-entry/"+doc_name
		frappe.msgprint("Final Payment Created <a href="+link+">"+doc_name+"</a>")



	if val['vehicle_type'] == "Market Vehicle":
		pe=frappe.new_doc("Payment Entry")
		pe.payment_type="Pay"
		pe.mode_of_payment="NEFT/RTGS/IMPS"
		pe.party_type="Supplier"
		pe.party=val['supplier']
		pe.party_name=val['supplier']
		pe.vehicle_no = val['market_vehicle_no_c']
		pe.paid_amount = val['outstanding_amount']
		pe.received_amount=val['outstanding_amount']
		pe.target_exchange_rate=1
		pe.base_received_amount=val['outstanding_amount']
		pe.paid_from="Cash - SCC"
		pe.paid_to="Creditors - SCC"
		pe.paid_from_account_currency="INR"
		pe.paid_to_account_currency="INR"
		pe.append("references",{"reference_doctype":"Acknowledgement","reference_name":val['name'],"total_amount":val['outstanding_amount'],"outstanding_amount":val['outstanding_amount'],"allocated_amount":val['outstanding_amount']})
		pe.save()
		doc_name=pe.name
		link="/app/payment-entry/"+doc_name
		frappe.msgprint("Final Payment Created <a href="+link+">"+doc_name+"</a>")



@frappe.whitelist()
def o_amount(self,method):
	if self.references:
		if self.references[0].reference_doctype == "Trip Allocation":
			doc=frappe.get_doc("Trip Allocation",self.references[0].reference_name)
			doc.mode_of_payment_c = self.mode_of_payment
	#	doc.ref_date_c = self.posting_date
			doc.payment_reference_c = self.name
			if doc.outstanding_amount:
				doc.outstanding_amount = doc.outstanding_amount - self.paid_amount
			else:
				doc.outstanding_amount = self.references[0].total_amount - self.paid_amount
			doc.save()
			#doc.submit()

			fts_name=frappe.db.get_value("Final Trip Sheet",{"linked_trip_allocation_c":self.references[0].reference_name},"name")
			doc=frappe.get_doc("Final Trip Sheet",fts_name)
			if doc.outstanding_amount:
				doc.outstanding_amount = doc.outstanding_amount - self.paid_amount
			else:
				doc.outstanding_amount = self.references[0].total_amount - self.paid_amount
			doc.save()
	#	doc.submit()


		if self.references[0].reference_doctype == "Acknowledgement":
			doc=frappe.get_doc("Acknowledgement",self.references[0].reference_name)
#		doc.mode_of_payment_c = self.mode_of_payment
			doc.reference_c = self.name
			if doc.outstanding_amount:

				doc.outstanding_amount = self.references[0].total_amount - self.paid_amount
	#	else:
	#		doc.outstanding_amount = self.references[0].total_amount - self.paid_amount
			doc.save()
		#doc.submit()

			ta_doc=frappe.db.get_value("Acknowledgement",{"name":self.references[0].reference_name},"final_trip_sheet")
			doc=frappe.get_doc("Final Trip Sheet",ta_doc)
			if doc.outstanding_amount:
				doc.outstanding_amount = self.references[0].total_amount - self.paid_amount
	#	else:
	#		doc.outstanding_amount = self.references[0].total_amount - self.paid_amount
			doc.save()
#		doc.submit()











