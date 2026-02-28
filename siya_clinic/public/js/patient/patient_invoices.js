/**
 * Load Sales Invoices into Patient → Invoices tab
 * Child Table: sr_sales_invoice_list
 * Child DocType: SR Patient Invoice View
 */

frappe.ui.form.on("Patient", {
	refresh(frm) {
		// Do not run for new patient
		if (frm.is_new()) return;

		// Clear table before loading
		frm.clear_table("sr_sales_invoice_list");

		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Sales Invoice",
				filters: {
					patient: frm.doc.name,   // Healthcare link
					docstatus: 1             // Submitted only
				},
				fields: [
					"name",
					"posting_date",
					"grand_total",
					"outstanding_amount"
				],
				order_by: "posting_date desc",
				limit_page_length: 100
			},
			callback(r) {
				(r.message || []).forEach((inv) => {
					let row = frm.add_child("sr_sales_invoice_list");

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