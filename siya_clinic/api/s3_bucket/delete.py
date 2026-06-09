from urllib.parse import unquote

import frappe

from .client import get_bucket, get_s3_client
from .utils import extract_key

logger = frappe.logger("siya_s3")


def delete_file_from_s3(file_url: str):
	if not file_url:
		return

	try:
		s3 = get_s3_client()
		bucket = get_bucket()

		if not s3 or not bucket:
			logger.info("S3_DISABLED | skipping delete")
			return

		key = extract_key(file_url)

		if not key:
			logger.info(f"S3_DELETE_SKIPPED | invalid_url={file_url}")
			return

		key = unquote(key)

		logger.info(f"S3_DELETE_ATTEMPT | bucket={bucket} | key={key}")

		s3.delete_object(Bucket=bucket, Key=key)

		logger.info(f"S3_DELETE_SUCCESS | bucket={bucket} | key={key}")

	except Exception:
		logger.error(f"S3_DELETE_FAILED | url={file_url}\n{frappe.get_traceback()}")


@frappe.whitelist()
def delete_s3_by_url(file_url: str):
	if not file_url:
		return {"status": "no_file_url"}

	delete_file_from_s3(file_url)

	return {
		"status": "deleted",
		"file_url": file_url,
	}
