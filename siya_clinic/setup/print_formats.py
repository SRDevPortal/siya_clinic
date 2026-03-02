import os
import frappe
import logging

from .utils import MODULE_DEF_NAME, upsert_property_setter

logger = logging.getLogger(__name__)


def _load(relpath: str) -> str:
    """Load HTML file from app."""
    app_path = frappe.get_app_path("siya_clinic")
    with open(os.path.join(app_path, relpath), "r", encoding="utf-8") as f:
        return f.read()


def _upsert_pf(name: str, doctype: str, relpath: str):
    """Create or update Print Format and set as default."""
    html = _load(relpath)

    payload = {
        "doc_type": doctype,
        "module": MODULE_DEF_NAME,
        "custom_format": 1,
        "print_format_type": "Jinja",
        "disabled": 0,
        "standard": "No",
        "html": html,
    }

    if frappe.db.exists("Print Format", name):
        pf = frappe.get_doc("Print Format", name)
        pf.update(payload)
        pf.save(ignore_permissions=True)
        logger.info(f"Updated Print Format: {name}")
    else:
        pf = frappe.get_doc({"doctype": "Print Format", "name": name, **payload})
        pf.insert(ignore_permissions=True)
        logger.info(f"Created Print Format: {name}")

    # Set as default print format
    upsert_property_setter(doctype, None, "default_print_format", name, "Data", module=MODULE_DEF_NAME)

    frappe.clear_cache(doctype=doctype)


def apply():
    """Apply print formats."""
    logger.info("Applying Siya Clinic print formats")

    # Patient Encounter
    # _upsert_pf(
    #     "Patient Encounter New",
    #     "Patient Encounter",
    #     "print_formats/patient_encounter_new.html",
    # )

    # Sales Invoice
    # _upsert_pf(
    #     "Sales Invoice New",
    #     "Sales Invoice",
    #     "print_formats/sales_invoice_new.html",
    # )

    # _upsert_pf(
    #     "Sales Invoice New2",
    #     "Sales Invoice",
    #     "print_formats/sales_invoice_new2.html",
    # )

    # Purchase Order
    _upsert_pf(
        "Purchase Order New",
        "Purchase Order",
        "print_formats/purchase_order_new.html",
    )

    logger.info("Print formats applied successfully")