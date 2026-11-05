/**
 * Load Sales Invoices into Patient → Invoices tab
 * Child Table: sr_sales_invoice_list
 * Child DocType: SR Patient Invoice View
 */

frappe.ui.form.on("Patient", {
	refresh(frm) {
		// Do not run for new patient
		if (frm.is_new()) return;

		const patient = frm.doc.name;
		const request = (frm.__siya_invoice_request || 0) + 1;
		frm.__siya_invoice_request = request;
		frm.clear_table("sr_sales_invoice_list");

		frappe.call({
			method: "siya_clinic.api.patient_invoices.get_patient_invoices",
			args: { patient, limit_page_length: 100 },
			callback(r) {
				if (frm.doc.name !== patient || frm.__siya_invoice_request !== request) return;
				frm.clear_table("sr_sales_invoice_list");
				(r.message || []).forEach((inv) => {
					// Summary rows must not mark the Patient as edited.
					let row = frappe.model.get_new_doc(
						frm.fields_dict.sr_sales_invoice_list.df.options, frm.doc, "sr_sales_invoice_list"
					);

					row.sr_invoice_no   = inv.name;
					row.sr_posting_date = inv.posting_date;
					row.sr_grand_total  = inv.grand_total;
					row.sr_outstanding  = inv.outstanding_amount;
				});

				frm.refresh_field("sr_sales_invoice_list");
			}
		});
	}
});