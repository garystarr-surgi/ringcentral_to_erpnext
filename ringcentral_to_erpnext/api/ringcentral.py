import json
import re
import requests

import frappe
from frappe import _
from frappe.utils import now_datetime, cstr


RC_TOKEN_URL    = "https://platform.ringcentral.com/restapi/oauth/token"
RC_TOKEN_URL_SB = "https://platform.devtest.ringcentral.com/restapi/oauth/token"


# ── Settings helper ───────────────────────────────────────────────────────────

def _get_settings():
    settings = frappe.get_single("RingCentral Settings")
    if not settings.enabled:
        frappe.throw(_("RingCentral integration is not enabled."))
    return settings


# ── 1. get_token — called by Frappe CRM frontend ─────────────────────────────

@frappe.whitelist()
def get_token():
    settings = _get_settings()

    if not settings.client_id or not settings.get_password("client_secret"):
        frappe.throw(_("RingCentral Client ID and Client Secret must be set."))

    token_url = RC_TOKEN_URL_SB if settings.use_sandbox else RC_TOKEN_URL

    try:
        resp = requests.post(
            token_url,
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion":  settings.get_password("jwt_token"),
            },
            auth=(settings.client_id, settings.get_password("client_secret")),
            timeout=10,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"RingCentral get_token failed: {e}", "RC Token Error")
        frappe.throw(_("Could not retrieve RingCentral token. Check credentials."))

    data = resp.json()
    return {
        "access_token": data.get("access_token"),
        "token_type":   data.get("token_type", "Bearer"),
        "expires_in":   data.get("expires_in", 3600),
        "scope":        data.get("scope", ""),
    }


# ── 2. handle_request — RC webhook endpoint ───────────────────────────────────

@frappe.whitelist(allow_guest=True)
def handle_request(**kwargs):
    # Validation is now handled by the /rc-webhook website page which can
    # set response headers properly. This endpoint only receives POST events.
    validation_token = frappe.request.headers.get("Validation-Token")
    if validation_token:
        frappe.response["http_status_code"] = 200
        frappe.response["message"] = validation_token
        return validation_token

    settings = _get_settings()

    # Verify the shared secret
    key = frappe.form_dict.get("key") or kwargs.get("key")
    if settings.webhook_verify_token and key != settings.webhook_verify_token:
        frappe.response["http_status_code"] = 403
        return "Unauthorized"

    # Parse payload
    try:
        payload = json.loads(frappe.request.data) if frappe.request.data else frappe.form_dict
    except Exception:
        frappe.log_error("RC webhook: bad payload", "RC Webhook")
        frappe.response["http_status_code"] = 400
        return "Bad Request"

    event_type = payload.get("event", "")
    if "telephony/sessions" in event_type:
        _handle_telephony_session(payload)
    else:
        frappe.log_error(f"Unhandled RC event: {event_type}", "RC Webhook")

    frappe.response["http_status_code"] = 200
    return "OK"


# ── 3. Telephony session handler ──────────────────────────────────────────────

def _handle_telephony_session(payload):
    body = payload.get("body", {})
    session_id = body.get("telephonySessionId") or body.get("sessionId")
    if not session_id:
        return

    parties = body.get("parties", [])
    party = next((p for p in parties if p.get("status", {}).get("code") == "Disconnected"), None)
    if not party:
        return

    direction   = party.get("direction", "Outbound")
    from_number = (party.get("from") or {}).get("phoneNumber", "")
    to_number   = (party.get("to")   or {}).get("phoneNumber", "")
    duration    = body.get("duration") or _calc_duration(body)
    start_time  = body.get("creationTime") or now_datetime()
    status      = party.get("status", {}).get("code", "Disconnected")
    recording   = (body.get("recordings") or [{}])[0]
    recording_url = recording.get("contentUri", "")

    extension_id = (party.get("extensionId")
                    or (party.get("to")   or {}).get("extensionId")
                    or (party.get("from") or {}).get("extensionId"))
    agent_user = _resolve_agent_user(extension_id)

    lookup_number = from_number if direction == "Inbound" else to_number
    contact_name, lead_name = _find_crm_record(lookup_number)

    _create_call_log(
        session_id=session_id,
        from_number=from_number,
        to_number=to_number,
        direction=direction,
        duration=int(duration or 0),
        status=_map_status(status),
        start_time=start_time,
        recording_url=recording_url,
        contact_name=contact_name,
        lead_name=lead_name,
        agent_user=agent_user,
    )


def _calc_duration(body):
    try:
        import dateutil.parser
        start = dateutil.parser.parse(body.get("creationTime", ""))
        end   = dateutil.parser.parse(body.get("modifiedTime", ""))
        return int((end - start).total_seconds())
    except Exception:
        return 0


# ── 4. Create CRM Call Log ────────────────────────────────────────────────────

def _create_call_log(session_id, from_number, to_number, direction,
                     duration, status, start_time, recording_url,
                     contact_name, lead_name, agent_user):
    if frappe.db.get_value("CRM Call Log", {"id": session_id}, "name"):
        return

    doc = frappe.get_doc({
        "doctype":       "CRM Call Log",
        "id":            session_id,
        "from":          from_number,
        "to":            to_number,
        "type":          direction,
        "duration":      duration,
        "status":        status,
        "start_time":    start_time,
        "recording_url": recording_url,
        "telephony_provider": "RingCentral",
    })
    if contact_name:
        doc.contact = contact_name
    if lead_name:
        doc.lead = lead_name
    if agent_user:
        doc.agent = agent_user

    doc.insert(ignore_permissions=True)
    frappe.db.commit()


def _map_status(rc_status):
    return {
        "Disconnected":  "Completed",
        "NoAnswer":      "No Answer",
        "Busy":          "Busy",
        "Voicemail":     "Voicemail",
        "Rejected":      "No Answer",
        "Missed":        "No Answer",
        "CallConnected": "Completed",
    }.get(rc_status, "Completed")


# ── 5. Phone / record helpers ─────────────────────────────────────────────────

def _digits(phone):
    return re.sub(r"\D", "", phone or "")[-10:]


def _find_crm_record(phone_number):
    digits = _digits(phone_number)
    if not digits:
        return None, None

    contact = frappe.db.sql("""
        SELECT parent FROM `tabContact Phone`
        WHERE REGEXP_REPLACE(phone, '[^0-9]', '') LIKE %s
        LIMIT 1
    """, ("%" + digits,), as_dict=True)
    if contact:
        return contact[0].parent, None

    lead = frappe.db.sql("""
        SELECT name FROM `tabCRM Lead`
        WHERE REGEXP_REPLACE(mobile_no, '[^0-9]', '') LIKE %s
           OR REGEXP_REPLACE(phone,     '[^0-9]', '') LIKE %s
        LIMIT 1
    """, ("%" + digits, "%" + digits), as_dict=True)
    if lead:
        return None, lead[0].name

    return None, None


def _resolve_agent_user(extension_id):
    if not extension_id:
        return None
    return frappe.db.get_value(
        "RingCentral Agent",
        {"rc_extension_id": cstr(extension_id)},
        "user",
    )


# ── 6. Frontend helpers ───────────────────────────────────────────────────────

@frappe.whitelist()
def get_settings():
    if not frappe.db.exists("DocType", "RingCentral Settings"):
        return {"enabled": False}
    settings = frappe.get_single("RingCentral Settings")
    return {
        "enabled":     settings.enabled,
        "client_id":   settings.client_id,
        "use_sandbox": settings.use_sandbox,
    }


@frappe.whitelist()
def get_agents():
    if not frappe.db.exists("DocType", "RingCentral Agent"):
        return []
    return frappe.get_all(
        "RingCentral Agent",
        fields=["user", "rc_extension_id", "rc_phone_number", "enabled"],
        filters={"enabled": 1},
    )
