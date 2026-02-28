# siya_clinic/api/customer/customer_id.py

import frappe
import re
from frappe.model.naming import make_autoname


def set_customer_id(doc, method=None):
    """
    Generate global Customer ID.

    Format:
        CUST1 → CUST999999
    """

    # Skip if already set
    if doc.get("sr_customer_id"):
        return

    # Ensure column exists (safe during install)
    if not frappe.db.has_column("Customer", "sr_customer_id"):
        return

    # Generate global numeric series
    generated = make_autoname("CUST-.######")

    # Remove leading zeros
    number = int(re.sub(r"\D", "", generated))

    # Final format
    doc.sr_customer_id = f"CUST{number}"