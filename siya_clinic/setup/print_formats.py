"""App-owned templates with a separate default selection for each site."""
import logging
from pathlib import Path

import frappe

from .utils import MODULE_DEF_NAME, upsert_property_setter

logger = logging.getLogger(__name__)
LEGACY_FORMAT = "Patient Encounter New"
ENCOUNTER_FORMATS = {
    "Domestic": "Patient Encounter Domestic",
    "International": "Patient Encounter International",
}


def _load(relpath):
    return (Path(frappe.get_app_path("siya_clinic")) / relpath).read_text(encoding="utf-8")


def _validate_region(region):
    if region not in ENCOUNTER_FORMATS:
        frappe.throw("Encounter Print Region must be Domestic or International.")
    return region


def get_encounter_print_region():
    """Read the persisted choice; infer only for sites upgrading without settings."""
    region = frappe.db.get_single_value("Clinic Settings", "encounter_print_region")
    if region:
        return _validate_region(region)

    current_default = frappe.get_meta("Patient Encounter").default_print_format
    for candidate, name in ENCOUNTER_FORMATS.items():
        if current_default == name:
            return candidate

    # Recognize the approved site-only international layout before replacing
    # the legacy format. Never infer region from a hostname or company address.
    existing_html = frappe.db.get_value("Print Format", LEGACY_FORMAT, "html") or ""
    international_html = _load("print_formats/patient_encounter_international.html")
    if existing_html.strip() == international_html.strip():
        return "International"
    return "Domestic"


def get_encounter_print_format():
    """Shared resolver for integrations that explicitly request an encounter PDF."""
    return ENCOUNTER_FORMATS[get_encounter_print_region()]


def _upsert_pf(name, doctype, relpath, **options):
    payload = {
        "doc_type": doctype,
        "module": MODULE_DEF_NAME,
        "custom_format": 1,
        "print_format_type": "Jinja",
        "disabled": 0,
        "standard": "No",
        "html": _load(relpath),
        **options,
    }
    if frappe.db.exists("Print Format", name):
        pf = frappe.get_doc("Print Format", name)
        pf.update(payload)
        pf.save(ignore_permissions=True)
    else:
        frappe.get_doc({"doctype": "Print Format", "name": name, **payload}).insert(ignore_permissions=True)


def _set_encounter_default(name):
    # Do not commit here: saving settings and changing the default must be atomic.
    key = frappe.db.get_value("Property Setter", {
        "doc_type": "Patient Encounter", "doctype_or_field": "DocType",
        "property": "default_print_format",
    }, "name")
    if key:
        setter = frappe.get_doc("Property Setter", key)
    else:
        setter = frappe.new_doc("Property Setter")
    setter.update({
        "doc_type": "Patient Encounter",
        "doctype_or_field": "DocType",
        "field_name": None,
        "property": "default_print_format",
        "property_type": "Data",
        "value": name,
        "module": MODULE_DEF_NAME,
    })
    setter.save(ignore_permissions=True)
    frappe.clear_cache(doctype="Patient Encounter")


def apply_encounter_formats(region=None):
    region = _validate_region(region) if region is not None else get_encounter_print_region()
    for candidate, name in ENCOUNTER_FORMATS.items():
        options = {"margin_top": 15, "margin_bottom": 15, "margin_left": 15, "margin_right": 15,
                   "font_size": 14, "pdf_generator": "wkhtmltopdf"}
        if candidate == "International":
            options.update(margin_top=10, margin_bottom=10, margin_left=12, margin_right=12, font_size=13)
        path = f"print_formats/patient_encounter_{candidate.lower()}.html"
        _upsert_pf(name, "Patient Encounter", path, **options)
        if candidate == region:
            # Compatibility for existing links, integrations, and saved print choices.
            _upsert_pf(LEGACY_FORMAT, "Patient Encounter", path, **options)
    frappe.db.set_single_value("Clinic Settings", "encounter_print_region", region)
    _set_encounter_default(ENCOUNTER_FORMATS[region])


def apply():
    """Called after install/migrate; never reset an existing site selection."""
    apply_encounter_formats()
    _upsert_pf("Purchase Order New", "Purchase Order", "print_formats/purchase_order_new.html")
    upsert_property_setter("Purchase Order", None, "default_print_format", "Purchase Order New", "Data", module=MODULE_DEF_NAME)
    frappe.clear_cache(doctype="Purchase Order")
    logger.info("Applied clinic print formats")
