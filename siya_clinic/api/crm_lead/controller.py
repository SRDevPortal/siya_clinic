# siya_clinic/api/crm_lead/controller.py
# Public APIs (normalize / assign / clear) for CRM Lead


from __future__ import annotations

import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions

from siya_clinic.api.crm_lead.config import REF_DOCTYPE, get_config, get_locked_fields
from siya_clinic.api.crm_lead.utils import clean_spaces


def normalize_phoneish_fields(doc, method=None):
	if doc.doctype != get_config().ref_doctype:
		return

	candidate_fields = (
		"mobile",
		"mobile_no",
		"phone",
		"phone_no",
		"whatsapp_no",
		"alternate_phone",
		"sr_mobile_no",
		"sr_whatsapp_no",
	)

	previous_flag = getattr(frappe.flags, "sr_bypass_field_guard", False)
	frappe.flags.sr_bypass_field_guard = True
	try:
		for fieldname in candidate_fields:
			value = doc.get(fieldname)
			cleaned = clean_spaces(value)
			if cleaned != value:
				doc.set(fieldname, cleaned)
	finally:
		frappe.flags.sr_bypass_field_guard = previous_flag


def _agent_allowed_for_pipeline(user: str, pipeline: str) -> bool:
	pipeline_doctype = get_config().pipeline_doctype
	if not pipeline_doctype:
		return False

	perms = get_user_permissions(user) or {}
	raw = perms.get(pipeline_doctype) or []

	allowed = set()
	for value in raw:
		if isinstance(value, str):
			allowed.add(value)
		elif isinstance(value, dict):
			allowed.add(value.get("doc") or value.get("value") or value.get("name"))

	allowed.discard(None)
	allowed.discard("")
	return pipeline in allowed


def _get_pipeline_title(pipeline_id: str) -> str:
	if not pipeline_id:
		return pipeline_id

	config = get_config()
	title_field = "sr_pipeline_name" if config.pipeline_doctype == "SR Lead Pipeline" else None
	if title_field and frappe.db.has_column(config.pipeline_doctype, title_field):
		return frappe.db.get_value(config.pipeline_doctype, pipeline_id, title_field) or pipeline_id
	return pipeline_id


@frappe.whitelist()
def get_crm_lead_role_context():
	from siya_clinic.api.crm_lead.access import (
		_is_assistant_team_lead,
		_is_effective_team_leader,
		_is_main_team_lead,
		_reports_to_team_leader,
		get_managed_team_users,
	)
	from siya_clinic.api.crm_lead.assign_guard import _is_team_leader
	from sriaas_role_permissions.api.roles import has_agent_role, has_team_leader_role, is_privileged

	user = frappe.session.user
	config = get_config()
	locked = get_locked_fields()
	reports_to = _reports_to_team_leader(user)

	return {
		"user": user,
		"ref_doctype": config.ref_doctype,
		"pipeline_doctype": config.pipeline_doctype,
		"pipeline_fieldname": config.pipeline_fieldname,
		"owner_fieldname": config.owner_fieldname,
		"team_leader_fieldname": config.team_leader_fieldname,
		"team_leader_label": config.team_leader_label,
		"agent_label": config.agent_label,
		"privileged_label": config.privileged_label,
		"lock_after_insert_fields": sorted(locked["lock_after_insert"]),
		"agent_always_lock_fields": sorted(locked["agent_always_lock"]),
		"is_privileged": is_privileged(user, REF_DOCTYPE),
		"has_team_leader_role": has_team_leader_role(user, REF_DOCTYPE),
		"has_agent_role": has_agent_role(user, REF_DOCTYPE),
		"reports_to_team_leader": reports_to,
		"is_main_team_lead": _is_main_team_lead(user),
		"is_assistant_team_lead": _is_assistant_team_lead(user),
		"is_effective_team_leader": _is_effective_team_leader(user),
		"managed_team_users": get_managed_team_users(user),
		"can_manage_assignment": _is_team_leader(user),
	}


def _ensure_assignment_target_allowed(new_owner: str) -> None:
	from siya_clinic.api.crm_lead.access import _is_privileged, get_managed_team_users

	if _is_privileged(frappe.session.user):
		return

	managed_users = set(get_managed_team_users(frappe.session.user))
	if managed_users and new_owner not in managed_users:
		frappe.throw(
			frappe._("{0} can assign only to active members of their managed team.").format(
				get_config().team_leader_label
			),
			title="Assignment Not Allowed",
			exc=frappe.PermissionError,
		)


def _ensure_can_manage_lead(doc) -> None:
	from siya_clinic.api.crm_lead.access import _is_privileged, crm_lead_has_permission

	if _is_privileged(frappe.session.user):
		return

	if not crm_lead_has_permission(doc, frappe.session.user):
		frappe.throw(
			frappe._("You can manage only leads visible to your managed team."),
			title="Lead Not Allowed",
			exc=frappe.PermissionError,
		)


@frappe.whitelist()
def assign_crm_lead_owner(leads, new_owner):
	from crm_lead_assignment.api.manual import assign_crm_leads

	return assign_crm_leads(leads, new_owner)

	from siya_clinic.api.crm_lead.assign_guard import _is_team_leader

	config = get_config()
	if not _is_team_leader(frappe.session.user):
		frappe.throw(
			f"Only configured {config.team_leader_label} users can assign {config.ref_doctype} records.",
			frappe.PermissionError,
		)

	if isinstance(leads, str):
		leads = frappe.parse_json(leads)

	if not frappe.db.exists("User", {"name": new_owner, "enabled": 1}):
		frappe.throw("Invalid or disabled user selected")

	_ensure_assignment_target_allowed(new_owner)

	for lead in leads:
		doc = frappe.get_doc(config.ref_doctype, lead)
		_ensure_can_manage_lead(doc)

		pipeline = doc.get(config.pipeline_fieldname)
		if pipeline and not _agent_allowed_for_pipeline(new_owner, pipeline):
			pipeline_name = _get_pipeline_title(pipeline)
			frappe.throw(
				frappe._(
					"This lead belongs to <b>{0}</b> pipeline.<br>"
					"{2} <b>{1}</b> is not allowed for this pipeline."
				).format(pipeline_name, new_owner, config.agent_label),
				title="Assignment Not Allowed",
			)

		if doc.get(config.owner_fieldname) == new_owner:
			continue

		doc.set(config.owner_fieldname, new_owner)
		doc.save(ignore_permissions=True)

		frappe.db.sql(
			"""
			update `tabToDo`
			set status='Closed'
			where reference_type=%s
			  and reference_name=%s
			  and status='Open'
			""",
			(config.ref_doctype, lead),
		)

		from frappe.desk.form.assign_to import add

		add(
			{
				"assign_to": [new_owner],
				"doctype": config.ref_doctype,
				"name": lead,
				"notify": 1,
			}
		)
		_repair_assignment_reference(lead, new_owner)

		doc.add_comment(
			"Info",
			f"Lead assigned to {new_owner} by {frappe.session.user}",
		)

	return {"status": "ok"}


def _repair_assignment_reference(lead, owner):
	config = get_config()
	frappe.db.sql(
		"""
		update `tabToDo`
		set reference_name = %s
		where reference_type = %s
		  and allocated_to = %s
		  and status = 'Open'
		  and (reference_name is null or reference_name = '')
		  and description like %s
		""",
		(lead, config.ref_doctype, owner, f"%{lead}%"),
	)


@frappe.whitelist()
def clear_crm_lead_owner(leads):
	from crm_lead_assignment.api.manual import clear_crm_leads

	return clear_crm_leads(leads)

	from siya_clinic.api.crm_lead.assign_guard import clear, _is_team_leader

	config = get_config()
	if not _is_team_leader(frappe.session.user):
		frappe.throw(
			f"Only configured {config.team_leader_label} users can clear {config.ref_doctype} assignments.",
			frappe.PermissionError,
		)

	if isinstance(leads, str):
		leads = frappe.parse_json(leads)

	for lead in leads:
		doc = frappe.get_doc(config.ref_doctype, lead)
		_ensure_can_manage_lead(doc)

		frappe.flags._sr_skip_owner_restore = True
		clear(config.ref_doctype, lead)
		frappe.db.set_value(
			config.ref_doctype,
			lead,
			config.owner_fieldname,
			None,
			update_modified=False,
		)

	return {"status": "ok"}
