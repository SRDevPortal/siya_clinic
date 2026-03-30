import frappe

def auto_set_order_channel(doc, method):

    if doc.order_source and not doc.order_channel:

        channels = frappe.get_all(
            "SR Order Channel",
            filters={
                "order_source": doc.order_source,
                "is_active": 1
            },
            fields=["name"],
            limit=2
        )

        if len(channels) == 1:
            doc.order_channel = channels[0].name