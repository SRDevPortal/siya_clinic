console.log("SIYA SALES INVOICE TEMPLATE LOADER LOADED");

// Show ONLY template_name in Link fields
frappe.form.link_formatters['Item Group Template'] = function(value, doc) {
    if (!doc) return value;
    return doc.template_name || value;
};

frappe.ui.form.on("Sales Invoice", {

    // =====================================================
    // SETUP
    // =====================================================
    setup(frm) {

        // Only show Active Templates in dropdown
        frm.set_query("item_group_template", function() {
            return {
                filters: {
                    is_active: 1
                }
            };
        });

    },

    // =====================================================
    // VALIDATE (Prevent using inactive template)
    // =====================================================
    validate(frm) {
        if (!frm.doc.item_group_template) return;

        frappe.db.get_value(
            "Item Group Template",
            frm.doc.item_group_template,
            "is_active"
        ).then(r => {
            if (!r.message || !r.message.is_active) {
                frappe.throw(
                    "The selected Item Group Template is Inactive. Please select an active template."
                );
            }
        });
    },

    // =====================================================
    // WHEN TEMPLATE IS SELECTED
    // =====================================================
    item_group_template(frm) {

        if (!frm.doc.item_group_template) {
            frm.clear_table("items");
            frm.refresh_field("items");
            return;
        }

         frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: "Item Group Template",
                name: frm.doc.item_group_template
            },
            callback(res) {

                if (!res.message) return;

                frm.clear_table("items");

                res.message.items.forEach(tpl_row => {

                    let row = frm.add_child("items");

                    // 1️⃣ Set item_code first
                    frappe.model.set_value(
                        row.doctype,
                        row.name,
                        "item_code",
                        tpl_row.item_code
                    );

                    // 2️⃣ Wait for ERPNext item scripts
                    setTimeout(() => {

                        const qty = tpl_row.qty || 1;

                        frappe.model.set_value(row.doctype, row.name, "conversion_factor", 1);
                        frappe.model.set_value(row.doctype, row.name, "qty", qty);
                        frappe.model.set_value(row.doctype, row.name, "stock_qty", qty);

                        // 3️⃣ Fetch GST & HSN
                        frappe.call({
                            method: "frappe.client.get",
                            args: {
                                doctype: "Item",
                                name: tpl_row.item_code
                            },
                            callback(item_res) {

                                let item = item_res.message;
                                if (!item) return;

                                frappe.model.set_value(
                                    row.doctype,
                                    row.name,
                                    "gst_hsn_code",
                                    item.gst_hsn_code || item.hsn_code
                                );

                                if (item.taxes && item.taxes.length) {
                                    frappe.model.set_value(
                                        row.doctype,
                                        row.name,
                                        "item_tax_template",
                                        item.taxes[0].item_tax_template
                                    );
                                }
                            }
                        });

                        // 4️⃣ Fetch Item Price
                        frappe.call({
                            method: "frappe.client.get_list",
                            args: {
                                doctype: "Item Price",
                                filters: {
                                    item_code: tpl_row.item_code,
                                    price_list: frm.doc.selling_price_list || "Standard Selling"
                                },
                                fields: ["price_list_rate"],
                                limit_page_length: 1
                            },
                            callback(price_res) {

                                if (!price_res.message || !price_res.message.length) return;

                                let price = price_res.message[0].price_list_rate;

                                frappe.model.set_value(row.doctype, row.name, "rate", price);
                                frappe.model.set_value(row.doctype, row.name, "price_list_rate", price);

                                frappe.model.trigger("qty", row.doctype, row.name);
                                frappe.model.trigger("rate", row.doctype, row.name);
                            }
                        });

                    }, 500);

                });

                frm.refresh_field("items");
            }
        });
    }

});
