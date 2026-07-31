[CmdletBinding()]
param(
    [string]$Repository = "yousef-812/Sahmi-Kasban",
    [string]$ApiBaseUrl = "https://sahmi-kasban.fly.dev",
    [string]$SentryMobileDsn = "",
    [string]$OutputDirectory = (Join-Path $HOME "Documents\SahmiKasbanReleaseKey"),
    [string]$KeyAlias = "sahmi-kasban-upload",
    [switch]$CheckOnly,
    [switch]$ForceRegenerate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Require-Command {
    param([Parameter(Mandatory)][string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' is not installed or is not on PATH."
    }
}

function New-RandomPassword {
    $bytes = [byte[]]::new(32)
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    return [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

function Get-RepositorySecretNames {
    param([Parameter(Mandatory)][string]$Repo)
    $json = gh secret list --repo $Repo --json name
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to list GitHub Actions secrets for $Repo."
    }
    return @($json | ConvertFrom-Json | ForEach-Object { $_.name })
}

function Set-RepositorySecret {
    param(
        [Parameter(Mandatory)][string]$Repo,
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Value
    )
    gh secret set $Name --repo $Repo --body $Value | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to set GitHub secret $Name."
    }
}

Require-Command gh
Require-Command keytool

gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI is not authenticated. Run 'gh auth login' first."
}

$apiUri = $null
if (-not [Uri]::TryCreate($ApiBaseUrl, [UriKind]::Absolute, [ref]$apiUri) -or $apiUri.Scheme -ne 'https') {
    throw "ApiBaseUrl must be an absolute HTTPS URL."
}

$integrationSecrets = @(
    "FIREBASE_ANDROID_GOOGLE_SERVICES_JSON",
    "ADMOB_ANDROID_APP_ID",
    "ADMOB_ANDROID_BANNER_ID",
    "ADMOB_ANDROID_NATIVE_ID",
    "ADMOB_ANDROID_INTERSTITIAL_ID"
)
$signingSecrets = @(
    "ANDROID_KEYSTORE_BASE64",
    "ANDROID_KEYSTORE_PASSWORD",
    "ANDROID_KEY_ALIAS",
    "ANDROID_KEY_PASSWORD",
    "ANDROID_EXPECTED_CERT_SHA256"
)
$allRequiredSecrets = @(
    "PRODUCTION_API_BASE_URL",
    "SENTRY_MOBILE_DSN"
) + $integrationSecrets + $signingSecrets

$existing = Get-RepositorySecretNames -Repo $Repository
$missingIntegrations = @($integrationSecrets | Where-Object { $_ -notin $existing })

Write-Host "Repository: $Repository"
Write-Host "Existing production integration secrets: $($integrationSecrets.Count - $missingIntegrations.Count)/$($integrationSecrets.Count)"

if ($missingIntegrations.Count -gt 0) {
    Write-Host "Missing provider secrets:" -ForegroundColor Yellow
    $missingIntegrations | ForEach-Object { Write-Host "  - $_" }
    throw "Add the missing Firebase/AdMob values in GitHub before preparing the signed release."
}

if ($CheckOnly) {
    $missing = @($allRequiredSecrets | Where-Object { $_ -notin $existing })
    if ($missing.Count -eq 0) {
        Write-Host "All Production Android Release secrets are present." -ForegroundColor Green
        exit 0
    }
    Write-Host "Missing Production Android Release secrets:" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  - $_" }
    exit 1
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$keystorePath = Join-Path $OutputDirectory "sahmi-kasban-upload.jks"
$backupPath = Join-Path $OutputDirectory "release-key-backup.txt"

if ((Test-Path $keystorePath) -and -not $ForceRegenerate) {
    throw "A keystore already exists at '$keystorePath'. Keep using the same key for updates, or pass -ForceRegenerate only before the first public release."
}

$storePassword = New-RandomPassword
$keyPassword = New-RandomPassword

& keytool -genkeypair -v `
    -keystore $keystorePath `
    -storetype JKS `
    -keyalg RSA `
    -keysize 2048 `
    -validity 10000 `
    -alias $KeyAlias `
    -dname "CN=Sahmi Kasban, OU=Mobile, O=Sahmi Kasban, L=Cairo, ST=Cairo, C=EG" `
    -storepass $storePassword `
    -keypass $keyPassword | Out-Null
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $keystorePath)) {
    throw "keytool did not create the release keystore."
}

$certificateOutput = & keytool -list -v `
    -keystore $keystorePath `
    -alias $KeyAlias `
    -storepass $storePassword
if ($LASTEXITCODE -ne 0) {
    throw "Unable to inspect the generated release certificate."
}

$shaLine = $certificateOutput | Where-Object { $_ -match '^\s*SHA256:' } | Select-Object -First 1
if (-not $shaLine) {
    throw "Unable to read the SHA-256 certificate fingerprint."
}
$certificateSha256 = ($shaLine -replace '^\s*SHA256:\s*', '').Trim()
$keystoreBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($keystorePath))

$backup = @"
SAHMI KASBAN ANDROID RELEASE KEY BACKUP

Keep this file and the JKS in an encrypted offline backup. Losing the key or passwords can prevent future direct updates.

Repository: $Repository
Keystore: $keystorePath
Alias: $KeyAlias
Store password: $storePassword
Key password: $keyPassword
Certificate SHA-256: $certificateSha256
Created UTC: $([DateTime]::UtcNow.ToString('O'))
"@
Set-Content -Path $backupPath -Value $backup -Encoding UTF8

Set-RepositorySecret -Repo $Repository -Name "PRODUCTION_API_BASE_URL" -Value $ApiBaseUrl
Set-RepositorySecret -Repo $Repository -Name "ANDROID_KEYSTORE_BASE64" -Value $keystoreBase64
Set-RepositorySecret -Repo $Repository -Name "ANDROID_KEYSTORE_PASSWORD" -Value $storePassword
Set-RepositorySecret -Repo $Repository -Name "ANDROID_KEY_ALIAS" -Value $KeyAlias
Set-RepositorySecret -Repo $Repository -Name "ANDROID_KEY_PASSWORD" -Value $keyPassword
Set-RepositorySecret -Repo $Repository -Name "ANDROID_EXPECTED_CERT_SHA256" -Value $certificateSha256

if (-not [string]::IsNullOrWhiteSpace($SentryMobileDsn)) {
    Set-RepositorySecret -Repo $Repository -Name "SENTRY_MOBILE_DSN" -Value $SentryMobileDsn
}

$finalNames = Get-RepositorySecretNames -Repo $Repository
$missingFinal = @($allRequiredSecrets | Where-Object { $_ -notin $finalNames })

Write-Host "Android release key created and signing secrets uploaded." -ForegroundColor Green
Write-Host "Permanent local backup: $OutputDirectory" -ForegroundColor Cyan
Write-Host "Do not delete the JKS or backup file. Store another encrypted offline copy."

if ($missingFinal.Count -gt 0) {
    Write-Host "The release is still missing:" -ForegroundColor Yellow
    $missingFinal | ForEach-Object { Write-Host "  - $_" }
    Write-Host "Run this script again with -SentryMobileDsn after creating the Sentry mobile project."
    exit 2
}

Write-Host "All Production Android Release secrets are present." -ForegroundColor Green
Write-Host "Run the GitHub Actions workflow 'Production Android Release' with confirmation RELEASE_PRODUCTION."
