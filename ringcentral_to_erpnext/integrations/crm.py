import frappe
from frappe import _

from crm.integrations.api import get_user_default_calling_medium


def _is_ringcentral_enabled() -> bool:
	if not frappe.db.exists("DocType", "RingCentral Settings"):
		return False
	return bool(frappe.db.get_single_value("RingCentral Settings", "enabled"))


@frappe.whitelist()
def is_call_integration_enabled():
	"""Extend Frappe CRM's telephony discovery to include RingCentral."""
	return {
		"integrations": {
			"twilio": bool(frappe.db.get_single_value("CRM Twilio Settings", "enabled")),
			"exotel": bool(frappe.db.get_single_value("CRM Exotel Settings", "enabled")),
			"ringcentral": _is_ringcentral_enabled(),
		},
		"default_calling_medium": get_user_default_calling_medium(),
	}


@frappe.whitelist()
def make_a_call(to_number: str):
	"""Outbound click-to-call via RingCentral RingOut (used by CRM frontend)."""
	from ringcentral_to_erpnext.api.ringcentral import make_ring_out_call

	return make_ring_out_call(to_number)
