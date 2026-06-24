#!/usr/bin/env bash
set -euo pipefail

CRM_ROOT="${1:?Usage: apply-overlay.sh /path/to/crm-fork}"
OVERLAY_ROOT="$(cd "$(dirname "$0")/frontend" && pwd)"

copy_file() {
  local rel="$1"
  local src="$OVERLAY_ROOT/$rel"
  local dst="$CRM_ROOT/frontend/$rel"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  echo "Copied $rel"
}

copy_file "src/components/Telephony/CallUI.vue"
copy_file "src/components/Telephony/RingCentralCallUI.vue"
copy_file "src/components/Settings/Telephony/TelephonySettings.vue"
copy_file "src/components/Settings/Telephony/TelephonyPage.vue"
copy_file "src/components/Settings/Telephony/RingCentralSettings.vue"

python3 - <<'PY' "$CRM_ROOT"
import pathlib, sys
root = pathlib.Path(sys.argv[1])
replacements = [
    (root / "crm/fcrm/doctype/crm_telephony_agent/crm_telephony_agent.json",
     '"options": "\\nTwilio\\nExotel"',
     '"options": "\\nTwilio\\nExotel\\nRingCentral"'),
    (root / "crm/fcrm/doctype/crm_call_log/crm_call_log.json",
     '"options": "\\nManual\\nTwilio\\nExotel"',
     '"options": "\\nManual\\nTwilio\\nExotel\\nRingCentral"'),
    (root / "crm/fcrm/doctype/crm_call_log/crm_call_log.py",
     'DF.Literal["", "Manual", "Twilio", "Exotel"]',
     'DF.Literal["", "Manual", "Twilio", "Exotel", "RingCentral"]'),
]
for path, old, new in replacements:
    text = path.read_text()
    if old not in text:
        print(f"WARNING: pattern not found in {path}")
        continue
    path.write_text(text.replace(old, new))
    print(f"Updated {path.name}")
PY

echo "Done. Commit changes in your CRM fork and redeploy."
