# Copyright (c) 2022, Shivansh and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


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



@frappe.whitelist()
def create_sales_invoice(name,customer):
	ack = frappe.get_doc("Acknowledgement",name)
	fts = frappe.get_doc("Final Trip Sheet",ack.final_trip_sheet)
	doc = frappe.new_doc("Sales Invoice")
	doc.customer = customer
	doc.due_date = today()
	item_code = frappe.db.get_value("Item",{"invoice_item":1},"name")
	item_doc = frappe.get_doc("Item",item_code)
	doc.append("items",{"item_code":item_code,"description":item_doc.description,"uom":item_doc.stock_uom,"qty":1})
	if ack.vehicle_type == "Own Vehicle":
		doc.append("acknowledgement_item",{"date":ack.date_c,"consigne_no":ack.name,"from":ack.loading_point_c,"to":ack.destination_c,"vehicle_no":ack.vehicle_reg_no,"vehicle_type":ack.vehicle_type_c,"distributor":ack.consignor_c,"total_amount":ack.lorry_hire,"trip_id":fts.trip_id_no,"load_id_1":fts.load_id1,"load_id_2":fts.load_id2,"invoice_no":fts.invoice_no_c})
	doc.save()
	return doc


#"trip_id":"","load_id_1":"","load_id_2":""
