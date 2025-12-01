import frappe

def customer_autoname(doc, method):
    """
    Custom autoname logic for 'Individual' customers.
    Sets both doc.name and doc.custom_spire_id.
    """
    def safe(s, n):
        s = (s or "").strip()
        if not s:
            return ""
        s = "".join(ch for ch in s if ch.isalnum())
        return s[:n].upper()

    # # Only handle Individuals
    # if (doc.customer_type or "").strip().lower() != "individual":
    #     return

    # If custom_spire_id already exists, use it
    if doc.custom_spire_id:
        desired = doc.custom_spire_id
    else:
        fullname = (doc.customer_name or "").strip()
        parts = fullname.split()
        first = parts[0] if parts else ""
        last = parts[-1] if len(parts) > 1 else ""
        city = (doc.custom_city or "").strip()

        if fullname and city:
            base = safe(first, 3) + safe(city, 3)
        elif first and last:
            base = safe(first, 3) + safe(last, 3)
        elif first:
            base = safe(first, 6)
        else:
            base = "CUST" + frappe.generate_hash(length=4).upper()

        # Ensure uniqueness
        candidate = base
        i = 1
        while frappe.db.exists("Customer", candidate) and i <= 9999:
            candidate = f"{base}-{i}"
            i += 1
        desired = candidate

        doc.custom_spire_id = desired
        
    frappe.log_error(f"Generated ID: {desired}", "Customer Autoname")

    # Set the doc name
    doc.name = desired
