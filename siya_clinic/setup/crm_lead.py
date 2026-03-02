# siya_clinic/setup/crm_lead.py

import frappe
from .utils import create_cf_with_module, upsert_property_setter, ensure_field_after, set_label

DT = "CRM Lead"


def apply():
    """Entry point called from setup.runner"""
    _make_crm_lead_fields()
    _apply_crm_lead_ui_customizations()


# =========================================================
# Custom Fields
# =========================================================
def _make_crm_lead_fields():
    """Add custom fields, tabs, and tracking sections to CRM Lead"""

    if not frappe.db.exists("DocType", DT):
        return

    create_cf_with_module({
        DT: [

            # ---------------- Lead Details TAB ----------------
            {
                "fieldname": "sr_lead_pipeline",
                "label": "Pipeline",
                "fieldtype": "Link",
                "options": "SR Lead Pipeline",
                "reqd": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "details",
            },
            {"fieldname": "sr_lead_details_cb2", "fieldtype": "Column Break", "insert_after": "lead_owner"},
            {
                "fieldname": "sr_lead_platform",
                "label": "Platform",
                "fieldtype": "Link",
                "options": "SR Lead Platform",
                "reqd": 1,
                "in_list_view": 1,
                "insert_after": "sr_lead_details_cb2",
            },
            {
                "fieldname": "sr_lead_disposition",
                "label": "Lead Disposition",
                "fieldtype": "Link",
                "options": "SR Lead Disposition",
                "depends_on": "eval: !!doc.status",
                "insert_after": "sr_lead_platform",
            },

            # ---------------- Country & Contact Info ----------------
            {
                "fieldname": "sr_lead_country",
                "label": "Country",
                "fieldtype": "Link",
                "options": "Country",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "email",
            },
            {
                "fieldname": "sr_lead_personal_cb2",
                "fieldtype": "Column Break",
                "insert_after": "mobile_no",
            },
            {
                "fieldname": "sr_lead_message",
                "label": "Message",
                "fieldtype": "Small Text",
                "insert_after": "sr_lead_personal_cb2",
            },
            {
                "fieldname": "sr_lead_notes",
                "label": "Notes",
                "fieldtype": "Small Text",
                "insert_after": "sr_lead_message",
            },
            {
                "fieldname": "sr_lead_disease",
                "label": "Disease",
                "fieldtype": "Data",
                "insert_after": "sr_lead_notes",
            },

            # ---------------- PEX TAB ----------------
            {
                "fieldname": "sr_lead_pex_tab",
                "label": "PEX",
                "fieldtype": "Tab Break",
                "insert_after": "status_change_log",
            },
            {
                "fieldname": "sr_lead_pex_launcher_html",
                "label": "PEX Launcher",
                "fieldtype": "HTML",
                "insert_after": "sr_lead_pex_tab",
            },

            # ---------------- Appointment TAB ----------------
            {
                "fieldname": "sr_lead_pa_tab",
                "label": "Appointment",
                "fieldtype": "Tab Break",
                "insert_after": "sr_lead_pex_launcher_html",
            },
            {
                "fieldname": "sr_lead_pa_launcher_html",
                "label": "Patient Appointment Launcher",
                "fieldtype": "HTML",
                "insert_after": "sr_lead_pa_tab",
            },

            # ---------------- Meta Details TAB ----------------
            {"fieldname": "sr_meta_tab", "label": "Meta Details", "fieldtype": "Tab Break", "insert_after": "sr_lead_pa_launcher_html"},

            # ---------- General Tracking ----------
            {
                "fieldname": "sr_meta_general_sb",
                "label": "General Tracking",
                "fieldtype": "Section Break",
                "insert_after": "sr_meta_tab",
            },
            {"fieldname": "sr_ip_address", "label": "IP Address", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_meta_general_sb"},
            {"fieldname": "sr_vpn_status", "label": "VPN Status", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_ip_address"},
            {"fieldname": "sr_landing_page", "label": "Landing Page", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_vpn_status"},
            {"fieldname": "sr_meta_general_cb2", "fieldtype": "Column Break", "insert_after": "sr_landing_page"},
            {"fieldname": "sr_remote_location", "label": "Remote Location", "fieldtype": "Small Text", "read_only": 1, "insert_after": "sr_meta_general_cb2"},
            {"fieldname": "sr_user_agent", "label": "User Agent", "fieldtype": "Small Text", "read_only": 1, "insert_after": "sr_remote_location"},

            # # ---------- Google Tracking ----------
            {
                "fieldname": "sr_meta_google_sb",
                "label": "Google Tracking",
                "fieldtype": "Section Break",
                "insert_after": "sr_user_agent",
            },
            {"fieldname": "sr_utm_source", "label": "UTM Source", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_meta_google_sb"},
            {"fieldname": "sr_utm_campaign", "label": "UTM Campaign", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_utm_source"},
            {"fieldname": "sr_utm_campaign_id", "label": "UTM Campaign ID", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_utm_campaign"},
            {"fieldname": "sr_gclid", "label": "GCLID", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_utm_campaign_id"},
            {"fieldname": "sr_meta_google_cb2", "fieldtype": "Column Break", "insert_after": "sr_gclid"},
            {"fieldname": "sr_utm_medium", "label": "UTM Medium", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_meta_google_cb2"},
            {"fieldname": "sr_utm_term", "label": "UTM Term", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_utm_medium"},
            {"fieldname": "sr_utm_adgroup_id", "label": "UTM Ad Group ID", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_utm_term"},

            # # ---------- Facebook Tracking ----------
            {
                "fieldname": "sr_meta_facebook_sb",
                "label": "Facebook Tracking",
                "fieldtype": "Section Break",
                "insert_after": "sr_utm_adgroup_id",
            },
            {"fieldname": "sr_f_ad_id", "label": "Facebook Ad ID", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_meta_facebook_sb"},
            {"fieldname": "sr_f_ad_name", "label": "Facebook Ad Name", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_f_ad_id"},
            {"fieldname": "sr_f_adset_id", "label": "Facebook Ad Set ID", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_f_ad_name"},
            {"fieldname": "sr_f_adset_name", "label": "Facebook Ad Set Name", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_f_adset_id"},
            {"fieldname": "sr_meta_fb_cb2", "fieldtype": "Column Break", "insert_after": "sr_f_adset_name"},
            {"fieldname": "sr_f_campaign_id", "label": "Facebook Campaign ID", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_meta_fb_cb2"},
            {"fieldname": "sr_f_campaign_name", "label": "Facebook Campaign Name", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_f_campaign_id"},
            {"fieldname": "sr_f_utm_medium", "label": "UTM Medium (Facebook)", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_f_campaign_name"},
            {"fieldname": "sr_fbclid", "label": "FBCLID", "fieldtype": "Data", "length": 255, "read_only": 1, "insert_after": "sr_f_utm_medium"},

            # # ---------- Interakt Tracking ----------
            {
                "fieldname": "sr_meta_interakt_sb",
                "label": "Interakt Tracking",
                "fieldtype": "Section Break",
                "insert_after": "sr_fbclid",
             },
            {"fieldname": "sr_w_source_id", "label": "W Source ID", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_meta_interakt_sb"},
            {"fieldname": "sr_w_source_url", "label": "W Source URL", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_w_source_id"},
            {"fieldname": "sr_w_ctwa_clid", "label": "W CTWA CLID", "fieldtype": "Data", "read_only": 1, "insert_after": "sr_w_source_url"},
            {"fieldname": "sr_w_team_user", "label": "W Team User", "fieldtype": "Link", "options": "User", "read_only": 1, "insert_after": "sr_w_ctwa_clid"},
        ]
    })


# =========================================================
# UI Customizations
# =========================================================
def _apply_crm_lead_ui_customizations():
    """Apply UI rules, field order, permissions, and cleanup"""

    if not frappe.db.exists("DocType", DT):
        return
    
    set_label(DT, "details", "Lead Details")

    # # ---------- Status ----------
    upsert_property_setter(DT, "status", "in_standard_filter", "1", "Check")
    upsert_property_setter(DT, "status", "default", "New", "Data")

    # # ---------- Field Requirements ----------
    upsert_property_setter(DT, "first_name", "reqd", "0", "Check")
    upsert_property_setter(DT, "mobile_no", "reqd", "1", "Check")
    upsert_property_setter(DT, "mobile_no", "in_list_view", "1", "Check")
    upsert_property_setter(DT, "mobile_no", "in_standard_filter", "1", "Check")

    # # ---------- Lead Source ----------
    upsert_property_setter(DT, "source", "options", "SR Lead Source", "Link")
    upsert_property_setter(DT, "source", "in_list_view", "1", "Check")
    upsert_property_setter(DT, "source", "in_standard_filter", "1", "Check")

    # # ---------- Rename Tab ----------
    set_label(DT, "person_tab", "Patient Details")

    # # ---------- Field Ordering ----------
    ensure_field_after(DT, "middle_name", "first_name")
    ensure_field_after(DT, "lead_name", "last_name")
    ensure_field_after(DT, "phone", "mobile_no")
    ensure_field_after(DT, "gender", "phone")

    ensure_field_after(DT, "lead_owner", "sr_lead_pipeline")
    ensure_field_after(DT, "source", "lead_owner")

    ensure_field_after(DT, "sr_lead_details_cb2", "source")
    ensure_field_after(DT, "status", "sr_lead_platform")
    ensure_field_after(DT, "sr_lead_disposition", "status")

    upsert_property_setter(DT, "naming_series", "hidden", "1", "Check")

    # ---------- Hide Unused Fields ----------
    targets = (
        # Hide From Lead Details tab
        "organization", "website", "territory", "industry", "job_title",
        # hide from Patient Details tab
        "salutation", "lead_name",
        # hide from Others tab
        "naming_series", "no_of_employees", "annual_revenue", "image", "converted",
        # hide from Products tab
        "products", "total", "net_total",
        # hide SLA tab
        "sla_tab",
        # hide Syncing tab
        "syncing_tab",
    )

    for fieldname in targets:
        cfname = frappe.db.get_value("Custom Field", {"dt": DT, "fieldname": fieldname}, "name")

        if cfname:
            cf = frappe.get_doc("Custom Field", cfname)
            cf.hidden = 1
            cf.in_list_view = 0
            cf.in_standard_filter = 0
            cf.save(ignore_permissions=True)
        else:
            upsert_property_setter(DT, fieldname, "hidden", "1", "Check")
            upsert_property_setter(DT, fieldname, "in_list_view", "0", "Check")
            upsert_property_setter(DT, fieldname, "in_standard_filter", "0", "Check")
