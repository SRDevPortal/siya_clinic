// siya_clinic/public/js/encounter/order_item.js

console.log("Order Item JS file loaded");

frappe.ui.form.on("SR Order Item", {
	// Trigger when quantity or rate is changed
	sr_item_qty(frm, cdt, cdn) {
		sr_set_amount(cdt, cdn);
	},

	sr_item_rate(frm, cdt, cdn) {
		sr_set_amount(cdt, cdn);
	},

	// Trigger when item code is changed
	sr_item_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		const item_code = row.sr_item_code;
		if (!item_code) return;

		// Fetch price list rate from 'Item Price' based on item code and default price list
		frappe.db
			.get_value("Item Price", { item_code: item_code, price_list: "Standard Selling" }, [
				"price_list_rate",
			])
			.then((r) => {
				const price_list_rate = (r && r.message && r.message.price_list_rate) || 0;
				// Set the price list rate as sr_item_rate
				sr_set_if_exists(cdt, cdn, "sr_item_rate", price_list_rate);

				// Fetch other details (item_name, description, stock_uom) from the Item master
				frappe.db
					.get_value("Item", item_code, ["stock_uom", "item_name", "description"])
					.then((r) => {
						const m = (r && r.message) || {};
						// Set fetched values into the corresponding fields
						sr_set_if_exists(cdt, cdn, "sr_item_uom", m.stock_uom);
						sr_set_if_exists(cdt, cdn, "sr_item_name", m.item_name);
						if (!sr_set_if_exists(cdt, cdn, "sr_item_description", m.description)) {
							sr_set_if_exists(cdt, cdn, "description", m.description);
						}
						sr_set_amount(cdt, cdn);
					});
			});
	},
});

// Function to set amount (quantity * rate)
function sr_set_amount(cdt, cdn) {
	const d = locals[cdt][cdn] || {};
	const qty = Number(d.sr_item_qty ?? d.qty) || 0;
	const rate = Number(d.sr_item_rate ?? d.rate) || 0;
	const amt = qty * rate;

	// Write to custom amount if present, else standard
	if (!sr_set_if_exists(cdt, cdn, "sr_item_amount", amt)) {
		sr_set_if_exists(cdt, cdn, "amount", amt);
	}
}

// Helper function to set values only if the field exists in the child table
function sr_set_if_exists(cdt, cdn, fieldname, value) {
	const exists = Boolean(
		frappe.meta.get_docfield("SR Order Item", fieldname, (locals[cdt][cdn] || {}).parent),
	);
	if (!exists) return false;
	frappe.model.set_value(cdt, cdn, fieldname, value);
	return true;
}
