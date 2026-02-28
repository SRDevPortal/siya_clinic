import frappe
import re
from siya_clinic.api.common.global_duplicates import (
    validate_global_mobile,
    validate_global_email,
)

def normalize_indian_mobile(value):
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    return digits[-10:] if len(digits) >= 10 else None


def normalize_contact_phone_fields(doc, method=None):
    if doc.mobile_no:
        doc.mobile_no = normalize_indian_mobile(doc.mobile_no)

    if doc.phone:
        doc.phone = normalize_indian_mobile(doc.phone)


def validate_contact_global_duplicates(doc, method=None):
    validate_global_mobile(doc.mobile_no or doc.phone, "Contact", doc.name)
    validate_global_email(doc.email_id, "Contact", doc.name)