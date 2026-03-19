# siya_clinic/api/patient/patient_id.py

import frappe

def set_patient_id(doc, method=None):
    """
    Sync sr_patient_id with naming series (name)

    Example:
    name            = EEPL-PAT-12452
    sr_patient_id   = EEPL12452
    """

    # Ensure name exists
    if not doc.name:
        return

    # Extract number from name
    if "-" in doc.name:
        number = doc.name.split("-")[-1]

        # Get company abbr
        company = frappe.defaults.get_global_default("company")
        abbr = frappe.db.get_value("Company", company, "abbr")

        # Set sr_patient_id
        doc.sr_patient_id = f"{abbr}{number}"


# import frappe
# import re
# from frappe.model.naming import make_autoname

# def set_patient_id(doc, method=None):
#     """
#     Generate Business Patient ID

#     Format:
#         EEPL.1 → EEPL.999999
#     """

#     # Skip if already set
#     if doc.get("sr_patient_id"):
#         return

#     # Get default company
#     company = frappe.defaults.get_global_default("company")
#     if not company:
#         frappe.throw("Default Company not set")

#     # Fetch company abbreviation
#     abbr = frappe.db.get_value("Company", company, "abbr")
#     if not abbr:
#         frappe.throw(f"Company abbreviation missing for {company}")

#     # Generate series (max 6 digits)
#     generated = make_autoname(f"{abbr}.######")

#     # Extract numeric part safely
#     number_part = re.sub(r"\D", "", generated)
#     clean_number = int(number_part)  # removes leading zeros

#     # Final format
#     doc.sr_patient_id = f"{abbr}{clean_number}"
