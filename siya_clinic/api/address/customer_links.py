# siya_clinic/api/address/customer_links.py

import frappe

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _get_title(doctype: str, name: str) -> str:
    meta = frappe.get_meta(doctype)
    title_field = (meta.title_field or "").strip() if getattr(meta, "title_field", None) else ""
    if not title_field or title_field == "name":
        return name
    return frappe.get_cached_value(doctype, name, title_field) or name


def _append_customer_link_if_missing(doc, customer: str) -> bool:
    """Attach Customer link if not already present."""
    if not customer or not frappe.db.exists("Customer", customer):
        return False

    for link in (doc.links or []):
        if link.link_doctype == "Customer" and link.link_name == customer:
            return False

    doc.append("links", {
        "link_doctype": "Customer",
        "link_name": customer,
        "link_title": _get_title("Customer", customer),
    })
    return True


# ---------------------------------------------------------
# Address → Customer auto-link
# ---------------------------------------------------------
def ensure_address_has_customer_link(doc, method=None):
    """
    If Address is linked to Patient,
    ensure it is also linked to Customer.
    """

    patients = [
        r.link_name for r in (doc.links or [])
        if r.link_doctype == "Patient" and r.link_name
    ]

    if not patients:
        return

    customers = frappe.get_all(
        "Patient",
        filters={"name": ["in", patients]},
        pluck="customer"
    )

    for customer in customers:
        if customer:
            _append_customer_link_if_missing(doc, customer)


# ---------------------------------------------------------
# Address Validation
# ---------------------------------------------------------
def validate_state(doc, method=None):
    """Require state for India addresses."""
    if (doc.country or "").lower() == "india" and not (doc.state or "").strip():
        frappe.throw("State/Province is required for addresses in India.")