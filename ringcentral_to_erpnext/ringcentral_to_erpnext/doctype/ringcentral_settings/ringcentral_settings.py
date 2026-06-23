import requests
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url

RC_TOKEN_URL    = "https://platform.ringcentral.com/restapi/oauth/token"
RC_TOKEN_URL_SB = "https://platform.devtest.ringcentral.com/restapi/oauth/token"
RC_API_BASE     = "https://platform.ringcentral.com"
RC_API_BASE_SB  = "https://platform.devtest.ringcentral.com"


class RingCentralSettings(Document):
    def validate(self):
        if self.enabled and not self.client_id:
            frappe.throw(_("Client ID is required to enable RingCentral integration."))


@frappe.whitelist()
def register_webhook():
    settings = frappe.get_single("RingCentral Settings")

    if not settings.enabled:
        frappe.throw(_("Enable RingCentral integration and save before registering."))
    if not settings.webhook_verify_token:
        frappe.throw(_("Set a Webhook Verify Token and save before registering."))

    token_url = RC_TOKEN_URL_SB if settings.use_sandbox else RC_TOKEN_URL
    api_base  = RC_API_BASE_SB  if settings.use_sandbox else RC_API_BASE

    # Exchange JWT for access token
    try:
        token_resp = requests.post(
            token_url,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion":  settings.get_password("jwt_token"),
            },
            auth=(settings.client_id, settings.get_password("client_secret")),
            timeout=10,
        )
        token_resp.raise_for_status()
    except Exception as e:
        frappe.log_error(f"RC register_webhook token error: {e}", "RC Webhook")
        frappe.throw(_("Could not get RingCentral access token. Check credentials."))

    access_token = token_resp.json()["access_token"]

    webhook_url = (
        f"{get_url()}/api/method/ringcentral_to_erpnext.api.ringcentral.handle_request"
        f"?key={settings.webhook_verify_token}"
    )

    # Create the subscription
    try:
        sub_resp = requests.post(
            f"{api_base}/restapi/v1.0/subscription",
            json={
                "eventFilters": [
                    "/restapi/v1.0/account/~/extension/~/telephony/sessions"
                ],
                "deliveryMode": {
                    "transportType": "WebHook",
                    "address": webhook_url,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        sub_resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        try:
            body = e.response.json() if e.response is not None else str(e)
        except Exception:
            body = e.response.text if e.response is not None else str(e)
        frappe.log_error(f"RC subscription {status}: {body}", "RC Webhook")
        frappe.throw(_(f"RingCentral rejected the subscription ({status}): {body}"))
    except Exception as e:
        frappe.log_error(f"RC subscription error: {e}", "RC Webhook")
        frappe.throw(_("Failed to create webhook subscription. Check Error Log."))

    subscription_id = sub_resp.json().get("id", "")
    frappe.db.set_value("RingCentral Settings", "RingCentral Settings",
                        "webhook_subscription_id", subscription_id)
    frappe.db.commit()
    return subscription_id
