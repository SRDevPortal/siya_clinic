import frappe
from frappe.utils.data import cint


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def master_query(doctype, txt, searchfield, start, page_len, filters):

    filters = filters or {}

    meta = frappe.get_meta(doctype)

    # dynamic display field
    field = filters.pop("field", meta.title_field or "name")

    # ensure field exists in doctype
    if field not in [d.fieldname for d in meta.fields] and field != "name":
        field = "name"

    # sort order validation
    order = filters.pop("order", "asc").lower()
    if order not in ("asc", "desc"):
        order = "asc"

    conditions = ["is_active = 1", f"{field} LIKE %(txt)s"]

    values = {
        "txt": f"%{txt}%",
        "start": cint(start),
        "page_len": cint(page_len)
    }

    # apply dynamic filters
    for key, val in filters.items():
        conditions.append(f"{key} = %({key})s")
        values[key] = val

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT name, {field}
        FROM `tab{doctype}`
        WHERE {where_clause}
        ORDER BY {field} {order}
        LIMIT %(start)s, %(page_len)s
    """

    return frappe.db.sql(query, values)