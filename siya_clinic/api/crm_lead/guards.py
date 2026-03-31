# siya_clinic/api/crm_lead/guards.py

from __future__ import annotations
import frappe

# ---------------------------------------------------------
# Roles
# ---------------------------------------------------------
TL = "Team Leader"
AG = "Agent"

# ---------------------------------------------------------
# Field Rules
# ---------------------------------------------------------
# TL → only on insert
# Agent → never
LOCK_FIELDS = {
    "sr_lead_pipeline",
    "sr_lead_platform",
    "source",
    "sr_lead_saleteam",
    "mobile_no",
    "phone",
}

# Agent extra restriction
AGENT_LOCK = {"lead_owner"}

# Privileged bypass
PRIVILEGED_USERS = {"Administrator"}
PRIVILEGED_ROLES = {"System Manager"}


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def _roles(user: str) -> set[str]:
    try:
        return set(frappe.get_roles(user) or [])
    except Exception:
        return set()


def _is_privileged(user: str) -> bool:
    if user in PRIVILEGED_USERS:
        return True
    return bool(_roles(user) & PRIVILEGED_ROLES)


def _has_role(user: str, role: str) -> bool:
    return role in _roles(user)


def _changed(doc, field: str, old_doc=None) -> bool:
    """Check if field value changed"""
    if doc.is_new():
        val = doc.get(field)
        return val not in (None, "", [])

    return (doc.get(field) or "") != (old_doc.get(field) or "")


# def _changed(doc, field: str) -> bool:
#     if doc.is_new():
#         val = doc.get(field)
#         return val not in (None, "", [])
#     prev = frappe.db.get_value(doc.doctype, doc.name, field)
#     return (doc.get(field) or "") != (prev or "")


# ---------------------------------------------------------
# Main Guard
# ---------------------------------------------------------
def guard_restricted_fields(doc, method=None):

    if doc.doctype != "CRM Lead":
        return

    # Bypass flag (for scripts, patches, etc.)
    if getattr(frappe.flags, "sr_bypass_field_guard", False):
        return

    user = frappe.session.user or "Guest"

    # 👑 Admin / System Manager bypass
    if _is_privileged(user):
        return

    roles = _roles(user)
    is_tl = TL in roles
    is_agent = AG in roles

    blocked = set()

    # Fetch old doc once (performance optimized)
    old_doc = None
    if not doc.is_new():
        old_doc = doc.get_doc_before_save()

    # ---------------------------------------------------
    # 🔒 Main Field Rules
    # ---------------------------------------------------
    for f in LOCK_FIELDS:
        if _changed(doc, f, old_doc):

            # 🆕 On Insert
            if doc.is_new():
                if not is_tl:
                    blocked.add(f)

            # 💾 After Save → always locked
            else:
                blocked.add(f)

    # ---------------------------------------------------
    # 👨‍💻 Agent extra restriction
    # ---------------------------------------------------
    if is_agent:
        for f in AGENT_LOCK:
            if _changed(doc, f, old_doc):
                blocked.add(f)

    # ---------------------------------------------------
    # ❌ Block changes
    # ---------------------------------------------------
    if blocked:
        meta = frappe.get_meta(doc.doctype)

        # Convert fieldnames → labels for better UX
        labels = [meta.get_label(f) or f for f in sorted(blocked)]

        frappe.throw(
            "You are not allowed to modify restricted fields:<br><b>{}</b>".format(", ".join(labels)),
            title="Permission Denied",
        )