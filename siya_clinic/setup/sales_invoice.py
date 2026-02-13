# siya_clinic/setup/sales_invoice.py
import frappe
import logging

from .utils import (
    create_cf_with_module,
    ensure_field_after,
    upsert_property_setter,
)

logger = logging.getLogger(__name__)

PARENT = "Sales Invoice"


def apply():
    logger.info("Applying sales invoice customizations")
    _make_item_group_template_field()
    frappe.clear_cache(doctype=PARENT)


def _make_item_group_template_field():
    """
    Create Item Group Template field on Sales Invoice
    and ensure it is placed after update_stock.
    """

    # -------------------------------------------------
    # 1️⃣ Create the field (idempotent)
    # -------------------------------------------------
    logger.info("Ensuring Item Group Template field exists")

    create_cf_with_module({
        PARENT: [
            {
                "fieldname": "item_group_template",
                "label": "Item Group Template",
                "fieldtype": "Link",
                "options": "Item Group Template",
                "reqd": 0,
            }
        ]
    })

    # -------------------------------------------------
    # 2️⃣ Ensure position after update_stock
    # -------------------------------------------------
    meta = frappe.get_meta(PARENT)
    if meta.get_field("update_stock"):
        logger.info("Positioning field after update_stock")
        ensure_field_after(
            doctype=PARENT,
            fieldname="item_group_template",
            after="update_stock"
        )
    else:
        logger.warning("update_stock field not found — skipping position adjustment")

    # -------------------------------------------------
    # 3️⃣ UI polish (bold label)
    # -------------------------------------------------
    logger.info("Applying UI polish for item_group_template")

    upsert_property_setter(
        doctype=PARENT,
        fieldname="item_group_template",
        prop="bold",
        value="1",
        property_type="Check"
    )