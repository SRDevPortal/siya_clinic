# siya_clinic/install.py
import frappe
import logging

from .setup.runner import setup_all
from .setup.utils import MODULE_DEF_NAME, APP_PY_MODULE, ensure_module_def

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------

def _ensure_module():
    """Ensure Module Def exists (safety for partial installs)."""
    ensure_module_def(MODULE_DEF_NAME, APP_PY_MODULE)


def _clear_cache():
    frappe.clear_cache()


# ---------------------------------------------------------
# Lifecycle Hooks
# ---------------------------------------------------------

def before_install():
    """Runs before app installation."""
    logger.info("===== Siya Clinic: Before Install =====")
    _clear_cache()


def after_install():
    """Runs once after app installation."""
    logger.info("===== Siya Clinic: After Install Started =====")

    try:
        _ensure_module()

        # Run full setup
        setup_all()

        _clear_cache()
        frappe.db.commit()

        logger.info("===== Siya Clinic: After Install Completed =====")

    except Exception as e:
        frappe.db.rollback()
        logger.error(f"❌ Siya Clinic install failed: {e}")
        raise


def after_migrate():
    """
    Runs after migrations.
    Must be idempotent.
    """
    logger.info("===== Siya Clinic: After Migrate Started =====")

    try:
        _ensure_module()

        # Re-run setup safely
        setup_all()

        _clear_cache()
        frappe.db.commit()

        logger.info("===== Siya Clinic: After Migrate Completed =====")

    except Exception as e:
        frappe.db.rollback()
        logger.error(f"❌ Siya Clinic migrate setup failed: {e}")
        raise
