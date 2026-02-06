# apps/siya_clinic/siya_clinic/setup/masters.py

import frappe
from .utils import (
    MODULE_DEF_NAME, APP_PY_MODULE,
    ensure_module_def,
    reload_local_json_doctypes,
)

# ------------------------------------------------------------
# List of DocTypes shipped as JSON (folder names under doctype/)
# ------------------------------------------------------------
JSON_DOCTYPES = [
    # Example:
    # "sr_patient_disable_reason",
    # "sr_patient_invoice_view",
]

def apply():
    """
    Apply all master setup steps for Siya Clinic.

    This function is idempotent and safe to run multiple times.
    It ensures:
    - Module Def exists
    - JSON DocTypes are reloaded (if any)
    - All required master DocTypes are created
    """

    # --------------------------------------------------------
    # Ensure Module Definition exists
    # --------------------------------------------------------
    ensure_module_def(MODULE_DEF_NAME, APP_PY_MODULE)

    # --------------------------------------------------------
    # Reload local JSON DocTypes (if any are shipped)
    # --------------------------------------------------------
    reload_local_json_doctypes(JSON_DOCTYPES)

    # --------------------------------------------------------
    # Create any master DocTypes that are required but not shipped as JSON
    # --------------------------------------------------------
    create_item_group_template_item_doctype()
    create_item_group_template_doctype()


def create_item_group_template_item_doctype():
    """Creates the 'Item Group Template Item' child table DocType if it doesn't exist."""
    doctype = "Item Group Template Item"

    if frappe.db.exists("DocType", doctype):
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": doctype,
        "module": MODULE_DEF_NAME,
        "custom": 1,
        "istable": 1,
        "fields": [
            {
                "fieldname": "item_code",
                "label": "Item",
                "fieldtype": "Link",
                "options": "Item",
                "reqd": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "item_name",
                "label": "Item Name",
                "fieldtype": "Data",
                "fetch_from": "item_code.item_name",
                "read_only": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "qty",
                "label": "Qty",
                "fieldtype": "Float",
                "default": 1,
                "in_list_view": 1,
            },
            {
                "fieldname": "rate",
                "label": "Rate",
                "fieldtype": "Currency",
                "in_list_view": 1,
            },
            {
                "fieldname": "item_tax_template",
                "label": "GST Template",
                "fieldtype": "Link",
                "options": "Item Tax Template",
                "in_list_view": 1,
            },
        ],
    })

    doc.insert(ignore_permissions=True)


def create_item_group_template_doctype():
    """Creates the 'Item Group Template' master DocType if it doesn't exist."""
    doctype = "Item Group Template"

    if frappe.db.exists("DocType", doctype):
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": doctype,
        "module": MODULE_DEF_NAME,
        "custom": 1,
        "autoname": "field:template_name",
        "title_field": "template_name",
        "track_changes": 1,
        "fields": [
            {
                "fieldname": "template_name",
                "label": "Template Name",
                "fieldtype": "Data",
                "reqd": 1,
                "unique": 1,
            },
            {
                "fieldname": "description",
                "label": "Description",
                "fieldtype": "Small Text",
            },
            {
                "fieldname": "is_active",
                "label": "Is Active",
                "fieldtype": "Check",
                "default": 1,
            },
            {
                "fieldname": "section_items",
                "label": "Items",
                "fieldtype": "Section Break",
            },
            {
                "fieldname": "items",
                "label": "Items",
                "fieldtype": "Table",
                "options": "Item Group Template Item",
                "reqd": 1,
            },
        ],
        "permissions": [
            {
                "role": "System Manager",
                "read": 1,
                "write": 1,
                "create": 1,
                "delete": 1,
                "report": 1,
            }
        ],
    })

    doc.insert(ignore_permissions=True)
