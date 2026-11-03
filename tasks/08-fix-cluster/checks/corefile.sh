#!/usr/bin/env bash
set -euo pipefail

COREFILE=$(kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}')
echo "$COREFILE" | grep -q forward
echo "$COREFILE" | grep -qv notaplugin
