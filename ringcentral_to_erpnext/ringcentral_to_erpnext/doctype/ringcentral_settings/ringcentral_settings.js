frappe.ui.form.on('RingCentral Settings', {
	register_webhook: function(frm) {
		if (frm.is_dirty()) {
			frappe.msgprint(__('Please save the form before registering the webhook.'));
			return;
		}
		frappe.confirm(
			__('Register (or renew) the RingCentral webhook subscription? RingCentral will immediately send a validation request to your site.'),
			function() {
				frappe.call({
					method: 'ringcentral_to_erpnext.ringcentral_to_erpnext.doctype.ringcentral_settings.ringcentral_settings.register_webhook',
					freeze: true,
					freeze_message: __('Registering with RingCentral...'),
					callback: function(r) {
						if (r.message) {
							frappe.show_alert({
								message: __('Webhook registered. Subscription ID: ') + r.message,
								indicator: 'green'
							}, 10);
							frm.reload_doc();
						}
					}
				});
			}
		);
	}
});
