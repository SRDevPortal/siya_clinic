# siya_clinic/api/crm_lead/guards.py

from __future__ import annotations
import frappe

TL = "Team Leader"
AG = "Agent"

# Fields with rule:
# TL → only on insert
# Agent → never
LOCK_FIELDS = {"sr_lead_pipeline", "sr_lead_platform", "source", "mobile_no", "phone"}

AGENT_LOCK = {"lead_owner"}

PRIVILEGED_USERS = {"Administrator"}
PRIVILEGED_ROLES = {"System Manager"}


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


def _changed(doc, field: str) -> bool:
    if doc.is_new():
        val = doc.get(field)
        return val not in (None, "", [])
    prev = frappe.db.get_value(doc.doctype, doc.name, field)
    return (doc.get(field) or "") != (prev or "")


def guard_restricted_fields(doc, method=None):

    if doc.doctype != "CRM Lead":
        return

    if getattr(frappe.flags, "sr_bypass_field_guard", False):
        return

    user = frappe.session.user or "Guest"

    # 👑 Admin bypass
    if _is_privileged(user):
        return

    is_tl = _has_role(user, TL)
    is_agent = _has_role(user, AG)

    blocked = set()

    # ---------------------------------------------------
    # 🔒 Main Field Rules
    # ---------------------------------------------------
    for f in LOCK_FIELDS:
        if _changed(doc, f):

            # 🆕 On Insert
            if doc.is_new():
                if not is_tl:
                    blocked.add(f)

            # 💾 After Save
            else:
                blocked.add(f)

    # ---------------------------------------------------
    # 👨‍💻 Agent extra restriction
    # ---------------------------------------------------
    if is_agent:
        for f in AGENT_LOCK:
            if _changed(doc, f):
                blocked.add(f)

    # ---------------------------------------------------
    # ❌ Block
    # ---------------------------------------------------
    if blocked:
        frappe.throw(
            "You are not allowed to change: " + ", ".join(sorted(blocked)),
            title="Not permitted",
        )