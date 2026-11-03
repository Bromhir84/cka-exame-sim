#!/usr/bin/env python3
"""One-shot generator for the expanded 24 task directories (idempotent overwrite)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "tasks"


def write(task_id: str, files: dict[str, str]) -> None:
    d = ROOT / task_id
    d.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        path = d / name
        text = content.replace("\r\n", "\n").replace("\r", "\n")
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8", newline="\n")
        if name.endswith(".sh"):
            path.chmod(path.stat().st_mode | 0o111)
    print(f"wrote {task_id}")


# --- architecture ---
write(
    "09-clusterrole-binding",
    {
        "task.yaml": "id: 09-clusterrole-binding\ntitle: ClusterRole and ClusterRoleBinding\ndomain: architecture\n",
        "prompt.md": """# ClusterRole Binding

Create:

1. ClusterRole `node-viewer` that allows `get`, `list`, and `watch` on `nodes`
2. ServiceAccount `node-inspector` in namespace `arch-crb`
3. ClusterRoleBinding `node-viewer-binding` that binds ClusterRole `node-viewer` to that ServiceAccount

Namespace `arch-crb` already exists.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-crb --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole node-viewer >/dev/null
kubectl -n arch-crb get sa node-inspector >/dev/null
kubectl get clusterrolebinding node-viewer-binding >/dev/null
VERBS=$(kubectl get clusterrole node-viewer -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q get
echo "$VERBS" | grep -q list
echo "$VERBS" | grep -q watch
RES=$(kubectl get clusterrole node-viewer -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q nodes
REF=$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "node-viewer" ]
SUB=$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "node-inspector" ]
KIND=$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath='{.subjects[0].kind}')
[ "$KIND" = "ServiceAccount" ]
NS=$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath='{.subjects[0].namespace}')
[ "$NS" = "arch-crb" ]
exit 0
""",
    },
)

write(
    "10-rbac-secrets-reader",
    {
        "task.yaml": "id: 10-rbac-secrets-reader\ntitle: Role to read Secrets\ndomain: architecture\n",
        "prompt.md": """# Secrets Reader RBAC

In namespace `arch-secrets`:

1. Create ServiceAccount `secret-reader`
2. Create Role `secret-reader-role` allowing `get`, `list`, and `watch` on `secrets`
3. Create RoleBinding `secret-reader-binding` binding that Role to the ServiceAccount
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-secrets --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=arch-secrets
kubectl -n "$NS" get sa secret-reader >/dev/null
kubectl -n "$NS" get role secret-reader-role >/dev/null
kubectl -n "$NS" get rolebinding secret-reader-binding >/dev/null
RES=$(kubectl -n "$NS" get role secret-reader-role -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q secrets
for v in get list watch; do
  kubectl -n "$NS" get role secret-reader-role -o jsonpath='{.rules[0].verbs[*]}' | grep -q "$v"
done
exit 0
""",
    },
)

write(
    "11-role-services",
    {
        "task.yaml": "id: 11-role-services\ntitle: Role for Services\ndomain: architecture\n",
        "prompt.md": """# Services Role

In namespace `arch-svc-rbac`, create:

1. ServiceAccount `svc-manager`
2. Role `svc-manager-role` with verbs `get`, `list`, `create`, `delete` on resource `services`
3. RoleBinding `svc-manager-binding` linking them
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-svc-rbac --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=arch-svc-rbac
kubectl -n "$NS" get sa svc-manager >/dev/null
kubectl -n "$NS" get role svc-manager-role -o jsonpath='{.rules[0].resources[*]}' | grep -q services
for v in get list create delete; do
  kubectl -n "$NS" get role svc-manager-role -o jsonpath='{.rules[0].verbs[*]}' | grep -q "$v"
done
kubectl -n "$NS" get rolebinding svc-manager-binding >/dev/null
exit 0
""",
    },
)

write(
    "12-clusterrole-ns-get",
    {
        "task.yaml": "id: 12-clusterrole-ns-get\ntitle: ClusterRole for Namespaces\ndomain: architecture\n",
        "prompt.md": """# Namespace Lister

Create ClusterRole `ns-lister` allowing `get` and `list` on `namespaces`.

Create ServiceAccount `ns-auditor` in namespace `arch-ns`.

Create ClusterRoleBinding `ns-lister-binding` binding `ns-lister` to that ServiceAccount.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-ns --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole ns-lister -o jsonpath='{.rules[0].resources[*]}' | grep -q namespaces
kubectl get clusterrole ns-lister -o jsonpath='{.rules[0].verbs[*]}' | grep -q get
kubectl get clusterrole ns-lister -o jsonpath='{.rules[0].verbs[*]}' | grep -q list
kubectl -n arch-ns get sa ns-auditor >/dev/null
kubectl get clusterrolebinding ns-lister-binding -o jsonpath='{.roleRef.name}' | grep -qx ns-lister
exit 0
""",
    },
)

write(
    "13-sa-deploy-binding",
    {
        "task.yaml": "id: 13-sa-deploy-binding\ntitle: Deployment using a ServiceAccount\ndomain: architecture\n",
        "prompt.md": """# ServiceAccount on a Deployment

In namespace `arch-sa-deploy`:

1. Create ServiceAccount `app-sa`
2. Create Deployment `sa-demo` with 1 replica, image `nginx:1.27`, container name `web`
3. Set the Pod template `serviceAccountName` to `app-sa`

Ensure the Deployment is Ready.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-sa-deploy --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=arch-sa-deploy
kubectl -n "$NS" get sa app-sa >/dev/null
SA=$(kubectl -n "$NS" get deploy sa-demo -o jsonpath='{.spec.template.spec.serviceAccountName}')
[ "$SA" = "app-sa" ]
IMG=$(kubectl -n "$NS" get deploy sa-demo -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
kubectl -n "$NS" rollout status deploy/sa-demo --timeout=120s
exit 0
""",
    },
)

write(
    "14-rbac-jobs",
    {
        "task.yaml": "id: 14-rbac-jobs\ntitle: Role for batch Jobs\ndomain: architecture\n",
        "prompt.md": """# Jobs RBAC

In namespace `arch-jobs`:

1. ServiceAccount `job-runner`
2. Role `job-runner-role` allowing `get`, `list`, `create`, `delete` on `jobs` in API group `batch`
3. RoleBinding `job-runner-binding` binding the Role to the ServiceAccount
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace arch-jobs --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=arch-jobs
kubectl -n "$NS" get sa job-runner >/dev/null
kubectl -n "$NS" get role job-runner-role -o json | grep -q '"jobs"'
kubectl -n "$NS" get role job-runner-role -o json | grep -q '"batch"'
kubectl -n "$NS" get rolebinding job-runner-binding >/dev/null
exit 0
""",
    },
)

# --- workloads ---
write(
    "15-cronjob",
    {
        "task.yaml": "id: 15-cronjob\ntitle: Create a CronJob\ndomain: workloads\n",
        "prompt.md": """# CronJob

In namespace `wl-cron`, create CronJob `ping-cron` that:

- schedule: `*/5 * * * *`
- concurrencyPolicy: `Forbid`
- job template runs a container named `ping` with image `busybox:1.36` and command `["echo","cka-cron"]`
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-cron --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=wl-cron
SCHED=$(kubectl -n "$NS" get cronjob ping-cron -o jsonpath='{.spec.schedule}')
[ "$SCHED" = "*/5 * * * *" ]
POL=$(kubectl -n "$NS" get cronjob ping-cron -o jsonpath='{.spec.concurrencyPolicy}')
[ "$POL" = "Forbid" ]
IMG=$(kubectl -n "$NS" get cronjob ping-cron -o jsonpath='{.spec.jobTemplate.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
exit 0
""",
    },
)

write(
    "16-scale-deployment",
    {
        "task.yaml": "id: 16-scale-deployment\ntitle: Scale a Deployment\ndomain: workloads\n",
        "prompt.md": """# Scale Deployment

Namespace `wl-scale` has Deployment `api` with 1 replica.

Scale it to **4** replicas and ensure all are Ready.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-scale --dry-run=client -o yaml | kubectl apply -f -
kubectl -n wl-scale apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: wl-scale
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: nginx:1.27
EOF
kubectl -n wl-scale rollout status deploy/api --timeout=120s
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=wl-scale
REP=$(kubectl -n "$NS" get deploy api -o jsonpath='{.spec.replicas}')
[ "$REP" = "4" ]
kubectl -n "$NS" rollout status deploy/api --timeout=120s
READY=$(kubectl -n "$NS" get deploy api -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "4" ]
exit 0
""",
    },
)

write(
    "17-probes-deployment",
    {
        "task.yaml": "id: 17-probes-deployment\ntitle: Deployment with probes\ndomain: workloads\n",
        "prompt.md": """# Probes

In namespace `wl-probes`, create Deployment `probed` with:

- 2 replicas, image `nginx:1.27`, container name `web`
- readinessProbe: HTTP GET path `/` port `80`, initialDelaySeconds `5`
- livenessProbe: HTTP GET path `/` port `80`, initialDelaySeconds `10`

Ensure Ready.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-probes --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=wl-probes
REP=$(kubectl -n "$NS" get deploy probed -o jsonpath='{.spec.replicas}')
[ "$REP" = "2" ]
RP=$(kubectl -n "$NS" get deploy probed -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.path}')
[ "$RP" = "/" ]
LP=$(kubectl -n "$NS" get deploy probed -o jsonpath='{.spec.template.spec.containers[0].livenessProbe.httpGet.path}')
[ "$LP" = "/" ]
kubectl -n "$NS" rollout status deploy/probed --timeout=120s
exit 0
""",
    },
)

write(
    "18-resource-limits",
    {
        "task.yaml": "id: 18-resource-limits\ntitle: Deployment with resource limits\ndomain: workloads\n",
        "prompt.md": """# Resource Limits

In namespace `wl-limits`, create Deployment `limited` with 1 replica, image `nginx:1.27`, container `web`, and:

- requests: cpu `50m`, memory `32Mi`
- limits: cpu `200m`, memory `128Mi`

Ensure Ready.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-limits --dry-run=client -o yaml | kubectl apply -f -
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=wl-limits
RC=$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')
RM=$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}')
LC=$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.limits.cpu}')
LM=$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.limits.memory}')
[ "$RC" = "50m" ]
[ "$RM" = "32Mi" ]
[ "$LC" = "200m" ]
[ "$LM" = "128Mi" ]
kubectl -n "$NS" rollout status deploy/limited --timeout=120s
exit 0
""",
    },
)

# --- networking ---
write(
    "19-nodeport-service",
    {
        "task.yaml": "id: 19-nodeport-service\ntitle: NodePort Service\ndomain: networking\n",
        "prompt.md": """# NodePort

Namespace `net-nodeport` has Deployment `web` (label `app=web`) on container port 80.

Create Service `web-nodeport` of type **NodePort**, port **80**, targetPort **80**, nodePort **30080**, selector `app=web`.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-nodeport --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-nodeport apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: net-nodeport
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
EOF
kubectl -n net-nodeport rollout status deploy/web --timeout=120s
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=net-nodeport
TYPE=$(kubectl -n "$NS" get svc web-nodeport -o jsonpath='{.spec.type}')
[ "$TYPE" = "NodePort" ]
PORT=$(kubectl -n "$NS" get svc web-nodeport -o jsonpath='{.spec.ports[0].port}')
NP=$(kubectl -n "$NS" get svc web-nodeport -o jsonpath='{.spec.ports[0].nodePort}')
[ "$PORT" = "80" ]
[ "$NP" = "30080" ]
SEL=$(kubectl -n "$NS" get svc web-nodeport -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "web" ]
exit 0
""",
    },
)

write(
    "20-ingress-path",
    {
        "task.yaml": "id: 20-ingress-path\ntitle: Ingress with path prefix\ndomain: networking\n",
        "prompt.md": """# Ingress Path

Namespace `net-ingpath` has Deployment/Service `shop` exposing port 80.

Create Ingress `shop-ing` with:

- ingressClassName: `nginx`
- host: `shop.cka.local`
- path: `/shop` (Prefix) → Service `shop` port 80
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-ingpath --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-ingpath apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shop
  namespace: net-ingpath
spec:
  replicas: 1
  selector:
    matchLabels:
      app: shop
  template:
    metadata:
      labels:
        app: shop
    spec:
      containers:
        - name: shop
          image: nginx:1.27
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: shop
  namespace: net-ingpath
spec:
  selector:
    app: shop
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n net-ingpath rollout status deploy/shop --timeout=120s
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=net-ingpath
HOST=$(kubectl -n "$NS" get ingress shop-ing -o jsonpath='{.spec.rules[0].host}')
[ "$HOST" = "shop.cka.local" ]
PATHP=$(kubectl -n "$NS" get ingress shop-ing -o jsonpath='{.spec.rules[0].http.paths[0].path}')
[ "$PATHP" = "/shop" ]
SVC=$(kubectl -n "$NS" get ingress shop-ing -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}')
[ "$SVC" = "shop" ]
CLASS=$(kubectl -n "$NS" get ingress shop-ing -o jsonpath='{.spec.ingressClassName}')
[ "$CLASS" = "nginx" ]
exit 0
""",
    },
)

write(
    "21-networkpolicy-egress",
    {
        "task.yaml": "id: 21-networkpolicy-egress\ntitle: Egress NetworkPolicy\ndomain: networking\n",
        "prompt.md": """# Egress NetworkPolicy

Namespace `net-egress` has Pod `client` with label `app=client`.

Create NetworkPolicy `client-egress` that:

- selects `app=client`
- policyTypes: **Egress**
- allows egress only to pods with label `app=api` in the same namespace on TCP port **8080**
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-egress --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-egress apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: client
  namespace: net-egress
  labels:
    app: client
spec:
  containers:
    - name: c
      image: busybox:1.36
      command: ["sleep","3600"]
---
apiVersion: v1
kind: Pod
metadata:
  name: api
  namespace: net-egress
  labels:
    app: api
spec:
  containers:
    - name: a
      image: busybox:1.36
      command: ["sleep","3600"]
EOF
kubectl -n net-egress wait --for=condition=Ready pod/client pod/api --timeout=120s
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=net-egress
SEL=$(kubectl -n "$NS" get networkpolicy client-egress -o jsonpath='{.spec.podSelector.matchLabels.app}')
[ "$SEL" = "client" ]
TYPES=$(kubectl -n "$NS" get networkpolicy client-egress -o jsonpath='{.spec.policyTypes[*]}')
echo "$TYPES" | grep -q Egress
TO=$(kubectl -n "$NS" get networkpolicy client-egress -o jsonpath='{.spec.egress[0].to[0].podSelector.matchLabels.app}')
[ "$TO" = "api" ]
PORT=$(kubectl -n "$NS" get networkpolicy client-egress -o jsonpath='{.spec.egress[0].ports[0].port}')
[ "$PORT" = "8080" ]
exit 0
""",
    },
)

write(
    "22-clusterip-multi-port",
    {
        "task.yaml": "id: 22-clusterip-multi-port\ntitle: Multi-port ClusterIP Service\ndomain: networking\n",
        "prompt.md": """# Multi-port Service

Namespace `net-multiport` has Deployment `dual` with labels `app=dual` and containers exposing ports 80 and 8080 (named via container ports).

Create ClusterIP Service `dual-svc` selecting `app=dual` with:

- port name `http`, port **80**, targetPort **80**
- port name `metrics`, port **8080**, targetPort **8080**
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-multiport --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-multiport apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dual
  namespace: net-multiport
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dual
  template:
    metadata:
      labels:
        app: dual
    spec:
      containers:
        - name: dual
          image: hashicorp/http-echo:1.0
          args: ["-text=dual","-listen=:80"]
          ports:
            - containerPort: 80
            - containerPort: 8080
EOF
kubectl -n net-multiport rollout status deploy/dual --timeout=120s
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=net-multiport
TYPE=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.type}')
[ "$TYPE" = "ClusterIP" ] || [ -z "$TYPE" ]
N0=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[0].name}')
N1=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[1].name}')
echo "$N0$N1" | grep -q http
echo "$N0$N1" | grep -q metrics
PORTS=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[*].port}')
echo "$PORTS" | grep -q 80
echo "$PORTS" | grep -q 8080
exit 0
""",
    },
)

write(
    "23-service-labels",
    {
        "task.yaml": "id: 23-service-labels\ntitle: Service with specific selector\ndomain: networking\n",
        "prompt.md": """# Labeled Service

Namespace `net-svclabel` has Pods labeled `tier=frontend` and `env=prod` (Deployment `fe`).

Create ClusterIP Service `fe-svc` that:

- selects pods with **both** `tier=frontend` and `env=prod`
- exposes port **80** → targetPort **80**
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-svclabel --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-svclabel apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fe
  namespace: net-svclabel
spec:
  replicas: 1
  selector:
    matchLabels:
      tier: frontend
      env: prod
  template:
    metadata:
      labels:
        tier: frontend
        env: prod
    spec:
      containers:
        - name: fe
          image: nginx:1.27
          ports:
            - containerPort: 80
EOF
kubectl -n net-svclabel rollout status deploy/fe --timeout=120s
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=net-svclabel
T=$(kubectl -n "$NS" get svc fe-svc -o jsonpath='{.spec.selector.tier}')
E=$(kubectl -n "$NS" get svc fe-svc -o jsonpath='{.spec.selector.env}')
[ "$T" = "frontend" ]
[ "$E" = "prod" ]
P=$(kubectl -n "$NS" get svc fe-svc -o jsonpath='{.spec.ports[0].port}')
[ "$P" = "80" ]
exit 0
""",
    },
)

# --- storage ---
write(
    "24-pvc-busybox",
    {
        "task.yaml": "id: 24-pvc-busybox\ntitle: PVC mounted on busybox Pod\ndomain: storage\n",
        "prompt.md": """# PVC + busybox

In namespace `stor-busy`:

1. PVC `busy-pvc`: 500Mi, ReadWriteOnce, StorageClass `standard`
2. Pod `busy-pod`: image `busybox:1.36`, command `sleep 3600`, mount PVC at `/mnt/data`

Ensure Bound + Ready.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-busy --dry-run=client -o yaml | kubectl apply -f -
if ! kubectl get sc standard >/dev/null 2>&1; then
  kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF
fi
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=stor-busy
SIZE=$(kubectl -n "$NS" get pvc busy-pvc -o jsonpath='{.spec.resources.requests.storage}')
[ "$SIZE" = "500Mi" ]
SC=$(kubectl -n "$NS" get pvc busy-pvc -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "standard" ]
kubectl -n "$NS" wait --for=condition=Ready pod/busy-pod --timeout=120s
PHASE=$(kubectl -n "$NS" get pvc busy-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
CLAIM=$(kubectl -n "$NS" get pod busy-pod -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}')
[ "$CLAIM" = "busy-pvc" ]
exit 0
""",
    },
)

write(
    "25-pvc-storageclass",
    {
        "task.yaml": "id: 25-pvc-storageclass\ntitle: PVC with StorageClass standard\ndomain: storage\n",
        "prompt.md": """# StorageClass PVC

In namespace `stor-sc`, create PVC `app-data` requesting **2Gi**, accessModes **ReadWriteOnce**, storageClassName **standard**.

Also create Pod `app-data-pod` (busybox:1.36, sleep 3600) mounting it at `/var/app`.

PVC must become Bound.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-sc --dry-run=client -o yaml | kubectl apply -f -
if ! kubectl get sc standard >/dev/null 2>&1; then
  kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF
fi
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=stor-sc
SIZE=$(kubectl -n "$NS" get pvc app-data -o jsonpath='{.spec.resources.requests.storage}')
[ "$SIZE" = "2Gi" ]
SC=$(kubectl -n "$NS" get pvc app-data -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "standard" ]
kubectl -n "$NS" wait --for=condition=Ready pod/app-data-pod --timeout=120s
PHASE=$(kubectl -n "$NS" get pvc app-data -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
MP=$(kubectl -n "$NS" get pod app-data-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/var/app" ]
exit 0
""",
    },
)

write(
    "26-pvc-mount-subpath",
    {
        "task.yaml": "id: 26-pvc-mount-subpath\ntitle: PVC with subPath mount\ndomain: storage\n",
        "prompt.md": """# PVC subPath

In namespace `stor-sub`:

1. PVC `sub-pvc`: 1Gi, ReadWriteOnce, StorageClass `standard`
2. Pod `sub-pod` using `busybox:1.36` / `sleep 3600`
3. Mount `sub-pvc` at `/work` using **subPath** `cache`

Ensure Ready and Bound.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace stor-sub --dry-run=client -o yaml | kubectl apply -f -
if ! kubectl get sc standard >/dev/null 2>&1; then
  kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: standard
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF
fi
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=stor-sub
kubectl -n "$NS" wait --for=condition=Ready pod/sub-pod --timeout=120s
SP=$(kubectl -n "$NS" get pod sub-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].subPath}')
[ "$SP" = "cache" ]
MP=$(kubectl -n "$NS" get pod sub-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/work" ]
PHASE=$(kubectl -n "$NS" get pvc sub-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
exit 0
""",
    },
)

# --- troubleshooting ---
write(
    "27-crashloop-fix",
    {
        "task.yaml": "id: 27-crashloop-fix\ntitle: Fix CrashLoopBackOff\ndomain: troubleshooting\n",
        "prompt.md": """# CrashLoop

Namespace `ts-crash` has Deployment `looper` stuck in CrashLoopBackOff due to a bad command.

Fix it so the container runs `sleep 3600` with image `busybox:1.36` and the Deployment has 1 Ready replica.

Do not delete the Deployment.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-crash --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-crash apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: looper
  namespace: ts-crash
spec:
  replicas: 1
  selector:
    matchLabels:
      app: looper
  template:
    metadata:
      labels:
        app: looper
    spec:
      containers:
        - name: looper
          image: busybox:1.36
          command: ["sh","-c","exit 1"]
EOF
sleep 2
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=ts-crash
IMG=$(kubectl -n "$NS" get deploy looper -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
kubectl -n "$NS" rollout status deploy/looper --timeout=120s
READY=$(kubectl -n "$NS" get deploy looper -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "1" ]
exit 0
""",
    },
)

write(
    "28-wrong-selector",
    {
        "task.yaml": "id: 28-wrong-selector\ntitle: Fix Service selector\ndomain: troubleshooting\n",
        "prompt.md": """# Wrong Service Selector

Namespace `ts-selector` has Deployment `backend` (pods labeled `app=backend`) and Service `backend-svc` that does not select those pods.

Fix the Service so it selects `app=backend` and has Endpoints. Port should remain 80 → 80.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-selector --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-selector apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ts-selector
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: nginx:1.27
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: backend-svc
  namespace: ts-selector
spec:
  selector:
    app: backend-WRONG
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n ts-selector rollout status deploy/backend --timeout=120s
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=ts-selector
SEL=$(kubectl -n "$NS" get svc backend-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "backend" ]
EP=$(kubectl -n "$NS" get endpoints backend-svc -o jsonpath='{.subsets[0].addresses[0].ip}')
[ -n "$EP" ]
exit 0
""",
    },
)

write(
    "29-pending-nodeselector",
    {
        "task.yaml": "id: 29-pending-nodeselector\ntitle: Fix Pending nodeSelector\ndomain: troubleshooting\n",
        "prompt.md": """# Pending Pod

Namespace `ts-pending` has Pod `stuck` that stays Pending because of an impossible nodeSelector.

Fix scheduling so the Pod becomes Ready (you may remove/fix the nodeSelector). Keep image `nginx:1.27`.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-pending --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-pending apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: stuck
  namespace: ts-pending
spec:
  nodeSelector:
    disktype: not-a-real-label-xyz
  containers:
    - name: web
      image: nginx:1.27
EOF
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=ts-pending
IMG=$(kubectl -n "$NS" get pod stuck -o jsonpath='{.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
kubectl -n "$NS" wait --for=condition=Ready pod/stuck --timeout=120s
exit 0
""",
    },
)

write(
    "30-failing-probe",
    {
        "task.yaml": "id: 30-failing-probe\ntitle: Fix failing readiness probe\ndomain: troubleshooting\n",
        "prompt.md": """# Bad Readiness Probe

Namespace `ts-probe` has Deployment `web` that never becomes Ready because the readinessProbe path is wrong.

Fix the probe so it checks HTTP `/` on port 80 (nginx). Keep 2 replicas and image `nginx:1.27`.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-probe --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-probe apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: ts-probe
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
          readinessProbe:
            httpGet:
              path: /this-path-does-not-exist
              port: 80
            initialDelaySeconds: 1
            periodSeconds: 3
EOF
sleep 3
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=ts-probe
PATHP=$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.path}')
[ "$PATHP" = "/" ]
kubectl -n "$NS" rollout status deploy/web --timeout=120s
READY=$(kubectl -n "$NS" get deploy web -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "2" ]
exit 0
""",
    },
)

write(
    "31-missing-configmap",
    {
        "task.yaml": "id: 31-missing-configmap\ntitle: Fix missing ConfigMap mount\ndomain: troubleshooting\n",
        "prompt.md": """# Missing ConfigMap

Namespace `ts-cm` has Deployment `cfg-app` that fails because it mounts ConfigMap `app-settings` which does not exist.

Create ConfigMap `app-settings` with key `mode=online` (or otherwise fix the Deployment) so 1 replica becomes Ready. Prefer creating the missing ConfigMap.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-cm --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-cm apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cfg-app
  namespace: ts-cm
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cfg-app
  template:
    metadata:
      labels:
        app: cfg-app
    spec:
      containers:
        - name: app
          image: nginx:1.27
          volumeMounts:
            - name: cfg
              mountPath: /etc/cfg
      volumes:
        - name: cfg
          configMap:
            name: app-settings
EOF
sleep 2
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=ts-cm
kubectl -n "$NS" get cm app-settings >/dev/null
MODE=$(kubectl -n "$NS" get cm app-settings -o jsonpath='{.data.mode}')
[ "$MODE" = "online" ]
kubectl -n "$NS" rollout status deploy/cfg-app --timeout=120s
READY=$(kubectl -n "$NS" get deploy cfg-app -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "1" ]
exit 0
""",
    },
)

write(
    "32-service-wrong-target",
    {
        "task.yaml": "id: 32-service-wrong-target\ntitle: Fix Service targetPort\ndomain: troubleshooting\n",
        "prompt.md": """# Wrong targetPort

Namespace `ts-target` has Deployment `echo` listening on container port **8080**, but Service `echo-svc` targets port **80**.

Fix the Service so traffic on port 80 reaches targetPort **8080**. Selector `app=echo` should remain.
""",
        "setup.sh": """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-target --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-target apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo
  namespace: ts-target
spec:
  replicas: 1
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
    spec:
      containers:
        - name: echo
          image: hashicorp/http-echo:1.0
          args: ["-text=ok","-listen=:8080"]
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: echo-svc
  namespace: ts-target
spec:
  selector:
    app: echo
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n ts-target rollout status deploy/echo --timeout=120s
""",
        "grade.sh": """#!/usr/bin/env bash
set -euo pipefail
NS=ts-target
TP=$(kubectl -n "$NS" get svc echo-svc -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "8080" ]
PORT=$(kubectl -n "$NS" get svc echo-svc -o jsonpath='{.spec.ports[0].port}')
[ "$PORT" = "80" ]
SEL=$(kubectl -n "$NS" get svc echo-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "echo" ]
exit 0
""",
    },
)

print("done")
