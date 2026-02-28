// siya_clinic/public/js/crm_lead/form/lock_fields.js
// Loaded via hooks doctype_js for "CRM Lead"

frappe.ui.form.on('CRM Lead', {
  refresh(frm) {
    const is_new = frm.is_new();

    const is_tl  = frappe.user.has_role('Team Leader');
    const is_sys = frappe.user.has_role('System Manager') || frappe.session.user === 'Administrator';
    const is_agent = frappe.user.has_role('Agent');

    // ------------------------------------------------------------
    // 🔒 Field Locking (existing logic)
    // ------------------------------------------------------------
    if (!is_sys) {
      // lock field unless: it's new AND TL is creating
      const lock = (f) => frm.set_df_property(f, 'read_only', !(is_new && is_tl));
      ['sr_lead_pipeline','sr_lead_platform','source','mobile_no'].forEach(lock);
    }

    // ------------------------------------------------------------
    // 👁️ Hide Lead Owner for Agent only
    // ------------------------------------------------------------
    if (is_agent && !is_tl && !is_sys) {
      frm.set_df_property('lead_owner', 'hidden', 1);
    } else {
      frm.set_df_property('lead_owner', 'hidden', 0);
    }
  }
});
