# siya_clinic/api/crm_lead/guards.py
# Field-level protection + role helpers for CRM Lead

from __future__ import annotations

import frappe

from siya_clinic.api.crm_lead.config import REF_DOCTYPE, get_config, get_locked_fields


def _is_privileged(user: str) -> bool:
	from sriaas_role_permissions.api.roles import is_privileged

	return is_privileged(user, REF_DOCTYPE)


def _has_team_leader_role(user: str) -> bool:
	from sriaas_role_permissions.api.roles import has_team_leader_role

	return has_team_leader_role(user, REF_DOCTYPE)


def _has_agent_role(user: str) -> bool:
	from sriaas_role_permissions.api.roles import has_agent_role

	return has_agent_role(user, REF_DOCTYPE)


def _changed(doc, field: str, old_doc=None) -> bool:
	if doc.is_new():
		value = doc.get(field)
		return value not in (None, "", [])

	if old_doc:
		return (doc.get(field) or "") != (old_doc.get(field) or "")

	previous = frappe.db.get_value(doc.doctype, doc.name, field)
	return (doc.get(field) or "") != (previous or "")


def guard_restricted_fields(doc, method=None):
	config = get_config()
	if doc.doctype != config.ref_doctype:
		return

	if getattr(frappe.flags, "sr_bypass_field_guard", False):
		return

	user = frappe.session.user or "Guest"
	if _is_privileged(user):
		return

	is_team_leader = _has_team_leader_role(user)
	is_agent = _has_agent_role(user)
	locked_fields = get_locked_fields()
	lock_after_insert = locked_fields["lock_after_insert"]
	agent_always_lock = locked_fields["agent_always_lock"]

	blocked: set[str] = set()
	old_doc = None if doc.is_new() else doc.get_doc_before_save()

	for fieldname in lock_after_insert:
		if not _changed(doc, fieldname, old_doc):
			continue

		if doc.is_new():
			if not is_team_leader:
				blocked.add(fieldname)
		else:
			blocked.add(fieldname)

	if is_agent:
		for fieldname in agent_always_lock:
			if _changed(doc, fieldname, old_doc):
				blocked.add(fieldname)

	if blocked:
		meta = frappe.get_meta(doc.doctype)
		labels = [meta.get_label(fieldname) or fieldname for fieldname in sorted(blocked)]
		frappe.throw(
			"You are not allowed to modify restricted fields:<br><b>{}</b>".format(", ".join(labels)),
			title="Permission Denied",
		)
