import frappe

def trigger_bin_webhook(doc, method):
    """Trigger webhooks for the Bin affected by this Stock Ledger Entry"""
    
    # Get the bin
    bin_name = frappe.db.get_value("Bin", {
        "item_code": doc.item_code,
        "warehouse": doc.warehouse
    })
    
    if bin_name:
        # Get the bin document and trigger webhooks
        bin_doc = frappe.get_doc("Bin", bin_name)
        
        # This triggers all enabled webhooks for Bin
        bin_doc.run_method("on_update")