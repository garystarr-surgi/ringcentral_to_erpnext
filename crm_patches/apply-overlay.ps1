param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$CrmRoot
)

$ErrorActionPreference = "Stop"
$OverlayRoot = Join-Path $PSScriptRoot "frontend"

if (-not (Test-Path $CrmRoot)) {
    throw "CRM path not found: $CrmRoot"
}

$files = @(
    "src\components\Telephony\CallUI.vue",
    "src\components\Telephony\RingCentralCallUI.vue",
    "src\components\Settings\Telephony\TelephonySettings.vue",
    "src\components\Settings\Telephony\TelephonyPage.vue",
    "src\components\Settings\Telephony\RingCentralSettings.vue"
)

foreach ($rel in $files) {
    $src = Join-Path $OverlayRoot $rel
    $dst = Join-Path $CrmRoot ("frontend\" + $rel)
    if (-not (Test-Path $src)) {
        throw "Missing overlay file: $src"
    }
    $dstDir = Split-Path $dst -Parent
    if (-not (Test-Path $dstDir)) {
        New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
    }
    Copy-Item $src $dst -Force
    Write-Host "Copied $rel"
}

function Set-JsonOptions {
    param($Path, $Old, $New)
    $content = Get-Content $Path -Raw
    if ($content -notmatch [regex]::Escape($Old)) {
        Write-Warning "Pattern not found in $Path — update manually"
        return
    }
    ($content -replace [regex]::Escape($Old), $New) | Set-Content $Path -NoNewline
}

Set-JsonOptions `
    (Join-Path $CrmRoot "crm\fcrm\doctype\crm_telephony_agent\crm_telephony_agent.json") `
    '"options": "\nTwilio\nExotel"' `
    '"options": "\nTwilio\nExotel\nRingCentral"'

Set-JsonOptions `
    (Join-Path $CrmRoot "crm\fcrm\doctype\crm_call_log\crm_call_log.json") `
    '"options": "\nManual\nTwilio\nExotel"' `
    '"options": "\nManual\nTwilio\nExotel\nRingCentral"'

$pyPath = Join-Path $CrmRoot "crm\fcrm\doctype\crm_call_log\crm_call_log.py"
$py = Get-Content $pyPath -Raw
$pyOld = 'DF.Literal["", "Manual", "Twilio", "Exotel"]'
$pyNew = 'DF.Literal["", "Manual", "Twilio", "Exotel", "RingCentral"]'
if ($py -notmatch [regex]::Escape($pyOld)) {
    Write-Warning "Pattern not found in crm_call_log.py — update manually"
} else {
    ($py -replace [regex]::Escape($pyOld), $pyNew) | Set-Content $pyPath -NoNewline
    Write-Host "Updated crm_call_log.py"
}

Write-Host "Done. Commit changes in your CRM fork and redeploy."
