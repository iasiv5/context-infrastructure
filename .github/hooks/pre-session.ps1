param(
    [string]$WorkspaceRoot,
    [string]$PythonPath,
    [string]$StatePath
)

$ErrorActionPreference = 'Stop'
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = $utf8NoBom
[Console]::OutputEncoding = $utf8NoBom
$OutputEncoding = $utf8NoBom

if ($MyInvocation.ExpectingInput) {
    $null = ($input | Out-String)
}

function Resolve-WorkspaceRoot {
    param([string]$ExplicitRoot)
    if ($ExplicitRoot) {
        return (Resolve-Path $ExplicitRoot).Path
    }

    return (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

function Resolve-Python {
    param(
        [string]$ExplicitPython,
        [string]$Root
    )

    $candidates = @()
    if ($ExplicitPython) {
        $candidates += $ExplicitPython
    }
    $candidates += (Join-Path $Root '.venv\Scripts\python.exe')

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return (Resolve-Path $candidate).Path
        }
    }

    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    return $null
}

try {
    $root = Resolve-WorkspaceRoot -ExplicitRoot $WorkspaceRoot
    $python = Resolve-Python -ExplicitPython $PythonPath -Root $root
    if (-not $python) {
        exit 0
    }

    $preflight = Join-Path $root 'periodic_jobs\ai_heartbeat\src\v0\heartbeat_preflight.py'
    if (-not (Test-Path $preflight)) {
        exit 0
    }

    if (-not $StatePath) {
        $StatePath = Join-Path $root 'periodic_jobs\ai_heartbeat\state\heartbeat_status.json'
    }

    $output = & $python $preflight --hook-mode --state-path $StatePath 2>$null
    if ($LASTEXITCODE -ne 0) {
        exit 0
    }

    if ($output) {
        @{
            continue = $true
            systemMessage = ($output | Out-String).TrimEnd()
        } | ConvertTo-Json -Compress | Write-Output
    }
}
catch {
    exit 0
}