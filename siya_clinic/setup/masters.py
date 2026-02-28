# siya_clinic/setup/masters.py
import frappe
import logging

from .utils import (
    MODULE_DEF_NAME, APP_PY_MODULE,
    ensure_module_def,
    reload_local_json_doctypes,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# List of DocTypes shipped as JSON (folder names under doctype/)
# ------------------------------------------------------------
JSON_DOCTYPES = [
    # Example:
    # "sr_patient_disable_reason",
    # "sr_patient_invoice_view",
]

def apply():
    """
    Apply all master setup steps for Siya Clinic.
    Safe to run multiple times.
    """

    logger.info("Applying masters setup")

    # Ensure Module Definition exists
    ensure_module_def(MODULE_DEF_NAME, APP_PY_MODULE)

    # Reload local JSON DocTypes
    reload_local_json_doctypes(JSON_DOCTYPES)
    
    # CRM Masters
    create_lead_pipeline_doctype()
    create_lead_platform_doctype()
    create_lead_source_doctype()
    create_lead_disposition_doctype()
    
    # Patient Masters
    create_state_doctype()
    _seed_states()
    
    create_dpt_disease_doctype()
    create_dpt_language_doctype()
    create_patient_disable_reason_doctype()
    
    create_followup_status_doctype()
    _seed_followup_status_defaults()
    
    create_followup_id_doctype()
    _seed_followup_ids()

    create_followup_day_doctype()
    _seed_followup_days()

    create_patient_invoice_view_doctype()
    create_patient_payment_view_doctype()

    create_practitioner_pathy_doctype()
    _seed_practitioner_pathies()

    # Create DocTypes for Encounter
    create_encounter_type_doctype()
    _seed_encounter_type_data()
    create_encounter_place_doctype()
    _seed_encounter_place_data()
    create_sales_type_doctype()
    _seed_sales_type_data()
    create_encounter_status_doctype()
    _seed_encounter_status_defaults()
    create_diet_chart()

    create_instruction()
    create_medication_template_item()
    create_medication_template()

    seed_medication_class_data()

    create_delivery_type()
    _seed_delivery_type_data()    
    create_order_item()
    create_multi_mode_payment()
    
    create_item_group_template_item_doctype()
    create_item_group_template_doctype() 

    # Integration / Shipping Settings
    create_shipkia_settings()
    
    # Disable Quick Entry for Item
    disable_item_quick_entry()

    # Warehouse Masters
    _seed_company_warehouses_data()

    _seed_roles()
    
    # create_bulk_payment_upload()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Masters setup completed")


# ------------------------------------------------------------
# DocType Creators
# ------------------------------------------------------------

def create_lead_pipeline_doctype():
    """Create SR Lead Pipeline DocType if missing."""

    doctype = "SR Lead Pipeline"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "naming_series:",
            "title_field": "sr_pipeline_name",
            "show_title_field_in_link": 1,
            "search_fields": "sr_pipeline_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "fields": [

                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "PIPE-.#####",
                    "default": "PIPE-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "sr_pipeline_name",
                    "label": "Pipeline Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "print": 1,
                    "email": 1,
                    "export": 1,
                    "report": 1
                },
                {
                    "role": "Healthcare Administrator",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                },
            ]
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_lead_platform_doctype():
    """Create SR Lead Platform DocType if missing."""

    doctype = "SR Lead Platform"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "naming_series:",
            "title_field": "sr_platform_name",
            "show_title_field_in_link": 1,
            "search_fields": "sr_platform_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "fields": [

                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "PLAT-.#####",
                    "default": "PLAT-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "sr_platform_name",
                    "label": "Platform Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "sr_platform_details",
                    "label": "Platform Details",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "print": 1,
                    "email": 1,
                    "export": 1,
                    "report": 1
                },
                {
                    "role": "Healthcare Administrator",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                },
            ]
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_lead_source_doctype():
    """Create SR Lead Source DocType if missing."""

    doctype = "SR Lead Source"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "naming_series:",
            "title_field": "sr_source_name",
            "show_title_field_in_link": 1,
            "search_fields": "sr_source_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "fields": [

                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "SRC-.#####",
                    "default": "SRC-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "sr_source_name",
                    "label": "Source Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "sr_source_details",
                    "label": "Source Details",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "print": 1,
                    "email": 1,
                    "export": 1,
                    "report": 1
                },
                {
                    "role": "Healthcare Administrator",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                },
            ]
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_lead_disposition_doctype():
    """Create SR Lead Disposition DocType if missing."""

    doctype = "SR Lead Disposition"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "naming_series:",
            "title_field": "sr_disposition_name",
            "show_title_field_in_link": 1,
            "search_fields": "sr_disposition_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "fields": [

                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "DISP-.#####",
                    "default": "DISP-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "sr_disposition_name",
                    "label": "Disposition Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "sr_lead_status",
                    "label": "CRM Lead Status",
                    "fieldtype": "Link",
                    "options": "CRM Lead Status",
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "print": 1,
                    "email": 1,
                    "export": 1,
                    "report": 1
                },
                {
                    "role": "Healthcare Administrator",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                },
            ]
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_state_doctype():
    """Create SR State DocType if missing."""

    doctype = "SR State"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "field:sr_state_name",
            "title_field": "sr_state_name",
            "show_title_field_in_link": 1,
            "track_changes": 1,
            "fields": [
                {
                    "fieldname": "sr_state_name",
                    "label": "State Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "sr_country",
                    "label": "Country",
                    "fieldtype": "Link",
                    "options": "Country",
                    "default": "India",
                    "in_list_view": 1,
                },
                {
                    "fieldname": "sr_abbr",
                    "label": "Abbreviation",
                    "fieldtype": "Data",
                },
                {
                    "fieldname": "sr_is_union_territory",
                    "label": "Union Territory",
                    "fieldtype": "Check",
                    "default": 0,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                },
                {"role": "All", "read": 1},
            ],
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_states():
    """Insert Indian States & UTs safely."""

    states = [
        ("Andhra Pradesh", False),
        ("Arunachal Pradesh", False),
        ("Assam", False),
        ("Bihar", False),
        ("Chhattisgarh", False),
        ("Goa", False),
        ("Gujarat", False),
        ("Haryana", False),
        ("Himachal Pradesh", False),
        ("Jharkhand", False),
        ("Karnataka", False),
        ("Kerala", False),
        ("Madhya Pradesh", False),
        ("Maharashtra", False),
        ("Manipur", False),
        ("Meghalaya", False),
        ("Mizoram", False),
        ("Nagaland", False),
        ("Odisha", False),
        ("Punjab", False),
        ("Rajasthan", False),
        ("Sikkim", False),
        ("Tamil Nadu", False),
        ("Telangana", False),
        ("Tripura", False),
        ("Uttar Pradesh", False),
        ("Uttarakhand", False),
        ("West Bengal", False),
        ("Andaman and Nicobar Islands", True),
        ("Chandigarh", True),
        ("Dadra and Nagar Haveli and Daman and Diu", True),
        ("Delhi", True),
        ("Jammu and Kashmir", True),
        ("Ladakh", True),
        ("Lakshadweep", True),
        ("Puducherry", True),
    ]

    for state, is_ut in states:
        if not frappe.db.exists("SR State", {"sr_state_name": state}):
            frappe.get_doc({
                "doctype": "SR State",
                "sr_state_name": state,
                "sr_country": "India",
                "sr_is_union_territory": 1 if is_ut else 0,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_dpt_disease_doctype():
    """Create Regional Disease master."""

    doctype = "DPT Disease"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "naming_series:",
            "title_field": "dept_disease_name",
            "show_title_field_in_link": 1,
            "search_fields": "dept_disease_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "fields": [

                # 🔹 Regional Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "REG-DIS-.#####",
                    "default": "REG-DIS-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "dept_disease_name",
                    "label": "Disease Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Healthcare Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_dpt_language_doctype():
    """Create Regional Language master."""

    doctype = "DPT Language"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "naming_series:",
            "title_field": "dept_language_name",
            "show_title_field_in_link": 1,
            "search_fields": "dept_language_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "fields": [

                # 🔹 Regional Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "REG-LAN-.#####",
                    "default": "REG-LAN-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "dept_language_name",
                    "label": "Language",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Healthcare Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_patient_disable_reason_doctype():
    """Create SR Patient Disable Reason DocType if missing."""

    doctype = "SR Patient Disable Reason"

    if not frappe.db.exists("DocType", doctype):
        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "naming_series:",
            "title_field": "sr_reason_name",
            "show_title_field_in_link": 1,
            "search_fields": "sr_reason_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "allow_rename": 0,
            "fields": [

                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "PAT-DR-.#####",
                    "default": "PAT-DR-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "sr_reason_name",
                    "label": "Reason Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "export": 1},
                {"role": "Healthcare Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_followup_status_doctype():
    """Create SR Followup Status DocType and insert default records."""

    doctype = "SR Followup Status"

    if not frappe.db.exists("DocType", doctype):
        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "naming_series:",
            "title_field": "status_name",
            "show_title_field_in_link": 1,
            "search_fields": "status_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "allow_rename": 0,
            "fields": [

                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "FUP-.#####",
                    "default": "FUP-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "status_name",
                    "label": "Status Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "color",
                    "label": "Color",
                    "fieldtype": "Color",
                    "description": "Used for UI badges",
                },
                {
                    "fieldname": "sort_order",
                    "label": "Sort Order",
                    "fieldtype": "Int",
                    "default": 0,
                },
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Healthcare Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_followup_status_defaults():
    """Insert default follow-up statuses if missing."""

    defaults = [
        ("Pending", "#f39c12", 1),
        ("Done", "#27ae60", 2),
        ("Missed", "#e74c3c", 3),
        ("Rescheduled", "#3498db", 4),
        ("Not Interested", "#7f8c8d", 5),
    ]

    for name, color, order in defaults:
        if not frappe.db.exists("SR Followup Status", {"status_name": name}):
            frappe.get_doc({
                "doctype": "SR Followup Status",
                "status_name": name,
                "color": color,
                "sort_order": order,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_patient_invoice_view_doctype():
    """Create SR Patient Invoice View child table."""

    doctype = "SR Patient Invoice View"

    if not frappe.db.exists("DocType", doctype):
        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "istable": 1,
            "editable_grid": 1,
            "field_order": [
                "sr_invoice_no",
                "sr_posting_date",
                "sr_grand_total",
                "sr_outstanding",
            ],
            "fields": [
                {
                    "fieldname": "sr_invoice_no",
                    "label": "Sales Invoice",
                    "fieldtype": "Link",
                    "options": "Sales Invoice",
                    "in_list_view": 1,
                    "columns": 3,
                },
                {
                    "fieldname": "sr_posting_date",
                    "label": "Posting Date",
                    "fieldtype": "Date",
                    "in_list_view": 1,
                    "columns": 2,
                },
                {
                    "fieldname": "sr_grand_total",
                    "label": "Grand Total",
                    "fieldtype": "Currency",
                    "in_list_view": 1,
                    "columns": 2,
                },
                {
                    "fieldname": "sr_outstanding",
                    "label": "Outstanding",
                    "fieldtype": "Currency",
                    "in_list_view": 1,
                    "columns": 2,
                },
            ],
            "permissions": [],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_patient_payment_view_doctype():
    """Create SR Patient Payment View child table."""

    doctype = "SR Patient Payment View"

    if not frappe.db.exists("DocType", doctype):
        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "istable": 1,
            "editable_grid": 1,
            "field_order": [
                "sr_payment_entry",
                "sr_posting_date",
                "sr_paid_amount",
                "sr_mode_of_payment",
                "sr_reference_no",
                "sr_reference_date",
                "sr_payment_proof",
            ],
            "fields": [
                {
                    "fieldname": "sr_payment_entry",
                    "label": "Payment Entry",
                    "fieldtype": "Link",
                    "options": "Payment Entry",
                    "in_list_view": 1,
                    "columns": 2,
                },
                {
                    "fieldname": "sr_posting_date",
                    "label": "Posting Date",
                    "fieldtype": "Date",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "sr_paid_amount",
                    "label": "Paid Amount",
                    "fieldtype": "Currency",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "sr_mode_of_payment",
                    "label": "Mode of Payment",
                    "fieldtype": "Link",
                    "options": "Mode of Payment",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "sr_reference_no",
                    "label": "Payment Reference No",
                    "fieldtype": "Data",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "sr_reference_date",
                    "label": "Payment Reference Date",
                    "fieldtype": "Date",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "sr_payment_proof",
                    "label": "Payment Proof",
                    "fieldtype": "Attach",
                    "in_list_view": 1,
                    "columns": 3,
                },
            ],
            "permissions": [],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_followup_id_doctype():
    """Create SR Followup ID Master (0–9)."""

    doctype = "SR Followup ID"

    if not frappe.db.exists("DocType", doctype):
        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "field:digit",
            "title_field": "digit",
            "show_title_field_in_link": 1,
            "search_fields": "digit",
            "track_changes": 1,
            "allow_rename": 0,
            "fields": [
                {
                    "fieldname": "digit",
                    "label": "Digit",
                    "fieldtype": "Int",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "export": 1,
                },
                {
                    "role": "Healthcare Administrator",
                    "read": 1,
                },
            ],
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_followup_ids():
    """Insert digits 0–9 safely."""

    for i in range(10):
        if not frappe.db.exists("SR Followup ID", {"digit": i}):
            frappe.get_doc({
                "doctype": "SR Followup ID",
                "digit": i,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_followup_day_doctype():
    """Create SR Followup Day Master."""

    doctype = "SR Followup Day"

    if not frappe.db.exists("DocType", doctype):
        logger.info(f"Creating DocType: {doctype}")
        
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "field:day_name",
            "title_field": "day_name",
            "show_title_field_in_link": 1,
            "search_fields": "day_name",
            "track_changes": 1,
            "allow_rename": 0,
            "fields": [
                {
                    "fieldname": "day_name",
                    "label": "Day",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "sort_order",
                    "label": "Sort Order",
                    "fieldtype": "Int",
                    "default": 0,
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "export": 1,
                },
                {
                    "role": "Healthcare Administrator",
                    "read": 1,
                },
            ],
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_followup_days():
    """Insert Mon–Sat safely."""

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    for idx, day in enumerate(days):
        if not frappe.db.exists("SR Followup Day", {"day_name": day}):
            frappe.get_doc({
                "doctype": "SR Followup Day",
                "day_name": day,
                "sort_order": idx,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_practitioner_pathy_doctype():
    """Create SR Practitioner Pathy DocType if missing."""

    doctype = "SR Practitioner Pathy"

    if not frappe.db.exists("DocType", doctype):
        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "autoname": "field:sr_pathy_name",
            "title_field": "sr_pathy_name",
            "show_title_field_in_link": 1,
            "search_fields": "sr_pathy_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "allow_rename": 0,
            "fields": [
                {
                    "fieldname": "sr_pathy_name",
                    "label": "Pathy Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1, "export": 1
                },
                {
                    "role": "Healthcare Administrator",
                    "read": 1, "write": 1, "create": 1,
                },
                {"role": "All", "read": 1},
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_practitioner_pathies():
    defaults = ["Ayurveda", "Allopathy", "Homeopathy" "Unani", "Siddha"]

    for name in defaults:
        if not frappe.db.exists("SR Practitioner Pathy", {"sr_pathy_name": name}):
            frappe.get_doc({
                "doctype": "SR Practitioner Pathy",
                "sr_pathy_name": name,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_encounter_type_doctype():
    """Create SR Encounter Type DocType if missing."""

    doctype = "SR Encounter Type"

    if not frappe.db.exists("DocType", doctype):
        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            # "autoname": "naming_series:",
            "autoname": "field:encounter_type_name",
            # "naming_rule": "By fieldname",
            "title_field": "encounter_type_name",
            "show_title_field_in_link": 1,
            "search_fields": "encounter_type_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "custom": 1,
            "fields": [
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "ENC-.#####",
                    "default": "ENC-.#####",
                    "reqd": 1,
                    "hidden": 1
                },
                {
                    "fieldname": "encounter_type_name",
                    "label": "Encounter Type Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Healthcare Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_encounter_type_data():
    """Seed the SR Encounter Type data if missing"""
    encounter_types = ["Followup", "Order"]

    for encounter_type in encounter_types:
        if not frappe.db.exists("SR Encounter Type", {"encounter_type_name": encounter_type}):
            frappe.get_doc({
                "doctype": "SR Encounter Type",
                "encounter_type_name": encounter_type,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_encounter_place_doctype():
    """Create SR Encounter Place DocType if missing."""

    doctype = "SR Encounter Place"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            # "autoname": "naming_series:",
            "autoname": "field:encounter_place_name",
            # "naming_rule": "By fieldname",
            "title_field": "encounter_place_name",
            "show_title_field_in_link": 1,
            "search_fields": "encounter_place_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "custom": 1,
            "fields": [
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "ENCPL-.#####",
                    "default": "ENCPL-.#####",
                    "reqd": 1,
                    "hidden": 1
                },
                {
                    "fieldname": "encounter_place_name",
                    "label": "Encounter Place Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Healthcare Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_encounter_place_data():
    """Seed the SR Encounter Place data if missing"""
    encounter_places = ["Online", "OPD"]

    for encounter_place in encounter_places:
        if not frappe.db.exists("SR Encounter Place", {"encounter_place_name": encounter_place}):
            frappe.get_doc({
                "doctype": "SR Encounter Place",
                "encounter_place_name": encounter_place,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_sales_type_doctype():
    """Create SR Sales Type DocType if missing."""

    doctype = "SR Sales Type"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            # "autoname": "naming_series:",
            "autoname": "field:sales_type_name",
            # "naming_rule": "By fieldname",
            "title_field": "sales_type_name",
            "show_title_field_in_link": 1,
            "search_fields": "sales_type_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "custom": 1,
            "fields": [
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "SRST-.#####",
                    "default": "SRST-.#####",
                    "reqd": 1,
                    "hidden": 1
                },
                {
                    "fieldname": "sales_type_name",
                    "label": "Sales Type Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Healthcare Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_sales_type_data():
    """Seed the SR Sales Type data if missing"""
    sales_types = ["Discontinue", "Fresh", "Repeat"]

    for sales_type in sales_types:
        if not frappe.db.exists("SR Sales Type", {"sales_type_name": sales_type}):
            frappe.get_doc({
                "doctype": "SR Sales Type",
                "sales_type_name": sales_type,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_encounter_status_doctype():
    """Create SR Encounter Status DocType if missing."""

    doctype = "SR Encounter Status"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            # "autoname": "naming_series:",
            "autoname": "field:status_name",
            # "naming_rule": "By fieldname",
            "title_field": "status_name",
            "show_title_field_in_link": 1,
            "search_fields": "status_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "custom": 1,
            "fields": [
                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "ENC-STA-.#####",
                    "default": "ENC-STA-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "status_name",
                    "label": "Status Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "in_standard_filter": 1,
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "color",
                    "label": "Color",
                    "fieldtype": "Color",
                    "description": "Used for UI badges",
                },
                {
                    "fieldname": "sort_order",
                    "label": "Sort Order",
                    "fieldtype": "Int",
                    "default": 0,
                },
            ],
            "permissions": [
                {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "Healthcare Administrator", "read": 1, "write": 1, "create": 1, "delete": 1},
                {"role": "All", "read": 1}
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_encounter_status_defaults():
    """Insert default encounter statuses aligned with workflow."""

    statuses = [
        ("Draft", "#9b59b6", 1),
        ("Hold", "#34495e", 2),
        ("Duplicate", "#8e44ad", 3),
        ("Cancelled", "#34495e", 4),
        ("Completed", "#f1c40f", 5),
        ("Payment Disapproved", "#e74c3c", 6),
        ("Payment Approved", "#3498db", 7),
        ("Payment Approval", "#7f8c8d", 8),
        ("Reconfirmation", "#2ecc71", 9),
        ("Dispatch", "#1abc9c", 10),

        # --- PRX Workflow ---
        ("PRX Requested", "#e67e22", 11),
        ("PRX Ready", "#2c3e50", 12),
        ("PRX Hold", "#c0392b", 13),

        # --- Dispatch Workflow ---
        ("Ready to Dispatch", "#16a085", 14),
        ("Dispatched", "#27ae60", 15),

        # --- Utility ---
        ("Prx Print", "#f39c12", 16),
        ("PNS", "#27ae60", 17),
    ]

    for status_name, color, sort_order in statuses:
        if not frappe.db.exists("SR Encounter Status", {"status_name": status_name}):
            frappe.get_doc({
                "doctype": "SR Encounter Status",
                "status_name": status_name,
                "color": color,
                "sort_order": sort_order,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_diet_chart():
    """Create Diet Chart master."""

    doctype = "Diet Chart"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "autoname": "naming_series:",
            "naming_rule": "By fieldname",
            "title_field": "diet_chart_name",
            "show_title_field_in_link": 1,
            "search_fields": "diet_chart_name",
            "show_name_in_global_search": 1,
            "is_submittable": 0,
            "editable_grid": 0,
            "track_changes": 1,
            "custom": 1,
            "field_order": [
                "naming_series",
                "diet_chart_name",
                "instructions",
                "allowed_foods",
                "restricted_foods",
                "is_active",
            ],
            "fields": [
                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "DIET-.#####",
                    "default": "DIET-.#####",
                    "reqd": 1,
                    "hidden": 1,
                },
                {
                    "fieldname": "diet_chart_name",
                    "label": "Diet Chart Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                    "unique": 1,
                },
                {
                    "fieldname": "instructions",
                    "label": "General Instructions",
                    "fieldtype": "Long Text",
                },
                {
                    "fieldname": "allowed_foods",
                    "label": "Allowed Foods",
                    "fieldtype": "Long Text",
                },
                {
                    "fieldname": "restricted_foods",
                    "label": "Restricted Foods",
                    "fieldtype": "Long Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "export": 1,
                }
            ],
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_instruction():
    """Create SR Instruction master."""

    doctype = "SR Instruction"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "naming_rule": "By fieldname",
            "autoname": "field:sr_title",
            "title_field": "sr_title",
            "track_changes": 1,
            "allow_import": 1,
            "custom": 1,
            "field_order": [
                "sr_title",
                "sr_description",
                "is_active",
            ],
            "fields": [
                {
                    "fieldname": "sr_title",
                    "label": "Title",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "in_list_view": 1,
                    "unique": 1,
                },
                {
                    "fieldname": "sr_description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,  # Set default value to 1 (active)
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "print": 1,
                    "email": 1,
                    "export": 1,
                }
            ],
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_medication_template_item():
    """Create SR Medication Template Item master."""
    
    doctype = "SR Medication Template Item"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "track_changes": 1,
            "istable": 1,
            "custom": 1,
            "field_order": [
                "sr_medication",
                "sr_drug_code",
                "sr_medication_class",
                "sr_dosage",
                "sr_period",
                "sr_dosage_form",
                "sr_instruction",
            ],
            "fields": [
                {
                    "fieldname": "sr_medication",
                    "label": "Medication",
                    "fieldtype": "Link",
                    "options": "Medication",
                    "reqd": 1,
                    "in_list_view": 1,
                    "columns": 2,
                },
                {
                    "fieldname": "sr_drug_code",
                    "label": "Drug Code",
                    "fieldtype": "Link",
                    "options": "Item",
                },
                {
                    "fieldname": "sr_medication_class",
                    "label": "Medication Class",
                    "fieldtype": "Link",
                    "options": "Medication Class",
                    "reqd": 1,
                    "fetch_from": "sr_medication.medication_class",
                    "in_list_view": 1,
                    "read_only": 1,
                    "columns": 2,
                },
                {
                    "fieldname": "sr_dosage",
                    "label": "Dosage",
                    "fieldtype": "Link",
                    "options": "Prescription Dosage",
                    "reqd": 1,
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "sr_period",
                    "label": "Period",
                    "fieldtype": "Link",
                    "options": "Prescription Duration",
                    "reqd": 1,
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "sr_dosage_form",
                    "label": "Dosage Form",
                    "fieldtype": "Link",
                    "options": "Dosage Form",
                    "reqd": 1,
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "sr_instruction",
                    "label": "Instruction",
                    "fieldtype": "Link",
                    "options": "SR Instruction",
                    "reqd": 1,
                    "in_list_view": 1,
                    "columns": 3,
                },
            ],
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_medication_template():
    """Create SR Medication Template master."""

    doctype = "SR Medication Template"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc= frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "autoname": "naming_series:",
            "naming_rule": "By fieldname",
            "title_field": "sr_template_name",
            "show_title_field_in_link": 1,
            "search_fields": "sr_template_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "allow_import": 1,
            "custom": 1,
            "field_order": [
                "naming_series",
                "sr_template_name", # Series field
                "sr_tmpl_instruction",
                "sr_medications",
                "is_active",  # Active field
            ],
            "fields": [
                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "MTMPL-.#####",
                    "default": "MTMPL-.#####",
                    "reqd": 1,
                    "hidden": 1,
                },
                {
                    "fieldname": "sr_template_name",
                    "label": "Template Name",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "in_list_view": 1,
                    "unique": 1,
                },
                {
                    "fieldname": "sr_medications",
                    "label": "Medications",
                    "fieldtype": "Table",
                    "options": "SR Medication Template Item",
                },
                {
                    "fieldname": "sr_tmpl_instruction",
                    "label": "Instruction",
                    "fieldtype": "Small Text",
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "print": 1,
                    "email": 1,
                    "export": 1,
                }
            ],
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def seed_medication_class_data():
    """Create Medication Class seed if missing."""
    medication_classes = [
        "Allopathic",
        "Ayurvedic",
        "Cosmetic",
        "Homeopathic",
        "Protein Powder"
    ]

    for class_name in medication_classes:
        if not frappe.db.exists("Medication Class", {"medication_class": class_name}):
            # If the class doesn't already exist, create it
            frappe.get_doc({
                "doctype": "Medication Class",
                "medication_class": class_name,
                "is_active": 1  # Make sure the class is active
            }).insert(ignore_permissions=True)
            frappe.db.commit()  # Commit to save changes

            print(f"Medication Class '{class_name}' created.")


def create_delivery_type():
    """Create SR Delivery Type master."""

    doctype = "SR Delivery Type"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            # "autoname": "naming_series:",
            "autoname": "field:delivery_type_name",
            # "naming_rule": "By fieldname",
            "title_field": "delivery_type_name",
            "show_title_field_in_link": 1,
            "search_fields": "delivery_type_name",
            "show_name_in_global_search": 1,
            "track_changes": 1,
            "custom": 1,
            "field_order": [
                "naming_series",
                "delivery_type_name",
                "is_active",
            ],
            "fields": [
                # 🔹 Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "DEL-.#####",
                    "default": "DEL-.#####",
                    "reqd": 1,
                    "hidden": 1,
                },
                {
                    "fieldname": "delivery_type_name",
                    "label": "Delivery / Service Type",
                    "fieldtype": "Data",
                    "reqd": 1,
                    "unique": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "print": 1,
                    "email": 1,
                    "export": 1,
                }
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def _seed_delivery_type_data():
    """Seed the SR Delivery Type data if missing"""
    delivery_types = ["Courier", "OPD"]

    for delivery_type in delivery_types:
        if not frappe.db.exists("SR Delivery Type", {"delivery_type_name": delivery_type}):
            frappe.get_doc({
                "doctype": "SR Delivery Type",
                "delivery_type_name": delivery_type,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    frappe.db.commit()


def create_order_item():
    """Create SR Order Item master."""

    doctype = "SR Order Item"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "istable": 1,
            "editable_grid": 1,
            "issingle": 0,
            "track_changes": 1,
            "field_order": [
                "sr_item_code",
                "sr_item_name",
                "sr_item_description",
                "sr_item_uom",
                "sr_item_qty",
                "sr_item_rate",
                "sr_item_amount",
            ],
            "fields": [
                {
                    "fieldname": "sr_item_code",
                    "label": "Item",
                    "fieldtype": "Link",
                    "options": "Item",
                    "reqd": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "sr_item_name",
                    "label": "Item Name",
                    "fieldtype": "Data",
                    "read_only": 1,
                    "fetch_from": "sr_item_code.item_name",
                },
                {
                    "fieldname": "sr_item_uom",
                    "label": "UOM",
                    "fieldtype": "Link",
                    "options": "UOM",
                    "in_list_view": 1,
                },
                {
                    "fieldname": "sr_item_qty",
                    "label": "Qty",
                    "fieldtype": "Float",
                    "reqd": 1,
                    "in_list_view": 1,
                    "default": 1,
                },
                {
                    "fieldname": "sr_item_rate",
                    "label": "Rate",
                    "fieldtype": "Currency",
                    "reqd": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "sr_item_amount",
                    "label": "Amount",
                    "fieldtype": "Currency",
                    "in_list_view": 1,
                    "read_only": 1,
                },
                {
                    "fieldname": "sr_item_description",
                    "label": "Description",
                    "fieldtype": "Small Text",
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "print": 1,
                    "email": 1,
                    "export": 1,
                    "report": 1
                },
                {
                    "role": "Healthcare Administrator",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                },
            ]
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_multi_mode_payment():
    """Create SR Multi Mode Payment master."""

    doctype = "SR Multi Mode Payment"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "istable": 1,  # Indicates it's a child table
            "editable_grid": 1,  # Editable grid option
            "issingle": 0,
            "track_changes": 1,
            "field_order": [
                "mmp_paid_amount",
                "mmp_mode_of_payment",
                "mmp_reference_no",
                "mmp_reference_date",
                "mmp_payment_proof",
                "mmp_payment_entry",
                "mmp_posting_date",
            ],
            "fields": [
                {
                    "fieldname": "mmp_paid_amount",
                    "label": "Paid Amount",
                    "fieldtype": "Currency",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "mmp_mode_of_payment",
                    "label": "Mode of Payment",
                    "fieldtype": "Link",
                    "options": "Mode of Payment",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "mmp_reference_no",
                    "label": "Reference No",
                    "fieldtype": "Data",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "mmp_reference_date",
                    "label": "Reference Date",
                    "fieldtype": "Date",
                    "in_list_view": 1,
                    "columns": 1,
                },
                {
                    "fieldname": "mmp_payment_proof",
                    "label": "Payment Proof",
                    "fieldtype": "Attach",
                    "in_list_view": 1,
                    "columns": 3,
                },
                {
                    "fieldname": "mmp_payment_entry",
                    "label": "Payment Entry",
                    "fieldtype": "Link",
                    "options": "Payment Entry",
                    "in_list_view": 1,
                    "columns": 2,
                },
                {
                    "fieldname": "mmp_posting_date",
                    "label": "Posting Date",
                    "fieldtype": "Date",
                    "in_list_view": 1,
                    "columns": 1,
                },
            ],
            "permissions": [],  # You can specify permissions here if needed
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_item_group_template_item_doctype():
    """Create child table DocType if missing."""

    doctype = "Item Group Template Item"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "custom": 1,
            "istable": 1,
            "fields": [
                {
                    "fieldname": "item_code",
                    "label": "Item",
                    "fieldtype": "Link",
                    "options": "Item",
                    "reqd": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "item_name",
                    "label": "Item Name",
                    "fieldtype": "Data",
                    "fetch_from": "item_code.item_name",
                    "read_only": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "qty",
                    "label": "Qty",
                    "fieldtype": "Float",
                    "default": 1,
                    "in_list_view": 1,
                },
                {
                    "fieldname": "rate",
                    "label": "Rate",
                    "fieldtype": "Currency",
                    "in_list_view": 1,
                },
                {
                    "fieldname": "item_tax_template",
                    "label": "GST Template",
                    "fieldtype": "Link",
                    "options": "Item Tax Template",
                    "in_list_view": 1,
                },
            ],
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_item_group_template_doctype():
    """Create master DocType if missing."""

    doctype = "Item Group Template"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "autoname": "naming_series:",
            "title_field": "template_name",
            "search_fields": "template_name",
            "show_title_field_in_link": 1,
            "track_changes": 1,
            "custom": 1,
            "fields": [

                # Naming Series
                {
                    "fieldname": "naming_series",
                    "label": "Series",
                    "fieldtype": "Select",
                    "options": "IGT-.YY.-.#####",
                    "default": "IGT-.YY.-.#####",
                    "reqd": 1,
                    "hidden": 1
                },

                {
                    "fieldname": "template_name",
                    "label": "Template Name",
                    "fieldtype": "Data",
                    "reqd": 1
                },
                {
                    "fieldname": "description",
                    "label": "Description",
                    "fieldtype": "Small Text"
                },
                {
                    "fieldname": "is_active",
                    "label": "Is Active",
                    "fieldtype": "Check",
                    "default": 1,
                    "in_list_view": 1
                },
                {
                    "fieldname": "section_items",
                    "label": "Items",
                    "fieldtype": "Section Break"
                },
                {
                    "fieldname": "items",
                    "label": "Items",
                    "fieldtype": "Table",
                    "options": "Item Group Template Item",
                    "reqd": 1
                }
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 1,
                    "report": 1
                }
            ]
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()


def create_shipkia_settings():
    """Create Shipkia Settings (Single DocType) if not exists."""

    doctype = "Shipkia Settings"

    if not frappe.db.exists("DocType", doctype):

        logger.info(f"Creating DocType: {doctype}")

        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": doctype,
            "module": MODULE_DEF_NAME,
            "issingle": 1,
            "custom": 1,
            "track_changes": 1,
            "allow_rename": 0,
            "field_order": [
                "enable_sync",
                "webhook_url",
                "webhook_header_key",
                "webhook_header_token",
                "shipkia_order_url",
                "shipkia_order_token",
                "pickup_address",
                "order_channel",
                "shipkia_base_url",
                "shipkia_tracking_url",
            ],
            "fields": [
                # ============================
                # Enable Sync
                # ============================
                {
                    "fieldname": "enable_sync",
                    "label": "Enable Shipkia Sync",
                    "fieldtype": "Check",
                    "default": "0",
                },

                # ============================
                # Webhook (ERP → n8n)
                # ============================
                {
                    "fieldname": "webhook_url",
                    "label": "Webhook URL",
                    "fieldtype": "Data",
                    "reqd": 1,
                },
                {
                    "fieldname": "webhook_header_key",
                    "label": "Webhook Header Key",
                    "fieldtype": "Data",
                    "default": "x-api-key",
                },
                {
                    "fieldname": "webhook_header_token",
                    "label": "Webhook Header Token",
                    "fieldtype": "Password",
                    "reqd": 1,
                },

                # ============================
                # Shipkia Order API
                # ============================
                {
                    "fieldname": "shipkia_order_url",
                    "label": "Shipkia Order URL",
                    "fieldtype": "Data",
                    "reqd": 1,
                },
                {
                    "fieldname": "shipkia_order_token",
                    "label": "Shipkia Order Token",
                    "fieldtype": "Password",
                    "reqd": 1,
                },

                # ============================
                # Meta
                # ============================
                {
                    "fieldname": "pickup_address",
                    "label": "Pickup Address Code",
                    "fieldtype": "Data",
                    "reqd": 1,
                },
                {
                    "fieldname": "order_channel",
                    "label": "Order Channel",
                    "fieldtype": "Data",
                    "default": "",
                    "reqd": 1,
                },
                {
                    "fieldname": "shipkia_base_url",
                    "label": "Shipkia Base URL",
                    "fieldtype": "Data",
                },
                {
                    "fieldname": "shipkia_tracking_url",
                    "label": "Shipkia Tracking URL",
                    "fieldtype": "Data",
                    "reqd": 1,
                },
            ],
            "permissions": [
                {
                    "role": "System Manager",
                    "read": 1,
                    "write": 1,
                    "create": 1,
                    "delete": 0,
                }
            ],
        })
        
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        frappe.logger().info("✅ Shipkia Settings DocType created successfully.")


def disable_item_quick_entry():
    """Disable Quick Entry for Item DocType."""
    if frappe.db.exists("DocType", "Item"):
        frappe.db.set_value("DocType", "Item", "quick_entry", 0)


def _seed_company_warehouses_data():
    """
    Ensure required Siya Clinic warehouses exist for all companies.
    Safe to run multiple times.
    """
    companies = frappe.get_all("Company", pluck="name")

    for company in companies:
        _ensure_company_warehouse(company, "OPD Warehouse")
        _ensure_company_warehouse(company, "Packaging Warehouse")


def _ensure_company_warehouse(company: str, warehouse_name: str):
    if frappe.db.get_value("Warehouse", {
        "warehouse_name": warehouse_name,
        "company": company
    }):
        return

    parent = _get_company_root_warehouse(company)

    try:
        wh = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": warehouse_name,
            "company": company,
            "is_group": 0,
            "parent_warehouse": parent,
        })
        wh.insert(ignore_permissions=True, ignore_if_duplicate=True)

    except frappe.DuplicateEntryError:
        frappe.db.rollback()


def _get_company_root_warehouse(company: str) -> str:
    """
    Get or create root warehouse for company.
    """
    root = frappe.db.get_value(
        "Warehouse",
        {
            "company": company,
            "parent_warehouse": ["is", "not set"],
            "is_group": 1
        },
        "name"
    )

    if root:
        return root

    # fallback → create root warehouse
    root_name = f"All Warehouses - {company}"

    if not frappe.db.exists("Warehouse", root_name):
        root_doc = frappe.get_doc({
            "doctype": "Warehouse",
            "warehouse_name": "All Warehouses",
            "company": company,
            "is_group": 1,
        })
        root_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return root_doc.name

    return root_name


def _seed_roles():
    roles = [
        "Agent",
        "Team Leader",
        "Payment Approver",
        "Doctor PRX",
        "OPD Biller",
        "Packaging Biller",
    ]

    for role_name in roles:
        _ensure_role(role_name)
        _ensure_role_profile(role_name, [role_name])


def _ensure_role(role_name: str):
    if frappe.db.exists("Role", role_name):
        return

    try:
        frappe.get_doc({
            "doctype": "Role",
            "role_name": role_name,
        }).insert(ignore_permissions=True, ignore_if_duplicate=True)

    except frappe.DuplicateEntryError:
        frappe.db.rollback()


def _ensure_role_profile(profile_name: str, roles: list[str]):
    if frappe.db.exists("Role Profile", profile_name):
        return

    try:
        frappe.get_doc({
            "doctype": "Role Profile",
            "role_profile": profile_name,
            "roles": [{"role": r} for r in roles],
        }).insert(ignore_permissions=True, ignore_if_duplicate=True)

    except frappe.DuplicateEntryError:
        frappe.db.rollback()


# def create_bulk_payment_upload():
#     """
#     Create Bulk Payment Upload DocType (idempotent).
#     """

#     doctype_name = "Bulk Payment Upload"

#     if frappe.db.exists("DocType", doctype_name):
#         return

#     doc = frappe.get_doc({
#         "doctype": "DocType",
#         "name": doctype_name,
#         "module": MODULE_DEF_NAME,
#         "custom": 1,
#         "autoname": "hash",
#         "track_changes": 1,
#         "fields": [
#             {
#                 "label": "CSV File",
#                 "fieldname": "csv_file",
#                 "fieldtype": "Attach",
#                 "reqd": 1
#             },
#             {
#                 "label": "Run Actual (create entries)",
#                 "fieldname": "run_actual",
#                 "fieldtype": "Check",
#                 "default": "0"
#             },
#             {
#                 "label": "Process File",
#                 "fieldname": "process_button",
#                 "fieldtype": "Button"
#             },
#             {
#                 "label": "Result / Status",
#                 "fieldname": "status_html",
#                 "fieldtype": "HTML"
#             },
#             {
#                 "label": "Log File",
#                 "fieldname": "log_file",
#                 "fieldtype": "Attach",
#                 "read_only": 1
#             },
#             {
#                 "label": "Last Run",
#                 "fieldname": "last_run",
#                 "fieldtype": "Datetime"
#             }
#         ],
#         "permissions": [
#             {"role": "System Manager", "read": 1, "write": 1, "create": 1},
#             {"role": "Accounts Manager", "read": 1, "write": 1, "create": 1},
#         ]
#     })

#     doc.insert(ignore_permissions=True)
#     frappe.db.commit()
