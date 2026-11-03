#!/usr/bin/env bash
set -euo pipefail
SUB=$(kubectl -n arch-events60 get rolebinding event-watcher-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "event-watcher" ]
exit 0
