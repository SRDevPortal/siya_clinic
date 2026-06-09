import os

import frappe
from frappe.core.doctype.file import file as file_module
from frappe.core.doctype.file.file import File
from frappe.utils.file_manager import get_file_path

from .client import get_bucket, get_s3_client
from .delete import delete_file_from_s3
from .upload import upload_file_to_s3
from .utils import extract_key, is_s3_enabled


_original_exists_on_disk = File.exists_on_disk
_original_validate_file_url = File.validate_file_url
_original_file_validate = File.validate
_original_get_full_path = File.get_full_path
_original_get_content = File.get_content

if "s3://" not in file_module.URL_PREFIXES:
	file_module.URL_PREFIXES = (*file_module.URL_PREFIXES, "s3://")


def s3_safe_exists_on_disk(self):
	if self.file_url and str(self.file_url).startswith("s3://"):
		return False
	return _original_exists_on_disk(self)


def s3_safe_validate_file_url(self):
	if self.file_url and str(self.file_url).startswith("s3://"):
		return
	return _original_validate_file_url(self)


def s3_safe_file_validate(self):
	if self.file_url and str(self.file_url).startswith("s3://"):
		return
	return _original_file_validate(self)


def s3_safe_get_full_path(self):
	if self.file_url and str(self.file_url).startswith("s3://"):
		return self.file_url
	return _original_get_full_path(self)


def s3_safe_get_content(self):
	if self.file_url and str(self.file_url).startswith("s3://"):
		key = extract_key(self.file_url)
		s3 = get_s3_client()
		bucket = get_bucket()

		if not key or not s3 or not bucket:
			frappe.throw(f"Cannot read S3 file: {self.file_url}")

		try:
			response = s3.get_object(Bucket=bucket, Key=key)
			self._content = response["Body"].read()
			return self._content
		except Exception:
			frappe.log_error(frappe.get_traceback(), "S3_READ_FAILED")
			frappe.throw(f"Cannot read S3 file: {self.file_url}")

	return _original_get_content(self)


File.exists_on_disk = s3_safe_exists_on_disk
File.validate_file_url = s3_safe_validate_file_url
File.validate = s3_safe_file_validate
File.get_full_path = s3_safe_get_full_path
File.get_content = s3_safe_get_content


logger = frappe.logger("siya_s3")

PAYMENT_PROOF_PARENT_DOCTYPE = "Patient Encounter"
PAYMENT_PROOF_FIELD = "mmp_payment_proof"


def _skip_s3_delete_file_names():
	skip_names = getattr(frappe.flags, "siya_skip_s3_delete_file_names", None)
	if skip_names is None:
		skip_names = set()
		frappe.flags.siya_skip_s3_delete_file_names = skip_names
	return skip_names


def _is_payment_proof_file(doc):
	return (
		doc.attached_to_doctype == PAYMENT_PROOF_PARENT_DOCTYPE
		and doc.attached_to_field == PAYMENT_PROOF_FIELD
	)


def _delete_file_doc_only(file_name):
	if not file_name:
		return

	skip_names = _skip_s3_delete_file_names()
	skip_names.add(file_name)
	try:
		frappe.delete_doc("File", file_name, ignore_permissions=True)
	except frappe.DoesNotExistError:
		pass
	finally:
		skip_names.discard(file_name)


def _delete_payment_proof_file_docs(attached_to_name=None, file_url=None):
	filters = {
		"attached_to_doctype": PAYMENT_PROOF_PARENT_DOCTYPE,
		"attached_to_field": PAYMENT_PROOF_FIELD,
	}

	if attached_to_name:
		filters["attached_to_name"] = attached_to_name
	if file_url:
		filters["file_url"] = file_url

	for file_name in frappe.get_all("File", filters=filters, pluck="name"):
		_delete_file_doc_only(file_name)


def handle_file_after_insert(doc, method=None):
	if doc.attached_to_doctype == "Prepared Report":
		return

	if doc.file_name and doc.file_name.endswith((".json.gz", ".csv", ".xlsx")):
		return

	if not doc.attached_to_doctype:
		return

	if doc.is_folder:
		return

	if doc.file_url and str(doc.file_url).startswith("s3://"):
		return

	if not is_s3_enabled():
		return

	try:
		local_path = get_file_path(doc.file_url)

		key = upload_file_to_s3(doc)
		if not key:
			return

		s3_url = f"s3://{key}"
		doc.db_set("file_url", s3_url, update_modified=False)

		if _is_payment_proof_file(doc):
			if local_path and os.path.exists(local_path):
				os.remove(local_path)
			_delete_file_doc_only(doc.name)
			return

		if local_path and os.path.exists(local_path):
			os.remove(local_path)

	except Exception:
		frappe.log_error(frappe.get_traceback(), "S3_UPLOAD_FAILED")


def handle_file_on_trash(doc, method=None):
	if doc.name in _skip_s3_delete_file_names():
		return

	if not doc.file_url:
		return

	if _file_url_used_by_another_file(doc):
		logger.info(f"S3_DELETE_SKIPPED | shared_file_url={doc.file_url} | file={doc.name}")
		return

	key = extract_key(doc.file_url)
	if not key:
		return

	try:
		s3_url = f"s3://{key}"
		delete_file_from_s3(s3_url)

	except Exception:
		frappe.log_error(frappe.get_traceback(), "S3_DELETE_FAILED")


def _file_url_used_by_another_file(doc) -> bool:
	if not doc.file_url:
		return False

	return bool(
		frappe.db.exists(
			"File",
			{
				"name": ["!=", doc.name],
				"file_url": doc.file_url,
				"is_folder": 0,
			},
		)
	)


def cleanup_payment_proof_removals(doc, method=None):
	previous_doc = doc.get_doc_before_save()
	if not previous_doc:
		return

	previous_rows = {
		row.name: (row.mmp_payment_proof or "").strip()
		for row in (previous_doc.get("enc_multi_payments") or [])
		if getattr(row, "name", None)
	}
	current_rows = {
		row.name: (row.mmp_payment_proof or "").strip()
		for row in (doc.get("enc_multi_payments") or [])
		if getattr(row, "name", None)
	}
	current_urls = {url for url in current_rows.values() if url}
	deleted_urls = set()

	for row_name, old_url in previous_rows.items():
		if not old_url:
			continue

		if current_rows.get(row_name) == old_url:
			continue

		if old_url in current_urls or old_url in deleted_urls:
			continue

		_delete_payment_proof_file_docs(attached_to_name=doc.name, file_url=old_url)
		delete_file_from_s3(old_url)
		deleted_urls.add(old_url)
