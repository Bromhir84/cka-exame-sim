#!/usr/bin/env bash
set -euo pipefail
CIP=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.clusterIP}')
[ "$CIP" = "None" ]
SEL=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "store" ]
PORT=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.ports[0].port}')
[ "$PORT" = "80" ]
exit 0
