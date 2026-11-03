# DaemonSet

In namespace `wl-ds` create DaemonSet `node-agent` that:

- uses image `busybox:1.36`
- container name `agent`
- command `["sleep","3600"]`
- labels pods with `app=node-agent`

Ensure DaemonSet pods are Ready on schedulable nodes.
