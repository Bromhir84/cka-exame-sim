#!/usr/bin/env python3
"""Add more bank tasks (33+) across all domains. Idempotent overwrite."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "tasks"


def write(task_id: str, files: dict[str, str]) -> None:
    d = ROOT / task_id
    d.mkdir(parents=True, exist_ok=True)
    checks = d / "checks"
    for name, content in files.items():
        path = d / name
        path.parent.mkdir(parents=True, exist_ok=True)
        text = content.replace("\r\n", "\n").replace("\r", "\n")
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8", newline="\n")
        if name.endswith(".sh"):
            path.chmod(path.stat().st_mode | 0o111)
    print("wrote", task_id)


def task(
    tid: str,
    title: str,
    domain: str,
    prompt: str,
    setup: str,
    grade: str,
    checks: list[tuple[str, str, int, str]],
    answers: str,
) -> None:
    files: dict[str, str] = {
        "task.yaml": f"id: {tid}\ntitle: {title}\ndomain: {domain}\n",
        "prompt.md": prompt.strip() + "\n",
        "setup.sh": "#!/usr/bin/env bash\nset -euo pipefail\n" + setup.strip() + "\n",
        "grade.sh": "#!/usr/bin/env bash\nset -euo pipefail\n" + grade.strip() + "\nexit 0\n",
        "answers.md": answers.strip() + "\n",
        "assessment.yaml": "checks:\n"
        + "".join(
            f"  - id: {cid}\n    description: {desc}\n    weight: {w}\n    script: checks/{cid}.sh\n"
            for cid, desc, w, _ in checks
        ),
    }
    for cid, _desc, _w, body in checks:
        files[f"checks/{cid}.sh"] = (
            "#!/usr/bin/env bash\nset -euo pipefail\n" + body.strip() + "\nexit 0\n"
        )
    write(tid, files)


# ── architecture ─────────────────────────────────────────────
task(
    "33-clusterrole-pods-reader",
    "ClusterRole bound in a namespace",
    "architecture",
    """# ClusterRole + RoleBinding

Create:

1. ClusterRole `pods-reader` allowing `get`, `list`, and `watch` on `pods`
2. ServiceAccount `pod-auditor` in namespace `arch-pods`
3. **RoleBinding** (namespaced) `pods-reader-binding` in `arch-pods` that binds ClusterRole `pods-reader` to that ServiceAccount

Namespace `arch-pods` already exists. Use a RoleBinding referencing the ClusterRole (not a ClusterRoleBinding).
""",
    "kubectl create namespace arch-pods --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl get clusterrole pods-reader >/dev/null
kubectl -n arch-pods get sa pod-auditor >/dev/null
kubectl -n arch-pods get rolebinding pods-reader-binding >/dev/null
REF=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "pods-reader" ]
KIND=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.roleRef.kind}')
[ "$KIND" = "ClusterRole" ]
SUB=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "pod-auditor" ]
""",
    [
        (
            "cr",
            "ClusterRole verbs/resources",
            40,
            """
kubectl get clusterrole pods-reader >/dev/null
VERBS=$(kubectl get clusterrole pods-reader -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q get
echo "$VERBS" | grep -q list
echo "$VERBS" | grep -q watch
RES=$(kubectl get clusterrole pods-reader -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q pods
""",
        ),
        (
            "bind",
            "RoleBinding to SA",
            60,
            """
kubectl -n arch-pods get sa pod-auditor >/dev/null
kubectl -n arch-pods get rolebinding pods-reader-binding >/dev/null
REF=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "pods-reader" ]
KIND=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.roleRef.kind}')
[ "$KIND" = "ClusterRole" ]
SUB=$(kubectl -n arch-pods get rolebinding pods-reader-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "pod-auditor" ]
""",
        ),
    ],
    """## Goal
ClusterRole for pod reads, bound **only** in `arch-pods` via RoleBinding.

## Steps
```bash
kubectl create clusterrole pods-reader --verb=get,list,watch --resource=pods
kubectl -n arch-pods create sa pod-auditor
kubectl -n arch-pods create rolebinding pods-reader-binding \\
  --clusterrole=pods-reader \\
  --serviceaccount=arch-pods:pod-auditor
```

## Verify
```bash
kubectl -n arch-pods auth can-i list pods --as=system:serviceaccount:arch-pods:pod-auditor
kubectl get clusterrolebinding pods-reader-binding 2>/dev/null || echo "no CRB (good)"
```
""",
)

task(
    "34-resourcequota",
    "Namespace ResourceQuota",
    "architecture",
    """# ResourceQuota

In namespace `arch-quota` create ResourceQuota `team-quota` that limits:

- hard `requests.cpu`: `2`
- hard `requests.memory`: `2Gi`
- hard `pods`: `10`

Namespace `arch-quota` already exists.
""",
    "kubectl create namespace arch-quota --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl -n arch-quota get resourcequota team-quota >/dev/null
CPU=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.requests\\.cpu}')
[ "$CPU" = "2" ]
MEM=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.requests\\.memory}')
[ "$MEM" = "2Gi" ]
PODS=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.pods}')
[ "$PODS" = "10" ]
""",
    [
        (
            "exists",
            "ResourceQuota exists",
            30,
            'kubectl -n arch-quota get resourcequota team-quota >/dev/null',
        ),
        (
            "hard",
            "Hard limits correct",
            70,
            """
CPU=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.requests\\.cpu}')
[ "$CPU" = "2" ]
MEM=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.requests\\.memory}')
[ "$MEM" = "2Gi" ]
PODS=$(kubectl -n arch-quota get resourcequota team-quota -o jsonpath='{.spec.hard.pods}')
[ "$PODS" = "10" ]
""",
        ),
    ],
    """## Goal
Create ResourceQuota `team-quota` with the specified hard limits.

## Steps
```bash
kubectl -n arch-quota create quota team-quota \\
  --hard=requests.cpu=2,requests.memory=2Gi,pods=10
```

## Verify
```bash
kubectl -n arch-quota describe quota team-quota
```
""",
)

task(
    "35-limitrange",
    "Namespace LimitRange",
    "architecture",
    """# LimitRange

In namespace `arch-limits` create LimitRange `mem-limit-range` that sets default container limits:

- default request memory: `64Mi`
- default limit memory: `256Mi`

Namespace `arch-limits` already exists.
""",
    "kubectl create namespace arch-limits --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl -n arch-limits get limitrange mem-limit-range >/dev/null
REQ=$(kubectl -n arch-limits get limitrange mem-limit-range -o jsonpath='{.spec.limits[0].defaultRequest.memory}')
[ "$REQ" = "64Mi" ]
LIM=$(kubectl -n arch-limits get limitrange mem-limit-range -o jsonpath='{.spec.limits[0].default.memory}')
[ "$LIM" = "256Mi" ]
""",
    [
        (
            "exists",
            "LimitRange exists",
            30,
            "kubectl -n arch-limits get limitrange mem-limit-range >/dev/null",
        ),
        (
            "defaults",
            "Default memory request/limit",
            70,
            """
REQ=$(kubectl -n arch-limits get limitrange mem-limit-range -o jsonpath='{.spec.limits[0].defaultRequest.memory}')
[ "$REQ" = "64Mi" ]
LIM=$(kubectl -n arch-limits get limitrange mem-limit-range -o jsonpath='{.spec.limits[0].default.memory}')
[ "$LIM" = "256Mi" ]
""",
        ),
    ],
    """## Goal
LimitRange with default memory request 64Mi and limit 256Mi.

## Steps
```bash
kubectl -n arch-limits apply -f - <<'EOF'
apiVersion: v1
kind: LimitRange
metadata:
  name: mem-limit-range
  namespace: arch-limits
spec:
  limits:
    - type: Container
      defaultRequest:
        memory: 64Mi
      default:
        memory: 256Mi
EOF
```
""",
)

task(
    "36-serviceaccount-automount",
    "Disable SA token automount",
    "architecture",
    """# ServiceAccount automount

In namespace `arch-automount`:

1. Create ServiceAccount `no-token-sa` with `automountServiceAccountToken: false`
2. Create Pod `quiet` using image `busybox:1.36`, command `sleep 3600`, `serviceAccountName: no-token-sa`
3. Ensure the Pod also has `automountServiceAccountToken: false` (pod spec)

Pod must become Ready.
""",
    "kubectl create namespace arch-automount --dry-run=client -o yaml | kubectl apply -f -",
    """
SA=$(kubectl -n arch-automount get sa no-token-sa -o jsonpath='{.automountServiceAccountToken}')
[ "$SA" = "false" ]
PODSA=$(kubectl -n arch-automount get pod quiet -o jsonpath='{.spec.serviceAccountName}')
[ "$PODSA" = "no-token-sa" ]
AUTO=$(kubectl -n arch-automount get pod quiet -o jsonpath='{.spec.automountServiceAccountToken}')
[ "$AUTO" = "false" ]
kubectl -n arch-automount wait --for=condition=Ready pod/quiet --timeout=120s
""",
    [
        (
            "sa",
            "SA automount false",
            40,
            """
SA=$(kubectl -n arch-automount get sa no-token-sa -o jsonpath='{.automountServiceAccountToken}')
[ "$SA" = "false" ]
""",
        ),
        (
            "pod",
            "Pod SA + automount + Ready",
            60,
            """
PODSA=$(kubectl -n arch-automount get pod quiet -o jsonpath='{.spec.serviceAccountName}')
[ "$PODSA" = "no-token-sa" ]
AUTO=$(kubectl -n arch-automount get pod quiet -o jsonpath='{.spec.automountServiceAccountToken}')
[ "$AUTO" = "false" ]
kubectl -n arch-automount wait --for=condition=Ready pod/quiet --timeout=120s
""",
        ),
    ],
    """## Goal
SA and Pod both disable service account token automount.

## Steps
```bash
kubectl -n arch-automount apply -f - <<'EOF'
apiVersion: v1
kind: ServiceAccount
metadata:
  name: no-token-sa
  namespace: arch-automount
automountServiceAccountToken: false
---
apiVersion: v1
kind: Pod
metadata:
  name: quiet
  namespace: arch-automount
spec:
  serviceAccountName: no-token-sa
  automountServiceAccountToken: false
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
EOF
```
""",
)

# ── workloads ────────────────────────────────────────────────
task(
    "37-job-complete",
    "Batch Job",
    "workloads",
    """# Job

In namespace `wl-job` create Job `pi-job` that:

- uses image `busybox:1.36`
- container name `worker`
- command: `["sh","-c","echo 3.14 && exit 0"]`
- `restartPolicy: Never`
- `backoffLimit: 2`

The Job should succeed (Complete).
""",
    "kubectl create namespace wl-job --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl -n wl-job get job pi-job >/dev/null
IMG=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
RP=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.template.spec.restartPolicy}')
[ "$RP" = "Never" ]
BL=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.backoffLimit}')
[ "$BL" = "2" ]
kubectl -n wl-job wait --for=condition=Complete job/pi-job --timeout=120s
""",
    [
        (
            "spec",
            "Job image/restart/backoff",
            50,
            """
IMG=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
RP=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.template.spec.restartPolicy}')
[ "$RP" = "Never" ]
BL=$(kubectl -n wl-job get job pi-job -o jsonpath='{.spec.backoffLimit}')
[ "$BL" = "2" ]
""",
        ),
        (
            "complete",
            "Job Complete",
            50,
            "kubectl -n wl-job wait --for=condition=Complete job/pi-job --timeout=120s",
        ),
    ],
    """## Goal
Create a completing Job with Never restart and backoffLimit 2.

## Steps
```bash
kubectl -n wl-job create job pi-job --image=busybox:1.36 -- sh -c 'echo 3.14 && exit 0'
kubectl -n wl-job patch job pi-job -p '{"spec":{"backoffLimit":2}}'
# ensure restartPolicy Never (default for jobs)
kubectl -n wl-job wait --for=condition=Complete job/pi-job --timeout=120s
```
""",
)

task(
    "38-deploy-affinity",
    "Pod affinity required",
    "workloads",
    """# nodeAffinity

In namespace `wl-affinity` create Deployment `placed` with:

- 1 replica, image `nginx:1.27`, container `web`
- requiredDuringSchedulingIgnoredDuringExecution nodeAffinity requiring label `kubernetes.io/os` In `linux`

Ensure the Deployment is Ready.
""",
    "kubectl create namespace wl-affinity --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl -n wl-affinity get deploy placed >/dev/null
KEY=$(kubectl -n wl-affinity get deploy placed -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].key}')
[ "$KEY" = "kubernetes.io/os" ]
VAL=$(kubectl -n wl-affinity get deploy placed -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].values[0]}')
[ "$VAL" = "linux" ]
kubectl -n wl-affinity rollout status deploy/placed --timeout=120s
""",
    [
        (
            "affinity",
            "Required nodeAffinity",
            60,
            """
KEY=$(kubectl -n wl-affinity get deploy placed -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].key}')
[ "$KEY" = "kubernetes.io/os" ]
VAL=$(kubectl -n wl-affinity get deploy placed -o jsonpath='{.spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms[0].matchExpressions[0].values[0]}')
[ "$VAL" = "linux" ]
""",
        ),
        (
            "ready",
            "Deployment Ready",
            40,
            "kubectl -n wl-affinity rollout status deploy/placed --timeout=120s",
        ),
    ],
    """## Goal
Deployment with required nodeAffinity on `kubernetes.io/os=linux`.

## Steps
```bash
kubectl -n wl-affinity apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: placed
  namespace: wl-affinity
spec:
  replicas: 1
  selector:
    matchLabels: {app: placed}
  template:
    metadata:
      labels: {app: placed}
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: kubernetes.io/os
                    operator: In
                    values: ["linux"]
      containers:
        - name: web
          image: nginx:1.27
EOF
```
""",
)

task(
    "39-daemonset",
    "Create a DaemonSet",
    "workloads",
    """# DaemonSet

In namespace `wl-ds` create DaemonSet `node-agent` that:

- uses image `busybox:1.36`
- container name `agent`
- command `["sleep","3600"]`
- labels pods with `app=node-agent`

Ensure DaemonSet pods are Ready on schedulable nodes.
""",
    "kubectl create namespace wl-ds --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl -n wl-ds get ds node-agent >/dev/null
IMG=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
DESIRED=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.status.desiredNumberScheduled}')
READY=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.status.numberReady}')
[ -n "$DESIRED" ] && [ "$DESIRED" != "0" ]
[ "$READY" = "$DESIRED" ]
""",
    [
        (
            "spec",
            "DaemonSet image",
            40,
            """
kubectl -n wl-ds get ds node-agent >/dev/null
IMG=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "busybox:1.36" ]
""",
        ),
        (
            "ready",
            "All scheduled pods Ready",
            60,
            """
# wait a bit for scheduling
for i in 1 2 3 4 5 6 7 8 9 10; do
  DESIRED=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.status.desiredNumberScheduled}')
  READY=$(kubectl -n wl-ds get ds node-agent -o jsonpath='{.status.numberReady}')
  if [ -n "$DESIRED" ] && [ "$DESIRED" != "0" ] && [ "$READY" = "$DESIRED" ]; then
    exit 0
  fi
  sleep 3
done
exit 1
""",
        ),
    ],
    """## Goal
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
""",
)

task(
    "40-init-container",
    "Pod with initContainer",
    "workloads",
    """# Init container

In namespace `wl-init` create Pod `bootstrap` that:

1. Has initContainer `setup` using `busybox:1.36` running `["sh","-c","echo ready > /work/ok"]` mounting emptyDir `shared` at `/work`
2. Has container `app` using `busybox:1.36` running `["sh","-c","sleep 3600"]` mounting the same volume at `/data`

Pod must become Ready.
""",
    "kubectl create namespace wl-init --dry-run=client -o yaml | kubectl apply -f -",
    """
INIT=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.initContainers[0].name}')
[ "$INIT" = "setup" ]
APP=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.containers[0].name}')
[ "$APP" = "app" ]
kubectl -n wl-init wait --for=condition=Ready pod/bootstrap --timeout=120s
""",
    [
        (
            "init",
            "initContainer present",
            50,
            """
INIT=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.initContainers[0].name}')
[ "$INIT" = "setup" ]
IMG=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.initContainers[0].image}')
[ "$IMG" = "busybox:1.36" ]
""",
        ),
        (
            "ready",
            "Pod Ready",
            50,
            """
APP=$(kubectl -n wl-init get pod bootstrap -o jsonpath='{.spec.containers[0].name}')
[ "$APP" = "app" ]
kubectl -n wl-init wait --for=condition=Ready pod/bootstrap --timeout=120s
""",
        ),
    ],
    """## Goal
Pod with initContainer writing to a shared emptyDir, then main container Ready.

## Steps
```bash
kubectl -n wl-init apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: bootstrap
  namespace: wl-init
spec:
  initContainers:
    - name: setup
      image: busybox:1.36
      command: ["sh","-c","echo ready > /work/ok"]
      volumeMounts:
        - name: shared
          mountPath: /work
  containers:
    - name: app
      image: busybox:1.36
      command: ["sh","-c","sleep 3600"]
      volumeMounts:
        - name: shared
          mountPath: /data
  volumes:
    - name: shared
      emptyDir: {}
EOF
```
""",
)

task(
    "41-sidecar-pod",
    "Multi-container Pod",
    "workloads",
    """# Sidecar Pod

In namespace `wl-sidecar` create Pod `pair` with two containers:

1. `app` — image `nginx:1.27`
2. `sidecar` — image `busybox:1.36`, command `["sleep","3600"]`

Both must be Running / Pod Ready.
""",
    "kubectl create namespace wl-sidecar --dry-run=client -o yaml | kubectl apply -f -",
    """
C1=$(kubectl -n wl-sidecar get pod pair -o jsonpath='{.spec.containers[0].name}')
C2=$(kubectl -n wl-sidecar get pod pair -o jsonpath='{.spec.containers[1].name}')
echo "$C1 $C2" | grep -q app
echo "$C1 $C2" | grep -q sidecar
COUNT=$(kubectl -n wl-sidecar get pod pair -o jsonpath='{.spec.containers[*].name}' | wc -w)
[ "$COUNT" -eq 2 ]
kubectl -n wl-sidecar wait --for=condition=Ready pod/pair --timeout=120s
""",
    [
        (
            "containers",
            "Two named containers",
            50,
            """
NAMES=$(kubectl -n wl-sidecar get pod pair -o jsonpath='{.spec.containers[*].name}')
echo "$NAMES" | grep -qw app
echo "$NAMES" | grep -qw sidecar
""",
        ),
        (
            "ready",
            "Pod Ready",
            50,
            "kubectl -n wl-sidecar wait --for=condition=Ready pod/pair --timeout=120s",
        ),
    ],
    """## Goal
Multi-container Pod with `app` (nginx) and `sidecar` (busybox sleep).

## Steps
```bash
kubectl -n wl-sidecar apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: pair
  namespace: wl-sidecar
spec:
  containers:
    - name: app
      image: nginx:1.27
    - name: sidecar
      image: busybox:1.36
      command: ["sleep", "3600"]
EOF
```
""",
)

task(
    "42-pdb",
    "PodDisruptionBudget",
    "workloads",
    """# PodDisruptionBudget

Namespace `wl-pdb` has Deployment `api` with label `app=api`.

Create PodDisruptionBudget `api-pdb` that:

- selects `app=api`
- `minAvailable: 1`
""",
    """
kubectl create namespace wl-pdb --dry-run=client -o yaml | kubectl apply -f -
kubectl -n wl-pdb apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: wl-pdb
spec:
  replicas: 2
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
        - name: api
          image: nginx:1.27
EOF
kubectl -n wl-pdb rollout status deploy/api --timeout=120s
""",
    """
kubectl -n wl-pdb get pdb api-pdb >/dev/null
MIN=$(kubectl -n wl-pdb get pdb api-pdb -o jsonpath='{.spec.minAvailable}')
[ "$MIN" = "1" ]
SEL=$(kubectl -n wl-pdb get pdb api-pdb -o jsonpath='{.spec.selector.matchLabels.app}')
[ "$SEL" = "api" ]
""",
    [
        (
            "exists",
            "PDB exists",
            40,
            "kubectl -n wl-pdb get pdb api-pdb >/dev/null",
        ),
        (
            "spec",
            "minAvailable + selector",
            60,
            """
MIN=$(kubectl -n wl-pdb get pdb api-pdb -o jsonpath='{.spec.minAvailable}')
[ "$MIN" = "1" ]
SEL=$(kubectl -n wl-pdb get pdb api-pdb -o jsonpath='{.spec.selector.matchLabels.app}')
[ "$SEL" = "api" ]
""",
        ),
    ],
    """## Goal
PDB with minAvailable 1 for `app=api`.

## Steps
```bash
kubectl -n wl-pdb create poddisruptionbudget api-pdb --selector=app=api --min-available=1
```
""",
)

# ── networking ───────────────────────────────────────────────
task(
    "43-headless-service",
    "Headless Service",
    "networking",
    """# Headless Service

Namespace `net-headless` has Deployment `stateful-like` with label `app=store`.

Create Service `store-hs` that is **headless** (`clusterIP: None`), selects `app=store`, port **80** → targetPort **80**.
""",
    """
kubectl create namespace net-headless --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-headless apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stateful-like
  namespace: net-headless
spec:
  replicas: 2
  selector:
    matchLabels: {app: store}
  template:
    metadata:
      labels: {app: store}
    spec:
      containers:
        - name: web
          image: nginx:1.27
          ports:
            - containerPort: 80
EOF
kubectl -n net-headless rollout status deploy/stateful-like --timeout=120s
""",
    """
CIP=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.clusterIP}')
[ "$CIP" = "None" ]
SEL=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "store" ]
PORT=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.ports[0].port}')
[ "$PORT" = "80" ]
""",
    [
        (
            "headless",
            "clusterIP None",
            50,
            """
CIP=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.clusterIP}')
[ "$CIP" = "None" ]
""",
        ),
        (
            "sel",
            "Selector + port",
            50,
            """
SEL=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "store" ]
PORT=$(kubectl -n net-headless get svc store-hs -o jsonpath='{.spec.ports[0].port}')
[ "$PORT" = "80" ]
""",
        ),
    ],
    """## Goal
Headless Service for `app=store`.

## Steps
```bash
kubectl -n net-headless create service clusterip store-hs --clusterip=None --tcp=80:80
kubectl -n net-headless label svc store-hs unused=x --overwrite  # ensure exists
kubectl -n net-headless patch svc store-hs -p '{"spec":{"selector":{"app":"store"},"clusterIP":"None"}}'
```

Or apply YAML with `clusterIP: None` and selector `app: store`.
""",
)

task(
    "44-deny-all-ingress",
    "Default deny Ingress NetworkPolicy",
    "networking",
    """# Default deny

Namespace `net-deny` has Pod `web` (label `app=web`).

Create NetworkPolicy `deny-all-ingress` that:

- selects **all pods** in the namespace (empty podSelector)
- policyTypes: **Ingress**
- has **no** ingress rules (deny all ingress)
""",
    """
kubectl create namespace net-deny --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-deny run web --image=nginx:1.27 --labels=app=web --restart=Never
kubectl -n net-deny wait --for=condition=Ready pod/web --timeout=120s
""",
    """
kubectl -n net-deny get networkpolicy deny-all-ingress >/dev/null
TYPES=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o jsonpath='{.spec.policyTypes[*]}')
echo "$TYPES" | grep -q Ingress
ING=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o jsonpath='{.spec.ingress}')
[ -z "$ING" ] || [ "$ING" = "[]" ] || [ "$ING" = "null" ]
""",
    [
        (
            "exists",
            "Policy exists + Ingress type",
            50,
            """
kubectl -n net-deny get networkpolicy deny-all-ingress >/dev/null
TYPES=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o jsonpath='{.spec.policyTypes[*]}')
echo "$TYPES" | grep -q Ingress
""",
        ),
        (
            "empty",
            "No ingress allow rules",
            50,
            """
# empty podSelector is {} 
SEL=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o jsonpath='{.spec.podSelector}')
# ingress should be absent or empty
COUNT=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o json | grep -c '"ingress"' || true)
ING=$(kubectl -n net-deny get networkpolicy deny-all-ingress -o jsonpath='{.spec.ingress[*]}')
[ -z "$ING" ]
""",
        ),
    ],
    """## Goal
Deny-all ingress NetworkPolicy for the whole namespace.

## Steps
```bash
kubectl -n net-deny apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: net-deny
spec:
  podSelector: {}
  policyTypes:
    - Ingress
EOF
```
""",
)

task(
    "45-ingress-two-hosts",
    "Ingress with two hosts",
    "networking",
    """# Multi-host Ingress

Namespace `net-twohost` has Services `alpha-svc` and `beta-svc` (port 80).

Create Ingress `multi-ing` with `ingressClassName: nginx` and rules:

1. host `alpha.cka.local` path `/` (Prefix) → `alpha-svc:80`
2. host `beta.cka.local` path `/` (Prefix) → `beta-svc:80`
""",
    """
kubectl create namespace net-twohost --dry-run=client -o yaml | kubectl apply -f -
for name in alpha beta; do
  kubectl -n net-twohost create deploy "$name" --image=nginx:1.27
  kubectl -n net-twohost expose deploy "$name" --name="${name}-svc" --port=80
  kubectl -n net-twohost rollout status deploy/"$name" --timeout=120s
done
""",
    """
kubectl -n net-twohost get ingress multi-ing >/dev/null
H1=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.rules[0].host}')
H2=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.rules[1].host}')
echo "$H1 $H2" | grep -q alpha.cka.local
echo "$H1 $H2" | grep -q beta.cka.local
CLASS=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.ingressClassName}')
[ "$CLASS" = "nginx" ]
""",
    [
        (
            "hosts",
            "Both hosts present",
            60,
            """
HOSTS=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.rules[*].host}')
echo "$HOSTS" | grep -q alpha.cka.local
echo "$HOSTS" | grep -q beta.cka.local
""",
        ),
        (
            "class",
            "ingressClassName nginx",
            40,
            """
CLASS=$(kubectl -n net-twohost get ingress multi-ing -o jsonpath='{.spec.ingressClassName}')
[ "$CLASS" = "nginx" ]
""",
        ),
    ],
    """## Goal
One Ingress object with two host rules.

## Steps
```bash
kubectl -n net-twohost apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-ing
  namespace: net-twohost
spec:
  ingressClassName: nginx
  rules:
    - host: alpha.cka.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: {name: alpha-svc, port: {number: 80}}
    - host: beta.cka.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: {name: beta-svc, port: {number: 80}}
EOF
```
""",
)

task(
    "46-externalname-service",
    "ExternalName Service",
    "networking",
    """# ExternalName Service

In namespace `net-ext` create Service `search-ext` of type **ExternalName** pointing to external name `www.example.com` (no cluster IP selector).
""",
    "kubectl create namespace net-ext --dry-run=client -o yaml | kubectl apply -f -",
    """
TYPE=$(kubectl -n net-ext get svc search-ext -o jsonpath='{.spec.type}')
[ "$TYPE" = "ExternalName" ]
EXT=$(kubectl -n net-ext get svc search-ext -o jsonpath='{.spec.externalName}')
[ "$EXT" = "www.example.com" ]
""",
    [
        (
            "type",
            "Type ExternalName",
            40,
            """
TYPE=$(kubectl -n net-ext get svc search-ext -o jsonpath='{.spec.type}')
[ "$TYPE" = "ExternalName" ]
""",
        ),
        (
            "name",
            "externalName value",
            60,
            """
EXT=$(kubectl -n net-ext get svc search-ext -o jsonpath='{.spec.externalName}')
[ "$EXT" = "www.example.com" ]
""",
        ),
    ],
    """## Goal
ExternalName Service to `www.example.com`.

## Steps
```bash
kubectl -n net-ext create service externalname search-ext --external-name=www.example.com
```
""",
)

# ── storage ──────────────────────────────────────────────────
task(
    "47-configmap-volume",
    "ConfigMap as volume",
    "storage",
    """# ConfigMap volume

In namespace `stor-cmvol`:

1. Create ConfigMap `app-files` with key `config.txt` value `hello-cka`
2. Create Pod `cm-pod` (busybox:1.36, `sleep 3600`) mounting that ConfigMap at `/etc/config` (default keys as files)

Pod must be Ready.
""",
    "kubectl create namespace stor-cmvol --dry-run=client -o yaml | kubectl apply -f -",
    """
VAL=$(kubectl -n stor-cmvol get cm app-files -o jsonpath='{.data.config\\.txt}')
[ "$VAL" = "hello-cka" ]
MP=$(kubectl -n stor-cmvol get pod cm-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/etc/config" ]
kubectl -n stor-cmvol wait --for=condition=Ready pod/cm-pod --timeout=120s
""",
    [
        (
            "cm",
            "ConfigMap data",
            40,
            """
VAL=$(kubectl -n stor-cmvol get cm app-files -o jsonpath='{.data.config\\.txt}')
[ "$VAL" = "hello-cka" ]
""",
        ),
        (
            "mount",
            "Volume mount + Ready",
            60,
            """
MP=$(kubectl -n stor-cmvol get pod cm-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/etc/config" ]
SRC=$(kubectl -n stor-cmvol get pod cm-pod -o jsonpath='{.spec.volumes[0].configMap.name}')
[ "$SRC" = "app-files" ]
kubectl -n stor-cmvol wait --for=condition=Ready pod/cm-pod --timeout=120s
""",
        ),
    ],
    """## Goal
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
""",
)

task(
    "48-secret-volume",
    "Secret as volume",
    "storage",
    """# Secret volume

In namespace `stor-secvol`:

1. Create Secret `app-tls` (Opaque) with key `token` value `sekrit`
2. Create Pod `sec-pod` (busybox:1.36, `sleep 3600`) mounting the Secret at `/var/run/secrets/app`

Pod must be Ready.
""",
    "kubectl create namespace stor-secvol --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl -n stor-secvol get secret app-tls >/dev/null
MP=$(kubectl -n stor-secvol get pod sec-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/var/run/secrets/app" ]
SRC=$(kubectl -n stor-secvol get pod sec-pod -o jsonpath='{.spec.volumes[0].secret.secretName}')
[ "$SRC" = "app-tls" ]
kubectl -n stor-secvol wait --for=condition=Ready pod/sec-pod --timeout=120s
""",
    [
        (
            "secret",
            "Secret exists",
            40,
            "kubectl -n stor-secvol get secret app-tls >/dev/null",
        ),
        (
            "mount",
            "Secret mounted + Ready",
            60,
            """
MP=$(kubectl -n stor-secvol get pod sec-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/var/run/secrets/app" ]
SRC=$(kubectl -n stor-secvol get pod sec-pod -o jsonpath='{.spec.volumes[0].secret.secretName}')
[ "$SRC" = "app-tls" ]
kubectl -n stor-secvol wait --for=condition=Ready pod/sec-pod --timeout=120s
""",
        ),
    ],
    """## Goal
Mount Secret `app-tls` at `/var/run/secrets/app`.

## Steps
```bash
kubectl -n stor-secvol create secret generic app-tls --from-literal=token=sekrit
kubectl -n stor-secvol apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: sec-pod
  namespace: stor-secvol
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - name: tok
          mountPath: /var/run/secrets/app
  volumes:
    - name: tok
      secret:
        secretName: app-tls
EOF
```
""",
)

task(
    "49-emptydir-pod",
    "emptyDir volume",
    "storage",
    """# emptyDir

In namespace `stor-empty` create Pod `cache-pod` that:

- image `busybox:1.36`, command `sleep 3600`
- mounts an **emptyDir** volume named `cache` at `/cache`

Pod must be Ready.
""",
    "kubectl create namespace stor-empty --dry-run=client -o yaml | kubectl apply -f -",
    """
VOL=$(kubectl -n stor-empty get pod cache-pod -o jsonpath='{.spec.volumes[0].name}')
[ "$VOL" = "cache" ]
ED=$(kubectl -n stor-empty get pod cache-pod -o jsonpath='{.spec.volumes[0].emptyDir}')
[ -n "$ED" ] || kubectl -n stor-empty get pod cache-pod -o jsonpath='{.spec.volumes[0].emptyDir}' | grep -q .
MP=$(kubectl -n stor-empty get pod cache-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/cache" ]
kubectl -n stor-empty wait --for=condition=Ready pod/cache-pod --timeout=120s
""",
    [
        (
            "vol",
            "emptyDir named cache",
            50,
            """
VOL=$(kubectl -n stor-empty get pod cache-pod -o jsonpath='{.spec.volumes[0].name}')
[ "$VOL" = "cache" ]
kubectl -n stor-empty get pod cache-pod -o json | grep -q emptyDir
""",
        ),
        (
            "ready",
            "Mount path + Ready",
            50,
            """
MP=$(kubectl -n stor-empty get pod cache-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/cache" ]
kubectl -n stor-empty wait --for=condition=Ready pod/cache-pod --timeout=120s
""",
        ),
    ],
    """## Goal
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
""",
)

task(
    "50-hostpath-pv",
    "Static hostPath PV + PVC",
    "storage",
    """# Static provisioning

In namespace `stor-hostpath`:

1. Create PersistentVolume `hp-pv` with capacity **1Gi**, accessMode **ReadWriteOnce**, hostPath `/tmp/cka-hp-pv`, storageClassName `manual`
2. Create PVC `hp-pvc` requesting **1Gi**, RWO, storageClassName `manual`
3. Create Pod `hp-pod` (busybox:1.36, sleep 3600) mounting `hp-pvc` at `/data`

PVC must Bind; Pod must be Ready.
""",
    "kubectl create namespace stor-hostpath --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl get pv hp-pv >/dev/null
SC=$(kubectl get pv hp-pv -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "manual" ]
PHASE=$(kubectl -n stor-hostpath get pvc hp-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
kubectl -n stor-hostpath wait --for=condition=Ready pod/hp-pod --timeout=120s
""",
    [
        (
            "pv",
            "PV manual hostPath",
            40,
            """
kubectl get pv hp-pv >/dev/null
SC=$(kubectl get pv hp-pv -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "manual" ]
HP=$(kubectl get pv hp-pv -o jsonpath='{.spec.hostPath.path}')
[ "$HP" = "/tmp/cka-hp-pv" ]
""",
        ),
        (
            "bound",
            "PVC Bound + Pod Ready",
            60,
            """
PHASE=$(kubectl -n stor-hostpath get pvc hp-pvc -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
kubectl -n stor-hostpath wait --for=condition=Ready pod/hp-pod --timeout=120s
""",
        ),
    ],
    """## Goal
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
""",
)

task(
    "51-storageclass-custom",
    "Create StorageClass",
    "storage",
    """# StorageClass

Create StorageClass `fast-local` with:

- provisioner: `rancher.io/local-path` (same as kind's standard class family; use this exact provisioner string)
- `reclaimPolicy: Delete`
- `volumeBindingMode: WaitForFirstConsumer`

Then in namespace `stor-sc-custom` create PVC `fast-pvc` using that StorageClass, **1Gi**, RWO (does not need to Bind yet).
""",
    "kubectl create namespace stor-sc-custom --dry-run=client -o yaml | kubectl apply -f -",
    """
kubectl get storageclass fast-local >/dev/null
PROV=$(kubectl get storageclass fast-local -o jsonpath='{.provisioner}')
[ "$PROV" = "rancher.io/local-path" ]
RP=$(kubectl get storageclass fast-local -o jsonpath='{.reclaimPolicy}')
[ "$RP" = "Delete" ]
VBM=$(kubectl get storageclass fast-local -o jsonpath='{.volumeBindingMode}')
[ "$VBM" = "WaitForFirstConsumer" ]
SC=$(kubectl -n stor-sc-custom get pvc fast-pvc -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "fast-local" ]
""",
    [
        (
            "sc",
            "StorageClass fields",
            60,
            """
PROV=$(kubectl get storageclass fast-local -o jsonpath='{.provisioner}')
[ "$PROV" = "rancher.io/local-path" ]
RP=$(kubectl get storageclass fast-local -o jsonpath='{.reclaimPolicy}')
[ "$RP" = "Delete" ]
VBM=$(kubectl get storageclass fast-local -o jsonpath='{.volumeBindingMode}')
[ "$VBM" = "WaitForFirstConsumer" ]
""",
        ),
        (
            "pvc",
            "PVC uses StorageClass",
            40,
            """
SC=$(kubectl -n stor-sc-custom get pvc fast-pvc -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "fast-local" ]
""",
        ),
    ],
    """## Goal
Custom StorageClass + PVC referencing it.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-local
provisioner: rancher.io/local-path
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
EOF
kubectl -n stor-sc-custom apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: fast-pvc
  namespace: stor-sc-custom
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: fast-local
  resources:
    requests: {storage: 1Gi}
EOF
```
""",
)

task(
    "52-pvc-expand-request",
    "Larger PVC request",
    "storage",
    """# PVC size

In namespace `stor-big` create PVC `big-data` requesting **5Gi**, accessModes **ReadWriteOnce**, storageClassName **standard**.

Create Pod `big-pod` (busybox:1.36, sleep 3600) mounting it at `/data`. Ensure Bound + Ready.
""",
    "kubectl create namespace stor-big --dry-run=client -o yaml | kubectl apply -f -",
    """
REQ=$(kubectl -n stor-big get pvc big-data -o jsonpath='{.spec.resources.requests.storage}')
[ "$REQ" = "5Gi" ]
PHASE=$(kubectl -n stor-big get pvc big-data -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
kubectl -n stor-big wait --for=condition=Ready pod/big-pod --timeout=180s
""",
    [
        (
            "size",
            "PVC 5Gi",
            40,
            """
REQ=$(kubectl -n stor-big get pvc big-data -o jsonpath='{.spec.resources.requests.storage}')
[ "$REQ" = "5Gi" ]
""",
        ),
        (
            "ready",
            "Bound + Pod Ready",
            60,
            """
PHASE=$(kubectl -n stor-big get pvc big-data -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
kubectl -n stor-big wait --for=condition=Ready pod/big-pod --timeout=180s
""",
        ),
    ],
    """## Goal
5Gi PVC on `standard` + Pod mount.

## Steps
```bash
kubectl -n stor-big apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: big-data
  namespace: stor-big
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: standard
  resources:
    requests: {storage: 5Gi}
---
apiVersion: v1
kind: Pod
metadata:
  name: big-pod
  namespace: stor-big
spec:
  containers:
    - name: busybox
      image: busybox:1.36
      command: ["sleep", "3600"]
      volumeMounts:
        - {name: data, mountPath: /data}
  volumes:
    - name: data
      persistentVolumeClaim: {claimName: big-data}
EOF
```
""",
)

# ── troubleshooting ──────────────────────────────────────────
task(
    "53-fix-imagepull",
    "Fix ImagePullBackOff",
    "troubleshooting",
    """# ImagePullBackOff

Namespace `ts-pull` has Deployment `web` stuck pulling a bad image.

Fix it so pods run `nginx:1.27` and the Deployment has 1 Ready replica. Do not delete the Deployment.
""",
    """
kubectl create namespace ts-pull --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-pull apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: ts-pull
spec:
  replicas: 1
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: web}
    spec:
      containers:
        - name: web
          image: nginx:1.27-this-tag-does-not-exist
EOF
""",
    """
IMG=$(kubectl -n ts-pull get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
kubectl -n ts-pull rollout status deploy/web --timeout=120s
""",
    [
        (
            "image",
            "Image nginx:1.27",
            50,
            """
IMG=$(kubectl -n ts-pull get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
""",
        ),
        (
            "ready",
            "Deployment Ready",
            50,
            "kubectl -n ts-pull rollout status deploy/web --timeout=120s",
        ),
    ],
    """## Goal
Replace the invalid image with `nginx:1.27`.

## Steps
```bash
kubectl -n ts-pull set image deploy/web web=nginx:1.27
kubectl -n ts-pull rollout status deploy/web
```
""",
)

task(
    "54-fix-service-port",
    "Fix Service port mismatch",
    "troubleshooting",
    """# Wrong Service port

Namespace `ts-port` has Deployment `api` exposing container port **8080**, and Service `api-svc` currently listening on port **80** with targetPort **80** (broken).

Fix the Service so port **80** targets **8080**. Keep selector `app=api`.
""",
    """
kubectl create namespace ts-port --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-port apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: ts-port
spec:
  replicas: 1
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
        - name: api
          image: hashicorp/http-echo:1.0
          args: ["-text=ok", "-listen=:8080"]
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: api-svc
  namespace: ts-port
spec:
  selector: {app: api}
  ports:
    - port: 80
      targetPort: 80
EOF
kubectl -n ts-port rollout status deploy/api --timeout=180s
""",
    """
TP=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "8080" ]
SEL=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "api" ]
""",
    [
        (
            "target",
            "targetPort 8080",
            70,
            """
TP=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "8080" ]
""",
        ),
        (
            "sel",
            "Selector unchanged",
            30,
            """
SEL=$(kubectl -n ts-port get svc api-svc -o jsonpath='{.spec.selector.app}')
[ "$SEL" = "api" ]
""",
        ),
    ],
    """## Goal
Patch Service targetPort to 8080.

## Steps
```bash
kubectl -n ts-port patch svc api-svc -p '{"spec":{"ports":[{"port":80,"targetPort":8080}]}}'
```
""",
)

task(
    "55-fix-env-config",
    "Fix missing env from ConfigMap",
    "troubleshooting",
    """# Broken env

Namespace `ts-env` has Deployment `worker` expecting env `MODE` from ConfigMap `worker-config` key `MODE`.

The ConfigMap is missing or wrong. Create/fix ConfigMap `worker-config` with `MODE=batch` so the Deployment becomes Ready (1 replica). Prefer fixing the ConfigMap.
""",
    """
kubectl create namespace ts-env --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-env apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
  namespace: ts-env
spec:
  replicas: 1
  selector:
    matchLabels: {app: worker}
  template:
    metadata:
      labels: {app: worker}
    spec:
      containers:
        - name: worker
          image: busybox:1.36
          command: ["sh","-c","test -n \\"$MODE\\" && sleep 3600"]
          env:
            - name: MODE
              valueFrom:
                configMapKeyRef:
                  name: worker-config
                  key: MODE
EOF
""",
    """
VAL=$(kubectl -n ts-env get cm worker-config -o jsonpath='{.data.MODE}')
[ "$VAL" = "batch" ]
kubectl -n ts-env rollout status deploy/worker --timeout=120s
""",
    [
        (
            "cm",
            "ConfigMap MODE=batch",
            50,
            """
VAL=$(kubectl -n ts-env get cm worker-config -o jsonpath='{.data.MODE}')
[ "$VAL" = "batch" ]
""",
        ),
        (
            "ready",
            "Deployment Ready",
            50,
            "kubectl -n ts-env rollout status deploy/worker --timeout=120s",
        ),
    ],
    """## Goal
Provide ConfigMap `worker-config` with MODE=batch.

## Steps
```bash
kubectl -n ts-env create configmap worker-config --from-literal=MODE=batch
kubectl -n ts-env rollout restart deploy/worker
kubectl -n ts-env rollout status deploy/worker
```
""",
)

task(
    "56-fix-replicas",
    "Fix zero replicas",
    "troubleshooting",
    """# Scaled to zero

Namespace `ts-replicas` has Deployment `frontend` with **0** replicas (accidentally scaled down).

Scale it to **3** Ready replicas. Image must remain `nginx:1.27`.
""",
    """
kubectl create namespace ts-replicas --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-replicas apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ts-replicas
spec:
  replicas: 0
  selector:
    matchLabels: {app: frontend}
  template:
    metadata:
      labels: {app: frontend}
    spec:
      containers:
        - name: web
          image: nginx:1.27
EOF
""",
    """
REP=$(kubectl -n ts-replicas get deploy frontend -o jsonpath='{.spec.replicas}')
[ "$REP" = "3" ]
IMG=$(kubectl -n ts-replicas get deploy frontend -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
kubectl -n ts-replicas rollout status deploy/frontend --timeout=120s
""",
    [
        (
            "replicas",
            "replicas=3",
            50,
            """
REP=$(kubectl -n ts-replicas get deploy frontend -o jsonpath='{.spec.replicas}')
[ "$REP" = "3" ]
""",
        ),
        (
            "ready",
            "Ready + image unchanged",
            50,
            """
IMG=$(kubectl -n ts-replicas get deploy frontend -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
kubectl -n ts-replicas rollout status deploy/frontend --timeout=120s
""",
        ),
    ],
    """## Goal
Scale Deployment back to 3 replicas.

## Steps
```bash
kubectl -n ts-replicas scale deploy/frontend --replicas=3
kubectl -n ts-replicas rollout status deploy/frontend
```
""",
)

print("done")
