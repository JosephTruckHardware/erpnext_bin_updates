from frappe.utils import flt, now

def update_bin_qty(item_code, warehouse, qty_dict=None):
    from erpnext.stock.utils import get_bin

    bin = get_bin(item_code, warehouse)
    mismatch = False
    for field, value in qty_dict.items():
        if flt(bin.get(field)) != flt(value):
            bin.set(field, flt(value))
            mismatch = True

    if mismatch:
        bin.modified = now()
        bin.set_projected_qty()
        # Persist without running full save (avoids the "modified" race)
        bin.db_update()
        # Trigger webhooks / realtime listeners for this doc
        bin.notify_update()
        bin.clear_cache()