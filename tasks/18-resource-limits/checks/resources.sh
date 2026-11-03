#!/usr/bin/env bash
set -euo pipefail

NS=wl-limits
[ "$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')" = "50m" ]
[ "$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}')" = "32Mi" ]
[ "$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.limits.cpu}')" = "200m" ]
[ "$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.limits.memory}')" = "128Mi" ]
