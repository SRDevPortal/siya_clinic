import frappe

from healthcare.healthcare.doctype.patient_encounter.patient_encounter import (
    PatientEncounter as HealthcarePatientEncounter,
)


class PatientEncounter(HealthcarePatientEncounter):
    """Siya Clinic rules for prescriptions without stock Item mappings."""

    def validate_medications(self):
        """Allow an empty drug code while preserving Healthcare's reverse mapping."""
        for item in self.drug_prescription or []:
            if not item.drug_code or item.medication:
                continue

            medication = frappe.db.get_value(
                "Medication Linked Item",
                {"item": item.drug_code},
                "parent",
            )
            if medication:
                item.medication = medication

    def make_medication_request(self):
        """Create item-based orders only for prescriptions that have a drug code."""
        for drug in self.drug_prescription or []:
            if not drug.drug_code or drug.medication_request:
                continue

            medication = None
            if drug.medication:
                medication = frappe.get_doc("Medication", drug.medication)

            order = self.get_order_details(medication, drug, True)
            order.insert(ignore_permissions=True, ignore_mandatory=True)
            order.submit()
            drug.medication_request = order.name
