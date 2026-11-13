# Copy the game's own screenshots into docs/screenshots/ so that whoever works on the mod without the
# game can SEE the result.
#
# How to use it:
#   1. Start the game with the mod as usual and load into a country.
#   2. Press F11 for every picture you want (the game saves them itself).
#      Useful ones: fully zoomed out; zoomed in on Italy; after right-clicking a country (diplomacy).
#   3. Quit, then:   powershell -ExecutionPolicy Bypass -File tools/collect_screenshots.ps1
#   4. git add docs/screenshots ; commit ; push
#
# This script only copies files (newest first) and shrinks them to JPEG. It does not start the game,
# move the mouse, press keys or read the screen - the earlier tools/screenshot.ps1 did, and Windows
# Defender blocked it for that.
param(
    [int]$Count = 8,          # how many of the newest screenshots to take
    [int]$MaxWidth = 1920
)
$ErrorActionPreference = "Stop"
$mod = Split-Path -Parent $PSScriptRoot
$src = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "Paradox Interactive\Hearts of Iron IV\Screenshots"
$out = Join-Path $mod "docs\screenshots"
if (-not (Test-Path $src)) { "No screenshot folder yet: $src  (press F11 in the game first)"; exit 1 }
$files = Get-ChildItem $src -File | Where-Object { $_.Extension -match '^\.(png|jpg|jpeg|bmp|tga)$' } |
    Sort-Object LastWriteTime -Descending | Select-Object -First $Count
if (-not $files) { "No screenshots in $src  (press F11 in the game first)"; exit 1 }
New-Item -ItemType Directory -Force $out | Out-Null
Add-Type -AssemblyName System.Drawing
$jpeg = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
$quality = New-Object System.Drawing.Imaging.EncoderParameters 1
$quality.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter ([System.Drawing.Imaging.Encoder]::Quality, [long]85)
$n = 0
foreach ($f in $files) {
    $n++
    $stamp = $f.LastWriteTime.ToString("yyyyMMdd_HHmmss")
    $target = Join-Path $out ("{0}_{1:00}.jpg" -f $stamp, $n)
    try {
        $img = [System.Drawing.Image]::FromFile($f.FullName)
        $w = [Math]::Min($img.Width, $MaxWidth)
        $h = [int]($img.Height * $w / $img.Width)
        $small = New-Object System.Drawing.Bitmap $w, $h
        $g = [System.Drawing.Graphics]::FromImage($small)
        $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $g.DrawImage($img, 0, 0, $w, $h)
        $small.Save($target, $jpeg, $quality)
        $g.Dispose(); $small.Dispose(); $img.Dispose()
        "saved $target  ($($f.Name))"
    } catch {
        # a format Windows cannot read (e.g. TGA): copy it as it is
        $target = Join-Path $out ("{0}_{1:00}{2}" -f $stamp, $n, $f.Extension)
        Copy-Item $f.FullName $target -Force
        "copied $target  ($($f.Name))"
    }
}
"$n screenshots are in $out - please commit and push docs/screenshots."
