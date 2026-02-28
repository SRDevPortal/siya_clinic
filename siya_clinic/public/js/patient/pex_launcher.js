frappe.ui.form.on("Patient", {

    refresh(frm) {
        const field = frm.get_field("sr_pex_launcher_html");
        if (!field) return;

        const $wrapper = field.$wrapper;

        // prevent duplicate mount
        if ($wrapper.hasClass("pex-mounted")) return;
        $wrapper.addClass("pex-mounted");

        // Render launcher UI
        $wrapper.html(`
            <div style="display:flex; align-items:center; justify-content:space-between; margin:12px 0;">
                <div>
                    <h4 style="margin:0 0 4px;">Create Patient Encounter (PEX)</h4>
                    <div class="text-muted">Open Patient Encounter with pre-filled data.</div>
                </div>
                <button class="btn btn-primary" id="sr_open_full_pe">Create Encounter</button>
            </div>
        `);

        // Button handler
        $wrapper.find("#sr_open_full_pe").on("click", () => {
            frappe.route_options = {
                from_pex: 1,
                patient: frm.doc.name,
                company: frm.doc.company || frappe.defaults.get_default("company"),
                practitioner: frm.doc.primary_healthcare_practitioner || "",
            };

            frappe.new_doc("Patient Encounter");
        });
    }

});