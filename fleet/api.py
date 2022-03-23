from __future__ import unicode_literals
import frappe
from fleet.fleet.doctype.final_trip_sheet.final_trip_sheet import make_acknowledgements
from frappe.auth import LoginManager
from frappe.core.doctype.user.user import generate_keys

@frappe.whitelist(allow_guest = True)
def create_trip_order(**args):
	doc = frappe.new_doc("Trip Sheet")
	doc.branch = args["branch"]
	doc.consignor_c = args["consignor_c"]
	doc.destination_c = args["destination_c"]
	doc.loading_point_c = args["loading_point_c"]
	if args['one_way']:
		doc.one_way=1
	if args['two_way']:
		doc.two_way=1
	doc.vehicle_type_c = args["vehicle_type_c"]
	doc.product_group_c = args["product_group_c"]
	doc.save()
	doc.submit()
	ta = frappe.db.get_value("Trip Allocation",{"linked_trip_order_c":doc.name},"name")
	frappe.clear_messages()
	return [{"Trip Order":doc.name,"Trip Allocation":ta,"Lorry Hire":doc.price}]



@frappe.whitelist(allow_guest = True)
def trip_allocation(**args):
	doc = frappe.get_doc("Trip Allocation",args['name'])
	if args['vehicle_type'] == "Own Vehicle":
		doc.vehicle_type = "Own Vehicle"
		doc.reference_c = args["reference_c"]
		doc.driver = args['driver']
		doc.customer = args['customer']
		doc.driver_mobile = args['driver_mobile']
		doc.vehicle_reg_no = args['vehicle_reg_no']
		doc.dl_no_c = args["dl_no_c"]
		doc.vehicle_type_c = args["vehicle_type_c"]
		doc.pan_no_c = args["pan_no_c"]
		doc.pan_h_name_c = args["pan_h_name_c"]
		doc.advance_amount = args["advance_amount"]
	if args['vehicle_type'] == "Market Vehicle":
		doc.vehicle_type = "Market Vehicle"
		doc.reference_c = args["reference_c"]
		doc.market_driver_c = args["market_driver_c"]
		doc.supplier = args["supplier"]
		doc.dl_no_m = args["dl_no_m"]
		doc.market_vehicle_no_c = args["market_vehicle_no_c"]
		doc.market_driver_mobile_c = args["market_driver_mobile_c"]
		doc.vehicle_type_c = args["vehicle_type_c"]
		doc.pan_no_m = args["pan_no_m"]
		doc.market_lorry_hire_c = args["market_lorry_hire_c"]
		doc.pan_h_name_m = args["pan_h_name_m"]
		doc.market_advance_amount_c = args["market_advance_amount_c"]
	doc.save()
	doc.submit()
	fts = frappe.db.get_value("Final Trip Sheet",{"linked_trip_allocation_c":doc.name},"name")
	frappe.clear_messages()
	return [{"Final Trip Sheet":fts,"consignor_address":doc.consigner_address_display}]

@frappe.whitelist(allow_guest = True)
def final_trip_sheet(args):
#	return args
	doc = frappe.get_doc("Final Trip Sheet",args['name'])
	doc.consignor_mobile_no_c = args["consignor_mobile_no_c"]
	doc.consignee_c = args["consignee_c"]
	doc.consignee_mobile_no_c = args["consignee_mobile_no_c"]
	#return args
	for row in args["items"]:
		#return row
		doc.append("item",{"packages_c":row['packages_c'],"weight_c":row['weight_c'],"quantity_c":row['quantity_c'],"unit_c":row["unit_c"],"remarks_c":row["remarks_c"]})
	doc.e_way_bill_no = args["e_way_bill_no"]
	doc.invoice_no_c = args["invoice_no_c"]
	doc.shipment_no_c = args["shipment_no_c"]
	doc.grn_c = args["grn_c"]
	doc.po_no_c = args["po_no_c"]
	doc.save()
	doc.submit()
	make_acknowledgements(doc)
	a = frappe.db.get_value("Acknowledgement",{"final_trip_sheet":doc.name},"name")
	return [{"Acknowledgement":a}]



@frappe.whitelist(allow_guest=True)
def login(username, password):
	login_manager=LoginManager()
	login_manager.authenticate(username,password)
	frappe.set_user('Administrator')
	doc_name = frappe.db.get_value("User",{'username':username})
	api_secret=generate_keys(doc_name)
	#role=frappe.db.get_value("User",{'name':doc_name},'role_profile_name')
	api_key=frappe.db.get_value("User",{'name':doc_name},'api_key')
	frappe.local.response["message"] = "Logged In"
	frappe.local.response["login"]={"api_key":api_key , "api_secret":api_secret['api_secret']}




@frappe.whitelist(allow_guest = True)
def consignor():
	consignor = frappe.db.get_list("Consignor",{},"name")
	return consignor



@frappe.whitelist(allow_guest = True)
def consignee():
	consignee = frappe.db.get_list("Consignee",{},"name")
	return consignee

@frappe.whitelist(allow_guest = True)
def destination():
	destination = frappe.db.get_list("Destination",{},"name")
	return destination

@frappe.whitelist(allow_guest = True)
def branches():
	branches = frappe.db.get_list("Branches",{},"name")
	return branches


@frappe.whitelist(allow_guest = True)
def truck():
        truck = frappe.db.get_list("Truck",{},"name")
        return truck


@frappe.whitelist(allow_guest = True)
def truck_type():
	truck_type = frappe.db.get_list("Truck Type",{},"name")
	return truck_type


@frappe.whitelist(allow_guest = True)
def truck_driver():
	truck_driver = frappe.db.get_list("Truck Driver",{},"name")
	return truck_driver


@frappe.whitelist(allow_guest = True)
def customer():
	customer = frappe.db.get_list("Customer",{},"name")
	return customer



@frappe.whitelist(allow_guest = True)
def supplier():
	supplier = frappe.db.get_list("Supplier",{},"name")
	return supplier

@frappe.whitelist(allow_guest = True)
def product_group():
	product_group = frappe.db.get_list("Item Group",{},"name")
	return product_group


@frappe.whitelist(allow_guest = True)
def destination_filter(branch):
	b = frappe.db.get_list("Destination Table",{"parent":branch},"destination")
	if b:
		b_l = []
		for row in b:
			b_l.append(row.destination)
		return b_l
	else:
		return b



@frappe.whitelist(allow_guest = True)
def vehicle_type_filter(consignor):
	v_t = frappe.db.get_list("Vehicle Type Table",{"parent":consignor},"vehicle_type")
	if v_t:
		v = []
		for row in v_t:
			v.append(row.vehicle_type)
		return v
	else:
		return v_t
