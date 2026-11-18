#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

CSPROJ=$(find "$PROJECT_ROOT" -type f -name "*.csproj" -not -path "*/bin/*" -not -path "*/obj/*" -not -path "*/Tests/*" -not -path "*.Tests/*" | head -n 1)

if [ -z "$CSPROJ" ]; then
    echo -e "\033[0;31mNo MAUI app .csproj found.\033[0m"
    exit 2
fi

TFM=$(grep -o -E '<TargetFrameworks?>[^<]+' "$CSPROJ" | sed -E 's/<TargetFrameworks?>[[:space:]]*//' | head -n 1 || true)

echo "Project: $CSPROJ"
echo "Target framework: $TFM"

if [[ ! "$TFM" =~ net(8|9|10|11)\.0 ]]; then
    echo -e "\033[0;31mERROR: TargetFramework '$TFM' is not a supported modern .NET MAUI target (net8.0, net9.0, net10.0, or net11.0).\033[0m"
    echo -e "\033[0;33mRESULT: CHECK REQUIRED\033[0m"
    exit 1
fi

if [[ "$TFM" =~ net11\.0 ]]; then
    echo -e "\033[0;33mNOTICE: .NET 11 MAUI is preview. Avoid preview-only APIs unless required.\033[0m"
else
    echo -e "\033[0;32mTarget framework verified ($TFM).\033[0m"
fi

WHAT_NEW="https://learn.microsoft.com/en-us/dotnet/maui/whats-new/?view=net-maui-10.0"
if command -v curl >/dev/null 2>&1; then
    if ! curl -s -f --max-time 5 -o /dev/null "$WHAT_NEW"; then
        echo -e "\033[0;90mOFFLINE NOTICE: Microsoft Learn could not be reached in this network environment; local TFM validation passed.\033[0m"
    fi
fi

echo -e "\033[0;32mRESULT: PASS\033[0m"
exit 0
