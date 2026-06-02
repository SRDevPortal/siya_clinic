import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


TEAM_LEADER_FIELD = "sr_reports_to_team_leader"


def execute():
    create_custom_fields(
        {
            "User": [
                {
                    "fieldname": TEAM_LEADER_FIELD,
                    "label": "Reports To Team Leader",
                    "fieldtype": "Link",
                    "options": "User",
                    "insert_after": "role_profile_name",
                    "in_standard_filter": 1,
                    "description": "Restricts CRM Lead visibility for Team Leaders to their direct team.",
                }
            ]
        },
        update=True,
    )
    frappe.clear_cache(doctype="User")
