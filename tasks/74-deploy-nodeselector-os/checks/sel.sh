#!/usr/bin/env bash
set -euo pipefail
OS=$(kubectl -n wl-os74 get deploy linux-web -o jsonpath='{.spec.template.spec.nodeSelector.kubernetes\.io/os}')
[ "$OS" = "linux" ]
exit 0
