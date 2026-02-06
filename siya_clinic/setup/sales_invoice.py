import frappe
from .utils import (
    create_cf_with_module,
    ensure_field_after,
    upsert_property_setter,
)

PARENT = "Sales Invoice"


def apply():
    _make_item_group_template_field()


def _make_item_group_template_field():
    """
    Create Item Group Template field on Sales Invoice
    and ensure it is placed after update_stock.
    """

    # 1️⃣ Create the field (idempotent)
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

    # 2️⃣ Ensure position after update_stock
    ensure_field_after(
        doctype=PARENT,
        fieldname="item_group_template",
        after="update_stock"
    )

    # 3️⃣ Optional UI polish (recommended)
    upsert_property_setter(
        doctype=PARENT,
        fieldname="item_group_template",
        prop="bold",
        value="1",
        property_type="Check"
    )
