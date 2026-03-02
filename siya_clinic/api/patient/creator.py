import frappe

def set_patient_creator(doc, method=None):
    """
    Populate created_by_agent on insert only.
    Migrated from siya_clinic.
    """

    # Run only for new records
    if doc.is_new():

        # If field already set, do nothing
        if getattr(doc, "created_by_agent", None):
            return

        # Set creator from session
        doc.created_by_agent = frappe.session.user or "Administrator"