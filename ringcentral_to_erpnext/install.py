import frappe


def after_install():
    _sync_doctypes()


def after_migrate():
    _sync_doctypes()


def _sync_doctypes():
    for dt in ("ringcentral_settings", "ringcentral_agent"):
        frappe.reload_doc("ringcentral_to_erpnext", "doctype", dt, force=True)
    frappe.db.commit()
