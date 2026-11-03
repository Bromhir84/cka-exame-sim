#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-deploy59 get sa deployer >/dev/null
REF=$(kubectl -n arch-deploy59 get rolebinding deploy-manager-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "deploy-manager" ]
exit 0
