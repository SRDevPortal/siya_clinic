frappe.ui.form.on('Payment Entry', {
  refresh(frm) {

    // 🔎 View Sales Invoice
    frm.add_custom_button(__('View Sales Invoice'), async () => {
      try {
        const r = await frappe.call({
          method: 'siya_clinic.api.sales_invoice.pe_lookup.get_sales_invoices_for_payment_entry',
          args: { pe_name: frm.doc.name },
        });
        const rows = r.message || [];

        if (!rows.length) {
          frappe.msgprint(__('No Sales Invoice is linked to this Payment Entry.'));
          return;
        }

        let si_name = rows[0].name;

        if (rows.length > 1) {
          const labels = rows.map(d => `${d.name} (${d.status || (d.docstatus ? 'Submitted' : 'Draft')})`);
          const values = rows.map(d => d.name);
          const options = labels.map((label, i) => ({ label, value: values[i] }));

          const dlg = new frappe.ui.Dialog({
            title: __('Select Sales Invoice'),
            fields: [{ fieldname: 'si', label: 'Sales Invoice', fieldtype: 'Select', options }],
            primary_action_label: __('Open'),
            primary_action: (values) => {
              si_name = values.si;
              dlg.hide();
              frappe.set_route('Form', 'Sales Invoice', si_name);
            }
          });

          dlg.set_value('si', si_name);
          dlg.show();
        } else {
          frappe.set_route('Form', 'Sales Invoice', si_name);
        }

      } catch (e) {
        console.error(e);
        frappe.msgprint(__('Could not look up related Sales Invoices.'));
      }
    });

    // 👤 Patient Dashboard
    frm.add_custom_button(__('Patient Dashboard'), async () => {
      try {
        const r = await frappe.call({
          method: 'siya_clinic.api.si_payment_flow.pe_lookup.get_sales_invoices_for_payment_entry',
          args: { pe_name: frm.doc.name },
        });
        const rows = r.message || [];
        const with_patient = rows.filter(r => r.patient);

        if (!with_patient.length) {
          frappe.msgprint(__('No Patient found on linked Sales Invoice(s).'));
          return;
        }

        let patient = with_patient[0].patient;
        const uniquePatients = [...new Set(with_patient.map(r => r.patient))];

        if (uniquePatients.length > 1) {
          const dlg = new frappe.ui.Dialog({
            title: __('Select Patient'),
            fields: [{ fieldname: 'patient', label: 'Patient', fieldtype: 'Select', options: uniquePatients.join('\n') }],
            primary_action_label: __('Open'),
            primary_action: (values) => {
              patient = values.patient;
              dlg.hide();
              open_patient_form(patient);
            }
          });
          dlg.set_value('patient', patient);
          dlg.show();
        } else {
          open_patient_form(patient);
        }

      } catch (e) {
        console.error(e);
        frappe.msgprint(__('Could not determine Patient for this Payment Entry.'));
      }
    });

  },
});

function open_patient_form(patient_name) {
  frappe.set_route('Form', 'Patient', patient_name);
}