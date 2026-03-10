import frappe
import logging

logger = logging.getLogger(__name__)

def set_appointment_creator(doc, method=None):
    """
    Automatically set the user who created the Appointment.
    Triggered on before_insert.
    """

    try:
        # Run only for new records
        if not doc.is_new():
            return

        # Do not overwrite if already set
        if getattr(doc, "created_by_agent", None):
            return

        # Set creator
        doc.created_by_agent = frappe.session.user or "Administrator"

    except Exception:
        logger.exception(
            "Failed to set created_by_agent for Patient Appointment: %s", doc.name
        )