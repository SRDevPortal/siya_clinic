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


def normalize_customer_contact_numbers(doc, method=None):
    if doc.mobile_no:
        doc.mobile_no = normalize_indian_mobile(doc.mobile_no)


def normalize_customer_email(doc, method=None):
    if doc.email_id:
        doc.email_id = doc.email_id.strip().lower()


def validate_customer_global_duplicates(doc, method=None):

    # If mobile and email not changed, skip duplicate engine
    if not doc.has_value_changed("mobile_no") and not doc.has_value_changed("email_id"):
        return

    # Skip strict duplicate check during Shopify API reuse
    if getattr(frappe.flags, "in_shopify_api", False):
        return

    validate_global_mobile(doc.mobile_no, "Customer", doc.name)
    validate_global_email(doc.email_id, "Customer", doc.name)
