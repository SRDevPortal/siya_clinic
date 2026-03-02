// siya_clinic/public/js/encounter/patient_encounter.js

console.log("Patient Encounter JS file loaded");

frappe.ui.form.on('Patient Encounter', {
    
    // -----------------------------
    // Form Load
    // -----------------------------
    onload(frm) {
        apply_encounter_access_rules(frm);
        apply_active_master_filters(frm);
    },

    refresh(frm) {
        apply_encounter_access_rules(frm);
        apply_active_master_filters(frm);

        if (!frm.is_new()) {
            intercept_s3_attachments(frm);
        }
    },

    // -----------------------------
    // Field Triggers
    // -----------------------------
    sr_encounter_type(frm) {
        handle_encounter_source_requirement(frm);
    },

    sr_encounter_place(frm) {
        handle_encounter_source_requirement(frm);
    },

    // ✅ Template selection handler
    item_group_template(frm) {
        const template = frm.doc.item_group_template;

        // 🟠 If cleared → clear items
        if (!template) {
            frm.clear_table('sr_pe_order_items');
            frm.refresh_field('sr_pe_order_items');

            frappe.show_alert({
                message: __('Order items cleared'),
                indicator: 'orange'
            });

            frm._template_loaded = null;
            return;
        }

        // 🟢 Load template items
        load_items_from_template(frm);
    }
});


// ==========================================================
// Load Items from Item Group Template → Order Items
// ==========================================================
function load_items_from_template(frm) {
    const template = frm.doc.item_group_template;
    if (!template) return;

    // Prevent duplicate reload
    if (frm._template_loaded === template) return;
    frm._template_loaded = template;

    // Clear existing rows
    frm.clear_table('sr_pe_order_items');

    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Item Group Template",
            name: template
        },
        callback: function(r) {
            if (!r.message) return;

            const template_doc = r.message;

            (template_doc.items || []).forEach(item => {
                const row = frm.add_child('sr_pe_order_items');

                row.sr_item_code = item.item_code;
                row.sr_item_qty  = item.qty || 1;
                row.sr_item_rate = item.rate || 0;
                row.sr_item_name = item.item_name;

                // ✅ ensure amount calculated
                row.sr_item_amount = (row.sr_item_qty || 0) * (row.sr_item_rate || 0);
            });

            frm.refresh_field('sr_pe_order_items');
        }
    });
}


// ==========================================================
// Centralized Access Rules
// ==========================================================
function apply_encounter_access_rules(frm) {
    handle_encounter_place_access(frm);
    handle_encounter_source_requirement(frm);
    handle_encounter_status_access(frm);
}


// ==========================================================
// Apply Active Master Filters
// ==========================================================
function apply_active_master_filters(frm) {

    frm.set_query("sr_encounter_type", () => ({ filters: { is_active: 1 } }));
    frm.set_query("sr_encounter_place", () => ({ filters: { is_active: 1 } }));
    frm.set_query("sr_sales_type", () => ({ filters: { is_active: 1 } }));
    frm.set_query("sr_encounter_source", () => ({ filters: { is_active: 1 } }));
    frm.set_query("sr_encounter_status", () => ({ filters: { is_active: 1 } }));
    frm.set_query("sr_medication_template", () => ({ filters: { is_active: 1 } }));
    frm.set_query("sr_delivery_type", () => ({ filters: { is_active: 1 } }));
    frm.set_query("item_group_template", () => ({ filters: { is_active: 1 } }));
}


// ==========================================================
// Encounter Place Access Control
// ==========================================================
function handle_encounter_place_access(frm) {
    const roles = frappe.user_roles || [];

    const is_pure_agent =
        roles.includes('Agent') &&
        !roles.includes('System Manager') &&
        !roles.includes('Administrator') &&
        !roles.includes('Healthcare Practitioner');

    if (is_pure_agent) {
        // Agent-only users → Online only
        if (frm.doc.sr_encounter_place !== 'Online') {
            frm.set_value('sr_encounter_place', 'Online');
        }
        frm.set_df_property('sr_encounter_place', 'read_only', 1);
    } else {
        // Admin / Doctor / Others → full access
        frm.set_df_property('sr_encounter_place', 'read_only', 0);
    }
}


// ==========================================================
// Encounter Source Requirement (Agent Only)
// ==========================================================
function handle_encounter_source_requirement(frm) {
    const roles = frappe.user_roles || [];
    const is_agent = roles.includes('Agent');

    const is_required =
        is_agent &&
        ['Followup', 'Order'].includes(frm.doc.sr_encounter_type) &&
        frm.doc.sr_encounter_place === 'Online';

    frm.toggle_reqd('sr_encounter_source', is_required);
}


// ==========================================================
// Encounter Status Access Control (Agent Only)
// ==========================================================
function handle_encounter_status_access(frm) {
    const roles = frappe.user_roles || [];

    const is_pure_agent =
        roles.includes('Agent') &&
        !roles.includes('System Manager') &&
        !roles.includes('Administrator') &&
        !roles.includes('Healthcare Practitioner');

    frm.set_df_property(
        'sr_encounter_status',
        'read_only',
        is_pure_agent && !frm.is_new()
    );
}


// ==========================================================
// Intercept S3 Attachments
// ==========================================================
function intercept_s3_attachments(frm) {
    setTimeout(() => {
        const $wrapper = $(frm.wrapper);

        // Prevent duplicate bindings
        $wrapper.off('click.presign').on(
            'click.presign',
            'a[href]',
            function (e) {
                const href = $(this).attr('href');
                if (!href) return;

                // Only intercept S3 / AWS links
                if (href.startsWith('s3://') || href.includes('amazonaws.com')) {
                    e.preventDefault();
                    e.stopPropagation();

                    frappe.call({
                        method: 'siya_clinic.api.s3_bucket.presign.get_presigned_url',
                        args: { file_url: href },
                        callback(r) {
                            if (typeof r.message === 'string') {
                                window.open(r.message, '_blank');
                            } else {
                                frappe.msgprint(__('Could not generate secure file link.'));
                            }
                        }
                    });
                }
            }
        );
    }, 500);
}


// ==========================================================
// Child Table: SR Multi Mode Payment
// ==========================================================
frappe.ui.form.on('SR Multi Mode Payment', {
    mmp_payment_proof(frm, cdt, cdn) {
        const row = frappe.get_doc(cdt, cdn);

        if (!row.mmp_payment_proof && row.__last_proof) {
            frappe.call({
                method: 'siya_clinic.api.s3_bucket.delete.delete_s3_by_url',
                args: { file_url: row.__last_proof },
                silent: true
            });
        }

        row.__last_proof = row.mmp_payment_proof;
    }
});