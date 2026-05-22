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

function Get-HeartbeatSelectedTasks {
    param([string]$SelectedAction)

    switch ($SelectedAction) {
        'run_observer' { return @('observer') }
        'run_reflector' { return @('reflector') }
        'run_observer_and_reflector' { return @('observer', 'reflector') }
        default { return @() }
    }
}

function Get-HeartbeatPythonHint {
    param(
        [string]$Root,
        [string]$ResolvedPython
    )

    $localPython = Join-Path $Root '.venv\Scripts\python.exe'
    if (Test-Path $localPython) {
        return '.\.venv\Scripts\python.exe'
    }

    if ($ResolvedPython) {
        return $ResolvedPython
    }

    return 'python'
}

function Clear-LegacyHeartbeatPendingPayload {
    param(
        [string]$Root
    )

    $legacyPath = Join-Path $Root 'periodic_jobs\ai_heartbeat\state\heartbeat_local_tasks.json'
    if (Test-Path $legacyPath) {
        Remove-Item -Path $legacyPath -Force -ErrorAction SilentlyContinue
    }
}

function ConvertTo-HeartbeatQuotedArgument {
    param([string]$Value)

    return "'$($Value.Replace("'", "''"))'"
}

function Start-HeartbeatLocalExecution {
    param(
        [string[]]$Tasks,
        [string]$Root,
        [string]$ResolvedPython,
        [string]$StatePath,
        [string]$TargetDate,
        [string]$HostPath
    )

    if (-not $Tasks -or $Tasks.Count -eq 0) {
        return $false
    }

    $runnerPath = Join-Path $Root 'periodic_jobs\ai_heartbeat\src\v0\heartbeat_local_runner.py'
    if (-not (Test-Path $runnerPath)) {
        return $false
    }

    $pythonPath = if ($ResolvedPython) { $ResolvedPython } else { Get-HeartbeatPythonHint -Root $Root -ResolvedPython $ResolvedPython }
    $segments = @(
        '&',
        (ConvertTo-HeartbeatQuotedArgument -Value $pythonPath),
        (ConvertTo-HeartbeatQuotedArgument -Value $runnerPath)
    )

    foreach ($taskName in $Tasks) {
        $segments += (ConvertTo-HeartbeatQuotedArgument -Value $taskName)
    }

    if ($TargetDate) {
        $segments += (ConvertTo-HeartbeatQuotedArgument -Value '--target-date')
        $segments += (ConvertTo-HeartbeatQuotedArgument -Value $TargetDate)
    }

    if ($StatePath) {
        $segments += (ConvertTo-HeartbeatQuotedArgument -Value '--state-path')
        $segments += (ConvertTo-HeartbeatQuotedArgument -Value $StatePath)
    }

    $segments += (ConvertTo-HeartbeatQuotedArgument -Value '--workspace-root')
    $segments += (ConvertTo-HeartbeatQuotedArgument -Value $Root)

    $executionCommand = $segments -join ' '
    $shellCommand = @(
        "Set-Location $(ConvertTo-HeartbeatQuotedArgument -Value $Root)",
        "Write-Host 'AI Heartbeat 本地任务开始执行...' -ForegroundColor Cyan",
        $executionCommand,
        '$exitCode = $LASTEXITCODE',
        'Write-Host ""',
        'if ($exitCode -eq 0) { Write-Host "AI Heartbeat 本地任务执行完成。" -ForegroundColor Green } else { Write-Host ("AI Heartbeat 本地任务执行失败，退出码: " + $exitCode) -ForegroundColor Red }',
        'Read-Host "AI Heartbeat 任务已结束，按回车关闭窗口" | Out-Null'
    ) -join '; '

    Start-Process -FilePath $HostPath -WorkingDirectory $Root -ArgumentList @(
        '-NoExit',
        '-NoProfile',
        '-ExecutionPolicy',
        'Bypass',
        '-Command',
        $shellCommand
    ) | Out-Null

    return $true
}

function Show-HeartbeatExecutionError {
    param([string]$Message)

    Add-Type -AssemblyName System.Windows.Forms
    [void][System.Windows.Forms.MessageBox]::Show(
        $Message,
        'AI Heartbeat',
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
}

function Show-HeartbeatExecutionStarted {
    Add-Type -AssemblyName System.Windows.Forms
    [void][System.Windows.Forms.MessageBox]::Show(
        'AI Heartbeat 本地任务已在新窗口启动。窗口内会显示 observer / reflector 的执行结果。',
        'AI Heartbeat',
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Information
    )
}

function Start-HeartbeatSelectionExecution {
    param(
        [string[]]$Tasks,
        [string]$Root,
        [string]$ResolvedPython,
        [string]$StatePath,
        [string]$TargetDate
    )

    $hostPath = (Get-Process -Id $PID).Path
    if (-not $hostPath) {
        Show-HeartbeatExecutionError -Message '无法定位当前 PowerShell 主程序，AI Heartbeat 本地任务未启动。'
        return $false
    }

    $started = Start-HeartbeatLocalExecution -Tasks $Tasks -Root $Root -ResolvedPython $ResolvedPython -StatePath $StatePath -TargetDate $TargetDate -HostPath $hostPath
    if ($started) {
        Show-HeartbeatExecutionStarted
    }

    return $started
}

function Ensure-HeartbeatDialogInterop {
    if (-not ('HeartbeatDialogInterop' -as [type])) {
        Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public static class HeartbeatDialogInterop
{
    [DllImport("dwmapi.dll")]
    public static extern int DwmSetWindowAttribute(IntPtr hwnd, int attribute, ref int value, int size);
}
"@
    }
}

function Set-HeartbeatDialogDarkTitleBar {
    param([System.Windows.Forms.Form]$Form)

    try {
        Ensure-HeartbeatDialogInterop
        $enabled = 1
        $size = [System.Runtime.InteropServices.Marshal]::SizeOf([int]0)
        foreach ($attribute in 20, 19) {
            try {
                [void][HeartbeatDialogInterop]::DwmSetWindowAttribute($Form.Handle, $attribute, [ref]$enabled, $size)
            }
            catch {
            }
        }
    }
    catch {
    }
}

function Show-HeartbeatDialog {
    param([psobject]$Payload)

    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    [System.Windows.Forms.Application]::EnableVisualStyles()
    Ensure-HeartbeatDialogInterop

    $options = @($Payload.options)
    if (-not $options -or $options.Count -eq 0) {
        return $null
    }

    $surfaceColor = [System.Drawing.ColorTranslator]::FromHtml('#1E1E1E')
    $panelColor = [System.Drawing.ColorTranslator]::FromHtml('#252526')
    $borderColor = [System.Drawing.ColorTranslator]::FromHtml('#3C3C3C')
    $textColor = [System.Drawing.ColorTranslator]::FromHtml('#D4D4D4')
    $mutedTextColor = [System.Drawing.ColorTranslator]::FromHtml('#9DA5B4')
    $accentColor = [System.Drawing.ColorTranslator]::FromHtml('#0E639C')
    $secondaryButtonColor = [System.Drawing.ColorTranslator]::FromHtml('#3C3C3C')
    $buttonTextColor = [System.Drawing.Color]::White
    $clientWidth = 560
    $clientHeight = 204 + ($options.Count * 74)

    $form = New-Object System.Windows.Forms.Form
    $form.Text = if ($Payload.title) { [string]$Payload.title } else { 'AI Heartbeat 会前提醒' }
    $form.StartPosition = 'CenterScreen'
    $form.ClientSize = New-Object System.Drawing.Size($clientWidth, $clientHeight)
    $form.TopMost = $true
    $form.FormBorderStyle = 'FixedDialog'
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $form.BackColor = $surfaceColor
    $form.ForeColor = $textColor
    $form.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 9)
    $form.Padding = New-Object System.Windows.Forms.Padding(0)
    $form.Add_Shown({
        param($sender, $eventArgs)
        Set-HeartbeatDialogDarkTitleBar -Form $sender
    })

    $contentPanel = New-Object System.Windows.Forms.Panel
    $contentPanel.Location = New-Object System.Drawing.Point(0, 0)
    $contentPanel.Size = $form.ClientSize
    $contentPanel.BackColor = $surfaceColor
    $contentPanel.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor [System.Windows.Forms.AnchorStyles]::Bottom -bor [System.Windows.Forms.AnchorStyles]::Left -bor [System.Windows.Forms.AnchorStyles]::Right
    $form.Controls.Add($contentPanel)

    $titleLabel = New-Object System.Windows.Forms.Label
    $titleLabel.Location = New-Object System.Drawing.Point(18, 16)
    $titleLabel.Size = New-Object System.Drawing.Size(510, 24)
    $titleLabel.Text = if ($Payload.title) { [string]$Payload.title } else { 'AI Heartbeat 会前提醒' }
    $titleLabel.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 11, [System.Drawing.FontStyle]::Bold)
    $titleLabel.ForeColor = $textColor
    $titleLabel.BackColor = $surfaceColor
    $contentPanel.Controls.Add($titleLabel)

    $questionLabel = New-Object System.Windows.Forms.Label
    $questionLabel.Location = New-Object System.Drawing.Point(18, 44)
    $questionLabel.Size = New-Object System.Drawing.Size(510, 40)
    $questionLabel.Text = [string]$Payload.question
    $questionLabel.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 9)
    $questionLabel.ForeColor = $mutedTextColor
    $questionLabel.BackColor = $surfaceColor
    $contentPanel.Controls.Add($questionLabel)

    $divider = New-Object System.Windows.Forms.Panel
    $divider.Location = New-Object System.Drawing.Point(18, 88)
    $divider.Size = New-Object System.Drawing.Size(510, 1)
    $divider.BackColor = $borderColor
    $contentPanel.Controls.Add($divider)

    $radioButtons = @()
    $setOptionHandler = {
        param($sender, $eventArgs)

        $selectedRadio = $null
        if ($sender -is [System.Windows.Forms.RadioButton]) {
            $selectedRadio = [System.Windows.Forms.RadioButton]$sender
        }
        elseif ($sender.Tag -is [System.Windows.Forms.RadioButton]) {
            $selectedRadio = [System.Windows.Forms.RadioButton]$sender.Tag
        }

        if (-not $selectedRadio) {
            return
        }

        foreach ($candidate in $radioButtons) {
            $candidate.Checked = ($candidate -eq $selectedRadio)
        }
    }

    $y = 104
    foreach ($option in $options) {
        $panel = New-Object System.Windows.Forms.Panel
        $panel.Location = New-Object System.Drawing.Point(18, $y)
        $panel.Size = New-Object System.Drawing.Size(510, 58)
        $panel.BackColor = $panelColor
        $panel.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle

        $radio = New-Object System.Windows.Forms.RadioButton
        $radio.Location = New-Object System.Drawing.Point(14, 19)
        $radio.Size = New-Object System.Drawing.Size(18, 18)
        $radio.Text = ''
        $radio.Tag = [string]$option.action
        $radio.BackColor = $panelColor
        $radio.ForeColor = $textColor
        $radio.UseVisualStyleBackColor = $false
        $radio.AutoCheck = $false
        if ($radioButtons.Count -eq 0) {
            $radio.Checked = $true
        }

        $optionTitle = New-Object System.Windows.Forms.Label
        $optionTitle.Location = New-Object System.Drawing.Point(40, 10)
        $optionTitle.Size = New-Object System.Drawing.Size(440, 20)
        $optionTitle.Text = [string]$option.label
        $optionTitle.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 9.5, [System.Drawing.FontStyle]::Bold)
        $optionTitle.ForeColor = $textColor
        $optionTitle.BackColor = $panelColor

        $optionDescription = New-Object System.Windows.Forms.Label
        $optionDescription.Location = New-Object System.Drawing.Point(40, 30)
        $optionDescription.Size = New-Object System.Drawing.Size(440, 18)
        $optionDescription.Text = [string]$option.description
        $optionDescription.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 8.5)
        $optionDescription.ForeColor = $mutedTextColor
        $optionDescription.BackColor = $panelColor

        $panel.Tag = $radio
        $optionTitle.Tag = $radio
        $optionDescription.Tag = $radio
        $panel.Add_Click($setOptionHandler)
        $optionTitle.Add_Click($setOptionHandler)
        $optionDescription.Add_Click($setOptionHandler)
        $radio.Add_Click($setOptionHandler)

        $radioButtons += $radio
        $panel.Controls.Add($radio)
        $panel.Controls.Add($optionTitle)
        $panel.Controls.Add($optionDescription)
        $contentPanel.Controls.Add($panel)
        $y += 68
    }

    $buttonDivider = New-Object System.Windows.Forms.Panel
    $buttonDivider.Location = New-Object System.Drawing.Point(18, ($clientHeight - 102))
    $buttonDivider.Size = New-Object System.Drawing.Size(($clientWidth - 50), 1)
    $buttonDivider.BackColor = $borderColor
    $contentPanel.Controls.Add($buttonDivider)

    $okButton = New-Object System.Windows.Forms.Button
    $okButton.Text = '确定'
    $okButton.Location = New-Object System.Drawing.Point(($clientWidth - 214), ($clientHeight - 64))
    $okButton.Size = New-Object System.Drawing.Size(92, 32)
    $okButton.BackColor = $accentColor
    $okButton.ForeColor = $buttonTextColor
    $okButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
    $okButton.FlatAppearance.BorderSize = 0
    $okButton.Add_Click({
        foreach ($radio in $radioButtons) {
            if ($radio.Checked) {
                $form.Tag = [string]$radio.Tag
                break
            }
        }
        $form.DialogResult = [System.Windows.Forms.DialogResult]::OK
        $form.Close()
    })
    $contentPanel.Controls.Add($okButton)

    $cancelButton = New-Object System.Windows.Forms.Button
    $cancelButton.Text = '忽略'
    $cancelButton.Location = New-Object System.Drawing.Point(($clientWidth - 110), ($clientHeight - 64))
    $cancelButton.Size = New-Object System.Drawing.Size(92, 32)
    $cancelButton.BackColor = $secondaryButtonColor
    $cancelButton.ForeColor = $buttonTextColor
    $cancelButton.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
    $cancelButton.FlatAppearance.BorderColor = $borderColor
    $cancelButton.Add_Click({
        $form.Tag = 'ignore'
        $form.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
        $form.Close()
    })
    $contentPanel.Controls.Add($cancelButton)

    $form.AcceptButton = $okButton
    $form.CancelButton = $cancelButton
    $null = $form.ShowDialog()

    if ($form.Tag) {
        return [string]$form.Tag
    }

    return 'ignore'
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

    Clear-LegacyHeartbeatPendingPayload -Root $root

    $dialogSpecOutput = & $python $preflight --hook-dialog-spec --state-path $StatePath 2>$null
    if ($LASTEXITCODE -ne 0) {
        exit 0
    }

    if ($dialogSpecOutput) {
        try {
            $payload = ($dialogSpecOutput | Out-String).Trim() | ConvertFrom-Json
            $selectedAction = Show-HeartbeatDialog -Payload $payload
            $selectedTasks = Get-HeartbeatSelectedTasks -SelectedAction $selectedAction
            if ($selectedTasks.Count -gt 0) {
                $targetDate = if ($payload.target_date) { [string]$payload.target_date } else { $null }
                $null = Start-HeartbeatSelectionExecution -Tasks $selectedTasks -Root $root -ResolvedPython $python -StatePath $StatePath -TargetDate $targetDate
            }

            exit 0
        }
        catch {
            exit 0
        }
    }
}
catch {
    exit 0
}