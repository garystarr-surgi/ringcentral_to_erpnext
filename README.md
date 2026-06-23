# ringcentral_to_erpnext

RingCentral telephony integration for Frappe CRM / ERPNext.

Plugs RingCentral into Frappe CRM's native telephony framework so call buttons
on Lead, Deal, and Contact pages work with RingCentral — no manual widget
injection into the Vue frontend required.

**What you get:**
- Click-to-call on Lead / Deal / Contact pages in Frappe CRM via RingCentral
- Inbound and outbound calls auto-logged to CRM Call Log, linked to Contact or Lead
- RingCentral Settings doctype — one place for all credentials and webhook setup
- RingCentral Agent doctype — maps RC extensions to Frappe users

---

## Prerequisites

- Frappe v15 / v16 private bench on Frappe Cloud
- Frappe CRM app installed (`frappe/crm`)
- A RingCentral account with developer access
- Your Frappe site must be publicly accessible over HTTPS

---

## Step 1 — Register a RingCentral App

1. Go to [developers.ringcentral.com](https://developers.ringcentral.com)
2. **Create App** → **REST API App** → Next
3. Under **Auth**:
   - Select **JWT auth** (server-to-server)
   - **Platform type**: Server/Bot
   - No redirect URI needed
4. Under **Security** add these scopes:
   ```
   Read Accounts, Read Call Log, Read Call Recording,
   VoIP Calling, WebSocketSubscription, Ring Out,
   Webhook Subscriptions
   ```
5. Save. Copy your **Client ID** and **Client Secret**.
6. RC Admin Console → **Users** → select your service account user
7. Under that user's profile → **Credentials** → **Generate JWT** → copy the token.

---

## Step 2 — Install on Frappe Cloud

1. Push this repo to GitHub (can be private)
2. Frappe Cloud → your Bench → **Apps** → **Add App** → GitHub → select repo
3. Deploy the bench
4. Site → **Apps** → **Install App** → `ringcentral_to_erpnext`
5. Trigger an **In-Place Migration** from the site panel

---

## Step 3 — Configure RingCentral Settings

In Frappe Desk, search **RingCentral Settings** in the awesomebar.

Fill in:

| Field | Value |
|---|---|
| Enabled | ✓ |
| Client ID | from RC Developer Console |
| Client Secret | from RC Developer Console |
| JWT Token | generated in Step 1 |
| Webhook Verify Token | any secret string, e.g. `surgi-rc-2025` |
| Auto Log Calls | ✓ |

Save the form.

---

## Step 4 — Register the Webhook

Still in **RingCentral Settings**, click **Register Webhook with RingCentral**.

This button calls the RC API to create a webhook subscription pointing to your
site. RingCentral immediately sends a validation request — the handler echoes
it back automatically. On success, the **Webhook Subscription ID** field is
populated.

> RC webhook subscriptions expire after ~24 hours. Click the button again to
> renew whenever the subscription lapses. A future update will add
> auto-renewal via a scheduled job.

---

## Step 5 — Enable RingCentral in Frappe CRM Telephony Settings

1. In Frappe CRM → top-left menu → **Settings** → **Telephony**
2. Set **Provider** to `RingCentral`
3. Save

The call button will now appear on Lead / Deal / Contact pages.

---

## Step 6 — Add Telephony Agents

For each sales rep who will make/receive calls:

1. Frappe Desk → search **RingCentral Agent** → **New**
2. Set:
   - **Frappe User**: the rep's Frappe login
   - **RC Extension ID**: found in RC Admin Console → Users (their extension number)
   - **RC Direct Number**: their RC phone number in E.164 format (e.g. `+17275551234`)
3. Save

---

## File Structure

```
ringcentral_to_erpnext/              ← repo root
├── README.md
├── MANIFEST.in
├── pyproject.toml
├── setup.py
└── ringcentral_to_erpnext/          ← Python package
    ├── __init__.py
    ├── hooks.py                     ← lifecycle hooks + telephony provider
    ├── install.py                   ← bootstrap: Module Def + doctype sync
    ├── patches.txt
    ├── patches/
    │   └── v1_0/
    │       └── create_module_def.py
    ├── api/
    │   └── ringcentral.py           ← get_token, handle_request, helpers
    └── ringcentral_to_erpnext/      ← Frappe module
        ├── module.txt
        └── doctype/
            ├── ringcentral_settings/
            │   ├── ringcentral_settings.json
            │   ├── ringcentral_settings.py  ← includes register_webhook
            │   └── ringcentral_settings.js  ← button handler
            └── ringcentral_agent/
                ├── ringcentral_agent.json
                └── ringcentral_agent.py
```

---

## Troubleshooting

**RingCentral Settings not found in awesomebar**
→ Trigger an In-Place Migration from the Frappe Cloud site panel.

**500 error on desk after install**
→ Deploy the latest code (before_request hook in install.py prevents this).
→ Then run In-Place Migration to create the Module Def permanently.

**"Could not get RingCentral access token"**
→ The JWT Token has expired. Regenerate it in the RC Developer Console
  (Admin Console → Users → user → Credentials → Generate JWT) and update
  the field in RingCentral Settings.

**Register Webhook fails**
→ Confirm your RC App has the `Webhook Subscriptions` scope.
→ Confirm the site is publicly reachable over HTTPS (RC must be able to
  send the validation request to your URL).
→ Check Frappe Desk → Error Log for the RC API response body.

**Calls not being logged**
→ Check the Webhook Subscription ID field is populated (re-register if blank).
→ RC subscriptions expire — click Register Webhook again to renew.
→ Check Frappe error logs: Desk → Error Log.

**Phone numbers not matching contacts**
→ REGEXP_REPLACE requires MariaDB 10.5+. Frappe Cloud uses 10.6+ so this
  should work. Check bench DB version in Frappe Cloud → Bench → Overview.
