# siya_clinic/setup/patient_appointment.py

import frappe
import logging

from .utils import create_cf_with_module, upsert_property_setter, ensure_field_before, ensure_field_after

logger = logging.getLogger(__name__)

DT = "Patient Appointment"


def apply():
    """Apply Patient Appointment customizations."""
    logger.info("Applying Patient Appointment setup")

    _make_appointment_fields()
    # _hide_payment_child_fields()
    _apply_appointment_ui_customizations()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("Patient Appointment setup completed")


# ------------------------------------------------------------
# Custom Fields
# ------------------------------------------------------------

def _make_appointment_fields():
    """Add custom fields to Patient Appointment."""

    if not frappe.db.exists("DocType", DT):
        return

    create_cf_with_module({
        DT: [
            {
                "fieldname": "apt_patient_id",
                "label": "Patient ID",
                "fieldtype": "Data",
                "read_only": 1,
                "depends_on": "eval:doc.patient",
                "fetch_from": "patient.sr_patient_id",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "patient_name",
            },
            {
                "fieldname": "apt_mobile_number",
                "label": "Mobile Number",
                "fieldtype": "Data",
                "read_only": 1,
                "depends_on": "eval:doc.patient",
                "fetch_from": "patient.mobile",
                "in_list_view": 1,
                "in_standard_filter": 1,
                "insert_after": "apt_patient_id",
            },
            {
                "fieldname": "apt_patient_age",
                "label": "Patient Age",
                "fieldtype": "Data",
                "read_only": 1,
                "depends_on": "eval:doc.patient",
                "fetch_from": "patient.sr_patient_age",
                "insert_after": "patient_age",
            },
            {
                "fieldname": "apt_department",
                "label": "Patient Department",
                "fieldtype": "Link",
                "options": "Medical Department",
                "read_only": 1,
                "depends_on": "eval:doc.patient",
                "fetch_from": "patient.sr_medical_department",
                "in_standard_filter": 1,
                "insert_after": "apt_patient_age",
            },
            {
                "fieldname": "apt_payments_sb",
                "label": "Payments",
                "fieldtype": "Section Break",
                "collapsible": 0,
                "insert_after": "ref_sales_invoice",
            },
            {
                "fieldname": "apt_multi_payments",
                "fieldtype": "Table",
                "options": "SR Multi Mode Payment",
                "insert_after": "apt_payments_sb",
                "in_list_view": 0,
            },
            {
                "fieldname": "created_by_agent",
                "label": "Created By",
                "fieldtype": "Link",
                "options": "User",
                "read_only": 1,
                "insert_after": "appointment_date",
            },
        ]
    })


# ------------------------------------------------------------
# UI Customization
# ------------------------------------------------------------

def _apply_appointment_ui_customizations():
    """Apply UI and layout customizations for Patient Appointment."""

    targets = (
        "service_unit",
        "event",
        # "patient_age",
        "procedure_template",
        "get_procedure_from_encounter",
        "therapy_plan",
        "paid_amount", "mode_of_payment",
        "invoiced",
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