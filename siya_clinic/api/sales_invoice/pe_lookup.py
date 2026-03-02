import frappe


@frappe.whitelist()
def get_payment_entries_for_invoice(si_name: str):
    """
    Return Payment Entries linked to this Sales Invoice.
    Includes:
      • Submitted PEs referencing this SI
      • Draft PEs with intended_sales_invoice
    """

    if not si_name:
        return []

    # -------------------------------
    # Submitted Payment Entries
    # -------------------------------
    submitted = frappe.db.sql(
        """
        SELECT pe.name, pe.docstatus, pe.posting_date, pe.party, pe.party_type,
               pe.mode_of_payment, pe.received_amount, pe.paid_amount, pe.status
        FROM `tabPayment Entry` pe
        JOIN `tabPayment Entry Reference` per ON per.parent = pe.name
        WHERE per.reference_doctype = 'Sales Invoice'
          AND per.reference_name = %s
          AND pe.docstatus = 1
        ORDER BY pe.posting_date DESC, pe.creation DESC
        """,
        (si_name,),
        as_dict=True,
    )

    # -------------------------------
    # Draft Payment Entries (optional)
    # -------------------------------
    drafts = []
    if frappe.get_meta("Payment Entry").has_field("intended_sales_invoice"):
        drafts = frappe.db.sql(
            """
            SELECT name, docstatus, posting_date, party, party_type,
                   mode_of_payment, received_amount, paid_amount, status
            FROM `tabPayment Entry`
            WHERE intended_sales_invoice = %s AND docstatus = 0
            ORDER BY posting_date DESC, creation DESC
            """,
            (si_name,),
            as_dict=True,
        )

    return submitted + drafts


@frappe.whitelist()
def get_sales_invoices_for_payment_entry(pe_name: str):
    """
    Return Sales Invoices linked to a Payment Entry.

    Includes:
      • Submitted SIs via references
      • Intended SI (custom field)

    Returns:
      [{name, docstatus, status, posting_date, customer, patient}]
    """

    if not pe_name:
        return []

    # -------------------------------
    # Sales Invoices via references
    # -------------------------------
    via_refs = frappe.db.sql(
        """
        SELECT si.name, si.docstatus, si.status, si.posting_date, si.customer,
               si.patient
        FROM `tabPayment Entry Reference` per
        JOIN `tabSales Invoice` si ON si.name = per.reference_name
        WHERE per.parent = %s AND per.reference_doctype = 'Sales Invoice'
        ORDER BY si.posting_date DESC, si.creation DESC
        """,
        (pe_name,),
        as_dict=True,
    )

    # -------------------------------
    # Intended Sales Invoice (optional)
    # -------------------------------
    extra = []
    if frappe.get_meta("Payment Entry").has_field("intended_sales_invoice"):
        intended = frappe.db.get_value(
            "Payment Entry", pe_name, "intended_sales_invoice"
        )

        if intended and frappe.db.exists("Sales Invoice", intended):
            row = frappe.db.get_value(
                "Sales Invoice",
                intended,
                ["name", "docstatus", "status", "posting_date", "customer", "patient"],
                as_dict=True,
            )

            if row and not any(r["name"] == row["name"] for r in via_refs):
                extra.append(row)

    return via_refs + extra