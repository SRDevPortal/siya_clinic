"""Explicit Bench index repair; does not run during migration or HTTP requests.

Requires the compatible vobiz_ai maintenance helper on the same bench.
"""
from vobiz_ai.maintenance.lookup_indexes import repair_specs

TARGETS = {
    "patient_invoice_encounter": (
        "tabSales Invoice", "idx_si_encounter_status_posting",
        ("source_encounter", "docstatus", "posting_date", "creation"),
    ),
    "encounter_clinical_history": (
        "tabPatient Encounter", "idx_pe_patient_date_creation",
        ("patient", "encounter_date", "creation"),
    ),
}


def repair(target=None, apply=False):
    return repair_specs(TARGETS, target, apply)
