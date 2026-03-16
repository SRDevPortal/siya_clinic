import frappe


def mark_customer_patient_created(doc, method=None):
    """
    Mark Customer.is_patient_created = 1 when a Patient exists.

    Handles scenarios:
    1. Patient already linked directly to Customer
    2. Patient linked via Contact
    3. Customer auto-created from Patient
    """

    customer = doc.customer

    # --------------------------------------------------
    # Case 1 — Direct Customer link exists
    # --------------------------------------------------
    if customer:
        frappe.db.set_value(
            "Customer",
            customer,
            "is_patient_created",
            1,
            update_modified=False
        )
        return

    # --------------------------------------------------
    # Case 2 — Find Contact linked to Patient
    # --------------------------------------------------
    contact = frappe.db.get_value(
        "Dynamic Link",
        {
            "link_doctype": "Patient",
            "link_name": doc.name,
            "parenttype": "Contact"
        },
        "parent"
    )

    if not contact:
        return

    # --------------------------------------------------
    # Case 3 — Find Customer linked to Contact
    # --------------------------------------------------
    customer = frappe.db.get_value(
        "Dynamic Link",
        {
            "parent": contact,
            "parenttype": "Contact",
            "link_doctype": "Customer"
        },
        "link_name"
    )

    if not customer:
        return

    frappe.db.set_value(
        "Customer",
        customer,
        "is_patient_created",
        1,
        update_modified=False
    )