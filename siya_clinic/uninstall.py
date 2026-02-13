# siya_clinic/uninstall.py
import frappe
import logging

logger = logging.getLogger(__name__)

APP = "siya_clinic"
MODULE = "Siya Clinic"

# Customizations & fixtures installed by this app
CUSTOMIZATION_DT_LIST = [
    "Custom Field",
    "Property Setter",
    "Client Script",
    "Server Script",
    "Workspace",
    "Workspace Link",
    "Print Format",
    "Report",
    "Dashboard Chart",
    "Notification",
    "Web Template",
    "Form Tour",
    "Form Tour Step",
    "Custom DocPerm",
]

# ---------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------

def _delete_all(dt, filters=None):
    """Delete documents safely, only applying filters if fields exist."""
    if not frappe.db.exists("DocType", dt):
        return

    filters = filters or {}

    # Remove invalid filters (e.g., module column missing)
    meta = frappe.get_meta(dt)
    valid_filters = {}

    for key, value in filters.items():
        if key in meta.get_valid_columns():
            valid_filters[key] = value

    names = frappe.get_all(dt, pluck="name", filters=valid_filters)

    for name in names:
        try:
            frappe.delete_doc(
                dt,
                name,
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
        except Exception:
            # fallback: disable if possible
            if frappe.db.has_column(dt, "disabled"):
                frappe.db.set_value(dt, name, "disabled", 1)


def _delete_custom_fields_by_app():
    """Some Custom Fields may not have module set."""
    meta = frappe.get_meta("Custom Field")
    if "app" in meta.get_valid_columns():
        _delete_all("Custom Field", {"app": APP})


def _delete_module_doctypes():
    """
    Remove custom DocTypes created under this module.
    Bench uninstall normally removes these, but this is a safety net.
    """
    doctypes = frappe.get_all(
        "DocType",
        fields=["name", "module", "custom"],
        filters={"module": MODULE},
    )

    for dt in doctypes:
        # Only delete custom doctypes
        if not dt.custom:
            continue

        try:
            logger.info(f"Deleting custom DocType: {dt.name}")
            frappe.delete_doc(
                "DocType",
                dt.name,
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
        except Exception as e:
            logger.warning(f"Could not delete DocType {dt.name}: {e}")


def _delete_module_def():
    """Remove module record."""
    if frappe.db.exists("Module Def", MODULE):
        try:
            frappe.delete_doc(
                "Module Def",
                MODULE,
                force=True,
                ignore_permissions=True,
                delete_permanently=True,
            )
        except Exception as e:
            logger.warning(f"Failed to delete Module Def {MODULE}: {e}")


def _clear_global_search():
    """Clear global search entries to avoid ghost results."""
    try:
        frappe.db.sql(
            "DELETE FROM `__global_search` WHERE module=%s",
            (MODULE,),
        )
    except Exception:
        pass


# ---------------------------------------------------------
# Hooks
# ---------------------------------------------------------

def before_uninstall():
    """
    Runs BEFORE schema removal.
    This is the most important cleanup phase.
    """
    logger.info("===== Siya Clinic: Before Uninstall Started =====")

    frappe.clear_cache()

    # 1️⃣ Remove fixtures & customizations
    for dt in CUSTOMIZATION_DT_LIST:
        _delete_all(dt, {"module": MODULE})

    # 2️⃣ Remove custom fields linked by app name
    _delete_custom_fields_by_app()

    # 3️⃣ Remove custom DocTypes
    _delete_module_doctypes()

    # 4️⃣ Clear search index
    _clear_global_search()

    frappe.db.commit()
    logger.info("===== Siya Clinic: Before Uninstall Completed =====")


def after_uninstall():
    """
    Runs AFTER app is removed.
    Final cleanup.
    """
    logger.info("===== Siya Clinic: After Uninstall Started =====")

    _delete_module_def()

    frappe.clear_cache()
    frappe.db.commit()

    logger.info("===== Siya Clinic: After Uninstall Completed =====")
