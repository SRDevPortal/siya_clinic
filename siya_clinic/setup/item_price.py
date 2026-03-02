import frappe
import logging

from .utils import create_cf_with_module, upsert_property_setter

logger = logging.getLogger(__name__)

DT = "Item Price"


def apply():
    """Apply Item Price customizations safely."""
    if not frappe.db.exists("DocType", DT):
        logger.warning("Item Price DocType not found — skipping customization")
        return

    logger.info("Applying Item Price customizations")

    _make_item_price_fields()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Item Price customization completed")


# =========================================================
# Custom Fields
# =========================================================

def _make_item_price_fields():
    """
    Adds Cost Price field for margin calculations.
    Safe to run multiple times.
    """

    create_cf_with_module({
        DT: [
            {
                "fieldname": "sr_cost_price",
                "label": "Cost Price",
                "fieldtype": "Currency",
                "in_list_view": 1,
                "in_standard_filter": 0,
                "insert_after": "price_list_rate",
                "description": "Cost for this Item in this Price List (used for margin calculation).",
            }
        ]
    })
