import frappe

_MODULE = "Ringcentral To Erpnext"
_APP = "ringcentral_to_erpnext"
_MODULE_KEY = "ringcentral_to_erpnext"   # scrubbed; used as module_app dict key
_DOCTYPES = ("ringcentral_settings", "ringcentral_agent")


def after_install():
    _bootstrap()


def after_migrate():
    _bootstrap()


def _bootstrap():
    _ensure_module_def()
    _register_in_module_app()
    for dt in _DOCTYPES:
        frappe.reload_doc(_MODULE_KEY, "doctype", dt, force=True)
    frappe.db.commit()


def _ensure_module_def():
    if not frappe.db.exists("Module Def", _MODULE):
        frappe.get_doc({
            "doctype": "Module Def",
            "module_name": _MODULE,
            "app_name": _APP,
        }).insert(ignore_permissions=True)
        frappe.db.commit()


def patch_module_app():
    """
    before_request hook — runs on every request.
    Ensures our module is in frappe.local.module_app even when Module Def
    is absent from the database, preventing 500 errors on desk load.
    """
    _register_in_module_app()


def _register_in_module_app():
    module_map = getattr(frappe.local, "module_app", None)
    if module_map is None:
        frappe.local.module_app = {}
    if _MODULE_KEY not in frappe.local.module_app:
        frappe.local.module_app[_MODULE_KEY] = _APP
