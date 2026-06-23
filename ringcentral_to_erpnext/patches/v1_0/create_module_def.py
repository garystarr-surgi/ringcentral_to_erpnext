import frappe

_MODULE = "Ringcentral To Erpnext"
_APP = "ringcentral_to_erpnext"
_MODULE_KEY = "ringcentral_to_erpnext"


def execute():
    # Ensure Module Def row exists
    if not frappe.db.exists("Module Def", _MODULE):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": _MODULE,
            "app_name": _APP,
        }).insert(ignore_permissions=True)
        frappe.db.commit()

    # Patch module_app so reload_doc can resolve the file path in this process
    if not hasattr(frappe.local, "module_app") or frappe.local.module_app is None:
        frappe.local.module_app = {}
    frappe.local.module_app[_MODULE_KEY] = _APP

    # Sync both doctypes from their JSON definitions
    for dt in ("ringcentral_settings", "ringcentral_agent"):
        frappe.reload_doc(_MODULE_KEY, "doctype", dt, force=True)

    frappe.db.commit()
