# historical_imports/overrides/purchase_invoice.py

import frappe
from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice as ERPPurchaseInvoice

class PurchaseInvoice(ERPPurchaseInvoice):
    def on_submit(self):
        if self.get("custom_historical_import"):
            # Prevent stock update
            self.update_stock = 0

            # # Optionally run base validations but skip posting
            # try:
            #     super(ERPPurchaseInvoice, self).validate()
            # except Exception:
            #     pass

            frappe.msgprint(
                "Historical import: purchase invoice submitted without GL or stock postings.",
                title="Historical Import"
            )
            return

        return super().on_submit()
