"""Clinic-owned endpoints consumed by the shared Privacy Shield engine."""
ENDPOINTS = {
    "crm_get_data": "siya_clinic.api.crm_lead.privacy_views.get_data",
    "crm_get_notifications": "siya_clinic.api.crm_lead.privacy_notifications.get_notifications",
    "crm_mark_as_read": "siya_clinic.api.crm_lead.privacy_notifications.mark_as_read",
    "get_encounter_context": "siya_clinic.api.patient_intake.get_encounter_context",
}
TEMPLATES = {}  # SRIAAS pilot invoice previews are not enabled for Siya.
