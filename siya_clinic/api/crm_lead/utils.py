# siya_clinic/api/crm_lead/utils.py
# Shared utility functions for CRM Lead

def clean_spaces(value: str | None) -> str | None:
    """
    Remove all whitespace from a string.
    Safe for None and non-string values.
    """
    if not isinstance(value, str):
        return value
    return "".join(value.split())
