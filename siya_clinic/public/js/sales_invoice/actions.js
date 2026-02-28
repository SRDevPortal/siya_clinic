// Sales Invoice actions (Print Payment + Patient Dashboard)

frappe.ui.form.on('Sales Invoice', {
  refresh(frm) {

    // 🧾 Print Payment Entry
    frm.add_custom_button(__('Print Payment'), async () => {
      try {
        const r = await frappe.call({
          method: 'siya_clinic.api.sales_invoice.pe_lookup.get_payment_entries_for_invoice',
          args: { si_name: frm.doc.name },
        });

        const rows = r.message || [];
        if (!rows.length) {
          frappe.msgprint(__('No Payment Entry found for this Sales Invoice.'));
          return;
        }

        let pe_name = rows[0].name;

        if (rows.length > 1) {
          const options = rows.map(d => ({
            label: `${d.name} (${d.status || (d.docstatus ? 'Submitted' : 'Draft')})`,
            value: d.name,
          }));

          const dlg = new frappe.ui.Dialog({
            title: __('Select Payment Entry to print'),
            fields: [{ fieldname: 'pe', label: 'Payment Entry', fieldtype: 'Select', options }],
            primary_action_label: __('Print'),
            primary_action(values) {
              pe_name = values.pe;
              dlg.hide();
              open_print(pe_name);
            }
          });

          dlg.set_value('pe', pe_name);
          dlg.show();
        } else {
          open_print(pe_name);
        }

      } catch (e) {
        console.error(e);
        frappe.msgprint(__('Could not fetch Payment Entries.'));
      }
    });

    // 👤 Patient Dashboard
    if (frm.doc.patient) {
      frm.add_custom_button(__('Patient Dashboard'), () => {
        frappe.set_route('Form', 'Patient', frm.doc.patient);
      });
    }
  },
});

function open_print(pe_name) {
  const url = `/printview?doctype=Payment%20Entry&name=${encodeURIComponent(pe_name)}`;
  window.open(frappe.urllib.get_full_url(url), '_blank');
}