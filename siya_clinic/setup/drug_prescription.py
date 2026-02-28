import frappe
import logging

from .utils import create_cf_with_module, upsert_property_setter

logger = logging.getLogger(__name__)

DT = "Drug Prescription"


def apply():
    logger.info("Applying Drug Prescription customizations")

    _make_drug_prescription_fields()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Drug Prescription customization completed")


# =========================================================
# Custom Fields
# =========================================================

def _make_drug_prescription_fields():
    """
    Adds custom fields to Drug Prescription for better
    printing and instruction management.
    Safe to run multiple times.
    """

    create_cf_with_module({
        DT: [
            # -------------------------------------------------
            # Medication Name (for print & list view)
            # -------------------------------------------------
            {
                "fieldname": "sr_medication_name_print",
                "label": "Medication Name",
                "fieldtype": "Data",
                "read_only": 1,
                "in_list_view": 1,
                "in_standard_filter": 0,
                "insert_after": "medication",
            },

            # -------------------------------------------------
            # Instruction Link
            # -------------------------------------------------
            {
                "fieldname": "sr_drug_instruction",
                "label": "Instruction",
                "fieldtype": "Link",
                "options": "SR Instruction",
                "in_list_view": 1,
                "in_standard_filter": 0,
                "insert_after": "period",
            },
        ]
    })
