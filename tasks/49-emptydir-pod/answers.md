## Goal
Pod with emptyDir `cache` at `/cache`.

## Steps
```bash
kubectl -n stor-empty apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: cache-pod
  namespace: stor-empty
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - name: cache
          mountPath: /cache
  volumes:
    - name: cache
      emptyDir: {}
EOF
```
