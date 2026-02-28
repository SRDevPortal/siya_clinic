# siya_clinic/setup/healthcare_practitioner.py

import frappe
import logging

from .utils import create_cf_with_module, upsert_property_setter

logger = logging.getLogger(__name__)

DT = "Healthcare Practitioner"


def apply():
    """Apply Healthcare Practitioner customizations."""
    logger.info("Applying Healthcare Practitioner setup")

    _make_practitioner_fields()
    _apply_practitioner_ui_customizations()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Healthcare Practitioner setup completed")


# ------------------------------------------------------------
# Custom Fields
# ------------------------------------------------------------

def _make_practitioner_fields():
    """Add custom fields to Healthcare Practitioner."""

    create_cf_with_module({
        DT: [
            {
                "fieldname": "sr_reg_no",
                "label": "Registration No",
                "fieldtype": "Data",
                "insert_after": "office_phone",
            },
            {
                "fieldname": "sr_qualification",
                "label": "Qualification",
                "fieldtype": "Data",
                "reqd": 1,
                "insert_after": "sr_reg_no",
            },
            {
                "fieldname": "sr_college_university",
                "label": "College/University",
                "fieldtype": "Data",
                "insert_after": "sr_qualification",
            },
            {
                "fieldname": "sr_pathy",
                "label": "Pathy",
                "fieldtype": "Link",
                "options": "SR Practitioner Pathy",
                "reqd": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "practitioner_type",
            },
        ]
    })


# ------------------------------------------------------------
# Naming & Identity Rules
# ------------------------------------------------------------

def _apply_practitioner_ui_customizations():
    """Enforce naming rules for Healthcare Practitioner."""

    # Use practitioner_name as primary identity
    upsert_property_setter(DT, "", "autoname", "field:practitioner_name", "Data")
    upsert_property_setter(DT, "", "title_field", "practitioner_name", "Data")

    # Harden field
    upsert_property_setter(DT, "practitioner_name", "reqd", "1", "Check")
    upsert_property_setter(DT, "practitioner_name", "unique", "1", "Check")