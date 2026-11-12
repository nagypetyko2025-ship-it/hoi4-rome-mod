# Launch HoI4 with ONLY Ante Imperium enabled, wait for the main menu or a failure,
# then restore the user's mod list and summarise error.log.
# usage: powershell -ExecutionPolicy Bypass -File tools/test_launch.ps1 [-TimeoutSec 360] [-KeepRunning]
param([int]$TimeoutSec = 360, [switch]$KeepRunning, [string]$ExtraArgs = "")

$docs = Join-Path $env:USERPROFILE "Documents\Paradox Interactive\Hearts of Iron IV"
$game = "D:\SteamLibrary\steamapps\common\Hearts of Iron IV"
$logs = Join-Path $docs "logs"
$load = Join-Path $docs "dlc_load.json"
$backup = "$load.ante_backup"

Get-Process hoi4 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
if (-not (Test-Path $backup)) { Copy-Item $load $backup }
Set-Content -Path $load -Value '{"enabled_mods":["mod/ante_imperium.mod"],"disabled_dlcs":[]}' -Encoding ascii -NoNewline
$start = Get-Date
Start-Process -FilePath "$game\hoi4.exe" -WorkingDirectory $game -ArgumentList ("-gdpr-compliant " + $ExtraArgs)

$result = "TIMEOUT"
$crashDir = Join-Path $docs "crashes"
try {
    while (((Get-Date) - $start).TotalSeconds -lt $TimeoutSec) {
        Start-Sleep 5
        $procs = @(Get-Process hoi4 -ErrorAction SilentlyContinue)
        if ($procs.Count -eq 0) { $result = "EXITED"; break }
        $titles = ($procs | ForEach-Object { $_.MainWindowTitle }) -join " | "
        if ($titles -match "Fail|Error|error") { $result = "FAILED: $titles"; break }
        # quickstart: the game itself was launched
        if (Select-String -Path (Join-Path $logs "game.log") -Pattern "Launching SINGLEPLAYER" -Quiet) {
            Start-Sleep 30
            $newCrash = Get-ChildItem $crashDir -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $start }
            if ($newCrash -or @(Get-Process hoi4 -ErrorAction SilentlyContinue).Count -eq 0) { $result = "CRASHED at game start"; break }
            $result = "GAME RUNNING"; break
        }
        if ($ExtraArgs -match "start_tag") { continue }
        # history is executed for the default bookmark when the main menu is built
        if (Select-String -Path (Join-Path $logs "game.log") -Pattern "Executing History from 2\.1\.1\.1" -Quiet) {
            $p = $procs | Sort-Object WorkingSet64 -Descending | Select-Object -First 1
            if ($p.WorkingSet64 -gt 1.5GB) {
                $c1 = $p.TotalProcessorTime.TotalSeconds; Start-Sleep 6; $p.Refresh()
                $titles = (@(Get-Process hoi4 -ErrorAction SilentlyContinue) | ForEach-Object { $_.MainWindowTitle }) -join " | "
                if ($titles -match "Fail|Error|error") { $result = "FAILED: $titles"; break }
                if (($p.TotalProcessorTime.TotalSeconds - $c1) -lt 4) {
                    # must survive a while without a new crash dump
                    Start-Sleep 25
                    $crashes = Join-Path $docs "crashes"
                    $newCrash = Get-ChildItem $crashes -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $start }
                    if ($newCrash -or @(Get-Process hoi4 -ErrorAction SilentlyContinue).Count -eq 0) { $result = "CRASHED after menu"; break }
                    $result = "MENU"; break
                }
            }
        }
    }
} finally {
    Copy-Item $backup $load -Force
    Remove-Item $backup
}
$crash = Get-ChildItem $crashDir -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $start } | Select-Object -First 1
if ($crash -and $result -eq "EXITED") { $result = "CRASHED ($($crash.Name))" }
"RESULT: $result after $([int]((Get-Date) - $start).TotalSeconds)s (mod list restored)"
if (-not $KeepRunning -and $result -ne "MENU") { Get-Process hoi4 -ErrorAction SilentlyContinue | Stop-Process -Force }
"--- game.log tail"; Get-Content (Join-Path $logs "game.log") -Tail 4
"--- error.log: $((Get-Content (Join-Path $logs 'error.log')).Count) lines"
