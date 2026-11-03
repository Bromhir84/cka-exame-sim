## Goal
Mount ConfigMap `app-files` at `/etc/config`.

## Steps
```bash
kubectl -n stor-cmvol create configmap app-files --from-literal=config.txt=hello-cka
kubectl -n stor-cmvol apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: cm-pod
  namespace: stor-cmvol
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - name: cfg
          mountPath: /etc/config
  volumes:
    - name: cfg
      configMap:
        name: app-files
EOF
```
