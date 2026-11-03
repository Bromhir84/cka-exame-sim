## Goal
Projected ConfigMap+Secret volume.

## Steps
```bash
kubectl -n stor-proj93 create cm p-cm --from-literal=a=1
kubectl -n stor-proj93 create secret generic p-sec --from-literal=b=2
kubectl -n stor-proj93 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: proj-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    volumeMounts:
    - name: proj
      mountPath: /projected
  volumes:
  - name: proj
    projected:
      sources:
      - configMap:
          name: p-cm
      - secret:
          name: p-sec
EOF
```
