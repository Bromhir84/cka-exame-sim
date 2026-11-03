#!/usr/bin/env bash
set -euo pipefail

[ "$(kubectl -n broken-app get deploy frontend -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ]
