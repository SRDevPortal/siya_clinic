import frappe


def run(limit=200, start=0):

    print(f"\nStarting Customer → Patient migration | start={start} limit={limit}\n")

    frappe.flags.in_import = True
    frappe.flags.in_shopify_api = True

    customers = frappe.get_all(
        "Customer",
        fields=["name", "customer_name"],
        start=start,
        page_length=limit
    )

    if not customers:
        print("No customers found for this batch.")
        return

    for c in customers:

        patient_name = frappe.db.get_value("Patient", {"customer": c.name}, "name")

        # ---------------- GET CONTACT ----------------
        mobile = None
        email = None

        contact = frappe.db.get_value(
            "Dynamic Link",
            {
                "link_doctype": "Customer",
                "link_name": c.name,
                "parenttype": "Contact"
            },
            "parent"
        )

        if contact:
            mobile = frappe.db.get_value("Contact", contact, "mobile_no")
            email = frappe.db.get_value("Contact", contact, "email_id")

        if not mobile:
            print("Skipping", c.name, "(no mobile in Contact)")
            continue

         # ---------------- CREATE PATIENT ----------------
        if not patient_name:

            first = (c.customer_name or "").split(" ")[0] or "Unknown"

            patient = frappe.new_doc("Patient")
            patient.patient_name = c.customer_name
            patient.first_name = first
            patient.customer = c.name
            patient.mobile = mobile
            patient.email = email
            patient.sex = "Unknown"
            patient.sr_medical_department = "General"

            patient.insert(ignore_permissions=True)

            patient_name = patient.name

            print("Created Patient:", patient_name)

        # ---------------- LINK CONTACT ----------------
        contacts = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": c.name,
                "parenttype": "Contact"
            },
            pluck="parent"
        )

        for contact in contacts:

            contact_doc = frappe.get_doc("Contact", contact)

            if not any(
                l.link_doctype == "Patient" and l.link_name == patient_name
                for l in contact_doc.links
            ):

                contact_doc.append("links", {
                    "link_doctype": "Patient",
                    "link_name": patient_name
                })

                contact_doc.save(ignore_permissions=True)

        # ---------------- LINK ADDRESS ----------------
        addresses = frappe.get_all(
            "Dynamic Link",
            filters={
                "link_doctype": "Customer",
                "link_name": c.name,
                "parenttype": "Address"
            },
            pluck="parent"
        )

        for addr in addresses:

            addr_doc = frappe.get_doc("Address", addr)

            if not any(
                l.link_doctype == "Patient" and l.link_name == patient_name
                for l in addr_doc.links
            ):

                addr_doc.append("links", {
                    "link_doctype": "Patient",
                    "link_name": patient_name
                })

                addr_doc.save(ignore_permissions=True)

    frappe.db.commit()

    print("\nBatch completed successfully.")