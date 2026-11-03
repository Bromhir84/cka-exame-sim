#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-secrets get role secret-reader-role -o jsonpath="{.rules[0].resources[*]}" | grep -q secrets
for v in get list watch; do kubectl -n arch-secrets get role secret-reader-role -o jsonpath="{.rules[0].verbs[*]}" | grep -q "$v"; done
