import frappe

from .utils import create_cf_with_module


TEAM_LEADER_FIELD = "sr_reports_to_team_leader"


def apply():
    if not frappe.db.exists("DocType", "User"):
        return

    create_cf_with_module(
        {
            "User": [
                {
                    "fieldname": TEAM_LEADER_FIELD,
                    "label": "Reports To Team Leader",
                    "fieldtype": "Link",
                    "options": "User",
                    "insert_after": "role_profile_name",
                    "in_standard_filter": 1,
                    "description": (
                        "Restricts CRM Lead visibility for Team Leaders "
                        "to their direct team."
                    ),
                }
            ]
        }
    )
    frappe.clear_cache(doctype="User")
