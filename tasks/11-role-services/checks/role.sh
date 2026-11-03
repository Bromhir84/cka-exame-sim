#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-svc-rbac get role svc-manager-role -o jsonpath="{.rules[0].resources[*]}" | grep -q services
for v in get list create delete; do kubectl -n arch-svc-rbac get role svc-manager-role -o jsonpath="{.rules[0].verbs[*]}" | grep -q "$v"; done
