import frappe

def compose_full_name(doc, method=None):
    """
    Compose practitioner full name before validation.

    Ensures consistent naming for Healthcare Practitioner.
    """

    parts = [
        doc.get("first_name"),
        doc.get("middle_name"),
        doc.get("last_name"),
    ]

    # Filter empty parts and join
    full_name = " ".join([p.strip() for p in parts if p])

    if full_name:
        doc.practitioner_name = full_name