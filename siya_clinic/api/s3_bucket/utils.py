from urllib.parse import unquote, urlparse

import frappe


def extract_key(file_url: str) -> str | None:
	if not file_url:
		return None

	try:
		if file_url.startswith("s3://"):
			return unquote(file_url.replace("s3://", "", 1))

		parsed = urlparse(file_url)

		if parsed.scheme in ("http", "https"):
			return unquote(parsed.path.lstrip("/"))

		return None

	except Exception:
		frappe.log_error(frappe.get_traceback(), "S3_EXTRACT_KEY_FAILED")
		return None


def is_s3_enabled():
	return all(
		[
			frappe.conf.get("aws_s3_access_key_id"),
			frappe.conf.get("aws_s3_secret_access_key"),
			frappe.conf.get("aws_s3_region"),
			frappe.conf.get("aws_s3_bucket"),
		]
	)
