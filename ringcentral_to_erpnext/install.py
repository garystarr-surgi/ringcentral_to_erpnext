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
    Also patches frappe.utils.response.as_json once per worker process so
    RC webhook validation can receive the Validation-Token response header.
    """
    _register_in_module_app()
    _patch_as_json()


def _patch_as_json():
    """Patch frappe.utils.response.as_json once per gunicorn worker.

    frappe.utils.response.build_response() resolves 'as_json' via the
    module's own globals at call-time (not at import-time), so replacing
    the name in the module dict is enough to intercept every future call
    without touching handler.py's cached reference to build_response.

    The patch is a no-op on every request except the RC validation GET,
    where handle_request sets frappe.flags.rc_validation_token.
    """
    try:
        import frappe.utils.response as _resp_mod
        if getattr(_resp_mod, "_rc_patch_applied", False):
            return
        _orig_as_json = _resp_mod.as_json

        def _patched_as_json():
            response = _orig_as_json()
            token = getattr(frappe.flags, "rc_validation_token", None)
            if token and hasattr(response, "headers"):
                response.headers["Validation-Token"] = token
            return response

        _resp_mod.as_json = _patched_as_json
        _resp_mod._rc_patch_applied = True
    except Exception:
        pass



def _register_in_module_app():
    module_map = getattr(frappe.local, "module_app", None)
    if module_map is None:
        frappe.local.module_app = {}
    if _MODULE_KEY not in frappe.local.module_app:
        frappe.local.module_app[_MODULE_KEY] = _APP
