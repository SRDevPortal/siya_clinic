import frappe
from frappe.model.document import Document


class ClinicSettings(Document):
    def validate(self):
        if self.encounter_print_region not in ("Domestic", "International"):
            frappe.throw("Encounter Print Region must be Domestic or International.")

    def on_update(self):
        from siya_clinic.setup.print_formats import apply_encounter_formats

        apply_encounter_formats(self.encounter_print_region)
