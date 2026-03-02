# siya_clinic/api/address/link_to_patient.py

import frappe


# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------

def _get_title(doctype: str, name: str) -> str:
    meta = frappe.get_meta(doctype)
    title_field = (meta.title_field or "").strip() if getattr(meta, "title_field", None) else ""
    if not title_field or title_field == "name":
        return name
    return frappe.get_cached_value(doctype, name, title_field) or name


def _append_customer_link_if_missing(doc, customer: str, do_save: bool = False) -> bool:
    """Append Customer link to Address/Contact if missing."""
    if not customer or not frappe.db.exists("Customer", customer):
        frappe.logger("siya_clinic").warning(f"Customer not found: {customer}")
        return False

    for link in (doc.links or []):
        if link.link_doctype == "Customer" and link.link_name == customer:
            return False

    doc.append("links", {
        "link_doctype": "Customer",
        "link_name": customer,
        "link_title": _get_title("Customer", customer),
    })

    if do_save:
        try:
            doc.save(ignore_permissions=True)
        except Exception:
            frappe.logger("siya_clinic").exception(
                f"Failed saving {doc.doctype}:{doc.name} while linking Customer {customer}"
            )
            return False

    return True


# ---------------------------------------------------------
# Main Hook
# ---------------------------------------------------------

def link_to_customer(doc, method=None):
    """
    When Patient has Customer → ensure all linked
    Address & Contact also linked to that Customer.
    """

    customer = doc.get("customer")
    if not customer or not frappe.db.exists("Customer", customer):
        return

    patient = doc.name

    # Sync Addresses
    address_names = frappe.get_all(
        "Dynamic Link",
        filters={
            "parenttype": "Address",
            "link_doctype": "Patient",
            "link_name": patient
        },
        pluck="parent",
    )

    for addr in set(address_names):
        try:
            addr_doc = frappe.get_doc("Address", addr)
            _append_customer_link_if_missing(addr_doc, customer, do_save=True)
        except frappe.DoesNotExistError:
            frappe.logger("siya_clinic").warning(f"Address missing: {addr}")

    # Sync Contacts
    contact_names = frappe.get_all(
        "Dynamic Link",
        filters={
            "parenttype": "Contact",
            "link_doctype": "Patient",
            "link_name": patient
        },
        pluck="parent",
    )

    for contact in set(contact_names):
        try:
            contact_doc = frappe.get_doc("Contact", contact)
            _append_customer_link_if_missing(contact_doc, customer, do_save=True)
        except frappe.DoesNotExistError:
            frappe.logger("siya_clinic").warning(f"Contact missing: {contact}")