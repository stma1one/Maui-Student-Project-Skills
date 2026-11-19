param(
    [ValidateSet("student", "code")]
    [string]$Mode = "student",
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,
    [bool]$IncludeTests = $true,
    [ValidateSet("combined", "agent", "student")]
    [string]$TestManagementMode = "combined"
)

$configPath = Join-Path $ProjectRoot ".agents\MAUI-Agent-Mode.json"
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $configPath) | Out-Null

if ($Mode -eq "student") {
    $value = $true
    $label = "MAXIMIZE STUDENT CAPABILITY"
} else {
    $value = $false
    $label = "MAXIMIZE CODE GENERATED"
}

$effectiveTestWriter = if (-not $IncludeTests) { "ignored (includeTests=false)" } elseif (-not $value) { "agent (enforced in MAXIMIZE CODE GENERATED mode)" } else { $TestManagementMode }

$config = [ordered]@{
    studentCapabilityMode = $value
    includeTests = $IncludeTests
    testManagementMode = $TestManagementMode
    description = [ordered]@{
        true = "MAXIMIZE STUDENT CAPABILITY: staged planning, concept gates, ownership negotiation, student practice, and verification."
        false = "MAXIMIZE CODE GENERATED: implement complete feature slices efficiently while preserving verification and learning documentation when configured."
        includeTests = "Boolean (default: true). Whether the project provisions, writes, and validates xUnit tests (<AppName>.Tests). When false, testManagementMode is ignored and tests are skipped."
        testManagementMode = [ordered]@{
            combined = "(Default) Combined: Agent creates and explains tests at the end of each stage/slice, proposes selected test cases for the student to write, and documents all tests in Learning/Test-Documentation.md."
            agent = "Agent: Agent independently writes and runs xUnit tests as part of the slice workflow and documents them in Learning/Test-Documentation.md."
            student = "Student: Agent guides the student through a Socratic dialogue to identify required test cases and coaches the student in writing the xUnit tests."
            maximizeCodeOverride = "When studentCapabilityMode is false (MAXIMIZE CODE GENERATED) and includeTests is true, the agent ALWAYS writes and runs all tests regardless of testManagementMode and documents them in Learning/Test-Documentation.md."
        }
    }
} | ConvertTo-Json -Depth 5

$config | Set-Content $configPath -Encoding UTF8

Write-Host "Instructor updated agent mode to: $label (includeTests=$IncludeTests, testManagementMode=$TestManagementMode -> effective: $effectiveTestWriter) in $configPath" -ForegroundColor Green
