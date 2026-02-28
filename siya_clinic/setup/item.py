import frappe
import logging

from .utils import (
    create_cf_with_module,
    ensure_field_after,
    upsert_property_setter,
)

logger = logging.getLogger(__name__)

PARENT = "Item"


def apply():
    logger.info("Applying Item Package Details customization")

    _make_package_fields()
    _apply_item_ui_customizations()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Item Package customization completed")


# =========================================================
# Custom Fields
# =========================================================

def _make_package_fields():
    """
    Adds Package Details tab & fields to Item.
    """

    create_cf_with_module({
        PARENT: [

            # -------------------------------------------------
            # Package Details Tab
            # -------------------------------------------------
            {
                "fieldname": "sr_pkg_tab",
                "label": "Package Details",
                "fieldtype": "Tab Break",
                "insert_after": "total_projected_qty",
            },

            # -------------------------------------------------
            # Section Break
            # -------------------------------------------------
            {
                "fieldname": "sr_pkg_section",
                "label": "Package Information",
                "fieldtype": "Section Break",
                "insert_after": "sr_pkg_tab",
            },

            # -------------------------------------------------
            # Left Column
            # -------------------------------------------------
            {
                "fieldname": "sr_pkg_length",
                "label": "Package Length (cm)",
                "fieldtype": "Float",
                "precision": 2,
                "insert_after": "sr_pkg_section",
            },
            {
                "fieldname": "sr_pkg_width",
                "label": "Package Width (cm)",
                "fieldtype": "Float",
                "precision": 2,
                "insert_after": "sr_pkg_length",
            },
            {
                "fieldname": "sr_pkg_height",
                "label": "Package Height (cm)",
                "fieldtype": "Float",
                "precision": 2,
                "insert_after": "sr_pkg_width",
            },
            {
                "fieldname": "sr_pkg_dead_weight",
                "label": "Dead Weight (kg)",
                "fieldtype": "Float",
                "precision": 3,
                "insert_after": "sr_pkg_height",
            },

            # -------------------------------------------------
            # Right Column
            # -------------------------------------------------
            {
                "fieldname": "sr_pkg_cb",
                "fieldtype": "Column Break",
                "insert_after": "sr_pkg_dead_weight",
            },
            {
                "fieldname": "sr_pkg_vol_weight",
                "label": "Volumetric Weight (kg)",
                "fieldtype": "Float",
                "precision": 3,
                "read_only": 1,
                "insert_after": "sr_pkg_cb",
            },
            {
                "fieldname": "sr_pkg_applied_weight",
                "label": "Applied Weight (kg)",
                "fieldtype": "Float",
                "precision": 3,
                "read_only": 1,
                "insert_after": "sr_pkg_vol_weight",
            },
        ]
    })


# =========================================================
# UI Customizations
# =========================================================

def _apply_item_ui_customizations():
    """Optional UI improvements for Item Package fields."""

    meta = frappe.get_meta(PARENT)

    # Bold important calculated fields
    for field in ("sr_pkg_vol_weight", "sr_pkg_applied_weight"):
        if meta.get_field(field):
            upsert_property_setter(
                doctype=PARENT,
                fieldname=field,
                prop="bold",
                value="1",
                property_type="Check"
            )

    # Make applied weight visible in list view (optional)
    if meta.get_field("sr_pkg_applied_weight"):
        upsert_property_setter(PARENT, "sr_pkg_applied_weight", "in_list_view", "1", "Check")