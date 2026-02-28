import frappe
import logging

from .utils import create_cf_with_module, upsert_property_setter

logger = logging.getLogger(__name__)

DT = "Company"


def apply():
    """Apply Company customizations safely."""
    if not frappe.db.exists("DocType", DT):
        logger.warning("Company DocType not found — skipping customization")
        return

    logger.info("Applying Company customizations")

    _make_company_fields()
    _apply_ui_customizations()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Company customization completed")


# =========================================================
# Custom Fields
# =========================================================

def _make_company_fields():
    """Add CIN field to Company."""
    create_cf_with_module({
        DT: [
            {
                "fieldname": "sr_company_cin_no",
                "label": "CIN No",
                "fieldtype": "Data",
                "insert_after": "pan",
                "description": "Corporate Identification Number",
            }
        ]
    })


# =========================================================
# UI Enhancements (Optional)
# =========================================================

def _apply_ui_customizations():
    meta = frappe.get_meta(DT)

    if meta.get_field("sr_company_cin_no"):
        # Allow quick search
        upsert_property_setter(DT, "sr_company_cin_no", "in_standard_filter", "1", "Check")

        # Optional: show in list view
        upsert_property_setter(DT, "sr_company_cin_no", "in_list_view", "1", "Check")