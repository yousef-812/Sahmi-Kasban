param(
    [Parameter(Mandatory = $true)]
    [string]$Image,
    [string]$App = "sahmi-kasban"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command flyctl -ErrorAction SilentlyContinue)) {
    throw "flyctl is required."
}

Write-Host "Current releases:"
& flyctl releases --app $App --image

Write-Host "Rolling back $App to image $Image"
& flyctl deploy --app $App --image $Image --strategy rolling --yes
if ($LASTEXITCODE -ne 0) {
    throw "Fly rollback deployment failed."
}

$baseUrl = "https://$App.fly.dev"
Write-Host "Checking application health..."
$health = Invoke-RestMethod -Uri "$baseUrl/api/v1/health" -TimeoutSec 30
$db = Invoke-RestMethod -Uri "$baseUrl/api/v1/health/database" -TimeoutSec 30

if ($health.status -ne "ok" -or $db.status -ne "ok") {
    throw "Rollback completed but health verification failed."
}

Write-Host "Rollback verified successfully."
