# Find out WHICH generated file crashes the game at start.
#
# For every variant of tools/make_variants.py: swap the simplified file(s) into the mod, start the game with
# -quickstart (through tools/test_launch.ps1), note whether it runs or crashes, and put the original files back.
# The result table goes to docs/crash_reports/bisect_<date>.md; for every run that did not start, the last 300 lines
# of error.log go to bisect_<date>_<variant>_error_tail.txt - commit and push docs/crash_reports.
#
# usage:  powershell -ExecutionPolicy Bypass -File tools/bisect_launch.ps1
#         powershell -ExecutionPolicy Bypass -File tools/bisect_launch.ps1 -Variants baseline,rivers_blank
#
# Takes about a minute per variant. Stops after "baseline" when the committed files already run
# (pass -All to run every variant anyway, e.g. to confirm with the no_region_defines control).
# Needs git and python (numpy) on the PATH. map/, history/states and common/defines must have no uncommitted changes,
# because the originals are restored with "git checkout".
param([string[]]$Variants = @(), [int]$TimeoutSec = 240, [string]$Python = "python", [switch]$All)

$mod = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$docs = Join-Path $env:USERPROFILE "Documents\Paradox Interactive\Hearts of Iron IV"
$crashDir = Join-Path $docs "crashes"
$logs = Join-Path $docs "logs"
$tmp = Join-Path $env:TEMP "ante_bisect"
$maker = Join-Path $PSScriptRoot "make_variants.py"
$launcher = Join-Path $PSScriptRoot "test_launch.ps1"
# -crash_data_log makes the crash report name the file that was read last
# (-quickstart is fine here: it only has to show whether the game survives the start. A quickstarted game draws
#  no country colours, so never judge the look of the map from it - see tools/test_launch.ps1.)
$extra = "-quickstart -start_tag=ROM -crash_data_log"

function Restore-Mod {
    & git -C $mod checkout -- map history/states common/defines common/bookmarks common/countries
    & git -C $mod clean -fdq -- gfx/FX                      # shader variants add files there
    if (& git -C $mod ls-files -- gfx/FX) { & git -C $mod checkout -- gfx/FX }
}

$dirty = & git -C $mod status --porcelain -- map history/states common/defines common/bookmarks common/countries gfx/FX
if ($dirty) {
    "Uncommitted changes in map/, history/states or common/defines - commit or stash them first:"
    $dirty
    exit 1
}
# "-File ... -Variants a,b" hands the list over as one string: split it here
$Variants = @($Variants | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($Variants.Count -eq 0) {
    $Variants = @(& $Python $maker --list | ForEach-Object { ($_ -split "`t")[0] })
}
$desc = @{}
& $Python $maker --list | ForEach-Object { $p = $_ -split "`t"; $desc[$p[0]] = $p[1] }

$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$reportDir = Join-Path $mod "docs\crash_reports"
New-Item -ItemType Directory -Force $reportDir | Out-Null
$rows = @()
try {
    foreach ($v in $Variants) {
        "=== $v"
        Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Force $tmp | Out-Null
        $files = @(& $Python $maker $v $tmp)
        if ($LASTEXITCODE -ne 0) {
            $rows += [pscustomobject]@{ Variant = $v; Result = "variant could not be generated"; Crash = ""; LastRead = ""; LastError = "" }
            continue
        }
        foreach ($rel in $files) {
            Copy-Item (Join-Path $tmp $rel) (Join-Path $mod $rel) -Force
        }
        $start = Get-Date
        $out = & $launcher -TimeoutSec $TimeoutSec -ExtraArgs $extra
        $result = [string]($out | Where-Object { $_ -like "RESULT:*" } | Select-Object -First 1)
        $result = $result -replace "^RESULT:\s*", "" -replace "\s*\(mod list restored\)", ""
        $crash = ""; $lastRead = ""; $lastError = ""
        $dump = Get-ChildItem $crashDir -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt $start } |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($dump) {
            $exc = Join-Path $dump.FullName "exception.txt"
            if (Test-Path $exc) {
                $crash = [string](Get-Content $exc | Where-Object { $_ -match "Unhandled Exception" } | Select-Object -First 1)
                $crash = $crash -replace "^.*at address\s*", ""
            }
            $meta = Join-Path $dump.FullName "meta.yml"
            if (Test-Path $meta) {
                $lastRead = (@(Get-Content $meta | Where-Object { $_ -match "Last" }) -join "; ")
            }
        }
        $errLog = Join-Path $logs "error.log"
        if (Test-Path $errLog) {
            $lastError = [string](Get-Content $errLog -Tail 1)
            if ($lastError.Length -gt 160) { $lastError = $lastError.Substring(0, 160) }
            # the engine's own warnings ("... This will likely crash the game", MAP_ERROR) are the best lead
            $alarms = @(Select-String -Path $errLog -Pattern "likely crash|MAP_ERROR").Count
            if ($alarms -gt 0) { $lastError = "[$alarms 'likely crash' / MAP_ERROR lines] " + $lastError }
            if ($result -notmatch "GAME RUNNING") {
                Get-Content $errLog -Tail 300 |
                    Set-Content -Path (Join-Path $reportDir ("bisect_" + $stamp + "_" + $v + "_error_tail.txt")) -Encoding UTF8
            }
        }
        Restore-Mod
        $rows += [pscustomobject]@{ Variant = $v; Result = $result; Crash = $crash; LastRead = $lastRead; LastError = $lastError }
        "    $result"
        if ($v -eq "baseline" -and $result -match "GAME RUNNING" -and -not $All) {
            "The committed files run - no need to test the variants (use -All to run them anyway)."
            break
        }
    }
} finally {
    Restore-Mod
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

$report = Join-Path $reportDir ("bisect_" + $stamp + ".md")
$commit = [string](& git -C $mod rev-parse --short HEAD)
$lines = @("# Bisect of the crash at game start ($stamp, commit $commit)", "",
           "Started with: ``$extra``. One variant per row, originals restored after each run.", "",
           "| Variant | What it changes | Result | Crash address | Last read (meta.yml) | Last line of error.log |",
           "|---|---|---|---|---|---|")
foreach ($r in $rows) {
    $cells = @($r.Variant, $desc[$r.Variant], $r.Result, $r.Crash, $r.LastRead, $r.LastError) |
        ForEach-Object { ([string]$_) -replace "\|", "/" }
    $lines += "| " + ($cells -join " | ") + " |"
}
Set-Content -Path $report -Value $lines -Encoding UTF8
""
$rows | Format-Table Variant, Result, Crash -AutoSize
"Report written to $report (plus the last 300 lines of error.log for every run that did not start) - please commit and push docs/crash_reports."
