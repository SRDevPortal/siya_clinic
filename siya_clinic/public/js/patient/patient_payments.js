/**
 * Load Payment Entries into Patient → Payments tab
 * Child Table: sr_payment_entry_list
 * Child DocType: SR Patient Payment View
 */

frappe.ui.form.on("Patient", {
	refresh(frm) {
		if (frm.is_new()) return;

		const patient = frm.doc.name;
		const request = (frm.__siya_payment_request || 0) + 1;
		frm.__siya_payment_request = request;

		let filters = {
			docstatus: 1
		};

		// Healthcare setups vary → support both
		if (frm.doc.customer) {
			filters.party_type = "Customer";
			filters.party = frm.doc.customer;
		} else {
			filters.party_type = "Patient";
			filters.party = frm.doc.name;
		}

		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Payment Entry",
				filters: filters,
				fields: [
					"name",
					"posting_date",
					"paid_amount",
					"mode_of_payment",
					"reference_no",
					"reference_date"
				],
				order_by: "posting_date desc",
				limit_page_length: 100
			},
			callback(r) {
				if (frm.doc.name !== patient || frm.__siya_payment_request !== request) return;
				frm.clear_table("sr_payment_entry_list");
				(r.message || []).forEach((pay) => {
					// Summary rows must not mark the Patient as edited.
					let row = frappe.model.get_new_doc(
						frm.fields_dict.sr_payment_entry_list.df.options, frm.doc, "sr_payment_entry_list"
					);

					row.sr_payment_entry = pay.name;
					row.sr_posting_date = pay.posting_date;
					row.sr_paid_amount = pay.paid_amount;
					row.sr_mode_of_payment = pay.mode_of_payment;
					row.sr_reference_no = pay.reference_no;
					row.sr_reference_date = pay.reference_date;
				});

				frm.refresh_field("sr_payment_entry_list");
			}
		});
	},
});