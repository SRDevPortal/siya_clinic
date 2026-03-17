import frappe


# -----------------------------------
# STEP 1: Initialize Existing Records
# -----------------------------------

def init():

    print("\nInitializing existing customer patient flags...\n")

    patients = frappe.get_all("Patient", fields=["customer"])

    count = 0

    for p in patients:
        if p.customer:
            frappe.db.set_value(
                "Customer",
                p.customer,
                "is_patient_created",
                1,
                update_modified=False
            )
            count += 1

    frappe.db.commit()

    print(f"Customers updated: {count}\n")


# -----------------------------------
# STEP 2: Migration
# -----------------------------------

def run(limit=200):

    print(f"\nStarting Customer → Patient migration | limit={limit}\n")

    frappe.flags.in_import = True
    frappe.flags.in_shopify_api = True

    customers = frappe.get_all(
        "Customer",
        filters={"is_patient_created": 0},
        fields=["name", "customer_name"],
        page_length=limit
    )

    if not customers:
        print("No customers left to migrate.")
        return

    for c in customers:

        # ---------------- CHECK EXISTING PATIENT ----------------
        patient_name = frappe.db.get_value(
            "Patient",
            {"customer": c.name},
            "name"
        )

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

        if not mobile or not str(mobile).strip():
            print("Skipping", c.name, "(invalid or empty mobile)")
            continue

        # ---------------- CREATE PATIENT ----------------
        if not patient_name:

            name_parts = (c.customer_name or "").split()

            first = name_parts[0] if name_parts else "Unknown"
            last = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            patient = frappe.new_doc("Patient")

            patient.patient_name = c.customer_name
            patient.first_name = first
            patient.last_name = last
            patient.customer = c.name
            patient.mobile = str(mobile).strip()
            patient.email = email
            patient.sex = "Unknown"
            patient.sr_medical_department = "General"

            try:
                patient.insert(ignore_permissions=True)

                patient_name = patient.name
                print("Created Patient:", patient_name)

            except Exception as e:
                print(f"❌ Failed for {c.name} → {str(e)}")
                continue

        else:
            print("Patient already exists:", patient_name)

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

        for contact_name in contacts:

            contact_doc = frappe.get_doc("Contact", contact_name)

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

        # ---------------- MARK CUSTOMER PROCESSED ----------------
        frappe.db.set_value(
            "Customer",
            c.name,
            "is_patient_created",
            1,
            update_modified=False
        )

    frappe.db.commit()

    print("\nBatch completed successfully.")