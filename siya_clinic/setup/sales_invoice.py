# siya_clinic/setup/sales_invoice.py

import frappe
import logging

from .utils import (
    create_cf_with_module,
    ensure_field_after,
    upsert_property_setter,
    upsert_title_field,
)

logger = logging.getLogger(__name__)

PARENT = "Sales Invoice"
CHILD = "Sales Invoice Item"


def apply():
    logger.info("Applying Sales Invoice customizations")

    _make_invoice_fields()
    _make_item_group_template_field()
    _apply_invoice_ui_customizations()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Sales Invoice customization completed")


# =========================================================
# Custom Fields
# =========================================================

def _lead_source_doctype() -> str:
    """Return available Lead Source DocType in priority order."""
    if frappe.db.exists("DocType", "SR Lead Source"):
        return "SR Lead Source"
    if frappe.db.exists("DocType", "CRM Lead Source"):
        return "CRM Lead Source"
    return "Lead Source"


def _make_invoice_fields():
    """
    Adds tracking & workflow fields to Sales Invoice.
    Designed for Encounter → Sales Invoice automation.
    """

    lead_source_dt = _lead_source_doctype()

    create_cf_with_module({
        PARENT: [

            # -------------------------------------------------
            # Patient Info
            # -------------------------------------------------
            {
                "fieldname": "sr_si_patient_id",
                "label": "Patient ID",
                "fieldtype": "Data",
                "read_only": 1,
                "fetch_from": "patient.sr_patient_id",
                "insert_after": "customer_name",
            },
            {
                "fieldname": "sr_si_patient_department",
                "label": "Patient Department",
                "fieldtype": "Link",
                "options": "Medical Department",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "read_only": 1,
                "fetch_from": "patient.sr_medical_department",
                "insert_after": "sr_si_patient_id",
            },

            # -------------------------------------------------
            # Tracking Section
            # -------------------------------------------------
            {
                "fieldname": "sr_si_track_sb",
                "label": "Order Tracking Details",
                "fieldtype": "Section Break",
                "collapsible": 1,
                "insert_after": "gst_breakup_table",
            },

            # -------------------------------------------------
            # Order Source
            # -------------------------------------------------
            {
                "fieldname": "sr_si_order_source",
                "label": "Order Source",
                "fieldtype": "Link",
                "options": lead_source_dt,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "sr_si_track_sb",
            },

            # -------------------------------------------------
            # Encounter Place
            # -------------------------------------------------
            {
                "fieldname": "sr_si_encounter_place",
                "label": "Encounter Place",
                "fieldtype": "Link",
                "options": "SR Encounter Place",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "sr_si_order_source",
            },

            # -------------------------------------------------
            # Sales Type
            # -------------------------------------------------
            {
                "fieldname": "sr_si_sales_type",
                "label": "Sales Type",
                "fieldtype": "Link",
                "options": "SR Sales Type",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "sr_si_encounter_place",
            },

            # -------------------------------------------------
            # Delivery Type
            # -------------------------------------------------
            {
                "fieldname": "sr_si_delivery_type",
                "label": "Delivery Type",
                "fieldtype": "Link",
                "options": "SR Delivery Type",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "allow_on_submit": 1,
                "insert_after": "sr_si_sales_type",
            },

            # -------------------------------------------------
            # Shipkia Flag (Hidden)
            # -------------------------------------------------
            {
                "fieldname": "sent_to_shipkia",
                "label": "Sent to Shipkia",
                "fieldtype": "Check",
                "default": "0",
                "read_only": 1,
                "hidden": 1,
                "print_hide": 1,
                "insert_after": "sr_si_delivery_type",
            },

            # -------------------------------------------------
            # Audit Field
            # -------------------------------------------------
            {
                "fieldname": "created_by_agent",
                "label": "Created By",
                "fieldtype": "Link",
                "options": "User",
                "read_only": 1,
                "insert_after": "due_date",
            },
        ]
    })


def _make_item_group_template_field():
    """Create Item Group Template field on Sales Invoice and ensure it is placed after update_stock."""

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
        # logger.info("Positioning field after update_stock")
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


def _apply_invoice_ui_customizations():
    """Apply UI customizations to Sales Invoice (safe version)."""

    meta = frappe.get_meta(PARENT)

    # -------------------------------------------------
    # Hide only non-critical ERP fields
    # -------------------------------------------------
    safe_hide_fields = (
        "ewaybill",
        "e_waybill_status",
        "redeem_loyalty_points",
        "allocate_advances_automatically",
        "get_advances",
        "advances",
    )

    for f in safe_hide_fields:
        if meta.get_field(f):
            upsert_property_setter(PARENT, f, "hidden", "1", "Check")
            upsert_property_setter(PARENT, f, "print_hide", "1", "Check")
            upsert_property_setter(PARENT, f, "in_list_view", "0", "Check")
            upsert_property_setter(PARENT, f, "in_standard_filter", "0", "Check")

    # -------------------------------------------------
    # List & filter visibility
    # -------------------------------------------------
    if meta.get_field("company"):
        upsert_property_setter(PARENT, "company", "in_standard_filter", "0", "Check")
    
    if meta.get_field("contact_mobile"):
        upsert_property_setter(PARENT, "contact_mobile", "in_list_view", "1", "Check")
        upsert_property_setter(PARENT, "contact_mobile", "in_standard_filter", "1", "Check")
    
    if meta.get_field("patient_name"):
        upsert_property_setter(PARENT, "patient_name", "in_list_view", "1", "Check")
    
    # Set title field to patient_name
    upsert_title_field(PARENT, "patient_name")

    # -------------------------------------------------
    # ⭐ NEW: Show Patient Name as List Title
    # -------------------------------------------------
    if meta.get_field("patient_name"):
        upsert_property_setter(PARENT, "title_field", "default", "patient_name", "Data")
        upsert_property_setter(PARENT, "show_title_field_in_link", "default", "1", "Check")
        upsert_property_setter(PARENT, "patient_name", "in_standard_filter", "1", "Check")

    # Optional: hide default Title column
    if meta.get_field("title"):
        upsert_property_setter(PARENT, "title", "hidden", "1", "Check")
    