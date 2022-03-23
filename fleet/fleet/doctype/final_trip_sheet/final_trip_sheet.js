// Copyright (c) 2022, Shivansh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Final Trip Sheet', {
	//refresh: function(frm) {
		refresh: function(frm) {
                if((frm.doc.docstatus == 1 )&& (frm.doc.outstanding_amount != 0)){
                       frm.add_custom_button(__('Create Acknowledgement'),()=>{
                                frm.events.create_acknowledgement(frm);
                       });
                }

        },

        consignee_c: function(frm){
                if (frm.doc.consignee_c) {
                                frappe.call({
                                        method: 'fleet.fleet.doctype.final_trip_sheet.final_trip_sheet.get_address',
                                        args: {
                                                "val":frm.doc.consignee_c
                                        },
                                        callback: function(r) {
                                               // frappe.errprint(r.message)
                                                frm.set_value("consignee_address", r.message);
                                                frm.refresh_field("consignee_address")
                                                frm.trigger("consignee_address")
                                        }
                                });
                        }
        },

		consignee_address: function(frm) {
			if (frm.doc.consignee_address) {
				frappe.call({
					method: 'frappe.contacts.doctype.address.address.get_address_display',
					args: {
						"address_dict": frm.doc.consignee_address
					},
					callback: function(r) {
						frm.set_value("consignee_address_display", r.message);
						frm.refresh_fields();
					}
				});
			}
			if (!frm.doc.consignee_address) {
				frm.set_value("consignee_address_display", "");
			}
		},
	create_acknowledgement:function(frm){
                return frappe.call({
                        method:"fleet.fleet.doctype.final_trip_sheet.final_trip_sheet.make_acknowledgement",
                        args: {
                                frm:frm.doc
                        },
                callback: function (r)
                {
//                      var doc = frappe.model.sync(r.message);
//                      frappe.set_route("Form", doc[0].doctype, doc[0].name);
                },
                });
        },

});


frappe.ui.form.on("Deduction",{
	rate: function(frm,cdt,cdn){
		const d=locals[cdt][cdn]
		if(d.rate){
			frappe.model.set_value(cdt,cdn,"amount",d.rate*d.quantity);
		}
	}

});
