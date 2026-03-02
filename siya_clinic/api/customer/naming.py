# siya_clinic/api/customer/naming.py

import frappe
from frappe.model.naming import make_autoname


def set_customer_series(doc, method=None):
    """
    Company-based Customer naming.

    Format:
        COMPANY_ABBR-CUST-#
    """

    ## Prevent double execution
    if getattr(doc, "_series_applied", False):
        return

    # Skip if already named correctly
    if doc.name and "-CUST-" in doc.name:
        return

    # Get company
    company = doc.get("company") or frappe.defaults.get_global_default("company")
    if not company:
        frappe.throw("Default Company not set")

    # Get abbreviation
    abbr = frappe.db.get_value("Company", company, "abbr")
    if not abbr:
        frappe.throw(f"Company abbreviation missing for {company}")

    # Build naming series
    series = f"{abbr}-CUST-.#"

    # Generate name
    doc.name = make_autoname(series)

    # Prevent duplicate execution
    doc._series_applied = True