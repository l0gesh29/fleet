// Copyright (c) 2021, Shivansh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip Sheet', {
	refresh: function(frm) {

		frm.add_custom_button("Customer Advance",function(){
			debugger;

			// frappe.call({
			// 	"method":"fleet.fleet.doctype.trip_sheet.trip_sheet.insert_Payment",
			// 	"args":{
			// 		"cur_doc":frm.doc.name
			// 	},
			// 	"callback":function(res){
			// 		console.log(res)
			// 		frappe.set_route('Form', 'Payment Entry', res.message);
			// 	}
			// })

			// var doc = frappe.model.get_new_doc('Payment Entry');
			let d = new frappe.ui.Dialog({
				title: 'Enter details',
				fields: [
					{
						label: 'Advance Amount',
						fieldname: 'price',
						fieldtype: 'Currency'
					}
				],
				primary_action_label: 'Submit',
				primary_action(values) {
					console.log(values);
					frappe.call({
						"method":"fleet.fleet.doctype.trip_sheet.trip_sheet.insert_Payment",
						"args":{
							"cur_doc":frm.doc.name,
							"price": values.price
						},
						"callback":function(res){
							console.log(res)
							frappe.msgprint("Customer Advance of " + values.price + " is created successfully for Customer " + frm.doc.consignor_c)
							// frappe.set_route('Form', 'Payment Entry', res.message);
						}
					})
					d.hide();
				}
			});
			
			d.show();
			// var doc = frappe.model.get_new_doc('Payment Entry');
			// doc.payment_type = 'Receive';
			// doc.posting_date = new Date();
			// doc.mode_of_payment = 'Cash';
			// doc.party_type = 'Customer';
			// doc.party = frm.doc.consignor_c;
			// doc.paid_from = 'Cash - A';
			// // doc.paid_amount = frm.doc.price;
			// frappe.set_route('Form', 'Payment Entry', doc.name);
		}, __("Create"))

		frm.add_custom_button("Sales Invoice",function(){
			frappe.call({
				"method":"fleet.fleet.doctype.trip_sheet.trip_sheet.insert_sales_invoice",
				"args":{
					"cur_doc":frm.doc.name
				},
				"callback":function(res){
					console.log(res)
					if(res.message =="success")
					{
						frappe.msgprint("Sales Invoice Successfully Created")
					}
					else{
						frappe.msgprint("Sales Invoice already Created, Kindly delete it first to make new Invoice")
					}
				}
			})
		}, __("Create"))

		frm.add_custom_button("Purchase Invoice",function(){
			debugger;

			var doc = frappe.model.get_new_doc('Purchase Invoice');
			doc.trip_sheet_no = frm.doc.name;
			doc.trip_vehicle_no = frm.doc.vehicle_no_c;
			
			frappe.set_route('Form', 'Purchase Invoice', doc.name);
		}, __("Create"))

		frm.add_custom_button("Expense Claim",function(){
			

			var doc = frappe.model.get_new_doc('Expense Claim');
			doc.trip_sheet = frm.doc.name;
			doc.vehicle_no_c = frm.doc.vehicle_no_c;
			doc.employee = frm.doc.employee
			
			frappe.set_route('Form', 'Expense Claim', doc.name);
		}, __("Create"))
	},
	loading_point_c: function(frm){
		if(frm.doc.loading_point_c){
			if(frm.doc.destination_c){
				if(frm.doc.destination_c == frm.doc.loading_point_c){
					frm.set_value("loading_point_c", "")
					frappe.throw("Loading Point and Destination Cannot be same.")
				}
				get_price(frm);
			}
		}
	},
	destination_c: function(frm){
		if(frm.doc.destination_c){
			if(frm.doc.loading_point_c){
				if(frm.doc.destination_c == frm.doc.loading_point_c){
					frm.set_value("destination_c", "")
					frappe.throw("Loading Point and Destination Cannot be same.")
				}
				get_price(frm);
			}
		}
	},
	is_return_trip: function(frm){
		if(frm.doc.destination_c){
			if(frm.doc.loading_point_c){
				get_price(frm);
			}
		}
	}
});


function get_price(frm){
	frappe.call({
		"method":"fleet.fleet.doctype.trip_sheet.trip_sheet.get_price",
		"args":{
			"from_dest":frm.doc.loading_point_c,
			"to_dest": frm.doc.destination_c
		},
		"callback":function(res){
			console.log(res)
			if(res.message != 0){
				if(frm.doc.is_return_trip == 0){
					frm.set_value("price",res.message[0].price)
				}
				else{
					frm.set_value("price",res.message[0].return_trip_price)
				}
			}
			else{
				frm.set_value("price",res.message)
			}
			refresh_field("price")
		}
	})
}
