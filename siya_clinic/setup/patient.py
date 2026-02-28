# siya_clinic/setup/patient.py

import frappe
from .utils import create_cf_with_module, upsert_property_setter, ensure_field_after

DT = "Patient"


def apply():
    """Entry point called from setup.runner"""
    _make_patient_fields()
    _apply_patient_ui_customizations()


# =========================================================
# Custom Fields
# =========================================================
def _make_patient_fields():
    """Add custom fields to Patient"""

    create_cf_with_module({
        DT: [

            # ---------------- Department ----------------
            {
                "fieldname": "sr_medical_department",
                "label": "Department",
                "fieldtype": "Link",
                "options": "Medical Department",
                "insert_after": "patient_name",
                "reqd": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "allow_in_quick_entry": 1,
            },

            # ---------------- Business Patient ID ----------------
            {
                "fieldname": "sr_patient_id",
                "label": "Patient ID",
                "fieldtype": "Data",
                "insert_after": "sr_medical_department",
                "read_only": 1,
                "unique": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "search_index": 1,
            },

            {
                "fieldname": "sr_practo_id",
                "label": "Practo ID",
                "fieldtype": "Data",
                "insert_after": "sr_patient_id",
            },

            {
                "fieldname": "sr_patient_age",
                "label": "Patient Age",
                "fieldtype": "Data",
                "insert_after": "age_html",
                "allow_in_quick_entry": 1,
            },

            # ---------------- Regional Fields ----------------
            {
                "fieldname": "sr_dpt_disease",
                "label": "Disease",
                "fieldtype": "Link",
                "options": "DPT Disease",
                "depends_on": 'eval:doc.sr_medical_department=="Regional"',
                "mandatory_depends_on": 'eval:doc.sr_medical_department=="Regional"',
                "insert_after": "sr_patient_age",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "allow_in_quick_entry": 1,
            },
            {
                "fieldname": "sr_dpt_language",
                "label": "Language",
                "fieldtype": "Link",
                "options": "DPT Language",
                "depends_on": 'eval:doc.sr_medical_department=="Regional"',
                "mandatory_depends_on": 'eval:doc.sr_medical_department=="Regional"',
                "insert_after": "sr_dpt_disease",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "allow_in_quick_entry": 1,
            },

            # ---------------- Patient Follow-up ----------------
            {
                "fieldname": "sr_followup_disable_reason",
                "label": "Followup Disable Reason",
                "fieldtype": "Link",
                "options": "SR Patient Disable Reason",
                "insert_after": "status",
                "depends_on": 'eval:doc.status=="Disabled"',
                "mandatory_depends_on": 'eval:doc.status=="Disabled"',
            },
            {
                "fieldname": "sr_followup_status",
                "label": "Followup Status",
                "fieldtype": "Link",
                "options": "SR Followup Status",
                "insert_after": "user_id",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "allow_in_quick_entry": 1,
            },

            # ---------------- Invoices ----------------
            {
                "fieldname": "sr_invoices_tab",
                "label": "Invoices",
                "fieldtype": "Tab Break",
                "insert_after": "other_risk_factors"
            },
            {
                "fieldname": "sr_sales_invoice_list",
                "label": "Sales Invoices",
                "fieldtype": "Table",
                "options": "SR Patient Invoice View",
                "read_only": 1,
                "insert_after": "sr_invoices_tab",
            },

            # ---------------- Payments ----------------
            {
                "fieldname": "sr_payments_tab",
                "label": "Payments",
                "fieldtype": "Tab Break",
                "insert_after":"sr_sales_invoice_list",
            },
            {
                "fieldname": "sr_payment_entry_list",
                "label": "Payment Entries",
                "fieldtype": "Table",
                "options": "SR Patient Payment View",
                "read_only": 1,
                "insert_after": "sr_payments_tab",
            },

            # ---------------- Follow-up Marker ----------------
            {
                "fieldname": "sr_followup_marker_tab",
                "label": "Follow-up Marker",
                "fieldtype": "Tab Break",
                "insert_after": "sr_payment_entry_list",
            },

            {
                "fieldname": "sr_followup_id",
                "label": "Follow-up ID",
                "fieldtype": "Link",
                "options": "SR Followup ID",
                "read_only": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "search_index": 1,
                "insert_after": "sr_followup_marker_tab",
            },

            {
                "fieldname": "sr_followup_day",
                "label": "Follow-up Day",
                "fieldtype": "Link",
                "options": "SR Followup Day",
                "read_only": 1,
                "in_list_view": 1,
                "in_standard_filter": 1,
                "search_index": 1,
                "insert_after": "sr_followup_id",
            },

            # ---------------- PEX Launcher + Clinical History Modal ----------------
            {
                "fieldname": "sr_pex_tab",
                "label": "PEX",
                "fieldtype": "Tab Break",
                "insert_after": "sr_followup_day",
            },
            {
                "fieldname": "sr_pex_launcher_html",
                "label": "PE Launcher",
                "fieldtype": "HTML",
                "read_only": 1,
                "insert_after": "sr_pex_tab",
            },

            # ---------------- Created By ----------------
            {
                "fieldname": "created_by_agent",
                "label": "Created By",
                "fieldtype": "Link",
                "options": "User",
                "read_only": 1,
                "insert_after": "sr_followup_status",
            },
        ]
    })


# =========================================================
# UI Customizations + Naming Series
# =========================================================
def _apply_patient_ui_customizations():
    """Apply UI customizations & naming configuration"""

    ## ---------------- Status ----------------
    upsert_property_setter(DT, "status", "read_only", "0", "Check")
    upsert_property_setter(DT, "status", "in_standard_filter", "1", "Check")

    # ---------------- Contact Rules ----------------
    upsert_property_setter(DT, "mobile", "reqd", "0", "Check")
    upsert_property_setter(DT, "mobile", "in_standard_filter", "1", "Check")
    upsert_property_setter(DT, "phone", "in_standard_filter", "1", "Check")

    upsert_property_setter(DT, "uid", "in_standard_filter", "0", "Check")

    # ---------------- Hide Unused ----------------
    upsert_property_setter(DT, "invite_user", "default", "0", "Data")
    upsert_property_setter(DT, "invite_user", "hidden", "1", "Check")
    upsert_property_setter(DT, "age", "hidden", "1", "Check")

    # Hide naming_series (Python controls naming)
    upsert_property_setter(DT, "naming_series", "hidden", "1", "Check")

    # ---------------- Field Ordering ----------------
    ensure_field_after(DT, "sr_dpt_disease", "sr_medical_department")
    ensure_field_after(DT, "sr_dpt_language", "sr_dpt_disease")

    # ---------------- Link Title ----------------
    upsert_property_setter(DT, "title_field", "value", "patient_name", "Data")
    upsert_property_setter(DT, "show_title_field_in_link", "value", "1", "Check")

    # ---------------- Disable Rename ----------------
    upsert_property_setter(DT, "allow_rename", "default", "0", "Check")
