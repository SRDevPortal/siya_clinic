# siya_clinic/api/patient/naming.py

import frappe
from frappe.model.naming import make_autoname

def set_patient_series(doc, method=None):
    """
    Apply company-based naming:
    Unlimited incremental patient ID:
    company abbr + "-PAT-" + 7 digit number
    Example: EEPL-PAT-1, EEPL-PAT-2, ...
    """

    # Skip if already renamed by our logic
    if getattr(doc, "_series_applied", False):
        return

    # Get default company
    company = frappe.defaults.get_global_default("company")
    if not company:
        frappe.throw("Default Company not set")

    # Fetch company abbreviation
    abbr = frappe.db.get_value("Company", company, "abbr")
    if not abbr:
        frappe.throw(f"Company abbreviation missing for {company}")

    # Build naming series
    series = f"{abbr}-PAT-.#"

    # Apply new name
    doc.name = make_autoname(series)

    # Prevent double execution
    doc._series_applied = True