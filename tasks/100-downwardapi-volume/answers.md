## Goal
DownwardAPI volume with pod name.

## Steps
```bash
kubectl -n stor-down100 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: down-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    volumeMounts:
    - name: podinfo
      mountPath: /etc/podinfo
  volumes:
  - name: podinfo
    downwardAPI:
      items:
      - path: pod_name
        fieldRef:
          fieldPath: metadata.name
EOF
```
