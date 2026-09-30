"""Run with python -m unittest siya_clinic.tests.test_print_regions."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from siya_clinic.setup import print_formats as formats
from siya_clinic.siya_clinic.doctype.clinic_settings.clinic_settings import ClinicSettings


class PrintRegionTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(formats, "frappe")
        self.frappe = patcher.start()
        self.addCleanup(patcher.stop)
        self.frappe.db.get_single_value.return_value = None
        self.frappe.db.get_value.return_value = "old domestic template"
        self.frappe.get_meta.return_value = SimpleNamespace(default_print_format="Patient Encounter New")
        self.frappe.throw.side_effect = ValueError

    def test_explicit_region_wins_over_legacy_html(self):
        self.frappe.db.get_single_value.return_value = "Domestic"
        with patch.object(formats, "_load", return_value="international"):
            self.frappe.db.get_value.return_value = "international"
            self.assertEqual(formats.get_encounter_print_region(), "Domestic")
        self.frappe.db.get_value.assert_not_called()

    def test_upgrading_international_site_recognizes_approved_template(self):
        self.frappe.db.get_value.return_value = "international\n"
        with patch.object(formats, "_load", return_value="international"):
            self.assertEqual(formats.get_encounter_print_region(), "International")

    def test_unconfigured_domestic_site_keeps_domestic(self):
        with patch.object(formats, "_load", return_value="international"):
            self.assertEqual(formats.get_encounter_print_region(), "Domestic")

    def test_existing_named_default_is_preserved(self):
        self.frappe.get_meta.return_value.default_print_format = "Patient Encounter International"
        self.assertEqual(formats.get_encounter_print_region(), "International")

    def test_invalid_choice_cannot_silently_select_domestic(self):
        self.frappe.db.get_single_value.return_value = "Invalid"
        with self.assertRaises(ValueError):
            formats.get_encounter_print_region()

    def test_migrations_keep_each_regions_default_and_legacy_alias(self):
        for region in formats.ENCOUNTER_FORMATS:
            with self.subTest(region=region), patch.object(formats, "_upsert_pf") as upsert, patch.object(formats, "_set_encounter_default") as default:
                self.frappe.db.get_single_value.return_value = region
                formats.apply_encounter_formats()
                formats.apply_encounter_formats()
                self.assertEqual(default.call_args.args, (formats.ENCOUNTER_FORMATS[region],))
                aliases = [call for call in upsert.call_args_list if call.args[0] == formats.LEGACY_FORMAT]
                self.assertEqual(len(aliases), 2)
                self.assertTrue(all(call.args[2] == f"print_formats/patient_encounter_{region.lower()}.html" for call in aliases))
                self.frappe.db.set_single_value.assert_called_with("Clinic Settings", "encounter_print_region", region)

    def test_saving_settings_applies_selection_immediately(self):
        with patch.object(formats, "apply_encounter_formats") as apply:
            ClinicSettings.on_update(SimpleNamespace(encounter_print_region="International"))
            apply.assert_called_once_with("International")

    def test_site_specific_records_are_not_exported_as_fixtures(self):
        from siya_clinic.hooks import fixtures
        by_type = {item["dt"]: item for item in fixtures}
        self.assertNotIn("Clinic Settings", by_type)
        self.assertIn(["name", "not in", ["Patient Encounter-default_print_format", "Patient Encounter-main-default_print_format"]], by_type["Property Setter"]["filters"])
        excluded = next(f[2] for f in by_type["Print Format"]["filters"] if f[0] == "name")
        self.assertTrue(set(formats.ENCOUNTER_FORMATS.values()) | {formats.LEGACY_FORMAT} <= set(excluded))


if __name__ == "__main__":
    unittest.main()
