import unittest
from types import SimpleNamespace
from unittest.mock import patch
from siya_clinic.api.s3_bucket import file_hooks

class S3FileCleanupTests(unittest.TestCase):
    def test_s3_url_never_goes_to_local_disk_deletion(self):
        doc = SimpleNamespace(file_url="s3://synthetic/proof.pdf", thumbnail_url=None)
        with patch.object(file_hooks, "_original_delete_file_on_disk") as original:
            file_hooks.s3_safe_delete_file_on_disk(doc)
            original.assert_not_called()

    def test_local_file_keeps_native_cleanup(self):
        doc = SimpleNamespace(file_url="/private/files/proof.pdf")
        with patch.object(file_hooks, "_original_delete_file_on_disk") as original:
            file_hooks.s3_safe_delete_file_on_disk(doc)
            original.assert_called_once_with(doc)

    def test_request_initialization_precedes_native_duplicate_disk_check(self):
        from siya_clinic import hooks
        from frappe.core.doctype.file.file import File
        self.assertIn("siya_clinic.api.s3_bucket.file_hooks.initialize_file_support", hooks.before_request)
        file_hooks.initialize_file_support()
        duplicate = SimpleNamespace(file_url="s3://synthetic/existing-proof.jpeg")
        self.assertFalse(File.exists_on_disk(duplicate))

    def test_native_local_duplicate_check_is_preserved(self):
        doc = SimpleNamespace(file_url="/private/files/proof.jpeg")
        with patch.object(file_hooks, "_original_exists_on_disk", return_value=True) as original:
            self.assertTrue(file_hooks.s3_safe_exists_on_disk(doc))
            original.assert_called_once_with(doc)
