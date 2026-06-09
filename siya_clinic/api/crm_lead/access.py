# siya_clinic/api/crm_lead/access.py
# Visibility + Permissions + Owner-restore for CRM Lead

from __future__ import annotations
import frappe

from siya_clinic.api.crm_lead.config import REF_DOCTYPE, get_config, sql_column


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_privileged(user: str) -> bool:
	from sriaas_role_permissions.api.roles import is_privileged

	return is_privileged(user, REF_DOCTYPE)


def _has_team_leader_role(user: str) -> bool:
	from sriaas_role_permissions.api.roles import has_team_leader_role

	return has_team_leader_role(user, REF_DOCTYPE)


def _has_agent_role(user: str) -> bool:
	from sriaas_role_permissions.api.roles import has_agent_role

	return has_agent_role(user, REF_DOCTYPE)


def _reports_to_team_leader(user: str) -> str | None:
	if _has_team_doctype():
		rows = frappe.db.sql(
			"""
			select t.team_lead
			from `tabTeam User` tu
			inner join `tabTeam` t on t.name = tu.parent
			where tu.parenttype = 'Team'
			  and tu.user = %s
			  and tu.is_active = 1
			  and t.is_active = 1
			  and t.team_lead is not null
			  and t.team_lead != ''
			  and t.team_lead != %s
			limit 1
			""",
			(user, user),
			as_dict=True,
		)
		if rows:
			return rows[0].team_lead

	return None


def _is_effective_team_leader(user: str) -> bool:
	if not _has_team_leader_role(user):
		return False

	if _has_team_doctype():
		return bool(_managed_team_names(user))

	return not _reports_to_team_leader(user)


def _is_main_team_lead(user: str) -> bool:
	return bool(_teams_led_by(user))


def _is_assistant_team_lead(user: str) -> bool:
	if not _has_team_leader_role(user) or not _has_team_doctype():
		return False
	return bool(_teams_where_user_is_active_member(user) - _teams_led_by(user))


def _teams_led_by(user: str) -> set[str]:
	if not _has_team_doctype():
		return set()

	rows = frappe.get_all(
		"Team",
		filters={"team_lead": user, "is_active": 1},
		pluck="name",
	)
	return set(rows or [])


def _teams_where_user_is_active_member(user: str) -> set[str]:
	if not _has_team_doctype():
		return set()

	rows = frappe.db.sql(
		"""
		select distinct t.name
		from `tabTeam User` tu
		inner join `tabTeam` t on t.name = tu.parent
		where tu.parenttype = 'Team'
		  and tu.user = %s
		  and tu.is_active = 1
		  and t.is_active = 1
		""",
		user,
		as_dict=True,
	)
	return {row.name for row in rows}


def _managed_team_names(user: str) -> set[str]:
	if not _has_team_doctype() or not _has_team_leader_role(user):
		return set()

	return _teams_led_by(user) | _teams_where_user_is_active_member(user)


def get_managed_team_users(user: str | None = None) -> list[str]:
	user = user or frappe.session.user
	if _is_privileged(user):
		return []
	if not _is_effective_team_leader(user):
		return []

	return sorted(_team_owner_values(user))


def _lead_owner_sql_for_team(user: str) -> str:
	config = get_config()
	owners = _team_owner_values(user)

	owners = sorted(set(owner for owner in owners if owner))
	if not owners:
		return "1=0"

	escaped = ", ".join(frappe.db.escape(owner) for owner in owners)
	return f"{sql_column(config.owner_fieldname)} IN ({escaped})"


def _blank_lead_owner_sql() -> str:
	owner_col = sql_column(get_config().owner_fieldname)
	return f"({owner_col} IS NULL OR {owner_col} = '')"


def _team_owner_values(user: str) -> set[str]:
	config = get_config()
	owners = {user}

	if _has_team_doctype():
		teams = _managed_team_names(user)
		if not teams:
			return owners

		escaped_teams = ", ".join(frappe.db.escape(team) for team in sorted(teams))
		rows = frappe.db.sql(
			f"""
			select distinct tu.user
			from `tabTeam User` tu
			inner join `tabTeam` t on t.name = tu.parent
			where tu.parenttype = 'Team'
			  and t.name in ({escaped_teams})
			  and t.is_active = 1
			  and tu.is_active = 1
			  and tu.user is not null
			  and tu.user != ''
			""",
			as_dict=True,
		)
		owners.update(row.user for row in rows)
		owners.update(
			frappe.get_all(
				"Team",
				filters={"name": ["in", list(teams)], "is_active": 1},
				pluck="team_lead",
			)
			or []
		)
	elif config.team_leader_fieldname and frappe.db.has_column("User", config.team_leader_fieldname):
		owners.update(
			frappe.get_all(
				"User",
				filters={config.team_leader_fieldname: user, "enabled": 1},
				pluck="name",
			)
			or []
		)

	return {owner for owner in owners if owner}


def _has_team_doctype() -> bool:
	return bool(
		frappe.db.exists("DocType", "Team")
		and frappe.db.exists("DocType", "Team User")
	)


def _crm_lead_permission_dimensions() -> list[tuple[str, str]]:
	config = get_config()
	meta = frappe.get_meta(config.ref_doctype)
	dimensions: list[tuple[str, str]] = []

	if config.pipeline_doctype and config.pipeline_fieldname:
		dimensions.append((config.pipeline_doctype, config.pipeline_fieldname))

	for fieldname in ("sr_lead_platform", "source"):
		field = meta.get_field(fieldname)
		if field and field.fieldtype == "Link" and field.options:
			dimensions.append((field.options, fieldname))

	seen = set()
	unique_dimensions = []
	for doctype, fieldname in dimensions:
		key = (doctype, fieldname)
		if key in seen:
			continue
		seen.add(key)
		unique_dimensions.append(key)

	return unique_dimensions


def _allowed_values(user: str, doctype: str) -> set[str]:
	from frappe.core.doctype.user_permission.user_permission import get_user_permissions

	perms = get_user_permissions(user) or {}
	raw = perms.get(doctype) or []

	values = set()
	for value in raw:
		if isinstance(value, str):
			values.add(value)
		elif isinstance(value, dict):
			values.add(value.get("doc") or value.get("value") or value.get("name"))

	values.discard("")
	values.discard(None)
	return values


def _allowed_pipelines(user: str) -> set[str]:
	config = get_config()
	if not config.pipeline_doctype:
		return set()
	return _allowed_values(user, config.pipeline_doctype)


def _user_permission_filters(user: str) -> list[tuple[str, str, set[str]]]:
	filters = []
	for doctype, fieldname in _crm_lead_permission_dimensions():
		values = _allowed_values(user, doctype)
		if values:
			filters.append((doctype, fieldname, values))
	return filters


def _user_permission_filters_sql(user: str, deny_if_missing: bool = True) -> str:
	filters = _user_permission_filters(user)
	if not filters:
		return "1=0" if deny_if_missing else "1=1"

	conditions = []
	for _doctype, fieldname, values in filters:
		escaped = ", ".join(frappe.db.escape(value) for value in sorted(values))
		conditions.append(f"{sql_column(fieldname)} IN ({escaped})")

	return " AND ".join(f"({condition})" for condition in conditions)


def _doc_matches_user_permission_filters(doc, user: str) -> bool:
	filters = _user_permission_filters(user)
	if not filters:
		return False

	for _doctype, fieldname, values in filters:
		if getattr(doc, fieldname, None) not in values:
			return False

	return True


# ---------------------------------------------------------------------------
# Permission Query Condition (LIST / SEARCH / EXPORT)
# ---------------------------------------------------------------------------

def crm_lead_pqc(user: str) -> str:
	user = user or frappe.session.user

    # Admin / System Manager → everything
	if _is_privileged(user):
		return ""

    # Team managers see managed-team leads and blank-owner leads,
    # restricted by every CRM Lead User Permission dimension they have.
	if _is_effective_team_leader(user):
		owner_cond = _lead_owner_sql_for_team(user)
		permission_cond = _user_permission_filters_sql(user)

		if permission_cond == "1=0":
			return "1=0"

		blank_owner_cond = _blank_lead_owner_sql()
		visibility_cond = f"(({owner_cond}) OR ({blank_owner_cond}))"
		return f"({visibility_cond}) AND ({permission_cond})"

    # Agent: only lead_owner + every CRM Lead User Permission dimension.
	if _has_agent_role(user) or _reports_to_team_leader(user):
		# lead_owner is the authoritative visibility field. ToDo assignments
        # are UI/task helpers and can drift independently.
		owner_cond = f"{sql_column(get_config().owner_fieldname)}={frappe.db.escape(user)}"
		permission_cond = _user_permission_filters_sql(user)
		return f"({owner_cond}) AND ({permission_cond})"

    # Everyone else → nothing
	return "1=0"


# ---------------------------------------------------------------------------
# has_permission (OPEN / READ / WRITE)
# ---------------------------------------------------------------------------

def crm_lead_has_permission(doc, user: str | None = None, ptype: str | None = None) -> bool:
	user = user or frappe.session.user

    # Admin / System Manager
	if _is_privileged(user):
		return True

    # Team managers can open managed-team leads and blank-owner leads,
    # restricted by every CRM Lead User Permission dimension they have.
	if _is_effective_team_leader(user):
		config = get_config()
		lead_owner = getattr(doc, config.owner_fieldname, None)

		if not _doc_matches_user_permission_filters(doc, user):
			return False

		return lead_owner in _team_owner_values(user) or not lead_owner

    # Agent: must be lead_owner + every CRM Lead User Permission dimension.
	if _has_agent_role(user) or _reports_to_team_leader(user):
		config = get_config()
		if getattr(doc, config.owner_fieldname, None) != user:
			return False

		return _doc_matches_user_permission_filters(doc, user)

	return False


# ---------------------------------------------------------------------------
# Restore owner after unassign (conditional)
# ---------------------------------------------------------------------------

def restore_lead_owner_after_unassign(doc, method=None):
	"""
    Restore lead_owner ONLY for system-driven unassigns.
    Explicit clears from controller set _sr_skip_owner_restore.
    """

    # 🚫 Explicit clear → do NOT restore owner
	if getattr(frappe.flags, "_sr_skip_owner_restore", False):
		frappe.flags._sr_skip_owner_restore = False
		frappe.flags._sr_preserve_lead_owner = None
		return

	data = getattr(frappe.flags, "_sr_preserve_lead_owner", None)
	if not data:
		return

	config = get_config()
	if doc.doctype != config.ref_doctype:
		return

	if doc.name != data.get("lead"):
		return

	if not doc.get(config.owner_fieldname):
		doc.db_set(
			config.owner_fieldname,
			data.get("owner"),
			update_modified=False,
		)

	frappe.flags._sr_preserve_lead_owner = None
