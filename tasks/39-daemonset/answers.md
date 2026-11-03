## Goal
DaemonSet `node-agent` on every node.

## Steps
```bash
kubectl -n wl-ds apply -f - <<'EOF'
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-agent
  namespace: wl-ds
spec:
  selector:
    matchLabels: {app: node-agent}
  template:
    metadata:
      labels: {app: node-agent}
    spec:
      containers:
        - name: agent
          image: busybox:1.36
          command: ["sleep", "3600"]
EOF
kubectl -n wl-ds rollout status ds/node-agent
```
