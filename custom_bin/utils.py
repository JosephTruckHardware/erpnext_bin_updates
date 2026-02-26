import frappe
import json
import requests


@frappe.whitelist()
def parse_json_string(json_string):
    """
    Parse a JSON string and return the parsed object.
    
    Args:
        json_string (str): A valid JSON string
        
    Returns:
        dict/list: Parsed JSON object
        
    Raises:
        frappe.ValidationError: If the string is not valid JSON
    """
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        frappe.throw(f"Invalid JSON string: {str(e)}", frappe.ValidationError)


@frappe.whitelist()
def enqueue_webhook(webhook_name, doc_name, doctype=None, event=None):
    """
    Enqueue a webhook to be triggered asynchronously.
    
    Args:
        webhook_name (str): Name of the webhook to trigger
        doc_name (str): Name of the document
        doctype (str, optional): DocType of the document. Defaults to None.
        event (str, optional): Event that triggered the webhook. Defaults to None.
        
    Returns:
        dict: Status message
    """
    try:
        frappe.enqueue(
            "frappe.integrations.doctype.webhook.webhook.enqueue_webhook",
            webhook=webhook_name,
            doc=frappe.get_doc(doctype, doc_name) if doctype else None,
            now=frappe.flags.in_test
        )
        return {
            "status": "success",
            "message": f"Webhook {webhook_name} enqueued successfully"
        }
    except Exception as e:
        frappe.log_error(title="Webhook Enqueue Error", message=str(e))
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def trigger_webhook_for_doc(doctype, doc_name, webhook_name=None):
    """
    Trigger webhook(s) for a specific document.
    
    Args:
        doctype (str): DocType of the document
        doc_name (str): Name of the document
        webhook_name (str, optional): Specific webhook to trigger. If None, triggers all matching webhooks.
        
    Returns:
        dict: Status message with webhook details
    """
    try:
        doc = frappe.get_doc(doctype, doc_name)
        
        if webhook_name:
            # Trigger specific webhook
            frappe.enqueue(
                "frappe.integrations.doctype.webhook.webhook.enqueue_webhook",
                webhook=webhook_name,
                doc=doc,
                now=frappe.flags.in_test
            )
            return {
                "status": "success",
                "message": f"Webhook {webhook_name} triggered for {doctype} {doc_name}"
            }
        else:
            # Trigger all webhooks for this doctype
            doc.run_method("on_update")
            return {
                "status": "success",
                "message": f"All webhooks triggered for {doctype} {doc_name}"
            }
            
    except Exception as e:
        frappe.log_error(title="Webhook Trigger Error", message=str(e))
        return {
            "status": "error",
            "message": str(e)
        }


@frappe.whitelist()
def send_json_string(json_string, url=None, webhook_name=None):
    """
    Convert a string to JSON and send it via webhook or URL.
    
    Args:
        json_string (str): String to convert to JSON
        url (str, optional): Direct URL to send the JSON to
        webhook_name (str, optional): Name of Frappe Webhook to use
        
    Returns:
        dict: Response with status and message
    """
    try:
        # Parse the string to JSON
        json_data = json.loads(json_string)
        
        if url:
            # Send directly to URL
            response = requests.post(
                url,
                json=json_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            return {
                "status": "success",
                "message": "JSON sent successfully",
                "response_code": response.status_code,
                "data": json_data
            }
        elif webhook_name:
            # Use Frappe webhook
            webhook = frappe.get_doc("Webhook", webhook_name)
            frappe.enqueue(
                method="frappe.integrations.doctype.webhook.webhook.enqueue_webhook",
                webhook=webhook_name,
                data=json_data,
                now=frappe.flags.in_test
            )
            return {
                "status": "success",
                "message": f"JSON enqueued to webhook: {webhook_name}",
                "data": json_data
            }
        else:
            # Just return parsed JSON
            return {
                "status": "success",
                "message": "JSON parsed successfully",
                "data": json_data
            }
            
    except json.JSONDecodeError as e:
        frappe.throw(f"Invalid JSON string: {str(e)}")
    except Exception as e:
        frappe.log_error(title="Send JSON Error", message=str(e))
        frappe.throw(f"Error sending JSON: {str(e)}")


@frappe.whitelist()
def parse_and_send_to_webhook(json_string, webhook_name):
    """
    Simple function to parse JSON string and trigger a webhook.
    
    Args:
        json_string (str): String to convert to JSON
        webhook_name (str): Name of the webhook to trigger
        
    Returns:
        dict: Status message
    """
    try:
        data = json.loads(json_string)
        
        frappe.enqueue(
            method="frappe.integrations.doctype.webhook.webhook.enqueue_webhook",
            webhook=webhook_name,
            data=data,
            now=frappe.flags.in_test
        )
        
        return {
            "status": "success",
            "message": f"Data sent to webhook: {webhook_name}",
            "parsed_data": data
        }
    except json.JSONDecodeError as e:
        frappe.throw(f"Invalid JSON: {str(e)}")
    except Exception as e:
        frappe.log_error(title="Webhook Send Error", message=str(e))
        frappe.throw(str(e))