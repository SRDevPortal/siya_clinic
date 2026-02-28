// Global override for Customer link display
(function () {
    const original = frappe.form.formatters.Link;

    frappe.form.formatters.Link = function (value, df, options, doc) {
        // If this is a Customer link
        if (df && df.options === "Customer" && value) {

            // If cached → show name immediately
            if (locals.Customer && locals.Customer[value] && locals.Customer[value].customer_name) {
                return locals.Customer[value].customer_name;
            }

            // Async fetch → update DOM
            frappe.db.get_value("Customer", value, "customer_name").then(r => {
                if (r && r.message && r.message.customer_name) {
                    $(`[data-doctype="Customer"][data-name="${value}"]`)
                        .text(r.message.customer_name);
                }
            });

            // Temporary display
            return value;
        }

        // Default behavior for other links
        return original(value, df, options, doc);
    };

    console.log("✅ Global Customer link display override active");
})();