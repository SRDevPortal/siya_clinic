import frappe

# ---------------------------------------------------------
# Set Creator (Agent Tracking)
# ---------------------------------------------------------
def set_customer_creator(doc, method=None):
    """Populate created_by_agent on insert only."""
    if not doc.get("created_by_agent"):
        doc.created_by_agent = frappe.session.user or "Administrator"