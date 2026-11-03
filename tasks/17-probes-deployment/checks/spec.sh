#!/usr/bin/env bash
set -euo pipefail
[ "$(kubectl -n wl-probes get deploy probed -o jsonpath="{.spec.replicas}")" = "2" ]
[ "$(kubectl -n wl-probes get deploy probed -o jsonpath="{.spec.template.spec.containers[0].readinessProbe.httpGet.path}")" = "/" ]
[ "$(kubectl -n wl-probes get deploy probed -o jsonpath="{.spec.template.spec.containers[0].livenessProbe.httpGet.path}")" = "/" ]
