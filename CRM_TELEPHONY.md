# Frappe CRM telephony patch (RingCentral)

Frappe CRM only ships **Twilio** and **Exotel**. RingCentral requires a small CRM fork patch.

**Start here:** [`crm_patches/README.md`](crm_patches/README.md)

## Quick apply

```powershell
cd C:\path\to\your\crm-fork
git checkout -b ringcentral-telephony
git apply --3way C:\path\to\ringcentral_to_erpnext\crm_patches\0001-ringcentral-telephony-support.patch
git add -A
git commit -m "Add RingCentral telephony support"
git push -u origin ringcentral-telephony
```

Then point your Frappe Cloud bench at the CRM fork, deploy both apps, and run migration.

## Where to configure in CRM UI

**CRM app (`/crm`) → Settings → Telephony → Default Medium → RingCentral**

Credentials and webhooks stay in Frappe Desk → **RingCentral Settings**.

## What each repo owns

| Repo | Responsibility |
|------|----------------|
| `ringcentral_to_erpnext` | RC API, webhooks, call logging, `is_call_integration_enabled` override, RingOut API |
| Your `frappe/crm` fork | CRM UI: call button, telephony settings dropdown, RingCentral settings page |
