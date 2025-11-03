import frappe
import requests  # We'll use requests instead of frappe.make_get_request for simplicity

CONSUMER_KEY = "ck_71c8e56a59e12514f4693991b7a1bdcd12896f98"
CONSUMER_SECRET = "cs_0b275e50ad83b68588f7391ca66089e078bac2c6"
BASE_URL = "https://www.wildernessvans.com/wp-json/wc/v3"


@frappe.whitelist(allow_guest=True)
def update_product_stock(**kwargs):
    """
    Webhook endpoint to update WooCommerce stock by SKU.
    Expects JSON payload: {"item_code": "SKU123", "warehouse": "Stores - WV"}
    """
    try:
        sku = kwargs.get("item_code")
        warehouse = kwargs.get("warehouse")

        if not sku or not warehouse:
            frappe.throw("Missing item_code or warehouse in webhook payload.")

        # Get current stock level from ERPNext
        stock_level = get_stock_level(sku, warehouse)
        
        if stock_level is None:
            return {"status": "error", "message": f"Could not fetch stock level for {sku} in {warehouse}"}

        product_url = get_item_url(sku)
        if not product_url:
            return {"status": "error", "message": f"Product with SKU {sku} not found"}

        update_stock_level(product_url, stock_level)
        return {"status": "success", "sku": sku, "warehouse": warehouse, "stock_level": stock_level}

    except Exception as e:
        frappe.log_error(title="WooCommerce Webhook Error", message=str(e))
        return {"status": "error", "message": str(e)}


def get_stock_level(item_code, warehouse):
    """Fetch current stock level from ERPNext Bin"""
    try:
        bin_data = frappe.db.get_value(
            "Bin",
            {"item_code": item_code, "warehouse": warehouse},
            ["actual_qty"],
            as_dict=True
        )
        
        if bin_data:
            return int(bin_data.actual_qty)
        else:
            frappe.log_error(
                title="Stock Fetch Error", 
                message=f"No bin found for item {item_code} in warehouse {warehouse}"
            )
            return 0  # Return 0 if no bin exists
            
    except Exception as e:
        frappe.log_error(title="Stock Level Fetch Error", message=str(e))
        return None


def get_item_url(sku):
    """Fetch the WooCommerce product or variation URL based on SKU"""
    try:
        url = f"{BASE_URL}/products?sku={sku}&consumer_key={CONSUMER_KEY}&consumer_secret={CONSUMER_SECRET}"
        frappe.log_error(title="WooCommerce Fetch URL", message=url)

        response = requests.get(url).json()
        if response and response[0].get("id"):
            product_id = response[0]["id"]
            if response[0]["type"] == "variation":
                parent_id = response[0]["parent_id"]
                return f"{BASE_URL}/products/{parent_id}/variations/{product_id}"
            else:
                return f"{BASE_URL}/products/{product_id}"
        else:
            return None
    except Exception as e:
        frappe.log_error(title="WooCommerce Fetch Error", message=str(e))
        return None


def update_stock_level(url, stock_level):
    """Update the stock quantity of a WooCommerce product"""
    try:
        payload = {"stock_quantity": stock_level}
        url_with_auth = f"{url}?consumer_key={CONSUMER_KEY}&consumer_secret={CONSUMER_SECRET}"
        frappe.log_error(title="WooCommerce Stock Update", message=f"{url_with_auth} -> {payload}")

        response = requests.post(url_with_auth, json=payload)
        frappe.log_error(title="WooCommerce Stock Response", message=str(response.json()))
        return response.json()
    except Exception as e:
        frappe.log_error(title="WooCommerce Stock Update Error", message=str(e))
        return None
