import frappe
from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt as ERPPurchaseReceipt

class PurchaseReceipt(ERPPurchaseReceipt):
    def on_submit(self):
        """
        If this purchase receipt was flagged as a historical import, skip
        the stock/GL posting logic by returning early. Otherwise continue normal submit flow.
        """
        if self.get("custom_historical_import"):
            # Prevent stock updates
            self.update_stock = 0

            # # Optionally run base validations but skip posting
            # try:
            #     # You can run a lightweight validation if needed
            #     super(ERPPurchaseReceipt, self).validate()
            # except Exception:
            #     # If validation fails and you want to ignore, handle it here.
            #     pass

            frappe.msgprint("Historical import: Purchase Receipt submitted without stock/GL postings.")
            return

        # Normal behavior for non-historical purchase receipts
        return super().on_submit()