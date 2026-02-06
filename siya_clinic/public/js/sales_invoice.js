console.log("SIYA SALES INVOICE TEMPLATE LOADER LOADED");

frappe.ui.form.on("Sales Invoice", {
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

                    // 2️⃣ Wait for ERPNext item setup
                    setTimeout(() => {

                        const qty = tpl_row.qty || 1;

                        // 🔥 THIS IS THE CRITICAL PART
                        frappe.model.set_value(row.doctype, row.name, "conversion_factor", 1);
                        frappe.model.set_value(row.doctype, row.name, "qty", qty);
                        frappe.model.set_value(row.doctype, row.name, "stock_qty", qty);

                        // 3️⃣ Fetch Item master (HSN + GST)
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

                                // 🔥 Force final recalculation
                                frappe.model.trigger("qty", row.doctype, row.name);
                                frappe.model.trigger("rate", row.doctype, row.name);
                            }
                        });

                    }, 500); // delay ensures item_code scripts finish
                });

                frm.refresh_field("items");
            }
        });
    }
});
