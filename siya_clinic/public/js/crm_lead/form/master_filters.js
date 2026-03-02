// ======================================================
// CRM Lead Master Filters (Active-only)
// ======================================================

frappe.ui.form.on('CRM Lead', {

  onload(frm) {
    apply_active_master_filters(frm);
  },

  refresh(frm) {
    apply_active_master_filters(frm);
  }

});

// ------------------------------------------------------
// Apply active-only filters
// ------------------------------------------------------
function apply_active_master_filters(frm) {

  // 🔹 Pipeline → active only
  frm.set_query('sr_lead_pipeline', () => ({
    filters: { is_active: 1 }
  }));

  // 🔹 Platform → active only
  frm.set_query('sr_lead_platform', () => ({
    filters: { is_active: 1 }
  }));

  // 🔹 Source → active only (SR Lead Source)
  frm.set_query('source', () => ({
    filters: { is_active: 1 }
  }));

  // 🔹 Disposition → active + status filter
  frm.set_query('sr_lead_disposition', () => ({
    filters: {
      sr_lead_status: frm.doc.status || '',
      is_active: 1
    }
  }));
}
