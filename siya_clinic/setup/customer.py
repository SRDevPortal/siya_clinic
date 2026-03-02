# siya_clinic/setup/customer.py
import frappe
import logging

from .utils import create_cf_with_module, upsert_property_setter

logger = logging.getLogger(__name__)

DT = "Customer"


def apply():
    """Entry point called from setup.runner"""
    
    logger.info("Applying Customer setup")

    _make_customer_fields()
    # _apply_customer_ui_customizations()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Customer setup completed")


# =========================================================
# Custom Fields
# =========================================================

def _make_customer_fields():
    """Add custom fields to Customer"""

    create_cf_with_module({
        DT: [
            {
                "fieldname": "sr_customer_id",
                "label": "Customer ID",
                "fieldtype": "Data",
                "insert_after": "customer_name",
                "read_only": 1,
                "unique": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "search_index": 1,
            },
            {
                "fieldname": "created_by_agent",
                "label": "Created By",
                "fieldtype": "Link",
                "options": "User",
                "insert_after": "sr_customer_id",
                "read_only": 1,
                "in_list_view": 1,
            }
        ]
    })


# =========================================================
# Property Setters
# =========================================================

def _apply_customer_ui_customizations():
    """DocType-level tweaks for Customer"""

    # Disable rename
    upsert_property_setter("Customer", "allow_rename", "default", "0", "Check")

    # ✅ Show Customer Name in links
    upsert_property_setter("Customer", "title_field", "default", "customer_name", "Data")
    upsert_property_setter("Customer", "show_title_field_in_link", "default", "1", "Check")

    # ✅ Search by customer_name
    upsert_property_setter("Customer", "search_fields", "default", "customer_name, sr_customer_id", "Data")

    # ✅ Enable global search
    upsert_property_setter("Customer", "show_name_in_global_search", "default", "1", "Check")
