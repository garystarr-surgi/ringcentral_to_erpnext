# CRM fork patch — RingCentral telephony

Apply this patch to your fork of [frappe/crm](https://github.com/frappe/crm) so RingCentral
appears in **Settings → Telephony** and click-to-call works with the
[ringcentral_to_erpnext](https://github.com/garystarr-surgi/ringcentral_to_erpnext) app.

## Prerequisites

- `ringcentral_to_erpnext` installed and migrated on the same bench
- `frappe/crm` fork checked out locally

## Option 1 — `git apply` (recommended)

```bash
cd /path/to/your/crm-fork
git checkout -b ringcentral-telephony
git apply --3way /path/to/ringcentral_to_erpnext/crm_patches/0001-ringcentral-telephony-support.patch
# resolve any conflicts, then:
git add -A
git commit -m "Add RingCentral telephony support"
git push -u origin ringcentral-telephony
```

On Windows PowerShell:

```powershell
cd C:\path\to\your\crm-fork
git checkout -b ringcentral-telephony
git apply --3way C:\path\to\ringcentral_to_erpnext\crm_patches\0001-ringcentral-telephony-support.patch
git add -A
git commit -m "Add RingCentral telephony support"
git push -u origin ringcentral-telephony
```

## Option 2 — Copy overlay files

If `git apply` fails due to CRM version drift, copy files manually:

| Source (this repo) | Destination (crm fork) |
|---|---|
| `crm_patches/frontend/src/components/Telephony/CallUI.vue` | `frontend/src/components/Telephony/CallUI.vue` |
| `crm_patches/frontend/src/components/Telephony/RingCentralCallUI.vue` | `frontend/src/components/Telephony/RingCentralCallUI.vue` |
| `crm_patches/frontend/src/components/Settings/Telephony/TelephonySettings.vue` | `frontend/src/components/Settings/Telephony/TelephonySettings.vue` |
| `crm_patches/frontend/src/components/Settings/Telephony/TelephonyPage.vue` | `frontend/src/components/Settings/Telephony/TelephonyPage.vue` |
| `crm_patches/frontend/src/components/Settings/Telephony/RingCentralSettings.vue` | `frontend/src/components/Settings/Telephony/RingCentralSettings.vue` |

Also update these three backend files (see patch for exact lines):

- `crm/fcrm/doctype/crm_telephony_agent/crm_telephony_agent.json` — add `RingCentral` to `default_medium` options
- `crm/fcrm/doctype/crm_call_log/crm_call_log.json` — add `RingCentral` to `telephony_medium` options
- `crm/fcrm/doctype/crm_call_log/crm_call_log.py` — add `RingCentral` to the `telephony_medium` Literal type

Or run:

```powershell
.\crm_patches\apply-overlay.ps1 C:\path\to\your\crm-fork
```

## After applying

1. **Frappe Cloud** → Bench → point CRM app at your fork → Deploy
2. Rebuild CRM frontend assets (Frappe Cloud does this on deploy)
3. Site → **In-Place Migration**
4. Enable **RingCentral Settings** in Desk and create **RingCentral Agent** records
5. **CRM → Settings → Telephony** → set **Default Medium** to `RingCentral`

## What this patch changes

- Adds `RingCentralCallUI.vue` (RingOut click-to-call)
- Adds `RingCentralSettings.vue` (links to Desk configuration)
- Wires RingCentral into `CallUI.vue`, `TelephonySettings.vue`, `TelephonyPage.vue`
- Allows `RingCentral` as a valid telephony medium in CRM doctypes

Backend API discovery (`is_call_integration_enabled`) is provided by `ringcentral_to_erpnext`
via `override_whitelisted_methods` — no CRM Python API patch required.
