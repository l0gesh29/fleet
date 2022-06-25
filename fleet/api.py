from __future__ import unicode_literals
import frappe,json
from fleet.fleet.doctype.final_trip_sheet.final_trip_sheet import make_acknowledgements
from frappe.auth import LoginManager
from frappe.core.doctype.user.user import generate_keys
import base64
from frappe.utils import now
from frappe.contacts.doctype.address.address import get_address_display


@frappe.whitelist(allow_guest = True)
def update_trip_order(**args):
	doc = frappe.get_doc("Trip Sheet",args["name"])
	doc.consignor_c = args["consignor_c"]
	doc.loading_point_c = args["loading_point_c"]
	doc.branch = args["branch"]
	doc.destination_c = args["destination_c"]
	if args['one_way'] == 1:
		doc.one_way = 1
	elif args["two_way"] == 1:
		doc.two_way = 1
	doc.vehicle_type_c = args["vehicle_type_c"]
	doc.product_group_c = args["product_group_c"]
	doc.save()
	#doc.submit()
	#ta = frappe.db.get_value("Trip Allocation",{"linked_trip_order_c":doc.name},"name")
	#frappe.clear_messages()
	return {"success":1}

@frappe.whitelist(allow_guest = True)
def create_trip_order(**args):
	doc = frappe.new_doc("Trip Sheet")
	doc.consignor_c = args["consignor_c"]
	doc.loading_point_c = args["loading_point_c"]
	doc.branch = args["branch"]
	doc.destination_c = args["destination_c"]
	if args['one_way'] == 1:
		doc.one_way = 1
	elif args["two_way"] == 1:
		doc.two_way = 1
	doc.vehicle_type_c = args["vehicle_type_c"]
	doc.product_group_c = args["product_group_c"]
	doc.save()
	doc.submit()
	ta = frappe.db.get_value("Trip Allocation",{"linked_trip_order_c":doc.name},"name")
	frappe.clear_messages()
	return [{"Trip Order":doc.name,"Trip Allocation":ta,"Lorry Hire":doc.price}]



@frappe.whitelist(allow_guest = True)
def trip_allocation(**args):
	frappe.set_user('Administrator')
	doc = frappe.get_doc("Trip Allocation",args['name'])
	if doc.docstatus == 1:
		return "Already Submitted"
	if args['vehicle_type'] == "Own Vehicle":
		doc.vehicle_type = "Own Vehicle"
		doc.reference_c = args["reference_c"]
		doc.driver = args['market_driver_c']
		doc.customer = args['supplier']
		byte = args["rc_copy"]
		n = now() + "." + args["rc_extension"]
		path = "site1.local/public/files/" + n
		decodeit = open(path, 'wb')
		decodeit.write(base64.b64decode((byte)))
		decodeit.close()
		file = frappe.new_doc("File")
		file.file_url = "/files/"+ n
		file.save()
		doc.rc_copy = file.file_url
		byte = args["pan_copy"]
		n = now() + "." + args["pan_extension"]
		path = "site1.local/public/files/" + n
		decodeit = open(path, 'wb')
		decodeit.write(base64.b64decode((byte)))
		decodeit.close()
		file = frappe.new_doc("File")
		file.file_url = "/files/"+ n
		file.save()
		doc.pan_copy = file.file_url
		doc.driver_mobile = args['market_driver_mobile_c']
		doc.vehicle_reg_no = args['market_vehicle_no_c']
		doc.dl_no_c = args["dl_no_c"]
		doc.vehicle_type_c = args["vehicle_type_c"]
		doc.pan_no_c = args["pan_no_m"]
		doc.pan_h_name_c = args["pan_h_name_m"]
		doc.toll = args["toll"]
		doc.hamali = args["hamali"]
		doc.advance_amount = int(args["market_advance_amount_c"])
		doc.append("dr_table_c",{"loading_point_c":doc.loading_point_c,"destination_c":doc.destination_c})
		if args["define_route"] == 1:
			doc.define_route_c = 1
			for row in args["dr_table"]:
				doc.append("dr_table_c",{"loading_point_c":row["loading_point"],"destination_c":row["destination"]})
	if args['vehicle_type'] == "Market Vehicle":
		doc.vehicle_type = "Market Vehicle"
		doc.reference_c = args["reference_c"]
		doc.market_driver_c = args["market_driver_c"]
		doc.supplier = args["supplier"]
		doc.dl_no_m = args["dl_no_c"]
		byte = args["rc_copy"]
		n = now() + "." + args["rc_extension"]
		path = "site1.local/public/files/" + n
		decodeit = open(path, 'wb')
		decodeit.write(base64.b64decode((byte)))
		decodeit.close()
		file = frappe.new_doc("File")
		file.file_url = "/files/"+ n
		file.save()
		doc.rc_copy = file.file_url
		byte = args["pan_copy"]
		n = now() + "." + args["pan_extension"]
		path = "site1.local/public/files/" + n
		decodeit = open(path, 'wb')
		decodeit.write(base64.b64decode((byte)))
		decodeit.close()
		file = frappe.new_doc("File")
		file.file_url = "/files/"+ n
		file.save()
		doc.pan_copy = file.file_url
		doc.market_vehicle_no_c = args["market_vehicle_no_c"]
		doc.market_driver_mobile_c = args["market_driver_mobile_c"]
		doc.vehicle_type_c = args["vehicle_type_c"]
		doc.pan_no_m = args["pan_no_m"]
		doc.market_toll = args["toll"]
		doc.market_hamali = args["hamali"]
		doc.market_lorry_hire_c = int(args["market_lorry_hire_c"])
		doc.pan_h_name_m = args["pan_h_name_m"]
		doc.market_advance_amount_c = int(args["market_advance_amount_c"])
		doc.append("dr_table_c",{"loading_point_c":doc.loading_point_c,"destination_c":doc.destination_c})
		if args["define_route"] == 1:
			doc.define_route_c = 1
			for row in args["dr_table"]:
				doc.append("dr_table_c",{"loading_point_c":row["loading_point"],"destination_c":row["destination"]})
	doc.save()
	doc.submit()
	fts = frappe.db.get_list("Final Trip Sheet",{"linked_trip_allocation_c":doc.name},"name")
	frappe.clear_messages()
	return "Vehicle Allotted Successfully"


@frappe.whitelist(allow_guest = True)
def final_trip_sheet(**args):
#	return args
	doc = frappe.get_doc("Final Trip Sheet",args['name'])
	if doc.docstatus == 1:
		return "Already Submitted"
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
	byte = args["invoice_copy"]
	n = now() + "." + args["invoice_extension"]
	path = "site1.local/public/files/" + n
	decodeit = open(path, 'wb')
	decodeit.write(base64.b64decode((byte)))
	decodeit.close()
	file = frappe.new_doc("File")
	file.file_url = "/files/"+ n
	file.save()
	doc.invoice_copy = file.file_url
	doc.amount_c = args["amount"]
	doc.save()
	doc.submit()
	make_acknowledgements(doc)
	a = frappe.db.get_value("Acknowledgement",{"final_trip_sheet":doc.name},"name")
	return {"Acknowledgement":a}

@frappe.whitelist(allow_guest=True)
def login(mobile_no, password):
	login_manager=LoginManager()
	login_manager.authenticate(mobile_no,password)
	login_manager.post_login()
	doc_name = frappe.db.get_value("User",{"mobile_no":mobile_no},"name")
	if frappe.db.get_value("User",{"mobile_no":mobile_no},"api_secret"):
		api_secret = frappe.get_doc("User",doc_name).get_password("api_secret")
	else:
		api_secret=generate_keys(frappe.session.user)
		api_secret = api_secret["api_secret"]
	api_key=frappe.db.get_value("User",{'name':doc_name},'api_key')
	frappe.local.response["message"] = "Logged In"
	frappe.local.response["login"]={"api_key":api_key , "api_secret":api_secret,"username":doc_name}
	#except Exception as e:
	#	frappe.local.response["message"] = {
	#		"success_key":0
	#	}





@frappe.whitelist(allow_guest = True)
def consignor():
	consignor = frappe.db.get_list("Consignor",{},"name")
	return consignor



@frappe.whitelist(allow_guest = True)
def consignee():
	frappe.set_user('Administrator')
	consignee = frappe.db.get_list("Consignee",{},"name")
	return consignee

@frappe.whitelist(allow_guest = True)
def destination():
	frappe.set_user('Administrator')
	destination = frappe.db.get_list("Destination",{},"name")
	return destination

@frappe.whitelist(allow_guest = True)
def branches():
	frappe.set_user('Administrator')
	branches = frappe.db.get_list("Branches",{},"name")
	return branches


@frappe.whitelist(allow_guest = True)
def truck():
	frappe.set_user('Administrator')
	truck = frappe.db.get_list("Truck",{},"name")
	return truck


@frappe.whitelist(allow_guest = True)
def truck_type():
	frappe.set_user('Administrator')
	truck_type = frappe.db.get_list("Truck Type",{},"name")
	return truck_type


@frappe.whitelist(allow_guest = True)
def truck_driver():
	frappe.set_user('Administrator')
	truck_driver = frappe.db.get_list("Truck Driver",{},"name")
	return truck_driver


@frappe.whitelist(allow_guest = True)
def customer():
	frappe.set_user('Administrator')
	customer = frappe.db.get_list("Customer",{},"name")
	return customer



@frappe.whitelist(allow_guest = True)
def supplier():
	frappe.set_user('Administrator')
	supplier = frappe.db.get_list("Supplier",{},"name")
	return supplier

@frappe.whitelist(allow_guest = True)
def product_group():
	#frappe.set_user('Administrator')
	product_group = frappe.db.sql("""SELECT name FROM `tabItem Group` ORDER BY name ASC""",as_dict=True)
	return product_group

@frappe.whitelist(allow_guest = True)
def package():
	package = frappe.db.sql("""SELECT name FROM `tabItem` where disabled=0 ORDER BY name ASC""",as_dict=True)
	return package


@frappe.whitelist(allow_guest = True)
def unit():
	unit = frappe.db.sql("""SELECT name FROM `tabUOM` where enabled=1 ORDER BY name ASC""",as_dict=True)
	return unit
@frappe.whitelist(allow_guest = True)
def destination_filter(branch):
	frappe.set_user('Administrator')
	b = frappe.db.get_list("Destination Table",{"parent":branch},"destination")
	if b:
		b_l = []
		for row in b:
			b_l.append(row.destination)
		return b_l
	else:
		return b
@frappe.whitelist(allow_guest = True)
def loading_point_and_branch_filter(consignor):
	frappe.set_user('Administrator')
	b =frappe.db.sql("""select loading_point_c as loading_point,branch_c as branch from `tabConsignor` where name=%s """,(consignor),as_dict=1)
	if b:
		return b[0]
	else:
		return {}
@frappe.whitelist(allow_guest = True)
def vehicle_type_filter(consignor):
	frappe.set_user('Administrator')
	v_t = frappe.db.get_list("Vehicle Type Table",{"parent":consignor},"vehicle_type")
	if v_t:
		v = []
		for row in v_t:
			v.append(row.vehicle_type)
		return v
	else:
		return v_t



@frappe.whitelist(allow_guest = True)
def trip_order(username):
	return frappe.db.sql("""select t.name as order_no ,t.docstatus ,t.consignor_c, t.branch ,t.loading_point_c , t.destination_c , t.one_way , t.two_way ,t.no_of_vehicles,t.date_c,t.vehicle_type_c,t.product_group_c,ta.name as allocation_no from `tabTrip Sheet` as t join `tabTrip Allocation` as ta on t.name = ta.linked_trip_order_c where t.owner = '{0}'and t.docstatus!=2 Order By t.name DESC""".format(username),as_dict=True)



@frappe.whitelist(allow_guest = True)
def get_trip_allocation(username):
	ta = frappe.db.sql("""select name from `tabTrip Allocation` where owner='{0}' and docstatus!=2 Order By name DESC""".format(username),as_dict=True)
	ta_list = []
	for row in ta:
		doct = frappe.get_doc("Trip Allocation", row.name)
		doc = frappe._dict(doct.__dict__)
		doc.pop("_meta")
		ta_list.append(doc)
	return ta_list



@frappe.whitelist(allow_guest = True)
def get_final_trip_sheet(username):
	fts = frappe.db.sql("""select name from `tabFinal Trip Sheet` where owner='{0}' and docstatus!=2 Order By name DESC """.format(username),as_dict=True)
	fts_list = []
	for row in fts:
		doct = frappe.get_doc("Final Trip Sheet",row.name)
		if doct.rc_copy:
			doct.rc_copy = "http://68.183.95.177/" + doct.rc_copy
		if doct.pan_copy:
			doct.pan_copy = "http://68.183.95.177/" + doct.pan_copy
		doc = frappe._dict(doct.__dict__)
		doc.pop("_meta")
		fts_list.append(doc)
	return fts_list


@frappe.whitelist(allow_guest = True)
def amend(name):
	doc = frappe.get_doc("Trip Allocation",name)
	if doc.docstatus != 1:
		return "Please Submit the Allocation"
	else:
		doc.cancel()
		new_doc = frappe.copy_doc(doc)
		new_doc.save()
		return {"Trip Allocation":new_doc.name}


@frappe.whitelist(allow_guest = True)
def lorry_hire_amount(trip_allocation):
	amount = frappe.db.sql("""Select lorry_hire from `tabTrip Allocation` where name='{0}'""".format(trip_allocation),as_list = True)
	if amount[0][0]:
		return {"amount":amount[0][0]}
	else:
		return "Amount not specified in LH master"


@frappe.whitelist(allow_guest = True)
def get_consignee_address(val):
	address_name=frappe.db.get_value("Dynamic Link",{"link_doctype":"Consignee","link_name":val},"parent")
	if address_name:
		address = get_address_display(address_name)
		return {"name" : address_name,"address" : address.replace("<br>"," ")}
	else:
		return "Address not Found"

@frappe.whitelist(allow_guest = True)
def get_consignor_address(val):
	address_name=frappe.db.get_value("Dynamic Link",{"link_doctype":"Consignor","link_name":val},"parent")
	if address_name:
		address = get_address_display(address_name)
		return {"name" : address_name,"address" : address.replace("<br>"," ")}
	else:
		return "Address not Found"



@frappe.whitelist(allow_guest = True)
def trip_allocation_link():
        ta = frappe.db.sql("""select name from `tabTrip Allocation` where docstatus=1""",as_dict=True)
        return ta




@frappe.whitelist()
def autoname(self,method):
	if self.duplicate_entry:
		#frappe.errprint(self.name)
		duplicate_len = len(frappe.db.get_list("Final Trip Sheet",{"linked_trip_allocation_c":self.linked_trip_allocation_c ,"duplicate_entry":1},["name"]))
		#frappe.errprint(self.name)
		original_entry = frappe.db.get_value("Final Trip Sheet",{"linked_trip_allocation_c":self.linked_trip_allocation_c ,"duplicate_entry":0},"name")
		self.name = original_entry + "-" + chr(65+duplicate_len)




@frappe.whitelist()
def email(fts):
	fts = frappe.get_doc("Final Trip Sheet",fts)
	if fts.docstatus != 1:
		return "Submit the Final Trip Sheet"
	else:
		if fts.email:
			fts.email = 0
		else:
			fts.email = 1
	fts.save()
	fts.submit()
	return {"success":1}
