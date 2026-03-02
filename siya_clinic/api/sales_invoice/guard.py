from __future__ import annotations
import frappe

# -------------------------------------------------
# ROLE → KEYWORD MAP (dynamic)
# -------------------------------------------------
ROLE_WAREHOUSE_KEYWORDS = {
    "OPD Biller": "OPD",
    "Packaging Biller": "Packaging",
}

# Roles/users who bypass restrictions
BYPASS_ROLES = {"System Manager"}
BYPASS_USERS = {"Administrator"}


def _get_allowed_warehouse(user: str, company: str) -> str | None:
    """
    Return allowed warehouse dynamically based on role + company.
    Admin / System Manager → unrestricted
    """

    roles = set(frappe.get_roles(user))

    # Admin / System Manager → unrestricted
    if user in BYPASS_USERS or roles & BYPASS_ROLES:
        return None

    for role, keyword in ROLE_WAREHOUSE_KEYWORDS.items():
        if role in roles:
            warehouse = frappe.db.get_value(
                "Warehouse",
                {
                    "company": company,
                    "warehouse_name": ["like", f"%{keyword}%"],
                },
                "name",
            )
            return warehouse

    return None


def _has_other_warehouse(doc, allowed_warehouse: str) -> bool:
    """Check parent warehouse and child warehouses."""

    # Parent warehouse
    if doc.set_warehouse and doc.set_warehouse != allowed_warehouse:
        return True

    # Item warehouses
    for row in doc.get("items", []):
        if row.warehouse and row.warehouse != allowed_warehouse:
            return True

    return False


def validate_sales_invoice_warehouse(doc, method=None):
    """
    HARD GUARD — blocks illegal warehouse usage.

    Applied on:
    - validate
    - before_submit
    - before_cancel
    - before_amend
    """

    user = frappe.session.user
    company = doc.company

    allowed_warehouse = _get_allowed_warehouse(user, company)

    # unrestricted users
    if not allowed_warehouse:
        return

    if _has_other_warehouse(doc, allowed_warehouse):
        frappe.throw(
            f"You are allowed to work only on Sales Invoices for warehouse: {allowed_warehouse}",
            frappe.PermissionError,
        )
