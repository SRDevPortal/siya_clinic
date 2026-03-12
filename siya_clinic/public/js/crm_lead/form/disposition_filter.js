// ======================================================
// CRM Lead Disposition Rules
// ======================================================

frappe.ui.form.on('CRM Lead', {

  setup(frm) {
    apply_lead_disposition_rules(frm);
  },

  refresh(frm) {
    apply_lead_disposition_rules(frm);
  },

  // When status changes
  status(frm) {

    // Clear disposition when status changes
    if (frm.doc.sr_lead_disposition) {
      frm.set_value('sr_lead_disposition', null);
    }

    apply_lead_disposition_rules(frm);
  }

});

// ------------------------------------------------------
// Core Logic
// ------------------------------------------------------
function apply_lead_disposition_rules(frm) {

  const status = (frm.doc.status || '').trim();

  // No status → hide field
  if (!status) {
    frm.toggle_display('sr_lead_disposition', false);
    frm.toggle_reqd('sr_lead_disposition', false);
    return;
  }

  // Apply dropdown filter
  frm.set_query('sr_lead_disposition', () => ({
    filters: {
      sr_lead_status: status,
      is_active: 1
    },
    page_length: 100
  }));

  // Capture current status to avoid race conditions
  const current_status = status;

  // Check if dispositions exist
  frappe.db.count('SR Lead Disposition', {
    filters: {
      sr_lead_status: status,
      is_active: 1
    }
  }).then(count => {

    // Prevent race condition
    if ((frm.doc.status || '').trim() !== current_status) return;

    const show = count > 0;

    // Show / hide field
    frm.toggle_display('sr_lead_disposition', show);

    // Required only when options exist
    frm.toggle_reqd('sr_lead_disposition', show);

    // Clear invalid value
    if (!show && frm.doc.sr_lead_disposition) {
      frm.set_value('sr_lead_disposition', null);
    }

  });

}