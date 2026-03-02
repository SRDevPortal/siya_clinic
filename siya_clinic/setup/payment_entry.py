# siya_clinic/setup/payment_entry.py

import frappe
import logging

from .utils import (
    create_cf_with_module,
    upsert_property_setter,
    upsert_title_field,
    ensure_field_after,
)

logger = logging.getLogger(__name__)

DT = "Payment Entry"


def apply():
    logger.info("Applying Payment Entry customizations")

    _make_payment_entry_fields()
    _customize_payment_entry_doctype()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Payment Entry customization completed")


# =========================================================
# Helpers
# =========================================================

def _lead_source_dt() -> str:
    """Return available Lead Source DocType."""
    if frappe.db.exists("DocType", "SR Lead Source"):
        return "SR Lead Source"
    if frappe.db.exists("DocType", "CRM Lead Source"):
        return "CRM Lead Source"
    return "Lead Source"


# =========================================================
# Custom Fields
# =========================================================

def _make_payment_entry_fields():
    """
    Adds tracking & automation fields to Payment Entry.
    Safe to run multiple times.
    """

    lead_source_dt = _lead_source_dt()

    create_cf_with_module({
        DT: [

            # -------------------------------------------------
            # Hidden Link to Sales Invoice
            # -------------------------------------------------
            {
                "fieldname": "intended_sales_invoice",
                "label": "Intended Sales Invoice",
                "fieldtype": "Link",
                "options": "Sales Invoice",
                "insert_after": "references",
                "read_only": 1,
                "hidden": 1,
            },

            # -------------------------------------------------
            # Created By Agent (auto-filled via hook)
            # -------------------------------------------------
            {
                "fieldname": "created_by_agent",
                "label": "Created By",
                "fieldtype": "Link",
                "options": "User",
                "read_only": 1,
                "insert_after": "posting_date",
            },

            # -------------------------------------------------
            # Tracking Section
            # -------------------------------------------------
            {
                "fieldname": "sr_pe_track_sb",
                "label": "Order Tracking Details",
                "fieldtype": "Section Break",
                "collapsible": 1,
                "insert_after": "cost_center",
            },

            # -------------------------------------------------
            # Order Source
            # -------------------------------------------------
            {
                "fieldname": "sr_pe_order_source",
                "label": "Order Source",
                "fieldtype": "Link",
                "options": lead_source_dt,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "sr_pe_track_sb",
            },

            # -------------------------------------------------
            # Encounter Place
            # -------------------------------------------------
            {
                "fieldname": "sr_pe_encounter_place",
                "label": "Encounter Place",
                "fieldtype": "Link",
                "options": "SR Encounter Place",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "sr_pe_order_source",
            },

            # -------------------------------------------------
            # Sales Type
            # -------------------------------------------------
            {
                "fieldname": "sr_pe_sales_type",
                "label": "Sales Type",
                "fieldtype": "Link",
                "options": "SR Sales Type",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "sr_pe_encounter_place",
            },

            # -------------------------------------------------
            # Delivery Type
            # -------------------------------------------------
            {
                "fieldname": "sr_pe_delivery_type",
                "label": "Delivery Type",
                "fieldtype": "Link",
                "options": "SR Delivery Type",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "allow_on_submit": 0,
                "insert_after": "sr_pe_sales_type",
            },
        ]
    })


# =========================================================
# UI Customizations
# =========================================================

def _customize_payment_entry_doctype():
    """Additional UI and behavior customizations."""

    meta = frappe.get_meta(DT)

    # Ensure section position
    ensure_field_after(DT, "sr_pe_track_sb", "cost_center")

    # Hide intended_sales_invoice everywhere
    upsert_property_setter(DT, "intended_sales_invoice", "in_list_view", "0", "Check")
    upsert_property_setter(DT, "intended_sales_invoice", "in_standard_filter", "0", "Check")
    upsert_property_setter(DT, "intended_sales_invoice", "print_hide", "1", "Check")

    # created_by_agent UI control
    # if meta.get_field("created_by_agent"):
    #     upsert_property_setter(DT, "created_by_agent", "hidden", "0", "Check")
    #     upsert_property_setter(DT, "created_by_agent", "in_list_view", "0", "Check")
    #     upsert_property_setter(DT, "created_by_agent", "in_standard_filter", "0", "Check")
    #     upsert_property_setter(DT, "created_by_agent", "print_hide", "1", "Check")

    # Set title field
    upsert_title_field(DT, "party_name")