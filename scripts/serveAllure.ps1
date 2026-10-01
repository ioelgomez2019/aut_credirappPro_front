param(
    [ValidateRange(1, 65535)]
    [int]$Port = 8080
)

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$reportingRoot = Join-Path $repositoryRoot "reporting"
$sharedAllureDirectory = Join-Path $reportingRoot "allureResults"
$reportDirectory = Join-Path $reportingRoot "allureReport"

function Resolve-AllureCommand {
    $command = Get-Command allure.cmd -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) {
        return $command
    }

    $command = Get-Command allure.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command) {
        return $command
    }

    $command = Get-Command allure -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($command -and $command.CommandType -eq "Application" -and $command.Path -notlike "*.ps1") {
        return $command
    }

    return $null
}

function Copy-AllureFiles {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceDirectory,
        [Parameter(Mandatory = $true)]
        [string]$DestinationDirectory
    )

    $sourcePath = (Resolve-Path -LiteralPath $SourceDirectory).Path.TrimEnd('\')
    $destinationPath = (Resolve-Path -LiteralPath $DestinationDirectory).Path.TrimEnd('\')
    if ($sourcePath -ieq $destinationPath) {
        return
    }

    foreach ($file in (Get-ChildItem -LiteralPath $SourceDirectory -File -Force)) {
        Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $DestinationDirectory $file.Name) -Force
    }
}

function Aggregate-TimestampedRuns {
    foreach ($runDirectory in (Get-ChildItem -LiteralPath $reportingRoot -Directory -Force |
            Where-Object { $_.Name -match '^[A-Za-z0-9_-]+_\d{8}_\d{6}$' })) {
        $runAllureDirectory = Join-Path $runDirectory.FullName "allureResults"
        if (Test-Path -LiteralPath $runAllureDirectory -PathType Container) {
            Copy-AllureFiles -SourceDirectory $runAllureDirectory -DestinationDirectory $sharedAllureDirectory
        }
    }
}

function Get-AllureSnapshot {
    $snapshot = Get-ChildItem -LiteralPath $sharedAllureDirectory -File -Force |
        Where-Object { $_.Name -ne ".gitkeep" } |
        ForEach-Object { "{0}|{1}|{2}" -f $_.Name, $_.Length, $_.LastWriteTimeUtc.Ticks }
    return ($snapshot -join "`n")
}

function Generate-AllureReport {
    $allureCommand = Resolve-AllureCommand
    if (-not $allureCommand) {
        Write-Warning "Allure CLI is not installed; keeping results in $sharedAllureDirectory"
        return
    }

    try {
        & $allureCommand.Path generate $sharedAllureDirectory --clean -o $reportDirectory
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Allure report generation failed with exit code $LASTEXITCODE"
        }
    } catch {
        Write-Warning "Allure report generation failed: $($_.Exception.Message)"
    }
}

New-Item -ItemType Directory -Force -Path $reportingRoot, $sharedAllureDirectory, $reportDirectory | Out-Null
try {
    Aggregate-TimestampedRuns
} catch {
    Write-Warning "Could not aggregate existing Allure results: $($_.Exception.Message)"
}
Generate-AllureReport
$lastSnapshot = Get-AllureSnapshot

$pythonCommand = Get-Command python -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandType -eq "Application" } |
    Select-Object -First 1
if (-not $pythonCommand) {
    throw "Python executable was not found; cannot serve the Allure report."
}

$httpProcess = $null
try {
    $httpProcess = Start-Process -FilePath $pythonCommand.Path `
        -ArgumentList @("-m", "http.server", $Port, "--bind", "127.0.0.1") `
        -WorkingDirectory $reportDirectory -WindowStyle Hidden -PassThru
    Write-Host "Allure report: http://127.0.0.1:$Port/"
    Write-Host "Press Ctrl+C to stop."

    while ($true) {
        Start-Sleep -Seconds 2
        if ($httpProcess.HasExited) {
            Write-Warning "The Python HTTP server stopped unexpectedly."
            break
        }

        $currentSnapshot = Get-AllureSnapshot
        if ($currentSnapshot -ne $lastSnapshot) {
            Generate-AllureReport
            $lastSnapshot = $currentSnapshot
        }
    }
} finally {
    if ($httpProcess -and -not $httpProcess.HasExited) {
        Stop-Process -Id $httpProcess.Id -Force -ErrorAction SilentlyContinue
        $httpProcess.WaitForExit(2000)
    }
}
