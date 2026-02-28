import frappe


# --------------------------------------------------------
# 1️⃣ Set Followup ID (based on last digit)
# --------------------------------------------------------
def set_followup_id(doc, method=None):
    source = doc.get("sr_practo_id") or doc.get("sr_patient_id")

    if not source:
        return

    source = source.strip()

    last_digit = None
    for ch in source:
        if ch.isdigit():
            last_digit = ch

    if last_digit is None:
        return

    record = frappe.db.get_value(
        "SR Followup ID",
        {"digit": int(last_digit), "is_active": 1},
        "name"
    )

    if record:
        doc.sr_followup_id = record


# --------------------------------------------------------
# 2️⃣ Set Followup Day (digit % active days)
# --------------------------------------------------------
def set_followup_day(doc, method=None):
    if not doc.get("sr_followup_id"):
        return

    digit = frappe.db.get_value(
        "SR Followup ID",
        doc.sr_followup_id,
        "digit"
    )

    if digit is None:
        return

    days = frappe.get_all(
        "SR Followup Day",
        filters={"is_active": 1},
        order_by="sort_order asc",
        pluck="name"
    )

    if not days:
        return

    # Correct assignment (no db_set)
    doc.sr_followup_day = days[int(digit) % len(days)]


# --------------------------------------------------------
# 3️⃣ Set Default Followup Status
# --------------------------------------------------------
def set_default_followup_status(doc, method=None):
    if doc.get("sr_followup_status"):
        return

    default_status = "Pending"

    record = frappe.db.get_value(
        "SR Followup Status",
        {"status_name": default_status, "is_active": 1},
        "name"
    )

    if record:
        doc.sr_followup_status = record
    else:
        doc.sr_followup_status = default_status