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


def normalize_patient_contact_numbers(doc, method=None):
    if doc.mobile:
        doc.mobile = normalize_indian_mobile(doc.mobile)


def normalize_patient_email(doc, method=None):
    if doc.email:
        doc.email = doc.email.strip().lower()


def validate_patient_global_duplicates(doc, method=None):
    validate_global_mobile(doc.mobile, "Patient", doc.name)
    validate_global_email(doc.email, "Patient", doc.name)