param([string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = "Stop"

$files = Get-ChildItem $ProjectRoot -Include "*.cs","*.xaml" -Recurse -File |
    Where-Object { $_.FullName -notmatch "[\\/](bin|obj|Scripts|\.git|\.vs)[\\/]" }

if (-not $files.Count) {
    Write-Host "No source files found." -ForegroundColor Red
    exit 2
}

$rules = @(
    @{
        Pattern = '(\bPage\.IsBusy\b|\bthis\.IsBusy\s*=|\bIsBusy\s*=\s*(true|false)\b|\bIsBusy\s*=\s*"\{Binding)'
        Name = 'Page.IsBusy / IsBusy'
        Replacement = 'Use ViewModel IsLoading property + ActivityIndicator in XAML'
        Source = 'https://learn.microsoft.com/en-us/dotnet/maui/whats-new/dotnet-10?view=net-maui-10.0'
    },
    @{
        Pattern = '\bDisplay(Alert|ActionSheet|Prompt)\s*\('
        Name = 'Synchronous-named DisplayAlert / DisplayActionSheet / DisplayPrompt'
        Replacement = 'Use DisplayAlertAsync, DisplayActionSheetAsync, or DisplayPromptAsync in .NET 10 MAUI'
        Source = 'https://learn.microsoft.com/en-us/dotnet/maui/whats-new/dotnet-10?view=net-maui-10.0'
    },
    @{
        Pattern = '\b(FadeTo|ScaleTo|TranslateTo|RotateTo|RelRotateTo|RelScaleTo)\s*\('
        Name = 'Legacy non-Async Animation API (FadeTo/ScaleTo/TranslateTo/RotateTo)'
        Replacement = 'Use FadeToAsync, ScaleToAsync, TranslateToAsync, or RotateToAsync'
        Source = 'https://learn.microsoft.com/en-us/dotnet/maui/whats-new/dotnet-10?view=net-maui-10.0'
    },
    @{
        Pattern = '(<\s*ListView\b|\bnew\s+ListView\b|<\s*TableView\b|\bnew\s+TableView\b)'
        Name = 'ListView / TableView'
        Replacement = 'Use CollectionView or VerticalStackLayout with BindableLayout'
        Source = 'https://learn.microsoft.com/en-us/dotnet/maui/whats-new/dotnet-10?view=net-maui-10.0'
    },
    @{
        Pattern = '\bMessagingCenter\b'
        Name = 'MessagingCenter (Obsolete)'
        Replacement = 'Use direct ViewModel/Service coordination, C# events, or WeakReferenceMessenger (CommunityToolkit.Mvvm.Messaging)'
        Source = 'https://learn.microsoft.com/en-us/dotnet/maui/whats-new/dotnet-10?view=net-maui-10.0'
    },
    @{
        Pattern = '\bDevice\.(BeginInvokeOnMainThread|StartTimer)\b'
        Name = 'Device.BeginInvokeOnMainThread / Device.StartTimer (Obsolete)'
        Replacement = 'Use MainThread.BeginInvokeOnMainThread or IDispatcher'
        Source = 'https://learn.microsoft.com/en-us/dotnet/maui/platform-integration/appmodel/main-thread'
    },
    @{
        Pattern = '(\[ObservableProperty\]|\[RelayCommand\]|\[NotifyCanExecuteChangedFor|\[NotifyPropertyChangedFor|:\s*ObservableObject\b|:\s*ObservableValidator\b)'
        Name = 'MVVM source generators / base classes ([ObservableProperty], [RelayCommand], ObservableObject)'
        Replacement = 'Use explicit Vanilla C# INotifyPropertyChanged properties and ICommand/Command in K12 projects'
        Source = 'MAUI Specialist Guardrails - Vanilla C# MVVM Policy'
    }
)

$found = $false

foreach ($rule in $rules) {
    foreach ($file in $files) {
        foreach ($match in Select-String -Path $file.FullName -Pattern $rule.Pattern) {
            $found = $true
            Write-Host "[REVIEW] $($rule.Name) -> $($file.FullName):$($match.LineNumber)" -ForegroundColor Yellow
            Write-Host "  Replacement: $($rule.Replacement)"
            Write-Host "  Reference:   $($rule.Source)"
        }
    }
}

function Test-IsStrictDebugMsBuildCondition([string]$Cond) {
    if ([string]::IsNullOrWhiteSpace($Cond)) { return $false }
    $trimmed = $Cond.Trim()
    if ($trimmed -match '!=' -or $trimmed -match '!' -or $trimmed -match '(?i)\bOr\b' -or $trimmed -match '(?i)Release') {
        return $false
    }
    return ($trimmed -match "(?i)['`"]?\$\(Configuration\)['`"]?\s*==\s*['`"]Debug['`"]")
}

function Test-HasNegatedOrWiderMsBuildCondition([string]$Cond) {
    if ([string]::IsNullOrWhiteSpace($Cond)) { return $false }
    return ($Cond -match '!=' -or $Cond -match '!' -or $Cond -match '(?i)\bOr\b' -or $Cond -match '(?i)Release')
}

function Test-IsStrictDebugPreprocessorExpr([string]$Expr) {
    $clean = [regex]::Replace($Expr, '//.*$|/\*.*?\*/', '').Trim()
    if ([string]::IsNullOrWhiteSpace($clean)) { return $false }
    if ($clean -match '!' -or $clean -match '\|\|' -or $clean -match '\bRELEASE\b' -or $clean -match '\bfalse\b' -or $clean -match '\b0\b') {
        return $false
    }
    $parts = $clean -split '&&'
    $hasDebug = $false
    foreach ($part in $parts) {
        $tok = $part.Trim()
        while ($tok.StartsWith('(') -and $tok.EndsWith(')')) {
            $tok = $tok.Substring(1, $tok.Length - 2).Trim()
        }
        if ($tok -notmatch '^[A-Za-z_][A-Za-z0-9_]*$') {
            return $false
        }
        if ($tok -ceq 'DEBUG') {
            $hasDebug = $true
        }
    }
    return $hasDebug
}

# Check Microsoft.Maui.DevFlow Debug-only isolation (.csproj and MauiProgram.cs)
$csprojFiles = Get-ChildItem -Path $ProjectRoot -Recurse -Filter "*.csproj" -File |
    Where-Object { $_.FullName -notmatch "[\\/](bin|obj|\.git|\.vs)[\\/]" }

foreach ($csproj in $csprojFiles) {
    $xmlText = Get-Content -LiteralPath $csproj.FullName -Raw
    if ($xmlText -match 'Microsoft\.Maui\.DevFlow') {
        try {
            [xml]$xmlDoc = $xmlText
            $pkgNodes = $xmlDoc.SelectNodes("//*[local-name()='PackageReference' and contains(@Include, 'Microsoft.Maui.DevFlow')]")
            if (-not $pkgNodes -or $pkgNodes.Count -eq 0) {
                $found = $true
                Write-Host "[RELEASE LEAK] $($csproj.FullName): Microsoft.Maui.DevFlow reference must be a Debug-conditioned PackageReference (`Condition=`"'`$(Configuration)' == 'Debug'`"`)." -ForegroundColor Red
            }
            foreach ($node in $pkgNodes) {
                $itemCond = if ($node.Attributes["Condition"]) { $node.Attributes["Condition"].Value } else { "" }
                $parentCond = if ($node.ParentNode -and $node.ParentNode.Attributes -and $node.ParentNode.Attributes["Condition"]) { $node.ParentNode.Attributes["Condition"].Value } else { "" }
                $validDebug = ((Test-IsStrictDebugMsBuildCondition $itemCond) -or (Test-IsStrictDebugMsBuildCondition $parentCond)) `
                    -and (-not (Test-HasNegatedOrWiderMsBuildCondition $itemCond)) `
                    -and (-not (Test-HasNegatedOrWiderMsBuildCondition $parentCond))
                if (-not $validDebug) {
                    $found = $true
                    Write-Host "[RELEASE LEAK] $($csproj.FullName): Microsoft.Maui.DevFlow.Agent PackageReference must be strictly conditioned on Debug (`Condition=`"'`$(Configuration)' == 'Debug'`"`)." -ForegroundColor Red
                }
            }
        } catch {
            $found = $true
            Write-Host "[RELEASE LEAK] $($csproj.FullName): Could not verify strict Debug-only Condition on Microsoft.Maui.DevFlow.Agent." -ForegroundColor Red
        }
    }
}

$mauiProgramFiles = Get-ChildItem -Path $ProjectRoot -Recurse -Filter "MauiProgram.cs" -File |
    Where-Object { $_.FullName -notmatch "[\\/](bin|obj|\.git|\.vs)[\\/]" }

foreach ($mp in $mauiProgramFiles) {
    $mpLines = Get-Content -LiteralPath $mp.FullName
    $ifStack = New-Object System.Collections.Generic.List[bool]
    for ($i = 0; $i -lt $mpLines.Count; $i++) {
        $trimmed = $mpLines[$i].Trim()
        if ($trimmed -match '^#if\s+(.*)$') {
            $isDbg = Test-IsStrictDebugPreprocessorExpr $Matches[1]
            $ifStack.Add($isDbg)
            continue
        } elseif ($trimmed -match '^#(else|elif)\b') {
            if ($ifStack.Count -gt 0) {
                $ifStack[$ifStack.Count - 1] = $false
            }
            continue
        } elseif ($trimmed -match '^#endif\b') {
            if ($ifStack.Count -gt 0) {
                $ifStack.RemoveAt($ifStack.Count - 1)
            }
            continue
        }

        $codeNoComment = [regex]::Replace($trimmed, '//.*$', '')
        if ($codeNoComment -match 'AddMauiDevFlowAgent\s*\(' -or $codeNoComment -match '\busing\s+Microsoft\.Maui\.DevFlow') {
            $inStrictDebug = $ifStack.Contains($true)
            if (-not $inStrictDebug) {
                $found = $true
                Write-Host "[RELEASE LEAK] $($mp.FullName):$($i + 1) Microsoft.Maui.DevFlow usage (using / AddMauiDevFlowAgent()) must be wrapped strictly inside `#if DEBUG ... #endif`." -ForegroundColor Red
            }
        }
    }
}

if ($found) {
    Write-Host "RESULT: CHECK REQUIRED" -ForegroundColor Yellow
    exit 1
}

Write-Host "RESULT: PASS" -ForegroundColor Green
exit 0
