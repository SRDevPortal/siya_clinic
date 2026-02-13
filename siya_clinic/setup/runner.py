# siya_clinic/setup/runner.py
import frappe
import logging

from . import (
    masters,
    # patient, customer, practitioner, contact,
    # encounter, crm_lead, patient_appointment,
    # drug_prescription, item_price, item_package,
    # sales_invoice, payment_entry, purchase_order, user, company,
    # print_formats,
    sales_invoice,
)

logger = logging.getLogger(__name__)


def _should_skip():
    """Skip setup in test or patch contexts."""
    if getattr(frappe.flags, "in_test", False):
        return True
    if getattr(frappe.flags, "in_patch", False):
        return True
    return False


def setup_all():
    """
    Main setup orchestrator.
    Safe to run multiple times.
    """
    if _should_skip():
        logger.info("Skipping Siya Clinic setup (test/patch context)")
        return

    logger.info("🚀 Siya Clinic setup started")

    try:
        # -------------------------------------------------
        # Master Data fields/customizations
        # -------------------------------------------------
        logger.info("Applying masters setup")
        masters.apply()

        # -------------------------------------------------
        # Patient fields/customizations
        # -------------------------------------------------
        # logger.info("Applying patient setup")
        # patient.apply()

        # -------------------------------------------------
        # Customer fields/customizations
        # -------------------------------------------------
        # logger.info("Applying customer setup")
        # customer.apply()

        # -------------------------------------------------
        # Practitioner fields/customizations
        # -------------------------------------------------
        # logger.info("Applying practitioner setup")
        # practitioner.apply()

        # -------------------------------------------------
        # Contact/Address fields/customizations
        # -------------------------------------------------
        # logger.info("Applying contact setup")
        # contact.apply()

        # -------------------------------------------------
        # Patient Encounter fields/customizations
        # -------------------------------------------------
        # logger.info("Applying encounter setup")
        # encounter.apply()

        # -------------------------------------------------
        # CRM Lead fields/customizations
        # -------------------------------------------------
        # logger.info("Applying crm lead setup")
        # crm_lead.apply()

        # -------------------------------------------------
        # Patient Appointment fields/customizations
        # -------------------------------------------------
        # logger.info("Applying patient appointment setup")
        # patient_appointment.apply()

        # -------------------------------------------------
        # Drug Prescription fields/customizations
        # -------------------------------------------------
        # logger.info("Applying drug prescription setup")
        # drug_prescription.apply()

        # -------------------------------------------------
        # Item Price fields/customizations
        # -------------------------------------------------
        # logger.info("Applying item price setup")
        # item_price.apply()

        # -------------------------------------------------
        # Item Package fields/customizations
        # -------------------------------------------------
        # logger.info("Applying item package setup")
        # item_package.apply()

        # -------------------------------------------------
        # Sales Invoice fields/customizations
        # -------------------------------------------------
        logger.info("Applying sales invoice setup")
        sales_invoice.apply()

        # -------------------------------------------------
        # Payment Entry fields/customizations
        # -------------------------------------------------
        # logger.info("Applying payment entry setup")
        # payment_entry.apply()

        # -------------------------------------------------
        # Purchase Order fields/customizations
        # -------------------------------------------------
        # logger.info("Applying purchase order setup")
        # purchase_order.apply()

        # -------------------------------------------------
        # User fields/customizations
        # -------------------------------------------------
        # logger.info("Applying user setup")
        # user.apply()

        # -------------------------------------------------
        # Company fields/customizations
        # -------------------------------------------------
        # logger.info("Applying company setup")
        # company.apply()

        # -------------------------------------------------
        # Print Format fields/customizations
        # -------------------------------------------------
        # logger.info("Applying print formats setup")
        # print_formats.apply()

        # -------------------------------------------------
        # Finalize
        # -------------------------------------------------
        frappe.clear_cache()
        frappe.db.commit()

        logger.info("✅ Siya Clinic setup completed")

    except Exception as e:
        frappe.db.rollback()
        logger.error(f"❌ Siya Clinic setup failed: {e}")
        raise
