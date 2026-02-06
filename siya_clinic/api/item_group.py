import frappe

@frappe.whitelist()
def load_items_from_template(invoice_name):
    """
    Auto-load items from Item Group Template into Sales Invoice
    """

    invoice = frappe.get_doc("Sales Invoice", invoice_name)

    if not invoice.item_group_template:
        return

    template = frappe.get_doc(
        "Item Group Template",
        invoice.item_group_template
    )

    # 🔴 Clear existing items
    invoice.items = []

    # ➕ Add items from template
    for row in template.items:
        invoice.append("items", {
            "item_code": row.item_code,
            "qty": row.qty,
        })

    # Let ERPNext calculate rate & GST
    invoice.set_missing_values()
    invoice.calculate_taxes_and_totals()
    invoice.save()

    return True
