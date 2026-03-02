# siya_clinic/api/sales_invoice/handlers.py

import frappe


def set_created_by_agent(doc, method=None):
    """
    Ensure Sales Invoice ownership reflects the logged-in user
    even when ignore_permissions=True is used.

    ✔ Sets system owner field
    ✔ Sets custom created_by_agent field
    ✔ Safe for background jobs & integrations
    """

    user = frappe.session.user

    # Skip for Guest or automated integrations if needed
    if not user or user == "Guest":
        return

    # -------------------------------------------------
    # SYSTEM FIELD → fixes "Created By"
    # -------------------------------------------------
    if not doc.owner:
        doc.owner = user

    # -------------------------------------------------
    # CUSTOM AUDIT FIELD
    # -------------------------------------------------
    if hasattr(doc, "created_by_agent") and not getattr(doc, "created_by_agent", None):
        doc.created_by_agent = user