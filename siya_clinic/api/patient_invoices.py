"""Patient-scoped invoice summary using Siya's Encounter backlink."""
import frappe
from frappe.utils import cint

INVOICE_FIELDS = ("name", "posting_date", "grand_total", "outstanding_amount")


@frappe.whitelist()
def get_patient_invoices(patient: str, limit_page_length: int = 100):
    if not patient:
        raise frappe.ValidationError("Select a Patient to view invoices.")
    parent = frappe.get_doc("Patient", patient)
    parent.check_permission("read")
    # Native lists enforce the user's permissions on both linked DocTypes.
    # Do not fall back to Customer: a Customer may be shared by several Patients.
    encounters = frappe.get_list(
        "Patient Encounter", filters={"patient": parent.name}, fields=["name"],
        limit_page_length=0,
    )
    if not encounters:
        return []
    limit = max(1, min(cint(limit_page_length or 100), 100))
    return frappe.get_list(
        "Sales Invoice",
        filters={"source_encounter": ["in", [row.name for row in encounters]], "docstatus": 1},
        fields=list(INVOICE_FIELDS), order_by="posting_date desc, creation desc",
        limit_page_length=limit,
    )
