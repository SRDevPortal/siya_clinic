import frappe
import csv, os, traceback
from frappe.utils import flt, nowdate, getdate, now_datetime


@frappe.whitelist()
def process_file_settle_invoices(file_url="/files/sample.csv", submit=0, clearing_account=None):
    """
    Bulk settle invoices using Payment Entry.
    Supports dry-run and partial settlements.
    """

    submit = bool(int(submit))

    try:
        site_path = frappe.get_site_path()

        # ✅ Correct path resolution
        if file_url.startswith("/files/"):
            csv_path = os.path.join(site_path, "public", file_url.lstrip("/"))
        elif file_url.startswith("/private/files/"):
            csv_path = os.path.join(site_path, file_url.lstrip("/"))
        else:
            csv_path = file_url

        if not os.path.exists(csv_path):
            frappe.throw(f"CSV not found: {csv_path}")

        if not clearing_account:
            clearing_account = "Cash - EEPL"

        # ✅ Read CSV
        rows = []
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append({
                    (k.strip().lower() if k else k): (v.strip() if isinstance(v, str) else v)
                    for k, v in r.items()
                })

        result = {"processed": [], "skipped": [], "errors": []}
        log_rows = []

        for idx, row in enumerate(rows, start=1):
            try:
                invoice = (row.get("invoice") or row.get("id") or row.get("sinv") or "").strip()

                if not invoice:
                    result["skipped"].append({"row": idx, "reason": "missing invoice"})
                    log_rows.append([idx, "", "skipped", "missing invoice", ""])
                    continue

                # Fetch invoice
                try:
                    si = frappe.get_doc("Sales Invoice", invoice)
                except Exception as e:
                    msg = f"invoice not found: {e}"
                    result["errors"].append({"row": idx, "invoice": invoice, "error": msg})
                    log_rows.append([idx, invoice, "error", msg, ""])
                    continue

                current_outstanding = flt(si.outstanding_amount)

                # ✅ safer amount parsing
                requested_amount = row.get("amount")
                requested_amount = flt(requested_amount) if requested_amount not in (None, "",) else None

                if requested_amount is None:
                    requested_amount = current_outstanding

                if current_outstanding <= 0:
                    result["skipped"].append({"row": idx, "invoice": invoice, "reason": "already_settled"})
                    log_rows.append([idx, invoice, "skipped", "already_settled", ""])
                    continue

                allocate_amount = min(requested_amount, current_outstanding)

                if allocate_amount <= 0:
                    result["skipped"].append({"row": idx, "invoice": invoice, "reason": "invalid_allocate_amount"})
                    log_rows.append([idx, invoice, "skipped", "invalid_allocate_amount", ""])
                    continue

                posting_date = row.get("remittance_date") or nowdate()

                # remarks
                remarks_parts = [f"Clearing payment for {invoice}"]
                for k in ("utr", "awb", "crf_id", "courier"):
                    if row.get(k):
                        remarks_parts.append(f"{k.upper()}: {row.get(k)}")
                remarks = " | ".join(remarks_parts)

                # ================= DRY RUN =================
                if not submit:
                    note = ""
                    if requested_amount != allocate_amount:
                        note = f"requested {requested_amount} truncated to {allocate_amount}"

                    result["processed"].append({
                        "row": idx,
                        "invoice": invoice,
                        "requested_amount": requested_amount,
                        "allocated_amount": allocate_amount,
                        "posting_date": posting_date,
                        "note": note,
                        "action": "dry_run"
                    })
                    log_rows.append([idx, invoice, "dry_run", note, ""])
                    continue

                # ================= ACTUAL RUN =================
                pe_name = _create_payment_entry_and_allocate(
                    invoice, si, allocate_amount, posting_date, clearing_account, remarks
                )

                result["processed"].append({
                    "row": idx,
                    "invoice": invoice,
                    "amount": allocate_amount,
                    "payment_entry": pe_name
                })
                log_rows.append([idx, invoice, "created", "", pe_name])

            except Exception as e:
                frappe.log_error(traceback.format_exc(), "bulk_payment_error")
                result["errors"].append({"row": idx, "invoice": row.get("invoice"), "error": str(e)})
                log_rows.append([idx, row.get("invoice"), "error", str(e), ""])

        # ✅ always write log
        log_file = _write_log_csv_common(log_rows)
        result["log_file"] = log_file

        return result

    except Exception:
        frappe.log_error(traceback.format_exc(), "bulk_payment_outer")
        frappe.throw("Bulk payment processing failed. Check error logs.")


def _create_payment_entry_and_allocate(invoice_name, si_doc, amount, posting_date, paid_to_account, remarks):
    """Create & submit Payment Entry"""

    si_doc = frappe.get_doc("Sales Invoice", si_doc.name)
    outstanding = flt(si_doc.outstanding_amount)
    allocate_amount = min(amount, outstanding)

    if allocate_amount <= 0:
        frappe.throw(f"Invoice {invoice_name} has no outstanding.")

    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer"
    pe.party = si_doc.customer
    pe.party_name = si_doc.customer_name
    pe.company = si_doc.company
    pe.posting_date = getdate(posting_date)
    pe.mode_of_payment = "Cash"
    pe.paid_to = paid_to_account
    pe.paid_amount = allocate_amount
    pe.received_amount = allocate_amount
    pe.remark = remarks

    pe.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": invoice_name,
        "allocated_amount": allocate_amount
    })

    pe.insert(ignore_permissions=True)
    pe.submit()
    return pe.name


def _write_log_csv_common(rows):
    site_path = frappe.get_site_path()
    files_dir = os.path.join(site_path, "public", "files")
    os.makedirs(files_dir, exist_ok=True)

    fname = f"bulk_settle_log_{now_datetime().strftime('%Y%m%d%H%M%S')}.csv"
    fpath = os.path.join(files_dir, fname)

    with open(fpath, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["row", "invoice", "status", "reference", "error_or_note"])
        for r in rows:
            writer.writerow((list(r) + [""] * 5)[:5])

    return "/files/" + fname


@frappe.whitelist()
def process_file_from_ui(file_value, submit=0, clearing_account=None):
    """UI wrapper"""

    if not file_value:
        frappe.throw("Please attach a CSV file.")

    if file_value.startswith("/files/"):
        file_url = file_value
    elif frappe.db.exists("File", file_value):
        file_url = frappe.get_doc("File", file_value).file_url
    else:
        file_url = file_value

    # security
    if int(submit) == 1:
        allowed_roles = {"System Manager", "Accounts Manager"}
        if not (set(frappe.get_roles()) & allowed_roles):
            frappe.throw("Not authorized to run actual process.")

    return process_file_settle_invoices(file_url, submit, clearing_account)