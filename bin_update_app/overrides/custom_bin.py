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
        # Use save() to trigger webhooks instead of db_update()
        bin.save()
        bin.clear_cache()