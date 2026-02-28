# siya_clinic/setup/contact.py
import frappe
import logging

from .utils import upsert_property_setter

# Set up logger for the module
logger = logging.getLogger(__name__)

def apply():
    """Apply contact UI customizations and clear cache."""
    
    # Log the start of the contact setup process
    logger.info("Applying Contact setup")
    
    # Apply the contact UI customizations
    _apply_contact_ui_customizations()

    # Clear Frappe cache and commit changes to the database
    frappe.clear_cache()
    frappe.db.commit()

    # Log the completion of the contact setup
    logger.info("Contact setup completed")

def _apply_contact_ui_customizations():
    """Apply UI customizations for the Address DocType."""
    # Setting default value for "is_primary_address" field in "Address"
    upsert_property_setter("Address", "is_primary_address", "default", "1", "Text")
    
    # Setting default value for "is_shipping_address" field in "Address"
    upsert_property_setter("Address", "is_shipping_address", "default", "1", "Text")