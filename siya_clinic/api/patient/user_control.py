import frappe

def disable_invite_user(doc, method=None):
    """Force disable invite user."""
    doc.invite_user = 0