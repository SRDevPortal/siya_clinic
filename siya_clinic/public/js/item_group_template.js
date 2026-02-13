console.log("SIYA ITEM GROUP TEMPLATE JS LOADED");

const DEFAULT_PRICE_LIST = "Standard Selling"; // 🔧 make configurable later

frappe.ui.form.on("Item Group Template Item", {
    item_code(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (!row.item_code) return;

        console.log("Fetching item details for:", row.item_code);

        // ------------------------------------------
        // 1️⃣ Fetch GST Template from Item
        // ------------------------------------------
        frappe.db.get_doc("Item", row.item_code)
            .then(item => {
                if (item.taxes && item.taxes.length) {
                    frappe.model.set_value(
                        cdt,
                        cdn,
                        "item_tax_template",
                        item.taxes[0].item_tax_template
                    );
                }
            })
            .catch(err => {
                console.warn("Failed to fetch item taxes:", err);
            });

        // ------------------------------------------
        // 2️⃣ Fetch Rate from Item Price
        // ------------------------------------------
        frappe.db.get_list("Item Price", {
            filters: {
                item_code: row.item_code,
                price_list: DEFAULT_PRICE_LIST
            },
            fields: ["price_list_rate"],
            limit: 1
        })
        .then(res => {
            if (res.length) {
                frappe.model.set_value(
                    cdt,
                    cdn,
                    "rate",
                    res[0].price_list_rate
                );
            }
        })
        .catch(err => {
            console.warn("Failed to fetch item price:", err);
        });
    }
});
