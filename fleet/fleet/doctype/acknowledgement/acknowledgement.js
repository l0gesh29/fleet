// Copyright (c) 2022, Shivansh and contributors
// For license information, please see license.txt


frappe.ui.form.on('Acknowledgement', {
        //refresh: function(frm) {
	refresh: function(frm) {
		if((frm.doc.docstatus == 1 )&& (frm.doc.outstanding_amount != 0)){
			frm.add_custom_button(__('Create Payment Entry'),()=>{
				frm.events.create_payment_entry(frm);
			});
		}
		if((frm.doc.docstatus == 1 )&& (!frm.doc.sales_invoice)){
			frm.add_custom_button(__('Create Sales Invoice'),()=>{
                                frm.events.create_sales_invoice(frm);
                        });
		}
	},



	create_payment_entry:function(frm){
		return frappe.call({
			method:"fleet.fleet.doctype.trip_allocation.trip_allocation.make_payment_entry",
			args: {
				frm:frm.doc
			},
			callback: function (r)
			{
//                      	var doc = frappe.model.sync(r.message);
//                      	frappe.set_route("Form", doc[0].doctype, doc[0].name);
			},
			});
	},
	create_sales_invoice:function(frm){
		let d = new frappe.ui.Dialog({
    		title: 'Enter Customer',
    		fields: [
        			{
		        	    label: 'Customer',
	        		    fieldname: 'customer',
	        		    fieldtype: 'Link',
				    options: 'Customer',
				    reqd: 1
	        		}
    			],
   		 primary_action_label: 'Submit',
   		 primary_action(values) {
//       		 console.log(values);
        	 d.hide();
			return frappe.call({
                        	method:"fleet.fleet.doctype.acknowledgement.acknowledgement.create_sales_invoice",
                       	 	args: {
                        	        name:frm.doc.name,
					customer:values.customer
                        	},
                       	 	callback: function (r)
                        	{
                        	      var doc = frappe.model.sync(r.message);
                              		frappe.set_route("Form", doc[0].doctype, doc[0].name);
                        	},
                        });
    		}
		});

		d.show();
        },

});

