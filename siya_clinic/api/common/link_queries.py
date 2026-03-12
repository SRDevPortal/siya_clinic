import frappe

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def master_query(doctype, txt, searchfield, start, page_len, filters):

    field = filters.get("field", "name")
    order = filters.get("order", "asc")

    return frappe.db.sql(f"""
        SELECT
            name,
            {field}
        FROM `tab{doctype}`
        WHERE
            is_active = 1
            AND {field} LIKE %(txt)s
        ORDER BY {field} {order}
        LIMIT %(start)s, %(page_len)s
    """, {
        "txt": f"%{txt}%",
        "start": start,
        "page_len": page_len
    })