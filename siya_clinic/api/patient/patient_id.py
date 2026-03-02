# siya_clinic/api/patient/patient_id.py

import frappe
import re
from frappe.model.naming import make_autoname

def set_patient_id(doc, method=None):
    """
    Generate Business Patient ID

    Format:
        EEPL.1 → EEPL.999999
    """

    # Skip if already set
    if doc.get("sr_patient_id"):
        return

    # Get default company
    company = frappe.defaults.get_global_default("company")
    if not company:
        frappe.throw("Default Company not set")

    # Fetch company abbreviation
    abbr = frappe.db.get_value("Company", company, "abbr")
    if not abbr:
        frappe.throw(f"Company abbreviation missing for {company}")

    # Generate series (max 6 digits)
    generated = make_autoname(f"{abbr}.######")

    # Extract numeric part safely
    number_part = re.sub(r"\D", "", generated)
    clean_number = int(number_part)  # removes leading zeros

    # Final format
    doc.sr_patient_id = f"{abbr}{clean_number}"
