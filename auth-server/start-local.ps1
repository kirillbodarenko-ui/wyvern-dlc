$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$bootstrapPath = Join-Path $scriptRoot 'bootstrap-users.json'
$statePath = Join-Path $scriptRoot 'local-users.json'
# Optional, dev-machine-only accounts. bootstrap-users.json is also the seed the deployed server
# imports on its first boot, so test accounts must not go there: this file is read only by this
# script, and the Dockerfile copies only server.py, admin.py and bootstrap-users.json into the image.
$extraPath = Join-Path $scriptRoot 'local-extra-users.json'
$supportUrl = 'https://funpay.com/users/21337436/'
$clientVersion = '0.1-recode'
$sessions = @{}

function Read-Users {
    $bootstrap = @(Get-Content -LiteralPath $bootstrapPath -Raw -Encoding UTF8 | ConvertFrom-Json)
    $state = @{}
    $result = @()
    if (Test-Path -LiteralPath $statePath) {
        $saved = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($property in $saved.PSObject.Properties) {
            $state[$property.Name] = $property.Value
        }
    }
    foreach ($user in $bootstrap) {
        $hwid = if ($state.ContainsKey($user.username)) { $state[$user.username] } else { $null }
        $result += [PSCustomObject]@{
            username = [string]$user.username
            passwordSalt = [string]$user.passwordSalt
            passwordHash = [string]$user.passwordHash
            hwidHash = $hwid
        }
    }
    if (Test-Path -LiteralPath $extraPath) {
        $extra = @(Get-Content -LiteralPath $extraPath -Raw -Encoding UTF8 | ConvertFrom-Json)
        foreach ($user in $extra) {
            $hwid = if ($state.ContainsKey($user.username)) { $state[$user.username] } else { $null }
            $result += [PSCustomObject]@{
                username = [string]$user.username
                passwordSalt = [string]$user.passwordSalt
                passwordHash = [string]$user.passwordHash
                hwidHash = $hwid
            }
        }
    }
    return $result
}

function Save-Hwid($users) {
    $state = [ordered]@{}
    foreach ($user in $users) {
        if ($null -ne $user.hwidHash -and $user.hwidHash -ne '') {
            $state[$user.username] = $user.hwidHash
        }
    }
    $json = $state | ConvertTo-Json
    [IO.File]::WriteAllText($statePath, $json, [Text.UTF8Encoding]::new($false))
}

function Test-Password($password, $saltBase64, $hashBase64) {
    $salt = [Convert]::FromBase64String($saltBase64)
    $kdf = [Security.Cryptography.Rfc2898DeriveBytes]::new(
        $password, $salt, 310000, [Security.Cryptography.HashAlgorithmName]::SHA256)
    try {
        return [Convert]::ToBase64String($kdf.GetBytes(32)) -ceq $hashBase64
    } finally {
        $kdf.Dispose()
    }
}

function New-Session($username, $hwid) {
    $token = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    $expiresAt = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() + 300
    $sessions[$token] = [PSCustomObject]@{ Username = $username; Hwid = $hwid; ExpiresAt = $expiresAt }
    return [PSCustomObject]@{ Token = $token; ExpiresAt = $expiresAt }
}

function Send-Json($context, [int]$status, $body) {
    $json = $body | ConvertTo-Json -Compress
    $bytes = [Text.Encoding]::UTF8.GetBytes($json)
    $context.Response.StatusCode = $status
    $context.Response.ContentType = 'application/json; charset=utf-8'
    $context.Response.ContentLength64 = $bytes.Length
    $context.Response.Headers['Cache-Control'] = 'no-store'
    $context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    $context.Response.Close()
}

$listener = [Net.HttpListener]::new()
$listener.Prefixes.Add('http://127.0.0.1:8787/')
$listener.Start()
Write-Host 'Local karitsaDLC auth server started at 127.0.0.1:8787'

try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        try {
            $path = $context.Request.Url.AbsolutePath
            if ($context.Request.HttpMethod -eq 'GET' -and $path -eq '/health') {
                Send-Json $context 200 @{ ok = $true }
                continue
            }
            if ($context.Request.HttpMethod -ne 'POST') {
                Send-Json $context 404 @{ ok = $false; code = 'not_found' }
                continue
            }
            $reader = [IO.StreamReader]::new($context.Request.InputStream, [Text.Encoding]::UTF8)
            $body = $reader.ReadToEnd() | ConvertFrom-Json

            if ($path -eq '/api/v1/login') {
                if ($body.version -ne $clientVersion) {
                    Send-Json $context 426 @{ ok = $false; code = 'update_required'; message = 'Client update required' }
                    continue
                }
                $users = @(Read-Users)
                $user = $users | Where-Object { $_.username -ieq [string]$body.username } | Select-Object -First 1
                if ($null -eq $user) {
                    # Distinct from a wrong password on purpose: the deployed server deliberately
                    # merges the two, but locally that makes a typo and a malformed request look
                    # identical, and the client shows the server's message verbatim. ASCII only:
                    # this file is read as ANSI by Windows PowerShell, so non-ASCII arrives mangled.
                    Send-Json $context 401 @{ ok = $false; code = 'no_such_user'; message = 'local: no such user' }
                    continue
                }
                if (-not (Test-Password ([string]$body.password) $user.passwordSalt $user.passwordHash)) {
                    Send-Json $context 401 @{ ok = $false; code = 'bad_credentials'; message = 'local: password did not match' }
                    continue
                }
                if ($null -eq $user.hwidHash -or $user.hwidHash -eq '') {
                    $user.hwidHash = [string]$body.hwid
                    Save-Hwid $users
                } elseif ($user.hwidHash -cne [string]$body.hwid) {
                    Send-Json $context 409 @{
                        ok = $false
                        code = 'hwid_mismatch'
                        message = 'Account is linked to another computer'
                        supportUrl = $supportUrl
                    }
                    continue
                }
                $session = New-Session $user.username $user.hwidHash
                Send-Json $context 200 @{ ok = $true; token = $session.Token; expiresAt = $session.ExpiresAt }
                continue
            }

            if ($path -eq '/api/v1/validate') {
                $auth = [string]$context.Request.Headers['Authorization']
                $token = if ($auth.StartsWith('Bearer ')) { $auth.Substring(7) } else { '' }
                $session = $sessions[$token]
                $now = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
                if ($null -eq $session -or $session.ExpiresAt -lt $now -or $session.Hwid -cne [string]$body.hwid) {
                    Send-Json $context 401 @{ ok = $false; code = 'invalid_session' }
                    continue
                }
                $sessions.Remove($token)
                $next = New-Session $session.Username $session.Hwid
                Send-Json $context 200 @{ ok = $true; token = $next.Token; expiresAt = $next.ExpiresAt }
                continue
            }
            Send-Json $context 404 @{ ok = $false; code = 'not_found' }
        } catch {
            Write-Host $_.Exception.ToString()
            # A disconnected client must not terminate the entire auth server.
            try {
                if ($context.Response.OutputStream.CanWrite) {
                    Send-Json $context 500 @{ ok = $false; code = 'server_error'; message = 'Local auth server error' }
                }
            } catch {
                Write-Host 'Client disconnected before the error response could be sent'
            }
        }
    }
} finally {
    $listener.Stop()
    $listener.Close()
}
