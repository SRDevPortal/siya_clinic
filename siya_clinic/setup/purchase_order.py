import frappe
import logging

from .utils import create_cf_with_module, upsert_property_setter, ensure_field_after

logger = logging.getLogger(__name__)

# Child doctype which will receive the new field
DT_CHILD = "Purchase Order Item"

# Parent doctype (optional sanity checks)
PARENT_DT = "Purchase Order"


def apply():
    """Apply Purchase Order customizations safely."""
    if not frappe.db.exists("DocType", DT_CHILD):
        logger.warning("Purchase Order Item DocType not found — skipping customization")
        return

    logger.info("Applying Purchase Order Item customizations")

    _make_po_item_fields()
    _apply_ui_customizations()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Purchase Order customization completed")


# =========================================================
# Custom Fields
# =========================================================

def _make_po_item_fields():
    """
    Adds Batch No field to Purchase Order Item.
    Safe to run multiple times.
    """

    create_cf_with_module({
        DT_CHILD: [
            {
                "fieldname": "batch_no",
                "label": "Batch No",
                "fieldtype": "Link",
                "options": "Batch",
                "insert_after": "warehouse",
                "in_list_view": 1,
                "print_hide": 0,
            }
        ]
    })


# =========================================================
# UI Enhancements
# =========================================================

def _apply_ui_customizations():
    meta = frappe.get_meta(DT_CHILD)

    if meta.get_field("batch_no"):
        # Ensure correct placement after warehouse
        ensure_field_after(DT_CHILD, "batch_no", "warehouse")

        # Allow filtering by batch
        upsert_property_setter(DT_CHILD, "batch_no", "in_standard_filter", "1", "Check")