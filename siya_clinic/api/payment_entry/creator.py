import frappe


def set_created_by_agent(doc, method=None):
    """
    Hook: before_insert on Payment Entry
    Populate created_by_agent with current session user if empty.
    """

    try:
        if not getattr(doc, "created_by_agent", None):
            doc.created_by_agent = frappe.session.user

    except Exception:
        # Do not block document creation for non-critical errors
        frappe.log_error(
            f"set_created_by_agent failed for Payment Entry {getattr(doc, 'name', '')}",
            "siya_clinic Payment Entry Hook Error"
        )