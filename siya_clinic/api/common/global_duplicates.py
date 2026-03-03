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

        # 1️⃣ Direct link allowed
        if contact_belongs_to_entity(contact_name, current_doctype, current_name):
            return

        # 2️⃣ Allow if share same Customer
        current_customer = None

        if current_doctype == "Patient":
            current_customer = frappe.db.get_value("Patient", current_name, "customer")

        elif current_doctype == "Customer":
            current_customer = current_name

        if current_customer:
            contact_customer_link = frappe.db.get_value(
                "Dynamic Link",
                {
                    "parenttype": "Contact",
                    "parent": contact_name,
                    "link_doctype": "Customer"
                },
                "link_name"
            )

            if contact_customer_link and contact_customer_link == current_customer:
                return

        # 3️⃣ Shopify API reuse
        if getattr(frappe.flags, "in_shopify_api", False):
            return

        # 4️⃣ Saving Contact itself
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

        # 1️⃣ Direct link allowed
        if contact_belongs_to_entity(contact, current_doctype, current_name):
            return

        # 2️⃣ Allow if share same Customer
        current_customer = None

        if current_doctype == "Patient":
            current_customer = frappe.db.get_value("Patient", current_name, "customer")

        elif current_doctype == "Customer":
            current_customer = current_name

        if current_customer:
            contact_customer_link = frappe.db.get_value(
                "Dynamic Link",
                {
                    "parenttype": "Contact",
                    "parent": contact,
                    "link_doctype": "Customer"
                },
                "link_name"
            )

            if contact_customer_link and contact_customer_link == current_customer:
                return

        # 3️⃣ Shopify reuse
        if getattr(frappe.flags, "in_shopify_api", False):
            return

        # 4️⃣ Saving Contact itself
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