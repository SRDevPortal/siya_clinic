# siya_clinic/api/patient/followup_marker.py

import frappe
from frappe.utils import getdate, nowdate

# --------------------------------------------------------
# 1️⃣ Set Followup ID (based on last digit)
# --------------------------------------------------------
def set_followup_id(doc, method=None):
    # ✅ Skip if already set
    if doc.get("sr_followup_id"):
        return

    # Use best available source
    source = (
        doc.get("sr_practo_id")
        or doc.get("sr_patient_id")
        or doc.name
    )

    if not source:
        return

    source = str(source).strip()

    # Extract digits safely
    digits = [c for c in source if c.isdigit()]
    if not digits:
        return
    
    try:
        last_digit = int(digits[-1])
    except:
        return

    # Fetch matching Followup ID
    record = frappe.get_cached_value(
        "SR Followup ID",
        {"digit": last_digit, "is_active": 1},
        "name"
    )

    if record:
        doc.sr_followup_id = record


# --------------------------------------------------------
# 2️⃣ Set Followup Day (Weekday Based)
# --------------------------------------------------------
def set_followup_day(doc, method=None):
    # Skip if already set
    if doc.get("sr_followup_day"):
        return

    # Safe creation date
    creation_date = getdate(doc.creation) if doc.creation else getdate(nowdate())

    # Get short weekday (Mon, Tue, Wed...)
    weekday_name = creation_date.strftime("%a")

    # Try exact weekday match (cached)
    record = frappe.get_cached_value(
        "SR Followup Day",
        {"day_name": weekday_name, "is_active": 1},
        "name"
    )

    if record:
        doc.sr_followup_day = record
        return

    # Fallback → first active day
    fallback = frappe.get_all(
        "SR Followup Day",
        filters={"is_active": 1},
        order_by="sort_order asc",
        limit=1,
        pluck="name"
    )

    if fallback:
        doc.sr_followup_day = fallback[0]


# --------------------------------------------------------
# 3️⃣ Set Default Followup Status
# --------------------------------------------------------
def set_default_followup_status(doc, method=None):
    if doc.get("sr_followup_status"):
        return

    record = frappe.db.get_value(
        "SR Followup Status",
        {"status_name": "Pending", "is_active": 1},
        "name"
    )

    doc.sr_followup_status = record or "Pending"
