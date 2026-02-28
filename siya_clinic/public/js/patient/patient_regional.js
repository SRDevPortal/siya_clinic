frappe.ui.form.on("Patient", {

    onload(frm) {
        frm.trigger("sr_medical_department");
    },

    sr_medical_department(frm) {
        const isRegional = frm.doc.sr_medical_department === "Regional";

        // If NOT regional → clear fields
        if (!isRegional) {
            frm.set_value("sr_dpt_disease", null);
            frm.set_value("sr_dpt_language", null);
        }

        // Toggle visibility (optional but recommended)
        frm.toggle_display("sr_dpt_disease", isRegional);
        frm.toggle_display("sr_dpt_language", isRegional);

        // Refresh UI
        frm.refresh_field("sr_dpt_disease");
        frm.refresh_field("sr_dpt_language");
    },

});