// Lead Disposition rules for CRM Lead (final production version)
frappe.ui.form.on('CRM Lead', {

  // Run when form loads
  onload(frm) {
    frm.trigger('apply_lead_disposition_rules');
  },

  // Run on refresh
  refresh(frm) {
    frm.trigger('apply_lead_disposition_rules');
  },

  // When status changes
  status(frm) {
    // Clear disposition when status changes
    if (frm.doc.sr_lead_disposition) {
      frm.set_value('sr_lead_disposition', null);
    }

    frm.trigger('apply_lead_disposition_rules');
  },

  // Core logic
  apply_lead_disposition_rules(frm) {
    const status = (frm.doc.status || '').trim();

    // 🔹 No status → hide & not required
    if (!status) {
      frm.toggle_display('sr_lead_disposition', false);
      frm.toggle_reqd('sr_lead_disposition', false);
      return;
    }

    // 🔹 Apply filter for dropdown options
    frm.set_query('sr_lead_disposition', () => ({
      filters: {
        sr_lead_status: status,   // field on SR Lead Disposition
        is_active: 1
      }
    }));

    // 🔹 Capture current status to avoid race conditions
    const current_status = status;

    // 🔹 Check if dispositions exist for this status
    frappe.db.count('SR Lead Disposition', {
      filters: { sr_lead_status: status, is_active: 1 }
    }).then(count => {

      // 🚫 Prevent race condition if user changed status quickly
      if ((frm.doc.status || '').trim() !== current_status) return;

      const show = count > 0;

      // 🔹 Show/hide field
      frm.toggle_display('sr_lead_disposition', show);

      // 🔹 Required only when options exist
      frm.toggle_reqd('sr_lead_disposition', show);

      // 🔹 Clear invalid value if hiding field
      if (!show && frm.doc.sr_lead_disposition) {
        frm.set_value('sr_lead_disposition', null);
      }
    });
  }
});
