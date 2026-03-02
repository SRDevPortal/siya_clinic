# siya_clinic/doctype/customer/customer_hooks.py

import frappe

# ---------------------------------------------------------
# Set Creator (Agent Tracking)
# ---------------------------------------------------------
def set_customer_creator(doc, method=None):
    """Populate created_by_agent on insert only."""

    if not doc.get("created_by_agent"):
        doc.created_by_agent = frappe.session.user or "Administrator"


# ---------------------------------------------------------
# Phone Cleanup
# ---------------------------------------------------------
PHONE_FIELDS = (
    "mobile", "mobile_no",
    "phone", "phone_no",
    "whatsapp_no",
    "alternate_phone",
    "sr_mobile_no", "sr_whatsapp_no",
)

def _clean_spaces(value):
    return "".join(value.split()) if isinstance(value, str) else value


def sanitize_customer_contact_numbers(doc, method=None):
    """Remove spaces from phone numbers."""

    for field in PHONE_FIELDS:
        val = doc.get(field)
        cleaned = _clean_spaces(val)
        if cleaned != val:
            doc.set(field, cleaned)
    """
    Remove spaces from phone fields to prevent duplicates.
    """

    for field in PHONE_FIELDS:
        val = doc.get(field)
        cleaned = _clean_spaces(val)
        if cleaned != val:
            doc.set(field, cleaned)