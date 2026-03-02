// siya_clinic/public/js/encounter/draft_invoice.js

console.log("Draft Invoice JS file loaded");

frappe.ui.form.on('Patient Encounter', {
    refresh(frm) {
        toggle_draft_invoice_ui(frm);
    },

    onload_post_render(frm) {
        toggle_draft_invoice_ui(frm);

        // If brand-new Encounter, clear once
        if (frm.is_new()) {
            reset_draft_invoice_fields(frm);
            frm.refresh_field('sr_pe_order_items');
        }
    },

    // When type changes:
    sr_encounter_type(frm) {
        const is_new = frm.is_new();
        toggle_draft_invoice_ui(frm);
        if (is_new) {
            reset_draft_invoice_fields(frm);
            frm.refresh_field('sr_pe_order_items');
        }
    },

    // Also react when place changes
    sr_encounter_place(frm) {
        const is_new = frm.is_new();
        toggle_draft_invoice_ui(frm);
        if (is_new) {
            reset_draft_invoice_fields(frm);
            frm.refresh_field('sr_pe_order_items');
        }
    },
});

function is_order_for_any_place(frm) {
    const type = (frm.doc.sr_encounter_type || '').toLowerCase();
    const place = (frm.doc.sr_encounter_place || '').toLowerCase();

    // show for Order + (Online OR OPD). Allow empty place while user types.
    return type === 'order' && (place === 'online' || place === 'opd' || !place);
}

function toggle_draft_invoice_ui(frm) {
    // Tab visibility is controlled server-side via depends_on;
    // here we toggle inner sections/fields (multi-payments only)
    const show = is_order_for_any_place(frm);

    const sections = ['sr_items_list_sb', 'enc_mmp_sb'];
    const fields = ['sr_delivery_type', 'item_group_template', 'sr_pe_order_items', 'enc_multi_payments'];

    // Toggle sections (ignore missing fields)
    sections.forEach(f => {
        try { frm.toggle_display(f, show); } catch (e) { /* ignore if missing */ }
    });

    // Toggle fields (show new multi-payments when show=true)
    fields.forEach(f => {
        try { frm.toggle_display(f, show); } catch (e) { /* ignore if missing */ }
    });
}

function reset_draft_invoice_fields(frm) {
    frm.set_value('sr_delivery_type', null);
    frm.set_value('item_group_template', null);
    frm.set_value('sr_pe_order_items', []);
    frm.set_value('enc_multi_payments', []);
    toggle_draft_invoice_ui(frm);
}