#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n arch-sa-deploy get deploy sa-demo -o jsonpath="{.spec.template.spec.serviceAccountName}")" = "app-sa" ]
[ "$(kubectl -n arch-sa-deploy get deploy sa-demo -o jsonpath="{.spec.template.spec.containers[0].image}")" = "nginx:1.27" ]
