console.log("SIYA ITEM GROUP TEMPLATE JS LOADED");

frappe.ui.form.on("Item Group Template", {
    setup(frm) {

        frappe.ui.form.on("Item Group Template Item", {
            item_code(frm, cdt, cdn) {
                const row = locals[cdt][cdn];
                if (!row.item_code) return;

                // ✅ Fetch GST Template from Item → Taxes
                frappe.call({
                    method: "frappe.client.get",
                    args: {
                        doctype: "Item",
                        name: row.item_code
                    },
                    callback(r) {
                        if (r.message?.taxes?.length) {
                            frappe.model.set_value(
                                cdt,
                                cdn,
                                "item_tax_template",
                                r.message.taxes[0].item_tax_template
                            );
                        }
                    }
                });

                // ✅ Fetch Rate from Item Price
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Item Price",
                        filters: {
                            item_code: row.item_code,
                            price_list: "Standard Selling"
                        },
                        fields: ["price_list_rate"],
                        limit_page_length: 1
                    },
                    callback(res) {
                        if (res.message?.length) {
                            frappe.model.set_value(
                                cdt,
                                cdn,
                                "rate",
                                res.message[0].price_list_rate
                            );
                        }
                    }
                });
            }
        });
    }
});
