"""Short-lived, user-bound access to a payment proof before its parent is saved."""
import hashlib
import json
import re

import frappe
from frappe.model import get_permitted_fields

PARENT = "Patient Encounter"
TABLE = "enc_multi_payments"
FIELD = "mmp_payment_proof"
TTL = 1800


def _receipt_key(docname, key, bucket):
    identity = [frappe.session.user, PARENT, docname, bucket, key]
    digest = hashlib.sha256(json.dumps(identity).encode()).hexdigest()
    return "siya_pending_payment_proof:" + digest


def _fields_allowed():
    meta = frappe.get_meta(PARENT)
    table = meta.get_field(TABLE)
    if not table or table.fieldtype != "Table":
        return False
    if frappe.session.user == "Administrator":
        return True
    for permission in ("read", "write"):
        if table.permlevel not in meta.get_permlevel_access(permission_type=permission):
            return False
        if FIELD not in get_permitted_fields(
            table.options, parenttype=PARENT, permission_type=permission
        ):
            return False
    return True


def get_parent(docname):
    """Resolve saved parents or a permitted temporary Encounter upload target."""
    if isinstance(docname, str) and re.fullmatch(r"new-patient-encounter-[a-z0-9]+", docname):
        doc = frappe.new_doc(PARENT)
        doc.check_permission("create")
        doc.check_permission("write")
        doc.name = docname
        return doc
    return frappe.get_doc(PARENT, docname)


def remember_upload(file_doc, key, bucket):
    # Only the successful upload hook creates a receipt; this is not an RPC.
    if (
        frappe.session.user == "Guest"
        or file_doc.attached_to_doctype != PARENT
        or file_doc.attached_to_field != FIELD
        or not file_doc.attached_to_name
        or not key
        or not bucket
    ):
        return
    doc = get_parent(file_doc.attached_to_name)
    if not doc.has_permission("read") or not doc.has_permission("write") or not _fields_allowed():
        return
    receipt = _receipt_key(doc.name, key, bucket)
    frappe.cache.set_value(receipt, True, expires_in_sec=TTL)
    frappe.db.after_rollback.add(lambda: frappe.cache.delete_value(receipt))


def allows_preview(doc, key, bucket):
    if doc.doctype != PARENT or not frappe.cache.get_value(_receipt_key(doc.name, key, bucket)):
        return False
    # Re-check current permissions, including field levels, on every preview.
    doc.check_permission("write")
    return _fields_allowed()
