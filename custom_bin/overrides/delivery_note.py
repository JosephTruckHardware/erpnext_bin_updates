# historical_imports/overrides/delivery_note.py
import frappe
from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote as ERPDeliveryNote

class DeliveryNote(ERPDeliveryNote):
    def on_submit(self):
        if self.get("custom_historical_import"):
            # prevent stock ledger / reservations being applied
            # self.skip_delivery_note_make_gl_entries = True
            # ensure update_stock is false just in case
            self.update_stock = 0

            # # optionally run simple validations if you want
            # try:
            #     super(ERPDeliveryNote, self).validate()
            # except Exception:
            #     pass

            frappe.msgprint("Historical import: Delivery Note submitted without stock/GL postings.")
            return

        return super().on_submit()
