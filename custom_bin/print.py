import frappe
import requests

@frappe.whitelist()
def print_document(doctype, name, print_format="Standard", printer=None, copies=1, lp_opts=None, url=None, api_token=None):
    if not printer:
        frappe.throw("Printer is required")

    pdf_bytes = frappe.get_print(
        doctype=doctype,
        name=name,
        print_format=print_format,
        as_pdf=True
    )

    response = requests.post(
        url,
        files={"pdf": (f"{name}.pdf", pdf_bytes, "application/pdf")},
        data={
            "printer": printer,
            "copies": str(copies),
            "lp_opts": lp_opts or "{}"
        },
        headers={"X-Api-Token": api_token},
        timeout=30
    )

    if not response.ok:
        frappe.throw(f"Print failed: {response.text}")

    return response.json()