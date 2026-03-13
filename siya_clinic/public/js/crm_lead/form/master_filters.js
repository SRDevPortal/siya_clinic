// ======================================================
// CRM Lead Master Filters (Active-only)
// ======================================================

frappe.ui.form.on('CRM Lead', {
  setup(frm) {
    apply_active_master_filters(frm);
  }
});


// ------------------------------------------------------
// Apply active-only filters
// ------------------------------------------------------
function apply_active_master_filters(frm) {

  const active = { is_active: 1 };

  // Pipeline
  frm.set_query("sr_lead_pipeline", () => ({
    query: "siya_clinic.api.common.link_queries.master_query",
    filters: {
      ...active,
      field: "sr_pipeline_name",
      order: "asc"
    },
    page_length: 100
  }));

  // Platform
  frm.set_query("sr_lead_platform", () => ({
    query: "siya_clinic.api.common.link_queries.master_query",
    filters: {
      ...active,
      field: "sr_platform_name",
      order: "asc"
    },
    page_length: 100
  }));

  // Source
  frm.set_query("source", () => ({
    query: "siya_clinic.api.common.link_queries.master_query",
    filters: {
      ...active,
      field: "sr_source_name",
      order: "asc"
    },
    page_length: 100
  }));

  // Disease
  frm.set_query("sr_lead_disease", () => ({
    query: "siya_clinic.api.common.link_queries.master_query",
    filters: {
      ...active,
      field: "dept_disease_name",
      order: "asc"
    },
    page_length: 100
  }));

}