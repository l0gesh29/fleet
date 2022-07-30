# Copyright (c) 2022, Shivansh and contributors
# For license information, please see license.txt

import frappe,json
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display
from frappe import _

class FinalTripSheet(Document):
#	def before_save(self):
#		add=0
#		sub=0
#		amount=self.outstanding_amount
#		if len(self.addition):
#			for row in self.addition:
#				add+=row.amount
#		if len(self.deduction):
#			for row in self.deduction:
#				sub+=row.amount
#		self.outstanding_amount=(amount+add)-sub
#		self.total_addition = add
#		self.total_deduction = sub
	pass



@frappe.whitelist()
def make_acknowledgement(frm):
	if isinstance(frm, str):
		val = json.loads(frm)
	else:
		val = frm.as_dict()
	if val["vehicle_type"] == "Own Vehicle":
			doc = frappe.new_doc("Acknowledgement")
			doc.consignor_c = val["consignor_c"]
			doc.consignor_mobile_no_c = val["consignor_mobile_no_c"]
			doc.loading_point_c = val["loading_point_c"]
			doc.date_c = val["date_c"]
			doc.branch_c = val["branch_c"]
			doc.destination_c = val["destination_c"]
			doc.consignee_c = val["consignee_c"]
			doc.consignee_mobile_no_c = val["consignee_mobile_no_c"]
			doc.advance_amount = val["advance_amount"]
			doc.vehicle_reg_no = val["vehicle_reg_no"]
			doc.lorry_hire = val["lorry_hire"]
			doc.driver = val["driver"]
			doc.driver_mobile = val["driver_mobile"]
			doc.final_trip_sheet = val["name"]
			doc.outstanding_amount = val["outstanding_amount"]
			doc.vehicle_type_c = val["vehicle_type_c"]
			doc.vehicle_type = val["vehicle_type"]
			doc.customer = val["customer"]
			doc.vehicle_reg_no = val["vehicle_reg_no"]
			for row in val["item"]:
				doc.append("item",{"packages_c":row["packages_c"],"weight_c":row["weight_c"],"quantity_c":row["quantity_c"],"unit_c":row["unit_c"]})
			doc.save()
			link="/app/acknowledgement/"+doc.name
			frappe.msgprint("Acknowledgement Created <a href="+link+">"+doc.name+"</a>")
	if val["vehicle_type"] == "Market Vehicle":
			doc = frappe.new_doc("Acknowledgement")
			doc = frappe.new_doc("Acknowledgement")
			doc.consignor_c = val["consignor_c"]
			doc.consignor_mobile_no_c = val["consignor_mobile_no_c"]
			doc.loading_point_c = val["loading_point_c"]
			doc.date_c = val["date_c"]
			doc.branch_c = val["branch_c"]
			doc.destination_c = val["destination_c"]
			doc.consignee_c = val["consignee_c"]
			doc.consignee_mobile_no_c = val["consignee_mobile_no_c"]
			doc.advance_amount = val["advance_amount"]
			doc.vehicle_reg_no = val["vehicle_reg_no"]
			doc.lorry_hire = val["lorry_hire"]
			doc.final_trip_sheet = val["name"]
			doc.outstanding_amount = val["outstanding_amount"]
			doc.market_vehicle_no_c = val["market_vehicle_no_c"]
			doc.vehicle_type = val["vehicle_type"]
			doc.vehicle_type_c = val["vehicle_type_c"]
			doc.market_vehicle_no_c = val["market_vehicle_no_c"]
			doc.supplier = val["supplier"]
			for row in val["item"]:
				doc.append("item",{"packages_c":row["packages_c"],"weight_c":row["weight_c"],"quantity_c":row["quantity_c"],"unit_c":row["unit_c"]})
			doc.save()
			link="/app/acknowledgement/"+doc.name
			frappe.msgprint("Acknowledgement Created <a href="+link+">"+doc.name+"</a>")

@frappe.whitelist()
def make_acknowledgements(frm):
#       val=json.loads(frm)
        val=frm
        if val.vehicle_type == "Own Vehicle":
                        doc = frappe.new_doc("Acknowledgement")
                        doc.final_trip_sheet = val.name
                        doc.outstanding_amount = val.outstanding_amount
                        doc.vehicle_type_c = val.vehicle_type_c
                        doc.vehicle_type = val.vehicle_type
                        doc.customer = val.customer
                        doc.vehicle_reg_no = val.vehicle_reg_no
                        doc.save()
        if val.vehicle_type == "Market Vehicle":
                        doc = frappe.new_doc("Acknowledgement")
                        doc.final_trip_sheet = val.name
                        doc.outstanding_amount = val.outstanding_amount
                        doc.market_vehicle_no_c = val.market_vehicle_no_c
                        doc.vehicle_type = val.vehicle_type
                        doc.vehicle_type_c = val.vehicle_type_c
                        doc.market_vehicle_no_c = val.market_vehicle_no_c
                        doc.supplier = val.supplier
                        doc.save()

@frappe.whitelist()
def make_payment_entry(frm):
	val=frappe._dict(json.loads(frm))
	pe = frappe.new_doc("Payment Entry")
	if val.vehicle_type == "Own Vehicle":
		pe=frappe.new_doc("Payment Entry")
		pe.payment_type="Receive"
		pe.mode_of_payment="NEFT/RTGS/IMPS"
		pe.vehicle_no = val.vehicle_reg_no
		pe.party_type="Customer"
		pe.party=val.customer
		pe.party_name=val.customer
		pe.target_exchange_rate=1
#		pe.base_received_amount=self.advance_amount
		pe.paid_from= frappe.db.get_value("Company",{},"default_receivable_account")
		pe.paid_to= frappe.db.get_value("Company",{},"default_cash_account")
		pe.paid_from_account_currency="INR"
		pe.paid_to_account_currency="INR"
		pe.append("references",{"reference_doctype":"Final Trip Sheet","reference_name":val.name,"total_amount":val.total_lorry_hire,"outstanding_amount":val.total_lorry_hire,"allocated_amount":val.advance_amount})
		#pe.save()
		return pe


	if val.vehicle_type == "Market Vehicle":
		pe=frappe.new_doc("Payment Entry")
		pe.payment_type="Pay"
		pe.mode_of_payment="NEFT/RTGS/IMPS"
		pe.party_type="Supplier"
		pe.vehicle_no = val.market_vehicle_no_c
		pe.party=val.supplier
		pe.party_name=val.supplier
#		pe.paid_amount=self.market_advance_amount_c
#		pe.received_amount=self.market_advance_amount_c
		pe.target_exchange_rate=1
#		pe.base_received_amount=self.market_advance_amount_c
		pe.paid_from=frappe.db.get_value("Company",{},"default_cash_account")
		pe.paid_to=frappe.db.get_value("Company",{},"default_payable_account")
		pe.paid_from_account_currency="INR"
		pe.paid_to_account_currency="INR"
		pe.append("references",{"reference_doctype":"Final Trip Sheet","reference_name":val.name,"total_amount":val.market_lorry_hire_c,"outstanding_amount":val.market_lorry_hire_c,"allocated_amount":val.market_lorry_hire_c})
		return pe

@frappe.whitelist()
def get_address(val):
	address_name=frappe.db.get_value("Dynamic Link",{"link_doctype":"Consignee","link_name":val},"parent")
	address=get_address_display(address_name)
	return address_name

