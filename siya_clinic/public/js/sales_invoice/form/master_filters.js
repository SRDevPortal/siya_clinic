frappe.ui.form.on('Sales Invoice', {

    setup(frm) {

        const active = { is_active: 1 };

        // ---------------------------
        // Order Source
        // ---------------------------
        frm.set_query('order_source', () => ({
            query: "siya_clinic.api.common.link_queries.master_query",
            filters: {
                ...active,
                field: "sr_source_name",
                order: "asc"
            }
        }));

        // ---------------------------
        // Order Channel
        // ---------------------------
        frm.set_query('order_channel', () => {

            // ❗ No source → no options
            if (!frm.doc.order_source) {
                return {
                    filters: {
                        name: ""   // force empty
                    }
                };
            }

            return {
                query: "siya_clinic.api.common.link_queries.master_query",
                filters: {
                    ...active,
                    field: "order_channel_name",
                    order: "asc",
                    order_source: frm.doc.order_source
                }
            };
        });
    },

    // -----------------------------------
    // When Order Source Changes
    // -----------------------------------
    order_source(frm) {

        // Clear existing
        frm.set_value('order_channel', null);

        // Enable/Disable field
        frm.toggle_enable('order_channel', !!frm.doc.order_source);

        // Refresh UI
        frm.refresh_field('order_channel');

        // If no source → stop
        if (!frm.doc.order_source) return;

        // Fetch channels
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "SR Order Channel",
                filters: {
                    order_source: frm.doc.order_source,
                    is_active: 1
                },
                fields: ["name"],
                limit_page_length: 2   // important optimization
            },
            callback: function(r) {

                if (!r.message) return;

                // If only ONE channel → auto set
                if (r.message.length === 1) {
                    frm.set_value('order_channel', r.message[0].name);
                }
            }
        });
    },

    // -----------------------------------
    // On Form Load (important)
    // -----------------------------------
    refresh(frm) {

        // Ensure correct state on load/edit
        frm.toggle_enable('order_channel', !!frm.doc.order_source);
    }
});