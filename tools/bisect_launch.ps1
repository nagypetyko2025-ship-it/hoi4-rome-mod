# Find out WHICH generated file crashes the game at start.
#
# For every variant of tools/make_variants.py: swap the simplified file(s) into the mod, start the game with
# -quickstart (through tools/test_launch.ps1), note whether it runs or crashes, and put the original files back.
# The result table is written to docs/crash_reports/bisect_<date>.md - commit that file.
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
$extra = "-quickstart -start_tag=ROM -crash_data_log"

$dirty = & git -C $mod status --porcelain -- map history/states common/defines
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
        }
        & git -C $mod checkout -- map history/states common/defines
        $rows += [pscustomobject]@{ Variant = $v; Result = $result; Crash = $crash; LastRead = $lastRead; LastError = $lastError }
        "    $result"
        if ($v -eq "baseline" -and $result -match "GAME RUNNING" -and -not $All) {
            "The committed files run - no need to test the variants (use -All to run them anyway)."
            break
        }
    }
} finally {
    & git -C $mod checkout -- map history/states common/defines
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}

$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$report = Join-Path $mod "docs\crash_reports\bisect_$stamp.md"
New-Item -ItemType Directory -Force (Split-Path $report) | Out-Null
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
"Report written to $report - please commit and push it."
