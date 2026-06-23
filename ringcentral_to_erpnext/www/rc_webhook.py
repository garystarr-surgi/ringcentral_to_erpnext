import json
import frappe

no_cache = 1


def get_context(context):
    method = frappe.request.method.upper()

    if method == "GET":
        _do_validation(context)
    elif method == "POST":
        _do_event(context)
    else:
        frappe.local.response["http_status_code"] = 405
        context.body = "Method Not Allowed"


def _do_validation(context):
    token = frappe.request.headers.get("Validation-Token")
    if not token:
        frappe.local.response["http_status_code"] = 400
        context.body = "Missing Validation-Token"
        return

    # Frappe's website pipeline (website/serve.py) reads
    # frappe.local.response["headers"] and copies them into the actual
    # HTTP response — unlike the API pipeline which ignores this key.
    frappe.local.response["http_status_code"] = 200
    frappe.local.response["headers"] = {"Validation-Token": token}
    context.body = token


def _do_event(context):
    key = frappe.request.args.get("key") or frappe.form_dict.get("key")

    try:
        settings = frappe.get_single("RingCentral Settings")
    except Exception:
        frappe.local.response["http_status_code"] = 503
        context.body = "Service unavailable"
        return

    if settings.webhook_verify_token and key != settings.webhook_verify_token:
        frappe.local.response["http_status_code"] = 403
        context.body = "Unauthorized"
        return

    try:
        payload = json.loads(frappe.request.data) if frappe.request.data else {}
    except Exception:
        frappe.local.response["http_status_code"] = 400
        context.body = "Bad Request"
        return

    event_type = payload.get("event", "")
    if "telephony/sessions" in event_type:
        try:
            from ringcentral_to_erpnext.api.ringcentral import _handle_telephony_session
            _handle_telephony_session(payload)
        except Exception as e:
            frappe.log_error(f"RC event error: {e}", "RC Webhook")

    frappe.local.response["http_status_code"] = 200
    context.body = "OK"
