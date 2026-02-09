import frappe
from frappe.utils import nowdate
from frappe.utils.data import flt

"""
POST /api/method/siya_clinic.api.create_full_invoice

Creates/rehydrates:
- Customer
- Patient  (auto-fills from customer when patient_* missing OR patient_same_as_customer=1)
- Address  (Dynamic Links to Customer & Patient)
- Contact  (Dynamic Links to Customer & Patient)
- Sales Invoice (auto-applies GST template based on company vs customer state when taxes not passed)
- Payment Entry (optional if paid_amount > 0)

Optional payload flags/fields:
- patient_same_as_customer: 1
- company_state: "Haryana"        # if no Company address linked
- selling_price_list / price_list_currency / plc_conversion_rate
- autocreate_item: 1              # create a simple Service Item if item_code missing/not found
"""

# ------------------------------
# Helpers
# ------------------------------

def _get_json():
    data = frappe.request.get_json(silent=True) or {}
    if not data:
        data = frappe._dict(frappe.local.form_dict)
    return frappe._dict(data)

def _name_parts(full):
    full = (full or "").strip()
    if not full:
        return ("Patient", None)
    parts = full.split()
    first = parts[0]
    last = " ".join(parts[1:]) if len(parts) > 1 else None
    return first, last

def _default_address_title(customer, patient):
    """Pick a human title for Address without requiring it in payload."""
    title = None
    if customer and frappe.db.exists("Customer", customer):
        title = frappe.db.get_value("Customer", customer, "customer_name") or customer
    if not title and patient and frappe.db.exists("Patient", patient):
        title = frappe.db.get_value("Patient", patient, "patient_name") or patient
    return title or "Address"

def _company_has_field(fieldname: str) -> bool:
    return frappe.get_meta("Company").has_field(fieldname)

def _get_company_value(company: str, fieldname: str):
    if _company_has_field(fieldname):
        return frappe.db.get_value("Company", company, fieldname)
    return None

def _resolve_cost_center(company, cc_from_payload=None):
    # prefer payload if valid
    if _valid_cost_center(cc_from_payload, company):
        return cc_from_payload

    # try company defaults (handle schema differences)
    for fname in ("default_cost_center", "cost_center"):
        cc = _get_company_value(company, fname)
        if _valid_cost_center(cc, company):
            return cc

    # fallback: any leaf cost center for this company
    cc = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
    if cc:
        return cc

    frappe.throw(
        f"No leaf Cost Center found for company '{company}'. "
        f"Create one (Accounting → Cost Center) or pass 'cost_center' in items."
    )

def _valid_cost_center(name, company):
    if not name:
        return False
    return bool(frappe.db.exists("Cost Center", {"name": name, "company": company, "is_group": 0}))

def _resolve_income_account(company, acc_from_payload=None):
    # prefer payload if valid for the company
    if _valid_income_account(acc_from_payload, company):
        return acc_from_payload
    # company default income account
    acc = frappe.db.get_value("Company", company, "default_income_account")
    if _valid_income_account(acc, company):
        return acc
    # first leaf income account
    acc = frappe.db.get_value("Account", {"company": company, "root_type": "Income", "is_group": 0}, "name")
    if acc:
        return acc
    frappe.throw(f"No Income account found for company '{company}'. Set a default or pass 'income_account'.")

def _valid_income_account(name, company):
    if not name:
        return False
    return bool(frappe.db.exists("Account", {"name": name, "company": company, "is_group": 0, "root_type": "Income"}))

def _resolve_price_list(payload, currency):
    """Return (selling_price_list, price_list_currency, plc_conversion_rate) with safe defaults."""
    spl = payload.get("selling_price_list")
    if spl and not frappe.db.exists("Price List", spl):
        spl = None

    if not spl:
        default_pl = frappe.db.get_single_value("Selling Settings", "selling_price_list")
        if default_pl and frappe.db.exists("Price List", default_pl):
            spl = default_pl
        elif frappe.db.exists("Price List", "Standard Selling"):
            spl = "Standard Selling"
        else:
            # create a minimal selling price list in the company currency
            pl = frappe.get_doc({
                "doctype": "Price List",
                "price_list_name": "API Selling (INR)" if currency == "INR" else f"API Selling ({currency})",
                "enabled": 1,
                "selling": 1,
                "currency": currency
            }).insert(ignore_permissions=True)
            spl = pl.name

    plc = payload.get("price_list_currency") or frappe.db.get_value("Price List", spl, "currency") or currency
    rate = payload.get("plc_conversion_rate") or (1 if plc == currency else None)
    return spl, plc, rate

def _resolve_company(val):
    # 1) If nothing passed, use default or the only company
    if not val:
        default = frappe.db.get_single_value("Global Defaults", "default_company")
        if default and frappe.db.exists("Company", default):
            return default
        companies = frappe.get_all("Company", pluck="name")
        if len(companies) == 1:
            return companies[0]
        frappe.throw("company is required")

    # 2) Exact name
    if frappe.db.exists("Company", val):
        return val

    # 3) Match by abbreviation (case-insensitive)
    name = frappe.db.get_value("Company", {"abbr": val}, "name")
    if name:
        return name
    name = frappe.db.get_value("Company", {"abbr": ["like", val]}, "name")
    if name:
        return name

    # 4) Case-insensitive name match / prefix match
    name = frappe.db.get_value("Company", {"name": ["like", val]}, "name")
    if name:
        return name
    name = frappe.db.get_value("Company", {"name": ["like", f"{val}%"]}, "name")
    if name:
        return name

    # 5) If there’s only one company, use it
    companies = frappe.get_all("Company", pluck="name")
    if len(companies) == 1:
        return companies[0]

    frappe.throw(f"Company '{val}' not found (neither as name nor abbreviation).")

def _ic_enabled() -> bool:
    try:
        return "india_compliance" in set(frappe.get_installed_apps() or [])
    except Exception:
        return False

def _resolve_hsn_code(it, payload):
    # priority: item -> payload default -> site_config
    code = (it or {}).get("gst_hsn_code") \
        or (payload or {}).get("default_hsn_code") \
        or frappe.conf.get("siya_default_hsn")
    if _ic_enabled() and not code:
        frappe.throw(
            "HSN/SAC Code is required by India Compliance. "
            "Pass items[n].gst_hsn_code or default_hsn_code in payload, "
            "or set 'siya_default_hsn' in site_config.json."
        )
    return code

def _ensure_item(it, company):
    """Return a valid item_code; create a simple Service Item if missing and autocreate_item=1."""
    code = (it.get("item_code") or it.get("item_name") or "").strip()
    if not code:
        frappe.throw("Each item needs item_code or item_name.")
    norm = code.upper().replace(" ", "-")[:140]
    if frappe.db.exists("Item", code) or frappe.db.exists("Item", norm):
        return code if frappe.db.exists("Item", code) else norm

    hsn = _resolve_hsn_code(it, frappe.local.form_dict if hasattr(frappe.local, "form_dict") else None)

    # create minimal Service item
    doc = frappe.get_doc({
        "doctype": "Item",
        "item_code": norm,
        "item_name": it.get("item_name") or norm,
        "item_group": it.get("item_group") or "Ayurvedic",
        "stock_uom": it.get("uom") or "Nos",
        **({"gst_hsn_code": hsn} if hsn else {}),
        "is_stock_item": 0,
        "is_sales_item": 1,
        "disabled": 0
    }).insert(ignore_permissions=True)
    return doc.name

def _resolve_paid_to_account(company, mode_of_payment=None, paid_to=None):
    # explicit account passed?
    if paid_to and frappe.db.exists("Account", {"name": paid_to, "company": company, "is_group": 0}):
        return paid_to

    # try MoP mapping
    if mode_of_payment:
        acc = frappe.db.get_value("Mode of Payment Account",
                                  {"parent": mode_of_payment, "company": company},
                                  "default_account") \
              or frappe.db.get_value("Mode of Payment Account",
                                     {"parent": mode_of_payment, "company": company},
                                     "account")
        if acc and frappe.db.exists("Account", {"name": acc, "company": company, "is_group": 0}):
            return acc

    # fallback: Cash, then Bank
    acc = frappe.db.get_value("Account", {"company": company, "account_type": "Cash", "is_group": 0}, "name")
    if acc: return acc
    acc = frappe.db.get_value("Account", {"company": company, "account_type": "Bank", "is_group": 0}, "name")
    if acc: return acc

    frappe.throw(f"No Cash/Bank account found for company '{company}'. Map a Mode of Payment account or pass 'paid_to'.")

# ---------- Currency helpers ----------
def _safe_rate(from_curr, to_curr, posting_date):
    if not from_curr or not to_curr or from_curr == to_curr:
        return 1
    try:
        return frappe.utils.get_exchange_rate(from_curr, to_curr, posting_date)
    except Exception:
        return 1

# ------------------------------
# Customer
# ------------------------------

def _get_or_create_customer(payload):
    name = None
    email = payload.get("customer_email")
    phone = payload.get("customer_phone")
    cust_name = payload.get("customer_name")

    if email:
        name = frappe.db.get_value("Customer", {"email_id": email})
    if not name and phone:
        name = frappe.db.get_value("Customer", {"mobile_no": phone})
    if not name and cust_name:
        name = frappe.db.get_value("Customer", {"customer_name": cust_name})

    if name:
        return name

    doc = frappe.get_doc({
        "doctype": "Customer",
        "customer_name": cust_name or (email or phone),
        "customer_group": payload.get("customer_group") or "All Customer Groups",
        "territory": payload.get("territory") or "All Territories",
        "email_id": email,
        "mobile_no": phone
    }).insert(ignore_permissions=True)
    return doc.name

# ------------------------------
# Patient  (patient=customer fallback supported)
# ------------------------------

def _get_or_create_patient(payload, customer):
    """Create/reuse Patient. If patient_* not provided (or patient_same_as_customer=1),
    auto-fill from customer_* and populate first/last name when available."""
    same = payload.get("patient_same_as_customer")
    same = 1 if same in (1, "1", True, "true", "True") else 0

    def g(p_key, c_key):
        val = payload.get(p_key)
        return val if val not in (None, "", []) else payload.get(c_key)

    full_name = g("patient_name", "customer_name")
    email = g("patient_email", "customer_email")
    phone = g("patient_phone", "customer_phone")
    sex = payload.get("patient_sex") or "Other"

    first = payload.get("patient_first_name")
    last = payload.get("patient_last_name")
    if same or not (first or last):
        f2, l2 = _name_parts(full_name or email or phone or "Patient")
        first = first or f2
        if not last and l2:
            last = l2

    # find existing
    patient = None
    if phone:
        patient = frappe.db.get_value("Patient", {"mobile": phone})
    if not patient and email:
        patient = frappe.db.get_value("Patient", {"email": email})
    if not patient and full_name:
        patient = frappe.db.get_value("Patient", {"patient_name": full_name})

    meta = frappe.get_meta("Patient")
    has_first = meta.has_field("first_name")
    has_last = meta.has_field("last_name")

    if patient:
        pdoc = frappe.get_doc("Patient", patient)
        updated = False
        if has_first and not pdoc.get("first_name") and first:
            pdoc.first_name = first; updated = True
        if has_last and not pdoc.get("last_name") and last:
            pdoc.last_name = last; updated = True
        if not pdoc.get("customer") and customer:
            pdoc.customer = customer; updated = True
        if email and not pdoc.get("email"):
            pdoc.email = email; updated = True
        if phone and not pdoc.get("mobile"):
            pdoc.mobile = phone; updated = True
        if updated:
            pdoc.save(ignore_permissions=True)
        return pdoc.name

    data = {
        "doctype": "Patient",
        "patient_name": full_name or first,
        "sex": sex,
        "mobile": phone,
        "email": email,
        "customer": customer
    }
    if has_first:
        data["first_name"] = first
    if has_last:
        data["last_name"] = last

    pdoc = frappe.get_doc(data).insert(ignore_permissions=True)
    return pdoc.name

# ------------------------------
# Address & Contact (Dynamic Links to both)
# ------------------------------

def _make_dynamic_links(link_doctypes):
    return [{"link_doctype": d["link_doctype"], "link_name": d["link_name"]}
            for d in link_doctypes if d.get("link_name")]

def _create_or_update_address(payload, customer, patient):
    # Always compute a title if not provided
    addr_type = (payload.get("address_type") or "Billing").strip()
    pincode = payload.get("pincode")
    title = payload.get("address_title") or _default_address_title(customer, patient)

    # Find existing by (title, type, pincode) when possible
    filters = {"address_title": title, "address_type": addr_type}
    if pincode:
        filters["pincode"] = pincode

    existing = frappe.get_all("Address", filters=filters, pluck="name")

    links = _make_dynamic_links([
        {"link_doctype": "Customer", "link_name": customer},
        {"link_doctype": "Patient", "link_name": patient},
    ])

    if existing:
        ad = frappe.get_doc("Address", existing[0])
        for k in ["address_line1", "address_line2", "city", "state", "pincode", "country", "phone"]:
            if payload.get(k):
                setattr(ad, k, payload.get(k))
        ad.address_type = addr_type
        ad.links = []
        for l in links:
            ad.append("links", l)
        ad.save(ignore_permissions=True)
        return ad.name

    ad = frappe.get_doc({
        "doctype": "Address",
        "address_title": title,                 # <- auto defaulted
        "address_type": addr_type,
        "address_line1": payload.get("address_line1"),
        "address_line2": payload.get("address_line2"),
        "city": payload.get("city"),
        "state": payload.get("state"),
        "pincode": pincode,
        "country": payload.get("country") or "India",
        "phone": payload.get("customer_phone") or payload.get("contact_phone"),
        "is_primary_address": 1,
        "links": links
    }).insert(ignore_permissions=True)
    return ad.name

def _create_or_update_contact(payload, customer, patient):
    email = payload.get("contact_email") or payload.get("customer_email")
    phone = payload.get("contact_phone") or payload.get("customer_phone")
    # derive a first name from customer_name if contact_first_name absent
    fallback_name = payload.get("contact_first_name") or payload.get("customer_name") or "Customer"
    first_name, last_guess = _name_parts(fallback_name)
    first_name = payload.get("contact_first_name") or first_name
    last_name = payload.get("contact_last_name") or last_guess

    c = None
    if email:
        c = frappe.db.get_value("Contact", {"email_id": email})
    if not c and phone:
        c = frappe.db.get_value("Contact", {"mobile_no": phone})

    links = _make_dynamic_links([
        {"link_doctype": "Customer", "link_name": customer},
        {"link_doctype": "Patient", "link_name": patient},
    ])

    if c:
        cd = frappe.get_doc("Contact", c)
        if first_name: cd.first_name = first_name
        if last_name: cd.last_name = last_name
        if email: cd.email_id = email
        if phone: cd.mobile_no = phone
        cd.links = []
        for l in links:
            cd.append("links", l)
        cd.save(ignore_permissions=True)
        return cd.name

    cd = frappe.get_doc({
        "doctype": "Contact",
        "first_name": first_name,
        "last_name": last_name,
        "email_id": email,
        "mobile_no": phone,
        "links": links
    }).insert(ignore_permissions=True)
    return cd.name

# ------------------------------
# Sales Invoice (GST auto-pick + robust price list)
# ------------------------------

def _create_sales_invoice(payload, customer, patient):
    company = _resolve_company(payload.get("company"))
    company_currency = frappe.db.get_value("Company", company, "default_currency") or "INR"
    posting_date = payload.get("posting_date") or nowdate()
    currency = payload.get("currency") or company_currency
    due_date = payload.get("due_date") or posting_date

    items = payload.get("items") or []
    if not items:
        frappe.throw("At least one item is required")

    # ---- Company/Customer state to decide GST template ----
    company_state = payload.get("company_state")
    if not company_state:
        dl = frappe.get_all(
            "Dynamic Link",
            filters={"link_doctype": "Company", "link_name": company, "parenttype": "Address"},
            fields=["parent"], limit=1
        )
        if dl:
            company_state = frappe.db.get_value("Address", dl[0].parent, "state")

    customer_state = payload.get("state")
    if not customer_state:
        dl2 = frappe.get_all(
            "Dynamic Link",
            filters={"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
            fields=["parent"], limit=1
        )
        if dl2:
            customer_state = frappe.db.get_value("Address", dl2[0].parent, "state")

    taxes = payload.get("taxes")
    if not taxes:
        if company_state and customer_state:
            template_name = "Output GST In-state" if company_state.strip().lower() == customer_state.strip().lower() else "Output GST Out-state"
            taxes = frappe.get_all(
                "Sales Taxes and Charges",
                filters={"parent": template_name},
                fields=["charge_type", "account_head", "rate", "description", "included_in_print_rate"],
                order_by="idx asc",
            )
        else:
            taxes = []

    # If Shopify said prices include tax, force inclusivity
    if payload.get("taxes_included") in (1, "1", True, "true", "True"):
        for t in taxes:
            t["included_in_print_rate"] = 1

    # ---- Price List defaults / rates ----
    selling_price_list, price_list_currency, plc_conversion_rate = _resolve_price_list(payload, currency)

    if not plc_conversion_rate:
        if (price_list_currency or currency) == currency:
            plc_conversion_rate = 1
        else:
            try:
                plc_conversion_rate = frappe.utils.get_exchange_rate(price_list_currency, currency, posting_date)
            except Exception:
                plc_conversion_rate = 1

    conversion_rate = payload.get("conversion_rate")
    if not conversion_rate:
        if currency == company_currency:
            conversion_rate = 1
        else:
            try:
                conversion_rate = frappe.utils.get_exchange_rate(currency, company_currency, posting_date)
            except Exception:
                conversion_rate = 1

    # ---- Build Items (keep Rate = MRP; discount via percentage) ----
    autocreate = payload.get("autocreate_item") in (1, "1", True, "true", "True")
    has_disc_amount_field = frappe.get_meta("Sales Invoice Item").has_field("discount_amount")

    si_items = []
    for it in items:
        code = (it.get("item_code") or it.get("item_name"))
        if autocreate:
            code = _ensure_item(it, company)
        elif not code:
            frappe.throw("Each item needs item_code or item_name.")

        qty  = flt(it.get("qty") or 1)
        gross_rate = flt(it.get("rate") or 0)   # Shopify line price
        disc_pct = it.get("discount_percentage")
        disc_amt = flt(it.get("discount_amount") or 0)

        # If only fixed discount is given, convert to %
        if disc_amt and not disc_pct:
            per_unit_disc = disc_amt / qty
            disc_pct = (per_unit_disc / gross_rate * 100) if gross_rate else 0
        disc_pct = max(0, min(100, flt(disc_pct or 0)))

        cc  = _resolve_cost_center(company, it.get("cost_center"))
        inc = _resolve_income_account(company, it.get("income_account"))

        row = {
            "item_code": code,
            "item_name": it.get("item_name") or it.get("item_code"),
            "qty": qty,
            "uom": it.get("uom") or "Nos",
            # IMPORTANT: give only list rate + discount; DO NOT set "rate"
            "price_list_rate": gross_rate,
            "discount_percentage": disc_pct,
            "income_account": inc,
            "cost_center": cc,
            "gst_hsn_code": it.get("gst_hsn_code"),
        }
        if has_disc_amount_field:
            row["discount_amount"] = disc_amt  # so you can show this column in print
        si_items.append(row)

    # ---- Sales Invoice doc ----
    si_data = {
        "doctype": "Sales Invoice",
        "company": company,
        "currency": currency,
        "posting_date": posting_date,
        "due_date": due_date,
        "customer": customer,
        "debit_to": "Debtors - EEPL",
        "items": si_items,
        "taxes": taxes,
        "ignore_pricing_rule": 1,   # avoid rules changing your MRP+discount rows
    }

    # safety defaults
    si_data["selling_price_list"]  = selling_price_list or "Standard Selling"
    si_data["price_list_currency"] = price_list_currency or currency
    si_data["plc_conversion_rate"] = plc_conversion_rate or 1
    si_data["conversion_rate"]     = conversion_rate or 1

    # after building si_data and before frappe.get_doc(...)
    if str(payload.get("disable_rounded_total", 0)).lower() in ("1", "true"):
        si_data["disable_rounded_total"] = 1

    # Avoid double-discount: only apply invoice-level if NO item has discount
    if payload.get("discount_amount"):
        any_row_discount = any(
            flt(it.get("discount_amount") or 0) > 0 or flt(it.get("discount_percentage") or 0) > 0
            for it in items
        )
        if not any_row_discount:
            si_data["apply_discount_on"] = payload.get("apply_discount_on") or "Net Total"
            si_data["discount_amount"] = float(payload["discount_amount"])

    # patient field if present
    if frappe.get_meta("Sales Invoice").has_field("patient") and patient:
        si_data["patient"] = patient

    # ---- write custom "Others" fields from payload (safe & optional) ----
    si_meta = frappe.get_meta("Sales Invoice")

    def _add_custom(fieldname, value):
        """Set si_data[fieldname] only if the field exists and value is non-empty."""
        if si_meta.has_field(fieldname) and value not in (None, "", []):
            si_data[fieldname] = value

    # Normalize order_source to your allowed options
    _src_raw = (payload.get("order_source") or "").strip().lower()
    _src_map = {
        "shopify":  "Shopify",
        "amazon":   "Amazon",
        "flipkart": "Flipkart",
        "direct":   "Direct",
        "other":    "Other",
    }
    _src_val = _src_map.get(_src_raw) or (payload.get("order_source") or "Other")

    # Large numeric IDs (e.g., Shopify) can exceed INT range in MariaDB.
    # Store as string when very large; otherwise keep original.
    def _safe_id(val):
        try:
            n = int(val)
            return str(n) if n > 2147483647 else n
        except Exception:
            return val  # already string/None

    _add_custom("shopify_order_id",     _safe_id(payload.get("shopify_order_id")))
    _add_custom("shopify_order_number", _safe_id(payload.get("shopify_order_number")))
    _add_custom("buopso_order_id",      _safe_id(payload.get("buopso_order_id")))
    _add_custom("order_source",         _src_val)

    # frappe.log_error(title="SIYA DEBUG: SI data", message=frappe.as_json(si_data))

    si = frappe.get_doc(si_data)
    si.flags.ignore_permissions = True
    si.set_missing_values()
    si.calculate_taxes_and_totals()
    si.insert()
    if payload.get("submit_invoice", 1):
        si.submit()
    return si.name

# ------------------------------
# Payment Entry (optional)
# ------------------------------

def _create_payment_entry(payload, customer, sales_invoice):
    paid_company_currency = float(payload.get("paid_amount") or 0)
    if paid_company_currency <= 0:
        return None

    company = _resolve_company(payload.get("company"))
    mode_of_payment = payload.get("mode_of_payment") or "Cash"
    posting_date = payload.get("payment_posting_date") or nowdate()

    # amounts
    outstanding = float(frappe.db.get_value("Sales Invoice", sales_invoice, "outstanding_amount") or 0.0)
    company_amount = min(paid_company_currency, outstanding)

    # party (receivable) account: take from the Sales Invoice itself
    party_account = frappe.db.get_value("Sales Invoice", sales_invoice, "debit_to")
    if not party_account:
        # last-resort: any Receivable leaf account in this company
        party_account = frappe.db.get_value("Account", {"company": company, "account_type": "Receivable", "is_group": 0}, "name")
    if not party_account:
        frappe.throw(f"No receivable account found for company '{company}'. Set one on Company/Customer or pass 'debit_to' in SI.")

    # currencies
    company_currency = frappe.db.get_value("Company", company, "default_currency") or "INR"
    from_curr = frappe.db.get_value("Account", party_account, "account_currency") or company_currency

    paid_to_acc = _resolve_paid_to_account(company, mode_of_payment, payload.get("paid_to"))
    to_curr = frappe.db.get_value("Account", paid_to_acc, "account_currency") or company_currency

    # exchange rates
    source_rate = float(payload.get("source_exchange_rate") or _safe_rate(from_curr, company_currency, posting_date))
    target_rate = float(payload.get("target_exchange_rate") or _safe_rate(to_curr, company_currency, posting_date))

    # amounts in account currencies mapping to same base (company) amount
    paid_amount = company_amount if from_curr == company_currency else (company_amount / (source_rate or 1))
    received_amount = company_amount if to_curr == company_currency else (company_amount / (target_rate or 1))

    pe = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Receive",
        "company": company,
        "mode_of_payment": mode_of_payment,
        "party_type": "Customer",
        "party": customer,

        "paid_from": party_account,
        "paid_to": paid_to_acc,

        "paid_from_account_currency": from_curr,
        "paid_to_account_currency": to_curr,
        "source_exchange_rate": source_rate,
        "target_exchange_rate": target_rate,

        "paid_amount": paid_amount,
        "received_amount": received_amount,
        "posting_date": posting_date,

        "references": [{
            "reference_doctype": "Sales Invoice",
            "reference_name": sales_invoice,
            "allocated_amount": company_amount
        }]
    })
    pe.flags.ignore_permissions = True
    pe.insert()
    if payload.get("submit_payment", 1):
        pe.submit()
    return pe.name

# ------------------------------
# Public API
# ------------------------------

@frappe.whitelist(allow_guest=False, methods=["POST"])
def create_full_invoice():
    """
    Creates/links Patient, Customer, Address, Contact -> Sales Invoice -> Payment Entry.
    Uses patient_same_as_customer=1 to auto-fill patient fields.
    Auto-applies GST taxes when not provided and both states are known.
    Handles price list currency safely to avoid INR->None exchange rate errors.
    """
    payload = _get_json()
    res = {}
    try:
        frappe.db.savepoint("start_create_full_invoice")

        customer = _get_or_create_customer(payload)
        patient = _get_or_create_patient(payload, customer)
        address = _create_or_update_address(payload, customer, patient)
        contact = _create_or_update_contact(payload, customer, patient)
        si = _create_sales_invoice(payload, customer, patient)
        pe = _create_payment_entry(payload, customer, si)

        res = {
            "customer": customer,
            "patient": patient,
            "address": address,
            "contact": contact,
            "sales_invoice": si,
            "payment_entry": pe
        }
        frappe.db.commit()
    except Exception:
        frappe.db.rollback(save_point="start_create_full_invoice")
        frappe.log_error(title="create_full_invoice failed", message=frappe.get_traceback())
        frappe.throw("Failed to create documents. See Error Log.")

    return res
