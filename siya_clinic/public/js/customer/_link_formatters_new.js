// Ensure namespace exists
window.frappe = window.frappe || {};
frappe.link_formatters = frappe.link_formatters || {};

// Register formatter
frappe.link_formatters["Customer"] = function (value) {
    if (!value) return value;

    // Use cached doc if available
    if (locals.Customer && locals.Customer[value] && locals.Customer[value].customer_name) {
        return locals.Customer[value].customer_name;
    }

    return value; // fallback
};

console.log("✅ Customer link formatter registered");