// // siya_clinic/public/js/crm_lead/form/lock_fields.js
// // Loaded via hooks doctype_js for "CRM Lead"

frappe.ui.form.on('CRM Lead', {
  refresh(frm) {

    const is_tl  = frappe.user.has_role('Team Leader');
    const is_sys = frappe.user.has_role('System Manager') || frappe.session.user === 'Administrator';
    const is_agent = frappe.user.has_role('Agent');

    const fields = ['sr_lead_pipeline','sr_lead_platform','source','mobile_no'];

    // ------------------------------------------------------------
    // 🔒 Reset all fields first (safe practice)
    // ------------------------------------------------------------
    fields.forEach(f => frm.set_df_property(f, 'read_only', 1));
    frm.set_df_property('lead_owner', 'read_only', 1);
    frm.set_df_property('lead_owner', 'hidden', 0);

    // ------------------------------------------------------------
    // 👑 System Manager / Administrator
    // ------------------------------------------------------------
    if (is_sys) {
      fields.forEach(f => frm.set_df_property(f, 'read_only', 0));
      frm.set_df_property('lead_owner', 'read_only', 0);
    }

    // ------------------------------------------------------------
    // 👨‍💼 Team Leader
    // ------------------------------------------------------------
    else if (is_tl) {

      if (frm.is_new()) {
        // ✅ Only on NEW → allow editing
        fields.forEach(f => frm.set_df_property(f, 'read_only', 0));
        frm.set_df_property('lead_owner', 'read_only', 0);
      }

      else {
        // ❌ After save → lock
        frm.set_df_property('lead_owner', 'read_only', 0);
      }
    }

    // ------------------------------------------------------------
    // 👨‍💻 Agent
    // ------------------------------------------------------------
    else if (is_agent) {
      // ❌ Never allowed
      frm.set_df_property('lead_owner', 'hidden', 1);
      frm.set_df_property('lead_owner', 'read_only', 1);
    }
  }
});
