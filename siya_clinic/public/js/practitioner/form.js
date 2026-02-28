// ------------------------------------------------------------
// Healthcare Practitioner - Full Name Composer
// Siya Clinic
// ------------------------------------------------------------

function compose_full_name(frm) {
    const parts = [
        frm.doc.first_name,
        frm.doc.middle_name,
        frm.doc.last_name
    ].filter(Boolean);

    const full = parts.join(" ").trim();

    // Update only if changed to avoid loops
    if (full && frm.doc.practitioner_name !== full) {
        frm.set_value("practitioner_name", full);
    }
}

frappe.ui.form.on("Healthcare Practitioner", {

    // 🔹 Sync while typing
    first_name(frm) {
        compose_full_name(frm);
    },

    middle_name(frm) {
        compose_full_name(frm);
    },

    last_name(frm) {
        compose_full_name(frm);
    },

    // 🔹 Run before client-side validation
    validate(frm) {
        compose_full_name(frm);
    },

    // 🔹 Handle prefilled values (Quick Entry / API load)
    refresh(frm) {
        if (frm.is_new()) {
            compose_full_name(frm);
        }
    }
});