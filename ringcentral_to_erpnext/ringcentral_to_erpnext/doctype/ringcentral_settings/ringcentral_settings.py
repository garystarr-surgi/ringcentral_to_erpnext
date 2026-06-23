import frappe
from frappe.model.document import Document


class RingCentralSettings(Document):
    def validate(self):
        if self.enabled and not self.client_id:
            frappe.throw(
                frappe._("Client ID is required to enable RingCentral integration.")
            )
