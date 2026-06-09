import frappe
from botocore.exceptions import ClientError

from .client import get_bucket, get_s3_client
from .utils import extract_key

logger = frappe.logger("siya_s3")


@frappe.whitelist()
def get_presigned_url(file_url, expires=900):
	if not file_url:
		return None

	try:
		key = extract_key(file_url)

		if not key:
			logger.info(f"PRESIGN_SKIPPED | invalid_url={file_url}")
			return file_url

		s3 = get_s3_client()
		bucket = get_bucket()

		if not s3 or not bucket:
			logger.info("S3_DISABLED | returning original URL")
			return file_url

		try:
			s3.head_object(Bucket=bucket, Key=key)
		except ClientError as e:
			error_code = (e.response.get("Error") or {}).get("Code")
			if error_code in ("404", "NoSuchKey", "NotFound"):
				logger.error(f"PRESIGN_MISSING_KEY | bucket={bucket} | key={key}")
				frappe.throw(
					"This attachment record points to S3, but the file is missing from the bucket. "
					"Please re-upload the attachment."
				)
			raise

		try:
			expires = int(expires)
		except Exception:
			expires = 900

		url = s3.generate_presigned_url(
			ClientMethod="get_object",
			Params={
				"Bucket": bucket,
				"Key": key,
			},
			ExpiresIn=expires,
		)

		logger.info(f"PRESIGN_SUCCESS | key={key}")

		return url

	except Exception:
		logger.error(f"PRESIGN_FAILED | url={file_url}\n{frappe.get_traceback()}")
		return file_url
