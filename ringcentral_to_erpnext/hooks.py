app_name = "ringcentral_to_erpnext"
app_title = "RingCentral to ERPNext"
app_publisher = "SurgiShop"
app_description = "RingCentral telephony integration for Frappe CRM / ERPNext"
app_email = "gary@surgishop.com"
app_license = "MIT"

after_install = "ringcentral_to_erpnext.install.after_install"
after_migrate = "ringcentral_to_erpnext.install.after_migrate"
after_sync = "ringcentral_to_erpnext.install.after_migrate"

before_request = ["ringcentral_to_erpnext.install.patch_module_app"]

# Map hyphenated alias → underscore filename (Frappe derives routes from filenames)
website_route_rules = [
    {"from_route": "/rc-webhook", "to_route": "rc_webhook"},
]

# ── Tell Frappe CRM that RingCentral is a telephony provider ─────────────────
# Frappe CRM reads this hook to populate the "Provider" dropdown in
# Telephony Settings and to route get_token / handle_request calls.
telephony_providers = [
    {
        "name": "RingCentral",
        "module": "ringcentral_to_erpnext.api.ringcentral",
        "get_token": "get_token",
        "handle_request": "handle_request",
    }
]
