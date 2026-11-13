# Start the game with this mod (quickstart), take screenshots of the map and save them under
# docs/screenshots/ - so that whoever works on the mod without the game can SEE the result.
#
# usage:  powershell -ExecutionPolicy Bypass -File tools/screenshot.ps1
#         powershell -ExecutionPolicy Bypass -File tools/screenshot.ps1 -Tag CAR -Zooms 0,8,20,40
#         powershell -ExecutionPolicy Bypass -File tools/screenshot.ps1 -Attach            (game already running)
#         powershell -ExecutionPolicy Bypass -File tools/screenshot.ps1 -Variants colour   (visual bisect, see below)
#
# -Zooms     one picture per number, taken after zooming OUT by that many mouse-wheel notches from the
#            view the game starts in (0 = the start view). A last picture ("diplo") is taken after a
#            right-click in the middle of the screen: it should show the diplomacy colours.
# -Variants  names from "python tools/make_variants.py --list" (comma separated), or "colour" for the
#            set that hunts the grey-map bug. For each variant the files are swapped in, the game is
#            started, pictures are taken, and the originals are restored with git.
# The game is closed afterwards unless -KeepRunning is given. Commit and push docs/screenshots.
param([string]$Tag = "ROM", [int[]]$Zooms = @(0, 8, 20, 40), [int]$WaitSec = 25, [int]$TimeoutSec = 300,
      [string[]]$Variants = @(), [switch]$Attach, [switch]$KeepRunning, [string]$Python = "python")

$mod = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$docs = Join-Path $env:USERPROFILE "Documents\Paradox Interactive\Hearts of Iron IV"
$game = "D:\SteamLibrary\steamapps\common\Hearts of Iron IV"
$logs = Join-Path $docs "logs"
$load = Join-Path $docs "dlc_load.json"
$backup = "$load.ante_backup"
$outDir = Join-Path $mod "docs\screenshots"
$tmp = Join-Path $env:TEMP "ante_variant"
$maker = Join-Path $PSScriptRoot "make_variants.py"
$restore = @("map", "history/states", "common/defines", "common/bookmarks", "common/countries")
New-Item -ItemType Directory -Force $outDir | Out-Null

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class AnteWin {
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, int data, UIntPtr extra);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
"@
[void][AnteWin]::SetProcessDPIAware()
$jpeg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
$quality = New-Object System.Drawing.Imaging.EncoderParameters 1
$quality.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality, [long]85)

function Save-Window([IntPtr]$handle, [string]$path) {
    $r = New-Object AnteWin+RECT
    if (-not [AnteWin]::GetWindowRect($handle, [ref]$r)) { throw "window not found" }
    $w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
    if ($w -le 0 -or $h -le 0) { throw "window has no size" }
    $bmp = New-Object System.Drawing.Bitmap $w, $h
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $h))
    $g.Dispose()
    if ($w -gt 1600) {          # small enough for git, large enough to judge colours and borders
        $small = New-Object System.Drawing.Bitmap $bmp, 1600, ([int]($h * 1600 / $w))
        $bmp.Dispose(); $bmp = $small
    }
    $bmp.Save($path, $jpeg, $quality)
    $bmp.Dispose()
    return @(($r.Left + [int]($w / 2)), ($r.Top + [int]($h / 2)))
}

function Take-Pictures([string]$prefix) {
    $proc = Get-Process hoi4 -ErrorAction SilentlyContinue | Sort-Object WorkingSet64 -Descending | Select-Object -First 1
    if (-not $proc -or $proc.MainWindowHandle -eq [IntPtr]::Zero) { "No HoI4 window found."; return }
    [void][AnteWin]::SetForegroundWindow($proc.MainWindowHandle)
    Start-Sleep 2
    $done = 0
    $centre = $null
    foreach ($z in ($Zooms | Sort-Object)) {
        $file = "{0}_zoom{1:00}.jpg" -f $prefix, $z
        $centre = Save-Window $proc.MainWindowHandle $file          # also tells us where the window is
        if ($z -gt $done) {
            [void][AnteWin]::SetCursorPos($centre[0], $centre[1])
            for ($i = $done; $i -lt $z; $i++) {
                [AnteWin]::mouse_event(0x0800, 0, 0, -120, [UIntPtr]::Zero)      # wheel down = zoom out
                Start-Sleep -Milliseconds 120
            }
            $done = $z
            Start-Sleep 3
            [void](Save-Window $proc.MainWindowHandle $file)
        }
        "saved $file"
    }
    if ($centre) {
        # right-click in the middle: the diplomacy view of the country there; the map should now show
        # that country green, its enemies red, its allies blue
        [void][AnteWin]::SetCursorPos($centre[0], $centre[1])
        [AnteWin]::mouse_event(0x0008, 0, 0, 0, [UIntPtr]::Zero)
        Start-Sleep -Milliseconds 80
        [AnteWin]::mouse_event(0x0010, 0, 0, 0, [UIntPtr]::Zero)
        Start-Sleep 3
        [void](Save-Window $proc.MainWindowHandle ($prefix + "_diplo.jpg"))
        "saved ${prefix}_diplo.jpg"
    }
    $err = Join-Path $logs "error.log"
    if (Test-Path $err) {       # colour / graphics complaints show up at the end of error.log
        Get-Content $err -Tail 200 | Set-Content -Path ($prefix + "_error_tail.txt") -Encoding UTF8
    }
}

function Run-Game([string]$prefix) {
    Get-Process hoi4 -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep 2
    if (-not (Test-Path $backup)) { Copy-Item $load $backup }
    try {
        Set-Content -Path $load -Value '{"enabled_mods":["mod/ante_imperium.mod"],"disabled_dlcs":[]}' -Encoding ascii -NoNewline
        $begin = Get-Date
        Start-Process -FilePath "$game\hoi4.exe" -WorkingDirectory $game -ArgumentList "-gdpr-compliant -quickstart -start_tag=$Tag -crash_data_log"
        $running = $false
        while (((Get-Date) - $begin).TotalSeconds -lt $TimeoutSec) {
            Start-Sleep 5
            if (@(Get-Process hoi4 -ErrorAction SilentlyContinue).Count -eq 0) { break }
            if (Select-String -Path (Join-Path $logs "game.log") -Pattern "Launching SINGLEPLAYER" -Quiet) { $running = $true; break }
        }
        if (-not $running) { "The game did not reach a running session - no screenshots for $prefix."; return }
        Start-Sleep $WaitSec          # let the map finish drawing
        Take-Pictures $prefix
    } finally {
        Copy-Item $backup $load -Force
        Remove-Item $backup
        if (-not $KeepRunning) { Get-Process hoi4 -ErrorAction SilentlyContinue | Stop-Process -Force }
    }
}

function Restore-Mod {
    & git -C $mod checkout -- $restore
    & git -C $mod clean -fdq -- gfx/FX                      # shader variants add files there
    if (& git -C $mod ls-files -- gfx/FX) { & git -C $mod checkout -- gfx/FX }
}

$stamp = Get-Date -Format "yyyyMMdd_HHmm"
$Variants = @($Variants | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($Variants -contains "colour") {
    $Variants = @("baseline", "date_hour0", "daynight_off", "daynight_fit", "date_1936", "colours_bright", "no_impassable")
}

if ($Attach) {
    Take-Pictures (Join-Path $outDir ($stamp + "_" + $Tag))
} elseif ($Variants.Count -eq 0) {
    Run-Game (Join-Path $outDir ($stamp + "_" + $Tag))
} else {
    $dirty = & git -C $mod status --porcelain -- $restore gfx/FX
    if ($dirty) {
        "Uncommitted changes in $($restore -join ', ') or gfx/FX - commit (or remove) them first:"
        $dirty
        exit 1
    }
    try {
        foreach ($v in $Variants) {
            "=== $v"
            Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
            New-Item -ItemType Directory -Force $tmp | Out-Null
            $files = @(& $Python $maker $v $tmp)
            if ($LASTEXITCODE -ne 0) { "variant $v could not be generated"; continue }
            foreach ($rel in $files) {
                $dest = Join-Path $mod $rel
                New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
                Copy-Item (Join-Path $tmp $rel) $dest -Force
            }
            Run-Game (Join-Path $outDir ($stamp + "_" + $v))
            Restore-Mod
        }
    } finally {
        Restore-Mod
        Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}
"Screenshots are in $outDir - please commit and push docs/screenshots."
