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

# Extend Frappe CRM's hardcoded Twilio/Exotel telephony discovery.
# CRM frontend still needs the patch in crm_patches/ — see CRM_TELEPHONY.md.
override_whitelisted_methods = {
    "crm.integrations.api.is_call_integration_enabled": (
        "ringcentral_to_erpnext.integrations.crm.is_call_integration_enabled"
    ),
}
