import unittest
from unittest.mock import MagicMock, patch
import frappe
from siya_clinic.api import patient_invoices as api


class PatientInvoiceTests(unittest.TestCase):
    def setUp(self):
        self.parent = MagicMock()
        self.parent.name = "PAT-A"

    def test_parent_access_is_required_before_any_query(self):
        self.parent.check_permission.side_effect = frappe.PermissionError
        with patch.object(frappe, "get_doc", return_value=self.parent), patch.object(frappe, "get_list") as query:
            with self.assertRaises(frappe.PermissionError):
                api.get_patient_invoices.__wrapped__("PAT-A")
            query.assert_not_called()

    def test_no_readable_encounters_does_not_query_all_invoices(self):
        with patch.object(frappe, "get_doc", return_value=self.parent), patch.object(frappe, "get_list", return_value=[]) as query:
            self.assertEqual(api.get_patient_invoices.__wrapped__("PAT-A"), [])
            self.assertEqual(query.call_count, 1)
            self.assertEqual(query.call_args.kwargs["filters"], {"patient": "PAT-A"})

    def test_only_submitted_invoices_for_readable_patient_encounters_are_selected(self):
        invoice = {"name": "INV-A", "posting_date": "2026-11-04", "grand_total": 100, "outstanding_amount": 25}
        with patch.object(frappe, "get_doc", return_value=self.parent), patch.object(frappe, "get_list", side_effect=[[frappe._dict(name="ENC-A")], [invoice]]) as query:
            self.assertEqual(api.get_patient_invoices.__wrapped__("PAT-A"), [invoice])
            self.parent.check_permission.assert_called_once_with("read")
            dt = query.call_args.args[0]
            opts = query.call_args.kwargs
            self.assertEqual(dt, "Sales Invoice")
            self.assertEqual(opts["filters"], {"source_encounter": ["in", ["ENC-A"]], "docstatus": 1})
            self.assertEqual(set(opts["fields"]), {"name", "posting_date", "grand_total", "outstanding_amount"})
            for call in query.call_args_list:
                self.assertNotIn("ignore_permissions", call.kwargs)

    def test_native_encounter_and_invoice_denials_are_preserved(self):
        for result in [[frappe.PermissionError], [[frappe._dict(name="ENC-A")], frappe.PermissionError]]:
            with patch.object(frappe, "get_doc", return_value=self.parent), patch.object(frappe, "get_list", side_effect=result):
                with self.assertRaises(frappe.PermissionError):
                    api.get_patient_invoices.__wrapped__("PAT-A")

    def test_response_limit_cannot_disable_pagination(self):
        for requested, expected in [(10000, 100), (-1, 1), (0, 100)]:
            with patch.object(frappe, "get_doc", return_value=self.parent), patch.object(frappe, "get_list", side_effect=[[frappe._dict(name="ENC-A")], []]) as query:
                api.get_patient_invoices.__wrapped__("PAT-A", requested)
                self.assertEqual(query.call_args.kwargs["limit_page_length"], expected)

    def test_missing_patient_is_rejected_without_reading(self):
        with patch.object(frappe, "get_doc") as read:
            with self.assertRaises(frappe.ValidationError):
                api.get_patient_invoices.__wrapped__("")
            read.assert_not_called()
