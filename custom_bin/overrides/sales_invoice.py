import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice as ERPSalesInvoice

class SalesInvoice(ERPSalesInvoice):
    def on_submit(self):
        """
        If this invoice was flagged as a historical import, skip the
        GL and stock posting logic by returning early.
        Otherwise continue normal submit flow.
        """
        if self.get("custom_historical_import"):
            # Ensure stock won't be updated
            self.update_stock = 0

            # # Optional: run any validations you still want (call parent's validate)
            # try:
            #     super(ERPSalesInvoice, self).validate()
            # except Exception:
            #     # If validate fails and you want to ignore some validations, handle here.
            #     pass

            # Skip the rest of on_submit which creates GL / stock entries.
            frappe.msgprint(
                "Historical import: submit completed without GL or stock postings.",
                title="Historical Import"
            )
            return

        # Normal behavior for non-historical invoices
        return super().on_submit()
