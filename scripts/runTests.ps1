param(
    [ValidatePattern("^[A-Za-z0-9_-]+$")]
    [string]$TestType = "funcional",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$PytestArguments
)

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$reportingRoot = Join-Path $repositoryRoot "reporting"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportDirectory = Join-Path $reportingRoot "${TestType}_${timestamp}"
$allureDirectory = Join-Path $reportDirectory "allureResults"
$sharedAllureDirectory = Join-Path $reportingRoot "allureResults"

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

    New-Item -ItemType Directory -Force -Path $DestinationDirectory | Out-Null
    foreach ($file in (Get-ChildItem -LiteralPath $SourceDirectory -File -Force)) {
        Copy-Item -LiteralPath $file.FullName -Destination (Join-Path $DestinationDirectory $file.Name) -Force
    }
}

New-Item -ItemType Directory -Force -Path $allureDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $sharedAllureDirectory | Out-Null
$sharedAllureDirectory = (Resolve-Path -LiteralPath $sharedAllureDirectory).Path
$env:AUTOMATION_REPORT_DIR = $reportDirectory

& python -m pytest -m $TestType --test-type $TestType --alluredir $allureDirectory @PytestArguments
$testExitCode = $LASTEXITCODE

try {
    Copy-AllureFiles -SourceDirectory $allureDirectory -DestinationDirectory $sharedAllureDirectory
    Write-Host "Shared Allure results: $sharedAllureDirectory"
} catch {
    Write-Warning "Could not aggregate Allure results into $sharedAllureDirectory`: $($_.Exception.Message)"
}

$htmlDirectory = Join-Path $reportDirectory "allureReport"
$allureCommand = Resolve-AllureCommand
if ($allureCommand) {
    try {
        & $allureCommand.Path generate $allureDirectory --clean -o $htmlDirectory
        if ($LASTEXITCODE -eq 0) {
            Write-Host "HTML report: $htmlDirectory"
        } else {
            Write-Warning "Allure report generation failed with exit code $LASTEXITCODE; results remain available."
        }
    } catch {
        Write-Warning "Allure report generation failed: $($_.Exception.Message)"
    }
} else {
    Write-Warning "Allure CLI is not installed; results remain in $allureDirectory and $sharedAllureDirectory"
}

Write-Host "Report directory: $reportDirectory"
exit $testExitCode
