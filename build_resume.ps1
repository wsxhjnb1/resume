param(
    [string]$TectonicPath = $env:CODEX_TECTONIC_PATH
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($TectonicPath) -or -not (Test-Path -LiteralPath $TectonicPath)) {
    $TectonicPath = (Get-Command tectonic -ErrorAction Stop).Source
}
$resumeRoot = $PSScriptRoot
$resumeOutput = Join-Path $resumeRoot 'output\pdf'
$resumeLogs = Join-Path $resumeRoot 'tmp\pdfs'
New-Item -ItemType Directory -Force -Path $resumeOutput, $resumeLogs | Out-Null
Push-Location $resumeRoot
try {
    foreach ($resumeLanguage in @('en', 'zh')) {
        $resumeSource = "yuhao_xie_resume_$resumeLanguage.tex"
        $resumeLog = Join-Path $resumeLogs "build_$resumeLanguage.log"
        & $TectonicPath -X compile --outdir $resumeOutput --outfmt pdf --print --untrusted $resumeSource 2>&1 |
            Tee-Object -FilePath $resumeLog
        if ($LASTEXITCODE -ne 0) {
            throw "Compilation failed for $resumeSource. See $resumeLog."
        }
        if (Select-String -LiteralPath $resumeLog -Pattern 'Overfull \\[hv]box|Missing character:|Undefined control sequence' -Quiet) {
            throw "A layout or character error was found in $resumeLog."
        }
    }
} finally {
    Pop-Location
}
