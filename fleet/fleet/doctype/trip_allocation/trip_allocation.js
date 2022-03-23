// Copyright (c) 2022, Shivansh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip Allocation', {
	refresh: function(frm) {
//		if((frm.doc.docstatus == 1 )&& (frm.doc.outstanding_amount != 0)){
//			frm.add_custom_button(__('Payment Entry'),()=>{
//				frm.events.create_payment_entry(frm);
//			});
//		}

	},
	customer : function(frm){
		if(frm.doc.customer){
			frm.set_query("vehicle_reg_no", function() {
				return {
					"filters":{
						"customer": frm.doc.customer
					},
				};
			});

		}
	},
	//console.log("in")
	create_payment_entry:function(frm){
		return frappe.call({
			method:"fleet.fleet.doctype.trip_allocation.trip_allocation.make_payment_entry",
			args: {
				frm:frm.doc
			},
		callback: function (r)
		{
//			var doc = frappe.model.sync(r.message);
//			frappe.set_route("Form", doc[0].doctype, doc[0].name);
		},
		});
	}
});
