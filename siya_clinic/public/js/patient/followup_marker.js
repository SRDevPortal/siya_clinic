/**
 * Follow-up Marker Logic
 * - Filter active Followup Status
 * - Filter active Followup ID
 * - Filter active Followup Day
 */

frappe.ui.form.on("Patient", {
    setup(frm) {

        // ----------------------------------------------------
        // Filter Followup Status (only active)
        // ----------------------------------------------------
        frm.set_query("sr_followup_status", function () {
            return {
                filters: {
                    is_active: 1
                },
                order_by: "sort_order asc"
            };
        });

        // ----------------------------------------------------
        // Filter Followup ID (only active)
        // ----------------------------------------------------
        frm.set_query("sr_followup_id", function () {
            return {
                filters: {
                    is_active: 1
                }
            };
        });

        // ----------------------------------------------------
        // Filter Followup Day (only active, sorted)
        // ----------------------------------------------------
        frm.set_query("sr_followup_day", function () {
            return {
                filters: {
                    is_active: 1
                },
                order_by: "sort_order asc"
            };
        });

    }
});