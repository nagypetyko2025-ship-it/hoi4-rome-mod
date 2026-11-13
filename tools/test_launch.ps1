# Launch HoI4 with ONLY Ante Imperium enabled, wait for the main menu / the running game or a failure,
# then restore the user's mod list and say what happened.
#
#   powershell -ExecutionPolicy Bypass -File tools/test_launch.ps1                 -> stops at the MAIN MENU
#   powershell -ExecutionPolicy Bypass -File tools/test_launch.ps1 -Continue       -> loads the last save game
#   ... -KeepRunning      leave the game open (to play / to press F11 for screenshots)
#   ... -Game "X:\...\Hearts of Iron IV"   if the game is not found by itself (or set HOI4_DIR)
#
# How to look at the map:  start once through the menu (Single Player -> Start), let the clock run past the
# first of a month (the game writes autosave.hoi4), from then on  -Continue  jumps straight into that game
# without a click. After tools/world.py changed the world, start a new game through the menu again.
#
# DO NOT use the engine's own  -quickstart  to look at the map: a quickstarted game draws NO COUNTRY
# COLOURS at all (bare terrain with names - the base game does the same). It cost three test rounds
# (6-8) before this was found on 2026-11-13. It is still fine for crash tests (tools/bisect_launch.ps1).
param(
    [int]$TimeoutSec = 360,
    [switch]$KeepRunning,
    [switch]$Continue,
    [string]$ExtraArgs = "",
    [string]$Game = ""
)

$mod = Split-Path -Parent $PSScriptRoot
$docs = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "Paradox Interactive\Hearts of Iron IV"
$logs = Join-Path $docs "logs"
$load = Join-Path $docs "dlc_load.json"
$backup = "$load.ante_backup"

# --- where is the game?
if (-not $Game) { $Game = $env:HOI4_DIR }
if (-not $Game) {
    $tails = "SteamLibrary\steamapps\common\Hearts of Iron IV", "Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV",
             "Steam\steamapps\common\Hearts of Iron IV", "Games\Steam\steamapps\common\Hearts of Iron IV"
    foreach ($d in "D", "E", "C", "F", "G", "H", "I", "J") {
        foreach ($t in $tails) {
            if (-not $Game -and (Test-Path "${d}:\$t\hoi4.exe")) { $Game = "${d}:\$t" }
        }
    }
}
if (-not $Game -or -not (Test-Path (Join-Path $Game "hoi4.exe"))) {
    "RESULT: hoi4.exe not found - pass -Game ""X:\...\Hearts of Iron IV"" or set HOI4_DIR"; exit 1
}
if (-not (Test-Path $load)) { "RESULT: $load not found - start the game once through Steam first"; exit 1 }

# --- the launcher descriptor (Documents\...\mod\ante_imperium.mod) = descriptor.mod + path to this folder
New-Item -ItemType Directory -Force (Join-Path $docs "mod") | Out-Null
$desc = (Get-Content (Join-Path $mod "descriptor.mod") -Raw).TrimEnd() + "`n" + 'path="' + ($mod -replace '\\', '/') + '"' + "`n"
[IO.File]::WriteAllText((Join-Path $docs "mod\ante_imperium.mod"), $desc)

$launch = "-gdpr-compliant " + $ExtraArgs
if ($ExtraArgs -match "quickstart") {
    "NOTE: -quickstart draws no country colours (engine behaviour) - use it for crash tests only, never to judge the map."
}
if ($Continue) {
    $saves = Join-Path $docs "save games"
    if (-not (Test-Path $saves) -or -not (Get-ChildItem $saves -Filter *.hoi4 -ErrorAction SilentlyContinue)) {
        "RESULT: no save game yet. Run this script without -Continue, start a game through the menu"
        "        (Single Player -> Start), unpause until the first of a month (autosave), then use -Continue."
        exit 1
    }
    $launch += " --continuelastsave"
}

Get-Process hoi4 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
if (-not (Test-Path $backup)) { Copy-Item $load $backup }
Set-Content -Path $load -Value '{"enabled_mods":["mod/ante_imperium.mod"],"disabled_dlcs":[]}' -Encoding ascii -NoNewline
$start = Get-Date
Start-Process -FilePath (Join-Path $Game "hoi4.exe") -WorkingDirectory $Game -ArgumentList $launch

$result = "TIMEOUT"
$crashDir = Join-Path $docs "crashes"
$gameLog = Join-Path $logs "game.log"
$inGame = $Continue -or ($ExtraArgs -match "start_tag")
try {
    while (((Get-Date) - $start).TotalSeconds -lt $TimeoutSec) {
        Start-Sleep 5
        $procs = @(Get-Process hoi4 -ErrorAction SilentlyContinue)
        if ($procs.Count -eq 0) { $result = "EXITED"; break }
        $titles = ($procs | ForEach-Object { $_.MainWindowTitle }) -join " | "
        if ($titles -match "Fail|Error|error") { $result = "FAILED: $titles"; break }
        $fresh = (Test-Path $gameLog) -and ((Get-Item $gameLog).LastWriteTime -gt $start)
        # a session is running: loaded save game, or the engine's quickstart
        if ($fresh -and (Select-String -Path $gameLog -Pattern "Launching SINGLEPLAYER" -Quiet)) {
            Start-Sleep 30
            $newCrash = Get-ChildItem $crashDir -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $start }
            if ($newCrash -or @(Get-Process hoi4 -ErrorAction SilentlyContinue).Count -eq 0) { $result = "CRASHED at game start"; break }
            $result = "GAME RUNNING"; break
        }
        if ($inGame) { continue }
        # history is executed for the default bookmark when the main menu is built
        if ($fresh -and (Select-String -Path $gameLog -Pattern "Executing History from 2\.1\.1\.1" -Quiet)) {
            $p = $procs | Sort-Object WorkingSet64 -Descending | Select-Object -First 1
            if ($p.WorkingSet64 -gt 1.5GB) {
                $c1 = $p.TotalProcessorTime.TotalSeconds; Start-Sleep 6; $p.Refresh()
                $titles = (@(Get-Process hoi4 -ErrorAction SilentlyContinue) | ForEach-Object { $_.MainWindowTitle }) -join " | "
                if ($titles -match "Fail|Error|error") { $result = "FAILED: $titles"; break }
                if (($p.TotalProcessorTime.TotalSeconds - $c1) -lt 4) {
                    # must survive a while without a new crash dump
                    Start-Sleep 25
                    $newCrash = Get-ChildItem $crashDir -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $start }
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
if ($result -eq "MENU") { "        The game waits in the main menu: Single Player -> Start shows the map with country colours." }

$errLog = Join-Path $logs "error.log"
if (Test-Path $errLog) {
    $lines = @(Get-Content $errLog)
    "error.log: $($lines.Count) lines (most of them: base game scripts naming countries this mod does not have)"
    $mapLines = $lines | Where-Object { $_ -match "MAP_ERROR|will likely crash|Failed to|Exception in" }
    if ($mapLines) { "map / engine messages:"; $mapLines | Select-Object -First 25 }
}
if (-not $KeepRunning -and $result -ne "TIMEOUT") {
    Get-Process hoi4 -ErrorAction SilentlyContinue | Stop-Process -Force
} elseif ($KeepRunning) {
    "The game is left running (-KeepRunning). F11 takes a screenshot; tools/collect_screenshots.ps1 gathers them."
}
