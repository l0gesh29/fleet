// Copyright (c) 2022, Shivansh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consignor', {
	refresh: function(frm) {
		frappe.dynamic_link = {doc: frm.doc, fieldname: 'name', doctype: 'Consignor'}
		frm.toggle_display(['address_html','contact_html'], !frm.doc.__islocal);
		if (frm.doc.__islocal) {
			frm.set_df_property('address_and_contact_section', 'hidden', 1);
			frappe.contacts.clear_address_and_contact(frm);
		}
		else {
			frm.set_df_property('address_and_contact_section', 'hidden', 0);
			frappe.contacts.render_address_and_contact(frm);
		}
	}
});
