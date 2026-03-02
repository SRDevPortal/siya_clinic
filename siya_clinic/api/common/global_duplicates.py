import frappe
import re

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def normalize_mobile(value):
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    return digits[-10:] if len(digits) >= 10 else None


def normalize_email(value):
    return value.strip().lower() if value else None


# ---------------------------------------------------------
# Ownership helpers
# ---------------------------------------------------------

def get_contact_linked_entities(contact_name):
    """Return valid linked entities for a Contact"""
    links = frappe.get_all(
        "Dynamic Link",
        filters={"parenttype": "Contact", "parent": contact_name},
        fields=["link_doctype", "link_name"],
    )

    valid = []
    for l in links:
        if frappe.db.exists(l.link_doctype, l.link_name):
            valid.append(l)

    return valid


def contact_belongs_to_entity(contact_name, doctype, name):
    """Check if contact belongs to current entity"""
    links = get_contact_linked_entities(contact_name)

    for link in links:
        if link.link_doctype == doctype and link.link_name == name:
            return True

    return False


# ---------------------------------------------------------
# GLOBAL MOBILE CHECK
# ---------------------------------------------------------

def validate_global_mobile(mobile, current_doctype, current_name):
    mobile = normalize_mobile(mobile)
    if not mobile:
        return

    # ---------------- CONTACT ----------------
    contact_match = frappe.db.sql(
        """
        SELECT name FROM `tabContact`
        WHERE RIGHT(REPLACE(REPLACE(mobile_no,' ',''),'+91',''),10)=%s
           OR RIGHT(REPLACE(REPLACE(phone,' ',''),'+91',''),10)=%s
        LIMIT 1
        """,
        (mobile, mobile),
    )

    if contact_match:
        contact_name = contact_match[0][0]

        # ✅ allow if same entity
        if contact_belongs_to_entity(contact_name, current_doctype, current_name):
            pass
        else:
            # ✅ allow if contact belongs to same patient (Healthcare flow)
            if current_doctype == "Contact":
                return
            frappe.throw(f"Mobile already linked with Contact: {contact_name}")

    # ---------------- PATIENT ----------------
    patient = frappe.db.get_value(
        "Patient",
        {"mobile": mobile, "name": ["!=", current_name]},
        "name",
    )

    if patient:
        # allow if updating same patient via Contact save
        if current_doctype == "Contact":
            return

        if current_doctype != "Patient":
            frappe.throw(f"Mobile already linked with Patient: {patient}")

    # ---------------- CUSTOMER ----------------
    customer = frappe.db.get_value(
        "Customer",
        {"mobile_no": mobile, "name": ["!=", current_name]},
        "name",
    )

    if customer:
        if current_doctype == "Contact":
            return

        if current_doctype != "Customer":
            frappe.throw(f"Mobile already linked with Customer: {customer}")


# ---------------------------------------------------------
# GLOBAL EMAIL CHECK
# ---------------------------------------------------------

def validate_global_email(email, current_doctype, current_name):
    email = normalize_email(email)
    if not email:
        return

    # ---------------- CONTACT ----------------
    contact = frappe.db.get_value("Contact", {"email_id": email}, "name")

    if contact:
        if contact_belongs_to_entity(contact, current_doctype, current_name):
            pass
        else:
            if current_doctype == "Contact":
                return
            frappe.throw(f"Email already linked with Contact: {contact}")

    # ---------------- PATIENT ----------------
    patient = frappe.db.get_value(
        "Patient",
        {"email": email, "name": ["!=", current_name]},
        "name",
    )

    if patient:
        if current_doctype == "Contact":
            return

        if current_doctype != "Patient":
            frappe.throw(f"Email already linked with Patient: {patient}")

    # ---------------- CUSTOMER ----------------
    customer = frappe.db.get_value(
        "Customer",
        {"email_id": email, "name": ["!=", current_name]},
        "name",
    )

    if customer:
        if current_doctype == "Contact":
            return

        if current_doctype != "Customer":
            frappe.throw(f"Email already linked with Customer: {customer}")