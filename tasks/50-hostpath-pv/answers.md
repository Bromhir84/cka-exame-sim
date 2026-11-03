## Goal
Static hostPath PV + matching PVC + Pod.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: hp-pv
spec:
  capacity: {storage: 1Gi}
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  hostPath: {path: /tmp/cka-hp-pv}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: hp-pvc
  namespace: stor-hostpath
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: manual
  resources:
    requests: {storage: 1Gi}
---
apiVersion: v1
kind: Pod
metadata:
  name: hp-pod
  namespace: stor-hostpath
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - {name: data, mountPath: /data}
  volumes:
    - name: data
      persistentVolumeClaim: {claimName: hp-pvc}
EOF
```
