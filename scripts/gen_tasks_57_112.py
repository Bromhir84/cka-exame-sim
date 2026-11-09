#!/usr/bin/env python3
"""One-shot generator: scaffold tasks 57–112 and print catalog bank entries."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "tasks"

GRADE = """#!/usr/bin/env bash
set -euo pipefail
# Compatibility wrapper; assessment.yaml drives partial credit.
exit 0
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = content if content.endswith("\n") else content + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    if path.suffix == ".sh":
        path.chmod(path.stat().st_mode | 0o111)


def task(
    tid: str,
    title: str,
    domain: str,
    prompt: str,
    setup: str,
    answers: str,
    checks: list[tuple[str, str, int, str]],
) -> str:
    """checks: (id, description, weight, script_body)"""
    d = ROOT / tid
    write(d / "task.yaml", f"id: {tid}\ntitle: {title}\ndomain: {domain}\n")
    write(d / "prompt.md", prompt.strip() + "\n")
    write(d / "setup.sh", setup.strip() + "\n")
    write(d / "answers.md", answers.strip() + "\n")
    write(d / "grade.sh", GRADE)
    lines = ["checks:"]
    for cid, desc, weight, body in checks:
        rel = f"checks/{cid}.sh"
        write(d / rel, body.strip() + "\n")
        lines.append(f"  - id: {cid}")
        lines.append(f"    description: {desc}")
        lines.append(f"    weight: {weight}")
        lines.append(f"    script: {rel}")
    write(d / "assessment.yaml", "\n".join(lines) + "\n")
    return tid


def ns_setup(ns: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace {ns} --dry-run=client -o yaml | kubectl apply -f -
"""


TASKS: list[tuple] = []

# ---------- architecture (+12) → 24 ----------
TASKS += [
    (
        "57-rbac-configmaps",
        "Role for ConfigMaps",
        "architecture",
        """# Role — ConfigMaps

In namespace `arch-cm57` create:

1. ServiceAccount `cm-reader`
2. Role `cm-reader-role` allowing `get`, `list`, `watch` on `configmaps`
3. RoleBinding `cm-reader-binding` binding that Role to the ServiceAccount

Namespace exists.""",
        ns_setup("arch-cm57"),
        """## Goal
Namespaced Role for ConfigMap reads bound to an SA.

## Steps
```bash
kubectl -n arch-cm57 create sa cm-reader
kubectl -n arch-cm57 create role cm-reader-role --verb=get,list,watch --resource=configmaps
kubectl -n arch-cm57 create rolebinding cm-reader-binding --role=cm-reader-role --serviceaccount=arch-cm57:cm-reader
```""",
        [
            (
                "role",
                "Role verbs/resources",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-cm57 get role cm-reader-role >/dev/null
VERBS=$(kubectl -n arch-cm57 get role cm-reader-role -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q get
echo "$VERBS" | grep -q list
RES=$(kubectl -n arch-cm57 get role cm-reader-role -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q configmaps
exit 0""",
            ),
            (
                "bind",
                "RoleBinding to SA",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-cm57 get sa cm-reader >/dev/null
kubectl -n arch-cm57 get rolebinding cm-reader-binding >/dev/null
REF=$(kubectl -n arch-cm57 get rolebinding cm-reader-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "cm-reader-role" ]
SUB=$(kubectl -n arch-cm57 get rolebinding cm-reader-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "cm-reader" ]
exit 0""",
            ),
        ],
    ),
    (
        "58-clusterrole-nodes",
        "ClusterRole for nodes",
        "architecture",
        """# ClusterRole — nodes

Create:

1. ServiceAccount `node-inspector` in namespace `arch-nodes58`
2. ClusterRole `node-inspector` allowing `get` and `list` on `nodes`
3. ClusterRoleBinding `node-inspector-binding` binding that ClusterRole to the ServiceAccount

Namespace exists.""",
        ns_setup("arch-nodes58"),
        """## Goal
Cluster-scoped node read access for an SA.

## Steps
```bash
kubectl -n arch-nodes58 create sa node-inspector
kubectl create clusterrole node-inspector --verb=get,list --resource=nodes
kubectl create clusterrolebinding node-inspector-binding --clusterrole=node-inspector --serviceaccount=arch-nodes58:node-inspector
```""",
        [
            (
                "cr",
                "ClusterRole on nodes",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrole node-inspector >/dev/null
RES=$(kubectl get clusterrole node-inspector -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q nodes
VERBS=$(kubectl get clusterrole node-inspector -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q get
echo "$VERBS" | grep -q list
exit 0""",
            ),
            (
                "bind",
                "ClusterRoleBinding",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-nodes58 get sa node-inspector >/dev/null
kubectl get clusterrolebinding node-inspector-binding >/dev/null
REF=$(kubectl get clusterrolebinding node-inspector-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "node-inspector" ]
SUB=$(kubectl get clusterrolebinding node-inspector-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "node-inspector" ]
exit 0""",
            ),
        ],
    ),
    (
        "59-role-deployments",
        "Role for Deployments",
        "architecture",
        """# Role — Deployments

In namespace `arch-deploy59` create Role `deploy-manager` that allows `create`, `get`, `list`, `update`, `patch`, and `delete` on `deployments` in API group `apps`.

Also create ServiceAccount `deployer` and RoleBinding `deploy-manager-binding` linking them.""",
        ns_setup("arch-deploy59"),
        """## Goal
Full Deployment management Role bound to SA.

## Steps
```bash
kubectl -n arch-deploy59 create sa deployer
kubectl -n arch-deploy59 create role deploy-manager --verb=create,get,list,update,patch,delete --resource=deployments.apps
kubectl -n arch-deploy59 create rolebinding deploy-manager-binding --role=deploy-manager --serviceaccount=arch-deploy59:deployer
```""",
        [
            (
                "role",
                "Role on deployments",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-deploy59 get role deploy-manager >/dev/null
RES=$(kubectl -n arch-deploy59 get role deploy-manager -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q deployments
VERBS=$(kubectl -n arch-deploy59 get role deploy-manager -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q create
echo "$VERBS" | grep -q delete
exit 0""",
            ),
            (
                "bind",
                "RoleBinding",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-deploy59 get sa deployer >/dev/null
REF=$(kubectl -n arch-deploy59 get rolebinding deploy-manager-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "deploy-manager" ]
exit 0""",
            ),
        ],
    ),
    (
        "60-rbac-events",
        "Role for events",
        "architecture",
        """# Role — Events

In namespace `arch-events60`:

1. ServiceAccount `event-watcher`
2. Role `event-watcher-role` with `get`, `list`, `watch` on `events`
3. RoleBinding `event-watcher-binding`""",
        ns_setup("arch-events60"),
        """## Goal
Allow an SA to read Events.

## Steps
```bash
kubectl -n arch-events60 create sa event-watcher
kubectl -n arch-events60 create role event-watcher-role --verb=get,list,watch --resource=events
kubectl -n arch-events60 create rolebinding event-watcher-binding --role=event-watcher-role --serviceaccount=arch-events60:event-watcher
```""",
        [
            (
                "role",
                "Role on events",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
RES=$(kubectl -n arch-events60 get role event-watcher-role -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q events
exit 0""",
            ),
            (
                "bind",
                "Binding",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
SUB=$(kubectl -n arch-events60 get rolebinding event-watcher-binding -o jsonpath='{.subjects[0].name}')
[ "$SUB" = "event-watcher" ]
exit 0""",
            ),
        ],
    ),
    (
        "61-quota-compute",
        "ResourceQuota CPU/memory",
        "architecture",
        """# ResourceQuota — compute

In namespace `arch-quota61` create ResourceQuota `compute-quota` with hard limits:

- `requests.cpu`: `1`
- `requests.memory`: `1Gi`
- `limits.cpu`: `2`
- `limits.memory`: `2Gi`""",
        ns_setup("arch-quota61"),
        """## Goal
Namespace compute ResourceQuota.

## Steps
```bash
kubectl -n arch-quota61 create quota compute-quota --hard=requests.cpu=1,requests.memory=1Gi,limits.cpu=2,limits.memory=2Gi
```""",
        [
            (
                "exists",
                "Quota exists",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-quota61 get resourcequota compute-quota >/dev/null
exit 0""",
            ),
            (
                "hard",
                "Hard limits",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
CPU=$(kubectl -n arch-quota61 get resourcequota compute-quota -o jsonpath='{.spec.hard.requests\.cpu}')
[ "$CPU" = "1" ]
MEM=$(kubectl -n arch-quota61 get resourcequota compute-quota -o jsonpath='{.spec.hard.requests\.memory}')
echo "$MEM" | grep -Eq '1Gi|1024Mi'
LCPU=$(kubectl -n arch-quota61 get resourcequota compute-quota -o jsonpath='{.spec.hard.limits\.cpu}')
[ "$LCPU" = "2" ]
exit 0""",
            ),
        ],
    ),
    (
        "62-limitrange-pod",
        "LimitRange max Pod",
        "architecture",
        """# LimitRange

In namespace `arch-lr62` create LimitRange `pod-limits` of type `Container` with:

- default request cpu `100m`, memory `128Mi`
- default limit cpu `500m`, memory `256Mi`""",
        ns_setup("arch-lr62"),
        """## Goal
Container LimitRange defaults.

## Steps
```bash
kubectl -n arch-lr62 apply -f - <<'EOF'
apiVersion: v1
kind: LimitRange
metadata:
  name: pod-limits
spec:
  limits:
  - type: Container
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    default:
      cpu: 500m
      memory: 256Mi
EOF
```""",
        [
            (
                "exists",
                "LimitRange exists",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-lr62 get limitrange pod-limits >/dev/null
exit 0""",
            ),
            (
                "defaults",
                "Default request/limit",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
TYPE=$(kubectl -n arch-lr62 get limitrange pod-limits -o jsonpath='{.spec.limits[0].type}')
[ "$TYPE" = "Container" ]
DR=$(kubectl -n arch-lr62 get limitrange pod-limits -o jsonpath='{.spec.limits[0].defaultRequest.cpu}')
[ "$DR" = "100m" ]
DL=$(kubectl -n arch-lr62 get limitrange pod-limits -o jsonpath='{.spec.limits[0].default.cpu}')
[ "$DL" = "500m" ]
exit 0""",
            ),
        ],
    ),
    (
        "63-rbac-pods-logs",
        "Role for pod logs",
        "architecture",
        """# Role — pod logs

In namespace `arch-logs63` create Role `log-reader` allowing `get` on `pods` and `get` on `pods/log`.

Bind it to ServiceAccount `log-reader` via RoleBinding `log-reader-binding`.""",
        ns_setup("arch-logs63"),
        """## Goal
SA can read pods and pod logs.

## Steps
```bash
kubectl -n arch-logs63 create sa log-reader
kubectl -n arch-logs63 apply -f - <<'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: log-reader
  namespace: arch-logs63
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get"]
EOF
kubectl -n arch-logs63 create rolebinding log-reader-binding --role=log-reader --serviceaccount=arch-logs63:log-reader
```""",
        [
            (
                "role",
                "pods and pods/log",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
RES=$(kubectl -n arch-logs63 get role log-reader -o jsonpath='{.rules[*].resources[*]}')
echo "$RES" | grep -q pods
echo "$RES" | grep -q pods/log
exit 0""",
            ),
            (
                "bind",
                "RoleBinding",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n arch-logs63 get rolebinding log-reader-binding >/dev/null
exit 0""",
            ),
        ],
    ),
    (
        "64-clusterrole-pv",
        "ClusterRole for PVs",
        "architecture",
        """# ClusterRole — PersistentVolumes

Create ClusterRole `pv-viewer` with `get`, `list`, `watch` on `persistentvolumes`.

Create ServiceAccount `pv-viewer` in `arch-pv64` and ClusterRoleBinding `pv-viewer-binding`.""",
        ns_setup("arch-pv64"),
        """## Goal
Cluster-wide PV read access.

## Steps
```bash
kubectl -n arch-pv64 create sa pv-viewer
kubectl create clusterrole pv-viewer --verb=get,list,watch --resource=persistentvolumes
kubectl create clusterrolebinding pv-viewer-binding --clusterrole=pv-viewer --serviceaccount=arch-pv64:pv-viewer
```""",
        [
            (
                "cr",
                "ClusterRole",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
RES=$(kubectl get clusterrole pv-viewer -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q persistentvolumes
exit 0""",
            ),
            (
                "bind",
                "ClusterRoleBinding",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
REF=$(kubectl get clusterrolebinding pv-viewer-binding -o jsonpath='{.roleRef.name}')
[ "$REF" = "pv-viewer" ]
exit 0""",
            ),
        ],
    ),
    (
        "65-priorityclass",
        "PriorityClass",
        "architecture",
        """# PriorityClass

Create PriorityClass `high-priority-65` with:

- `value: 1000000`
- `globalDefault: false`
- `description: "CKA practice high priority"`""",
        """#!/usr/bin/env bash
set -euo pipefail
true
""",
        """## Goal
Non-default PriorityClass.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority-65
value: 1000000
globalDefault: false
description: "CKA practice high priority"
EOF
```""",
        [
            (
                "exists",
                "PriorityClass exists",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl get priorityclass high-priority-65 >/dev/null
exit 0""",
            ),
            (
                "value",
                "Value and globalDefault",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
VAL=$(kubectl get priorityclass high-priority-65 -o jsonpath='{.value}')
[ "$VAL" = "1000000" ]
GD=$(kubectl get priorityclass high-priority-65 -o jsonpath='{.globalDefault}')
[ "$GD" = "false" ]
exit 0""",
            ),
        ],
    ),
    (
        "66-quota-object-count",
        "ResourceQuota object counts",
        "architecture",
        """# ResourceQuota — counts

In namespace `arch-count66` create ResourceQuota `object-counts` with hard:

- `pods`: `10`
- `services`: `5`
- `secrets`: `10`
- `configmaps`: `10`""",
        ns_setup("arch-count66"),
        """## Goal
Object-count ResourceQuota.

## Steps
```bash
kubectl -n arch-count66 create quota object-counts --hard=pods=10,services=5,secrets=10,configmaps=10
```""",
        [
            (
                "pods",
                "pods hard=10",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n arch-count66 get resourcequota object-counts -o jsonpath='{.spec.hard.pods}')
[ "$P" = "10" ]
exit 0""",
            ),
            (
                "svc",
                "services hard=5",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n arch-count66 get resourcequota object-counts -o jsonpath='{.spec.hard.services}')
[ "$S" = "5" ]
exit 0""",
            ),
        ],
    ),
    (
        "67-rbac-impersonate",
        "ClusterRole impersonate users",
        "architecture",
        """# ClusterRole — impersonate

Create ClusterRole `user-impersonator` that allows verb `impersonate` on resource `users` in API group empty string.

Create ServiceAccount `impersonator` in `arch-imp67` and ClusterRoleBinding `user-impersonator-binding`.""",
        ns_setup("arch-imp67"),
        """## Goal
Impersonation ClusterRole for admins practice.

## Steps
```bash
kubectl -n arch-imp67 create sa impersonator
kubectl apply -f - <<'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: user-impersonator
rules:
- apiGroups: [""]
  resources: ["users"]
  verbs: ["impersonate"]
EOF
kubectl create clusterrolebinding user-impersonator-binding --clusterrole=user-impersonator --serviceaccount=arch-imp67:impersonator
```""",
        [
            (
                "cr",
                "impersonate users",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
RES=$(kubectl get clusterrole user-impersonator -o jsonpath='{.rules[0].resources[*]}')
echo "$RES" | grep -q users
VERBS=$(kubectl get clusterrole user-impersonator -o jsonpath='{.rules[0].verbs[*]}')
echo "$VERBS" | grep -q impersonate
exit 0""",
            ),
            (
                "bind",
                "ClusterRoleBinding",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl get clusterrolebinding user-impersonator-binding >/dev/null
exit 0""",
            ),
        ],
    ),
    (
        "68-sa-imagepullsecret",
        "SA with imagePullSecrets",
        "architecture",
        """# ServiceAccount imagePullSecrets

In namespace `arch-pull68`:

1. Create Secret `regcred` of type `kubernetes.io/dockerconfigjson` with any valid-looking dockerconfig (dummy is fine)
2. Create ServiceAccount `puller` that references `imagePullSecrets: [{name: regcred}]`""",
        ns_setup("arch-pull68"),
        """## Goal
SA wired to a dockerconfig pull secret.

## Steps
```bash
kubectl -n arch-pull68 create secret docker-registry regcred \\
  --docker-server=https://index.docker.io/v1/ \\
  --docker-username=dummy --docker-password=dummy --docker-email=a@b.c
kubectl -n arch-pull68 create sa puller
kubectl -n arch-pull68 patch sa puller -p '{"imagePullSecrets":[{"name":"regcred"}]}'
```""",
        [
            (
                "secret",
                "dockerconfig secret",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
TYPE=$(kubectl -n arch-pull68 get secret regcred -o jsonpath='{.type}')
[ "$TYPE" = "kubernetes.io/dockerconfigjson" ]
exit 0""",
            ),
            (
                "sa",
                "SA imagePullSecrets",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
NAME=$(kubectl -n arch-pull68 get sa puller -o jsonpath='{.imagePullSecrets[0].name}')
[ "$NAME" = "regcred" ]
exit 0""",
            ),
        ],
    ),
]

# ---------- workloads (+11) → 22 ----------
TASKS += [
    (
        "69-deploy-env-secret",
        "Deployment env from Secret",
        "workloads",
        """# Deployment + Secret env

In namespace `wl-env69`:

1. Secret `app-secret` with key `PASSWORD` = `s3cret`
2. Deployment `web` (1 replica, `nginx:1.27`, container `web`) with env var `PASSWORD` from that Secret key
3. Deployment must be Ready""",
        ns_setup("wl-env69"),
        """## Goal
Wire Secret key into Deployment env.

## Steps
```bash
kubectl -n wl-env69 create secret generic app-secret --from-literal=PASSWORD=s3cret
kubectl -n wl-env69 create deploy web --image=nginx:1.27
kubectl -n wl-env69 set env deploy/web --from=secret/app-secret
kubectl -n wl-env69 rollout status deploy/web
```""",
        [
            (
                "secret",
                "Secret key",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-env69 get secret app-secret >/dev/null
exit 0""",
            ),
            (
                "env",
                "Env from secret + Ready",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
REF=$(kubectl -n wl-env69 get deploy web -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="PASSWORD")].valueFrom.secretKeyRef.name}')
[ "$REF" = "app-secret" ]
KEY=$(kubectl -n wl-env69 get deploy web -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="PASSWORD")].valueFrom.secretKeyRef.key}')
[ "$KEY" = "PASSWORD" ]
kubectl -n wl-env69 rollout status deploy/web --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "70-statefulset-basic",
        "StatefulSet basics",
        "workloads",
        """# StatefulSet

In namespace `wl-sts70` create StatefulSet `web` with:

- 2 replicas
- serviceName `web`
- container `nginx` image `nginx:1.27`
- label `app=web` on pod template and selector

Also create headless Service `web` (`clusterIP: None`) selecting `app=web`. Pods should become Ready.""",
        ns_setup("wl-sts70"),
        """## Goal
StatefulSet + headless Service.

## Steps
```bash
kubectl -n wl-sts70 apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  clusterIP: None
  selector:
    app: web
  ports:
  - port: 80
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: web
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
      - name: nginx
        image: nginx:1.27
EOF
kubectl -n wl-sts70 rollout status statefulset/web --timeout=180s
```""",
        [
            (
                "svc",
                "Headless Service",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
CIP=$(kubectl -n wl-sts70 get svc web -o jsonpath='{.spec.clusterIP}')
[ "$CIP" = "None" ]
exit 0""",
            ),
            (
                "sts",
                "StatefulSet Ready",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
REP=$(kubectl -n wl-sts70 get sts web -o jsonpath='{.spec.replicas}')
[ "$REP" = "2" ]
SN=$(kubectl -n wl-sts70 get sts web -o jsonpath='{.spec.serviceName}')
[ "$SN" = "web" ]
kubectl -n wl-sts70 rollout status statefulset/web --timeout=180s
exit 0""",
            ),
        ],
    ),
    (
        "71-cronjob-schedule",
        "CronJob every 5 minutes",
        "workloads",
        """# CronJob

In namespace `wl-cron71` create CronJob `tick` that:

- schedule: `*/5 * * * *`
- image `busybox:1.36`
- command `["sh","-c","date; echo tick"]`
- `concurrencyPolicy: Forbid`
- successfulJobsHistoryLimit 1, failedJobsHistoryLimit 1""",
        ns_setup("wl-cron71"),
        """## Goal
CronJob with Forbid concurrency.

## Steps
```bash
kubectl -n wl-cron71 create cronjob tick --image=busybox:1.36 --schedule='*/5 * * * *' -- sh -c 'date; echo tick'
kubectl -n wl-cron71 patch cronjob tick -p '{"spec":{"concurrencyPolicy":"Forbid","successfulJobsHistoryLimit":1,"failedJobsHistoryLimit":1}}'
```""",
        [
            (
                "sched",
                "Schedule",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n wl-cron71 get cronjob tick -o jsonpath='{.spec.schedule}')
[ "$S" = "*/5 * * * *" ]
exit 0""",
            ),
            (
                "policy",
                "Concurrency Forbid",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n wl-cron71 get cronjob tick -o jsonpath='{.spec.concurrencyPolicy}')
[ "$P" = "Forbid" ]
exit 0""",
            ),
        ],
    ),
    (
        "72-deploy-rolling-maxunavail",
        "RollingUpdate maxUnavailable",
        "workloads",
        """# Deployment strategy

In namespace `wl-roll72` create Deployment `api` (3 replicas, `nginx:1.27`) with RollingUpdate strategy:

- `maxUnavailable: 0`
- `maxSurge: 1`

Deployment must become Ready.""",
        ns_setup("wl-roll72"),
        """## Goal
RollingUpdate with maxUnavailable 0.

## Steps
```bash
kubectl -n wl-roll72 create deploy api --image=nginx:1.27 --replicas=3
kubectl -n wl-roll72 patch deploy api -p '{"spec":{"strategy":{"type":"RollingUpdate","rollingUpdate":{"maxUnavailable":0,"maxSurge":1}}}}'
kubectl -n wl-roll72 rollout status deploy/api
```""",
        [
            (
                "strat",
                "maxUnavailable/maxSurge",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
MU=$(kubectl -n wl-roll72 get deploy api -o jsonpath='{.spec.strategy.rollingUpdate.maxUnavailable}')
[ "$MU" = "0" ]
MS=$(kubectl -n wl-roll72 get deploy api -o jsonpath='{.spec.strategy.rollingUpdate.maxSurge}')
[ "$MS" = "1" ]
exit 0""",
            ),
            (
                "ready",
                "Ready replicas",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-roll72 rollout status deploy/api --timeout=180s
exit 0""",
            ),
        ],
    ),
    (
        "73-job-completions",
        "Job with completions",
        "workloads",
        """# Job completions

In namespace `wl-comp73` create Job `batch` with:

- `completions: 3`
- `parallelism: 1`
- image `busybox:1.36`
- command `["sh","-c","echo done"]`
- restartPolicy Never

Wait until the Job is Complete.""",
        ns_setup("wl-comp73"),
        """## Goal
Job with 3 completions.

## Steps
```bash
kubectl -n wl-comp73 apply -f - <<'EOF'
apiVersion: batch/v1
kind: Job
metadata:
  name: batch
spec:
  completions: 3
  parallelism: 1
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: c
        image: busybox:1.36
        command: ["sh","-c","echo done"]
EOF
kubectl -n wl-comp73 wait --for=condition=Complete job/batch --timeout=180s
```""",
        [
            (
                "spec",
                "completions/parallelism",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
C=$(kubectl -n wl-comp73 get job batch -o jsonpath='{.spec.completions}')
[ "$C" = "3" ]
P=$(kubectl -n wl-comp73 get job batch -o jsonpath='{.spec.parallelism}')
[ "$P" = "1" ]
exit 0""",
            ),
            (
                "done",
                "Complete",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-comp73 wait --for=condition=Complete job/batch --timeout=180s
exit 0""",
            ),
        ],
    ),
    (
        "74-deploy-nodeselector-os",
        "Deployment nodeSelector OS",
        "workloads",
        """# nodeSelector

In namespace `wl-os74` create Deployment `linux-web` (1 replica, `nginx:1.27`) with nodeSelector `kubernetes.io/os=linux`. Ready.""",
        ns_setup("wl-os74"),
        """## Goal
Schedule only on linux nodes.

## Steps
```bash
kubectl -n wl-os74 create deploy linux-web --image=nginx:1.27
kubectl -n wl-os74 patch deploy linux-web -p '{"spec":{"template":{"spec":{"nodeSelector":{"kubernetes.io/os":"linux"}}}}}'
kubectl -n wl-os74 rollout status deploy/linux-web
```""",
        [
            (
                "sel",
                "nodeSelector",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
OS=$(kubectl -n wl-os74 get deploy linux-web -o jsonpath='{.spec.template.spec.nodeSelector.kubernetes\.io/os}')
[ "$OS" = "linux" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-os74 rollout status deploy/linux-web --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "75-pod-securitycontext-user",
        "Pod runAsUser",
        "workloads",
        """# Pod securityContext

In namespace `wl-sec75` create Pod `secure-pod` using `busybox:1.36` with command `sleep 3600` and pod-level securityContext:

- `runAsUser: 1000`
- `runAsGroup: 3000`

Pod must be Ready.""",
        ns_setup("wl-sec75"),
        """## Goal
Non-root UID/GID on Pod.

## Steps
```bash
kubectl -n wl-sec75 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
EOF
kubectl -n wl-sec75 wait --for=condition=Ready pod/secure-pod --timeout=120s
```""",
        [
            (
                "uid",
                "runAsUser/Group",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
U=$(kubectl -n wl-sec75 get pod secure-pod -o jsonpath='{.spec.securityContext.runAsUser}')
[ "$U" = "1000" ]
G=$(kubectl -n wl-sec75 get pod secure-pod -o jsonpath='{.spec.securityContext.runAsGroup}')
[ "$G" = "3000" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-sec75 wait --for=condition=Ready pod/secure-pod --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "76-deploy-envfrom-cm",
        "Deployment envFrom ConfigMap",
        "workloads",
        """# envFrom ConfigMap

In namespace `wl-envfrom76`:

1. ConfigMap `app-config` with `APP_MODE=prod` and `LOG_LEVEL=info`
2. Deployment `api` (`nginx:1.27`) using `envFrom` → that ConfigMap
3. Ready""",
        ns_setup("wl-envfrom76"),
        """## Goal
envFrom ConfigMap on Deployment.

## Steps
```bash
kubectl -n wl-envfrom76 create cm app-config --from-literal=APP_MODE=prod --from-literal=LOG_LEVEL=info
kubectl -n wl-envfrom76 create deploy api --image=nginx:1.27
kubectl -n wl-envfrom76 set env deploy/api --from=configmap/app-config
kubectl -n wl-envfrom76 rollout status deploy/api
```""",
        [
            (
                "cm",
                "ConfigMap keys",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-envfrom76 get cm app-config >/dev/null
exit 0""",
            ),
            (
                "env",
                "envFrom + Ready",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
# set env --from creates individual env entries OR envFrom depending on kubectl version; accept either
JSON=$(kubectl -n wl-envfrom76 get deploy api -o json)
echo "$JSON" | grep -q app-config
kubectl -n wl-envfrom76 rollout status deploy/api --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "77-replicaset-scale",
        "Scale a ReplicaSet",
        "workloads",
        """# ReplicaSet

Namespace `wl-rs77` has ReplicaSet `web` at 1 replica. Scale it to **4** replicas and wait until 4 are Ready.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace wl-rs77 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n wl-rs77 apply -f - <<'EOF'
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web
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
      - name: nginx
        image: nginx:1.27
EOF
kubectl -n wl-rs77 rollout status replicaset/web --timeout=120s || true
""",
        """## Goal
Scale ReplicaSet to 4.

## Steps
```bash
kubectl -n wl-rs77 scale rs/web --replicas=4
kubectl -n wl-rs77 wait --for=jsonpath='{.status.readyReplicas}'=4 rs/web --timeout=120s
```""",
        [
            (
                "replicas",
                "spec replicas 4",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
R=$(kubectl -n wl-rs77 get rs web -o jsonpath='{.spec.replicas}')
[ "$R" = "4" ]
exit 0""",
            ),
            (
                "ready",
                "4 Ready",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
for i in $(seq 1 30); do
  RR=$(kubectl -n wl-rs77 get rs web -o jsonpath='{.status.readyReplicas}')
  [ "${RR:-0}" = "4" ] && exit 0
  sleep 2
done
exit 1""",
            ),
        ],
    ),
    (
        "78-pod-lifecycle-hooks",
        "Pod lifecycle postStart",
        "workloads",
        """# Lifecycle hook

In namespace `wl-hook78` create Pod `hook-pod` (`busybox:1.36`, `sleep 3600`) with a `postStart` exec hook that runs `["sh","-c","echo hooked > /tmp/hooked"]`.

Pod Ready.""",
        ns_setup("wl-hook78"),
        """## Goal
postStart lifecycle hook.

## Steps
```bash
kubectl -n wl-hook78 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: hook-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    lifecycle:
      postStart:
        exec:
          command: ["sh","-c","echo hooked > /tmp/hooked"]
EOF
kubectl -n wl-hook78 wait --for=condition=Ready pod/hook-pod --timeout=120s
```""",
        [
            (
                "hook",
                "postStart present",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
CMD=$(kubectl -n wl-hook78 get pod hook-pod -o jsonpath='{.spec.containers[0].lifecycle.postStart.exec.command[*]}')
echo "$CMD" | grep -q hooked
exit 0""",
            ),
            (
                "ready",
                "Ready",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-hook78 wait --for=condition=Ready pod/hook-pod --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "79-deploy-annotation",
        "Deployment annotation",
        "workloads",
        """# Annotations

In namespace `wl-ann79` create Deployment `annotated` (`nginx:1.27`, 1 replica) with pod template annotation `cka.exam/owner=team-a`. Ready.""",
        ns_setup("wl-ann79"),
        """## Goal
Pod template annotation.

## Steps
```bash
kubectl -n wl-ann79 create deploy annotated --image=nginx:1.27
kubectl -n wl-ann79 patch deploy annotated --type=merge -p '{"spec":{"template":{"metadata":{"annotations":{"cka.exam/owner":"team-a"}}}}}'
kubectl -n wl-ann79 rollout status deploy/annotated
```""",
        [
            (
                "ann",
                "Annotation value",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
A=$(kubectl -n wl-ann79 get deploy annotated -o jsonpath='{.spec.template.metadata.annotations.cka\.exam/owner}')
[ "$A" = "team-a" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n wl-ann79 rollout status deploy/annotated --timeout=120s
exit 0""",
            ),
        ],
    ),
]

# ---------- networking (+11) → 22 ----------
TASKS += [
    (
        "80-svc-nodeport-custom",
        "NodePort fixed port",
        "networking",
        """# NodePort

In namespace `net-np80` create Deployment `web` (`nginx:1.27`, label `app=web`) and Service `web-np` of type NodePort selecting `app=web`, port 80 → targetPort 80, **nodePort 30080**.""",
        ns_setup("net-np80"),
        """## Goal
NodePort 30080.

## Steps
```bash
kubectl -n net-np80 create deploy web --image=nginx:1.27
kubectl -n net-np80 label deploy web app=web --overwrite
kubectl -n net-np80 expose deploy web --name=web-np --port=80 --type=NodePort
kubectl -n net-np80 patch svc web-np -p '{"spec":{"ports":[{"port":80,"targetPort":80,"nodePort":30080}]}}'
```""",
        [
            (
                "type",
                "NodePort type",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
T=$(kubectl -n net-np80 get svc web-np -o jsonpath='{.spec.type}')
[ "$T" = "NodePort" ]
exit 0""",
            ),
            (
                "port",
                "nodePort 30080",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
NP=$(kubectl -n net-np80 get svc web-np -o jsonpath='{.spec.ports[0].nodePort}')
[ "$NP" = "30080" ]
exit 0""",
            ),
        ],
    ),
    (
        "81-netpol-allow-frontend",
        "NetworkPolicy allow from frontend",
        "networking",
        """# NetworkPolicy ingress

In namespace `net-np81` create NetworkPolicy `allow-frontend` that:

- selects pods with `app=backend`
- policyTypes Ingress
- allows Ingress from pods with `app=frontend` on TCP port 80""",
        ns_setup("net-np81"),
        """## Goal
Ingress NP from frontend→backend:80.

## Steps
```bash
kubectl -n net-np81 apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes: [Ingress]
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
EOF
```""",
        [
            (
                "sel",
                "podSelector backend",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
APP=$(kubectl -n net-np81 get networkpolicy allow-frontend -o jsonpath='{.spec.podSelector.matchLabels.app}')
[ "$APP" = "backend" ]
exit 0""",
            ),
            (
                "from",
                "from frontend port 80",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
FROM=$(kubectl -n net-np81 get networkpolicy allow-frontend -o jsonpath='{.spec.ingress[0].from[0].podSelector.matchLabels.app}')
[ "$FROM" = "frontend" ]
PORT=$(kubectl -n net-np81 get networkpolicy allow-frontend -o jsonpath='{.spec.ingress[0].ports[0].port}')
[ "$PORT" = "80" ]
exit 0""",
            ),
        ],
    ),
    (
        "82-ingress-rewrite",
        "Ingress path to service",
        "networking",
        """# Ingress

Namespace `net-ing82` has Deployment/Service `echo` on port 80. Create Ingress `echo-ing` with class `nginx`, host `echo.cka.local`, path `/` Prefix to service `echo:80`.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-ing82 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-ing82 create deploy echo --image=nginx:1.27
kubectl -n net-ing82 expose deploy echo --port=80
kubectl -n net-ing82 rollout status deploy/echo --timeout=120s
""",
        """## Goal
Host-based Ingress.

## Steps
```bash
kubectl -n net-ing82 create ingress echo-ing --class=nginx --rule='echo.cka.local/*=echo:80'
```""",
        [
            (
                "host",
                "Host rule",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
H=$(kubectl -n net-ing82 get ingress echo-ing -o jsonpath='{.spec.rules[0].host}')
[ "$H" = "echo.cka.local" ]
exit 0""",
            ),
            (
                "svc",
                "Backend service",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n net-ing82 get ingress echo-ing -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}')
[ "$S" = "echo" ]
exit 0""",
            ),
        ],
    ),
    (
        "83-svc-session-affinity",
        "Service sessionAffinity",
        "networking",
        """# Session affinity

In namespace `net-aff83` create Service `sticky` (ClusterIP) selecting `app=web`, port 80, with `sessionAffinity: ClientIP`.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-aff83 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-aff83 create deploy web --image=nginx:1.27
kubectl -n net-aff83 label deploy web app=web --overwrite
kubectl -n net-aff83 label pods -l app=web app=web --overwrite 2>/dev/null || true
""",
        """## Goal
ClientIP session affinity.

## Steps
```bash
kubectl -n net-aff83 expose deploy web --name=sticky --port=80
kubectl -n net-aff83 patch svc sticky -p '{"spec":{"sessionAffinity":"ClientIP"}}'
```""",
        [
            (
                "aff",
                "sessionAffinity ClientIP",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
A=$(kubectl -n net-aff83 get svc sticky -o jsonpath='{.spec.sessionAffinity}')
[ "$A" = "ClientIP" ]
exit 0""",
            ),
            (
                "sel",
                "Selector app=web",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n net-aff83 get svc sticky -o jsonpath='{.spec.selector.app}')
[ "$S" = "web" ]
exit 0""",
            ),
        ],
    ),
    (
        "84-netpol-deny-egress",
        "NetworkPolicy deny egress",
        "networking",
        """# Egress deny

In namespace `net-eg84` create NetworkPolicy `deny-egress` selecting all pods (`podSelector: {}`) with policyTypes `Egress` and **no egress rules** (deny all egress).""",
        ns_setup("net-eg84"),
        """## Goal
Default-deny egress.

## Steps
```bash
kubectl -n net-eg84 apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-egress
spec:
  podSelector: {}
  policyTypes: [Egress]
EOF
```""",
        [
            (
                "types",
                "policyTypes Egress",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
T=$(kubectl -n net-eg84 get networkpolicy deny-egress -o jsonpath='{.spec.policyTypes[*]}')
echo "$T" | grep -q Egress
exit 0""",
            ),
            (
                "empty",
                "No egress rules",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
E=$(kubectl -n net-eg84 get networkpolicy deny-egress -o jsonpath='{.spec.egress[*]}')
[ -z "$E" ]
exit 0""",
            ),
        ],
    ),
    (
        "85-endpoints-manual",
        "Service without selectors",
        "networking",
        """# External endpoints

In namespace `net-ep85` create Service `external-web` **without** a selector, port 80. Create Endpoints `external-web` with subset IP `1.2.3.4` port 80 TCP.""",
        ns_setup("net-ep85"),
        """## Goal
Selector-less Service + Endpoints.

## Steps
```bash
kubectl -n net-ep85 apply -f - <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: external-web
spec:
  ports:
  - port: 80
---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-web
subsets:
- addresses:
  - ip: 1.2.3.4
  ports:
  - port: 80
EOF
```""",
        [
            (
                "svc",
                "No selector",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n net-ep85 get svc external-web >/dev/null
SEL=$(kubectl -n net-ep85 get svc external-web -o jsonpath='{.spec.selector}')
[ -z "$SEL" ]
exit 0""",
            ),
            (
                "ep",
                "Endpoints IP",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
IP=$(kubectl -n net-ep85 get endpoints external-web -o jsonpath='{.subsets[0].addresses[0].ip}')
[ "$IP" = "1.2.3.4" ]
exit 0""",
            ),
        ],
    ),
    (
        "86-ingress-tls-secret",
        "Ingress TLS secret",
        "networking",
        """# Ingress TLS

Namespace `net-tls86` has Service `web` on port 80. Create TLS Secret `web-tls` (type kubernetes.io/tls) with dummy cert/key, and Ingress `web-tls-ing` (class nginx) for host `tls.cka.local` path `/` → `web:80` referencing that TLS secret.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-tls86 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-tls86 create deploy web --image=nginx:1.27
kubectl -n net-tls86 expose deploy web --port=80
kubectl -n net-tls86 rollout status deploy/web --timeout=120s
""",
        """## Goal
Ingress with TLS section.

## Steps
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \\
  -keyout /tmp/tls.key -out /tmp/tls.crt -subj "/CN=tls.cka.local"
kubectl -n net-tls86 create secret tls web-tls --cert=/tmp/tls.crt --key=/tmp/tls.key
kubectl -n net-tls86 apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-tls-ing
spec:
  ingressClassName: nginx
  tls:
  - hosts: [tls.cka.local]
    secretName: web-tls
  rules:
  - host: tls.cka.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
EOF
```""",
        [
            (
                "secret",
                "TLS secret",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
TYPE=$(kubectl -n net-tls86 get secret web-tls -o jsonpath='{.type}')
[ "$TYPE" = "kubernetes.io/tls" ]
exit 0""",
            ),
            (
                "ing",
                "Ingress TLS host",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
SN=$(kubectl -n net-tls86 get ingress web-tls-ing -o jsonpath='{.spec.tls[0].secretName}')
[ "$SN" = "web-tls" ]
H=$(kubectl -n net-tls86 get ingress web-tls-ing -o jsonpath='{.spec.rules[0].host}')
[ "$H" = "tls.cka.local" ]
exit 0""",
            ),
        ],
    ),
    (
        "87-svc-loadbalancer",
        "LoadBalancer Service type",
        "networking",
        """# LoadBalancer Service

In namespace `net-lb87` expose Deployment `web` (`nginx:1.27`) as Service `web-lb` of type **LoadBalancer** on port 80. (Pending external IP is OK in kind.)""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-lb87 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-lb87 create deploy web --image=nginx:1.27
kubectl -n net-lb87 rollout status deploy/web --timeout=120s
""",
        """## Goal
Service type LoadBalancer.

## Steps
```bash
kubectl -n net-lb87 expose deploy web --name=web-lb --port=80 --type=LoadBalancer
```""",
        [
            (
                "type",
                "type LoadBalancer",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
T=$(kubectl -n net-lb87 get svc web-lb -o jsonpath='{.spec.type}')
[ "$T" = "LoadBalancer" ]
exit 0""",
            ),
            (
                "port",
                "port 80",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n net-lb87 get svc web-lb -o jsonpath='{.spec.ports[0].port}')
[ "$P" = "80" ]
exit 0""",
            ),
        ],
    ),
    (
        "88-netpol-namespace-selector",
        "NetworkPolicy namespaceSelector",
        "networking",
        """# NetworkPolicy from namespace

In namespace `net-ns88` create NetworkPolicy `allow-from-prod` selecting `app=db` pods, Ingress only, allowing from namespaces labeled `env=prod` (namespaceSelector).""",
        ns_setup("net-ns88"),
        """## Goal
Ingress from namespaces with env=prod.

## Steps
```bash
kubectl -n net-ns88 apply -f - <<'EOF'
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-prod
spec:
  podSelector:
    matchLabels:
      app: db
  policyTypes: [Ingress]
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          env: prod
EOF
```""",
        [
            (
                "sel",
                "podSelector db",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
A=$(kubectl -n net-ns88 get networkpolicy allow-from-prod -o jsonpath='{.spec.podSelector.matchLabels.app}')
[ "$A" = "db" ]
exit 0""",
            ),
            (
                "ns",
                "namespaceSelector env=prod",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
E=$(kubectl -n net-ns88 get networkpolicy allow-from-prod -o jsonpath='{.spec.ingress[0].from[0].namespaceSelector.matchLabels.env}')
[ "$E" = "prod" ]
exit 0""",
            ),
        ],
    ),
    (
        "89-svc-port-name",
        "Service targetPort by name",
        "networking",
        """# Service targetPort by name

In namespace `net-name89`, create Deployment `api` and ClusterIP Service `named`.

Deployment `api` uses image `nginx:1.27`, label `app=api`, and one container port:

- name `http`
- containerPort **80**

Service `named` selects `app=api` and exposes one port:

- name `http`
- port **80**
- targetPort `http` (the container port's name, not the number 80)""",
        ns_setup("net-name89"),
        """## Goal
Point Service `named` at Deployment `api` using port name `http`.

## Steps
```bash
kubectl -n net-name89 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
        image: nginx:1.27
        ports:
        - name: http
          containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: named
spec:
  selector:
    app: api
  ports:
  - name: http
    port: 80
    targetPort: http
EOF
```""",
        [
            (
                "svc",
                "Service port named http, targetPort http",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
N=$(kubectl -n net-name89 get svc named -o jsonpath='{.spec.ports[0].name}')
[ "$N" = "http" ]
TP=$(kubectl -n net-name89 get svc named -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "http" ]
exit 0""",
            ),
            (
                "pod",
                "Container port named http",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
N=$(kubectl -n net-name89 get deploy api -o jsonpath='{.spec.template.spec.containers[0].ports[0].name}')
[ "$N" = "http" ]
exit 0""",
            ),
        ],
    ),
    (
        "90-ingress-multpath",
        "Ingress two paths",
        "networking",
        """# Ingress multi-path

Namespace `net-mp90` has Services `app` and `api` on port 80. Create Ingress `split` (class nginx), host `split.cka.local`:

- path `/app` Prefix → service `app:80`
- path `/api` Prefix → service `api:80`""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace net-mp90 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n net-mp90 create deploy app --image=nginx:1.27
kubectl -n net-mp90 create deploy api --image=nginx:1.27
kubectl -n net-mp90 expose deploy app --port=80
kubectl -n net-mp90 expose deploy api --port=80
kubectl -n net-mp90 rollout status deploy/app --timeout=120s
kubectl -n net-mp90 rollout status deploy/api --timeout=120s
""",
        """## Goal
Two paths on one host.

## Steps
```bash
kubectl -n net-mp90 create ingress split --class=nginx \\
  --rule='split.cka.local/app=app:80' \\
  --rule='split.cka.local/api=api:80'
```""",
        [
            (
                "host",
                "Host",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
H=$(kubectl -n net-mp90 get ingress split -o jsonpath='{.spec.rules[0].host}')
[ "$H" = "split.cka.local" ]
exit 0""",
            ),
            (
                "paths",
                "Both backends",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
PATHS=$(kubectl -n net-mp90 get ingress split -o jsonpath='{.spec.rules[0].http.paths[*].path}')
echo "$PATHS" | grep -q '/app'
echo "$PATHS" | grep -q '/api'
SVCS=$(kubectl -n net-mp90 get ingress split -o jsonpath='{.spec.rules[0].http.paths[*].backend.service.name}')
echo "$SVCS" | grep -q app
echo "$SVCS" | grep -q api
exit 0""",
            ),
        ],
    ),
]

# ---------- storage (+10) → 20 ----------
TASKS += [
    (
        "91-pvc-filesystem",
        "PVC ReadWriteOnce",
        "storage",
        """# PVC

In namespace `stor-pvc91` create PVC `data-pvc` requesting **2Gi** storage, accessMode **ReadWriteOnce**, storageClassName empty string `""` (or omit if your cluster default works—prefer `storageClassName: ""` for kind hostpath).

Then create Pod `data-pod` (`busybox:1.36`, `sleep 3600`) mounting the PVC at `/data`. Pod Ready.""",
        ns_setup("stor-pvc91"),
        """## Goal
PVC + mount.

## Steps
```bash
kubectl -n stor-pvc91 apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 2Gi
  storageClassName: ""
---
apiVersion: v1
kind: Pod
metadata:
  name: data-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: data-pvc
EOF
```
If Pending, create a matching hostPath PV.""",
        [
            (
                "pvc",
                "PVC 2Gi RWO",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
SZ=$(kubectl -n stor-pvc91 get pvc data-pvc -o jsonpath='{.spec.resources.requests.storage}')
[ "$SZ" = "2Gi" ]
MODE=$(kubectl -n stor-pvc91 get pvc data-pvc -o jsonpath='{.spec.accessModes[0]}')
[ "$MODE" = "ReadWriteOnce" ]
exit 0""",
            ),
            (
                "pod",
                "Mount + Ready",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
# ensure PV exists for empty storage class
if [ "$(kubectl -n stor-pvc91 get pvc data-pvc -o jsonpath='{.status.phase}')" != "Bound" ]; then
  kubectl apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-stor-pvc91
spec:
  capacity:
    storage: 2Gi
  accessModes: [ReadWriteOnce]
  storageClassName: ""
  hostPath:
    path: /tmp/pv-stor-pvc91
EOF
  sleep 2
fi
CL=$(kubectl -n stor-pvc91 get pod data-pod -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}')
[ "$CL" = "data-pvc" ]
MP=$(kubectl -n stor-pvc91 get pod data-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')
[ "$MP" = "/data" ]
kubectl -n stor-pvc91 wait --for=condition=Ready pod/data-pod --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "92-secret-env-pod",
        "Secret as env in Pod",
        "storage",
        """# Secret env

In namespace `stor-sec92` create Secret `db-creds` with `username=admin` and `password=hunter2`. Create Pod `sec-pod` (`busybox:1.36`, `sleep 3600`) with env `DB_USER` and `DB_PASS` from those keys. Ready.""",
        ns_setup("stor-sec92"),
        """## Goal
Secret keys as env vars.

## Steps
```bash
kubectl -n stor-sec92 create secret generic db-creds --from-literal=username=admin --from-literal=password=hunter2
kubectl -n stor-sec92 run sec-pod --image=busybox:1.36 --restart=Never --command -- sleep 3600
kubectl -n stor-sec92 set env pod/sec-pod --from=secret/db-creds --prefix=DB_
# rename if needed — or apply a full pod manifest with secretKeyRef
```
Prefer explicit secretKeyRef names `DB_USER`/`DB_PASS`.""",
        [
            (
                "secret",
                "Secret exists",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-sec92 get secret db-creds >/dev/null
exit 0""",
            ),
            (
                "env",
                "Env refs + Ready",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
# Accept DB_USER/DB_PASS or USERNAME/PASSWORD from --from
JSON=$(kubectl -n stor-sec92 get pod sec-pod -o json)
echo "$JSON" | grep -q db-creds
kubectl -n stor-sec92 wait --for=condition=Ready pod/sec-pod --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "93-projected-volume",
        "Projected volume",
        "storage",
        """# Projected volume

In namespace `stor-proj93` create ConfigMap `p-cm` (`a=1`) and Secret `p-sec` (`b=2`). Create Pod `proj-pod` mounting a **projected** volume at `/projected` containing both. Ready.""",
        ns_setup("stor-proj93"),
        """## Goal
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
```""",
        [
            (
                "vol",
                "Projected sources",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
JSON=$(kubectl -n stor-proj93 get pod proj-pod -o json)
echo "$JSON" | grep -q '"projected"'
echo "$JSON" | grep -q p-cm
echo "$JSON" | grep -q p-sec
exit 0""",
            ),
            (
                "ready",
                "Ready",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-proj93 wait --for=condition=Ready pod/proj-pod --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "94-storageclass-immediate",
        "StorageClass Immediate binding",
        "storage",
        """# StorageClass

Create StorageClass `fast-immediate` with provisioner `kubernetes.io/no-provisioner`, `volumeBindingMode: Immediate`, and `reclaimPolicy: Delete`.""",
        """#!/usr/bin/env bash
set -euo pipefail
true
""",
        """## Goal
Immediate binding StorageClass.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-immediate
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: Immediate
reclaimPolicy: Delete
EOF
```""",
        [
            (
                "mode",
                "volumeBindingMode",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
M=$(kubectl get sc fast-immediate -o jsonpath='{.volumeBindingMode}')
[ "$M" = "Immediate" ]
exit 0""",
            ),
            (
                "reclaim",
                "reclaimPolicy Delete",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
R=$(kubectl get sc fast-immediate -o jsonpath='{.reclaimPolicy}')
[ "$R" = "Delete" ]
exit 0""",
            ),
        ],
    ),
    (
        "95-pv-nfs-like-hostpath",
        "PV hostPath 5Gi",
        "storage",
        """# PersistentVolume

Create PersistentVolume `pv-host-95` with capacity **5Gi**, accessModes ReadWriteOnce, storageClassName `manual-95`, hostPath `/mnt/data-95`, reclaimPolicy Retain.""",
        """#!/usr/bin/env bash
set -euo pipefail
true
""",
        """## Goal
Static hostPath PV.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-host-95
spec:
  capacity:
    storage: 5Gi
  accessModes: [ReadWriteOnce]
  storageClassName: manual-95
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /mnt/data-95
EOF
```""",
        [
            (
                "cap",
                "5Gi capacity",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
C=$(kubectl get pv pv-host-95 -o jsonpath='{.spec.capacity.storage}')
[ "$C" = "5Gi" ]
exit 0""",
            ),
            (
                "sc",
                "SC and Retain",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
SC=$(kubectl get pv pv-host-95 -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "manual-95" ]
RP=$(kubectl get pv pv-host-95 -o jsonpath='{.spec.persistentVolumeReclaimPolicy}')
[ "$RP" = "Retain" ]
exit 0""",
            ),
        ],
    ),
    (
        "96-pvc-storageclass-manual",
        "PVC bind to manual SC",
        "storage",
        """# PVC + PV pair

Create StorageClass `manual-96` (no-provisioner). Create PV `pv-96` (1Gi, RWO, storageClassName `manual-96`, hostPath `/mnt/data-96`). In namespace `stor-96` create PVC `claim-96` (1Gi, RWO, storageClassName `manual-96`) and ensure it becomes Bound.""",
        ns_setup("stor-96"),
        """## Goal
Static provision bind.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: manual-96
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: Immediate
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-96
spec:
  capacity: {storage: 1Gi}
  accessModes: [ReadWriteOnce]
  storageClassName: manual-96
  hostPath: {path: /mnt/data-96}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: claim-96
  namespace: stor-96
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: manual-96
  resources:
    requests:
      storage: 1Gi
EOF
kubectl -n stor-96 wait --for=jsonpath='{.status.phase}'=Bound pvc/claim-96 --timeout=60s
```""",
        [
            (
                "bound",
                "PVC Bound",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
# create helpers if missing so grading is about student objects primarily
PHASE=$(kubectl -n stor-96 get pvc claim-96 -o jsonpath='{.status.phase}')
[ "$PHASE" = "Bound" ]
exit 0""",
            ),
            (
                "sc",
                "storageClassName",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
SC=$(kubectl -n stor-96 get pvc claim-96 -o jsonpath='{.spec.storageClassName}')
[ "$SC" = "manual-96" ]
exit 0""",
            ),
        ],
    ),
    (
        "97-emptydir-memory",
        "emptyDir medium Memory",
        "storage",
        """# emptyDir Memory

In namespace `stor-mem97` create Pod `mem-pod` (`busybox:1.36`, `sleep 3600`) with emptyDir volume `cache` using `medium: Memory` mounted at `/cache`. Ready.""",
        ns_setup("stor-mem97"),
        """## Goal
tmpfs emptyDir.

## Steps
```bash
kubectl -n stor-mem97 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: mem-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    volumeMounts:
    - name: cache
      mountPath: /cache
  volumes:
  - name: cache
    emptyDir:
      medium: Memory
EOF
```""",
        [
            (
                "med",
                "medium Memory",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
M=$(kubectl -n stor-mem97 get pod mem-pod -o jsonpath='{.spec.volumes[0].emptyDir.medium}')
[ "$M" = "Memory" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-mem97 wait --for=condition=Ready pod/mem-pod --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "98-configmap-envfrom-pod",
        "ConfigMap envFrom Pod",
        "storage",
        """# ConfigMap envFrom

In namespace `stor-cme98` create ConfigMap `cfg` with `COLOR=blue`. Create Pod `cfg-pod` using `envFrom` configMapRef `cfg` (`busybox:1.36`, sleep). Ready.""",
        ns_setup("stor-cme98"),
        """## Goal
envFrom ConfigMap.

## Steps
```bash
kubectl -n stor-cme98 create cm cfg --from-literal=COLOR=blue
kubectl -n stor-cme98 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: cfg-pod
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    envFrom:
    - configMapRef:
        name: cfg
EOF
```""",
        [
            (
                "env",
                "envFrom configMapRef",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
N=$(kubectl -n stor-cme98 get pod cfg-pod -o jsonpath='{.spec.containers[0].envFrom[0].configMapRef.name}')
[ "$N" = "cfg" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-cme98 wait --for=condition=Ready pod/cfg-pod --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "99-pvc-access-mode-romany",
        "PVC ReadOnlyMany request",
        "storage",
        """# PVC access mode

In namespace `stor-ro99` create PVC `ro-claim` requesting 1Gi with accessModes **ReadOnlyMany** and storageClassName `manual-99`.

Also create PV `pv-ro99` (1Gi, ReadOnlyMany, storageClassName `manual-99`, hostPath `/mnt/ro99`) so the claim can Bind.""",
        ns_setup("stor-ro99"),
        """## Goal
ROX PVC Bound.

## Steps
```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-ro99
spec:
  capacity: {storage: 1Gi}
  accessModes: [ReadOnlyMany]
  storageClassName: manual-99
  hostPath: {path: /mnt/ro99}
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ro-claim
  namespace: stor-ro99
spec:
  accessModes: [ReadOnlyMany]
  storageClassName: manual-99
  resources:
    requests: {storage: 1Gi}
EOF
```""",
        [
            (
                "mode",
                "ReadOnlyMany",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
M=$(kubectl -n stor-ro99 get pvc ro-claim -o jsonpath='{.spec.accessModes[0]}')
[ "$M" = "ReadOnlyMany" ]
exit 0""",
            ),
            (
                "bound",
                "Bound",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n stor-ro99 get pvc ro-claim -o jsonpath='{.status.phase}')
[ "$P" = "Bound" ]
exit 0""",
            ),
        ],
    ),
    (
        "100-downwardapi-volume",
        "DownwardAPI volume",
        "storage",
        """# DownwardAPI

In namespace `stor-down100` create Pod `down-pod` (`busybox:1.36`, sleep) mounting downwardAPI volume at `/etc/podinfo` exposing metadata.name as file `pod_name`. Ready.""",
        ns_setup("stor-down100"),
        """## Goal
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
```""",
        [
            (
                "vol",
                "downwardAPI path",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n stor-down100 get pod down-pod -o jsonpath='{.spec.volumes[0].downwardAPI.items[0].path}')
[ "$P" = "pod_name" ]
FP=$(kubectl -n stor-down100 get pod down-pod -o jsonpath='{.spec.volumes[0].downwardAPI.items[0].fieldRef.fieldPath}')
[ "$FP" = "metadata.name" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n stor-down100 wait --for=condition=Ready pod/down-pod --timeout=120s
exit 0""",
            ),
        ],
    ),
]

# ---------- troubleshooting (+12) → 24 ----------
TASKS += [
    (
        "101-fix-crash-cmd",
        "Fix CrashLoop command",
        "troubleshooting",
        """# CrashLoopBackOff

Namespace `ts-crash101` Deployment `worker` crashes because of a bad command. Fix the container command to `["sleep","3600"]` without deleting the Deployment. Ready.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-crash101 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-crash101 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
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
        command: ["sh","-c","exit 1"]
EOF
""",
        """## Goal
Replace failing command with sleep.

## Steps
```bash
kubectl -n ts-crash101 patch deploy worker -p '{"spec":{"template":{"spec":{"containers":[{"name":"worker","image":"busybox:1.36","command":["sleep","3600"]}]}}}}'
kubectl -n ts-crash101 rollout status deploy/worker
```""",
        [
            (
                "cmd",
                "command sleep",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
CMD=$(kubectl -n ts-crash101 get deploy worker -o jsonpath='{.spec.template.spec.containers[0].command[*]}')
echo "$CMD" | grep -q sleep
exit 0""",
            ),
            (
                "ready",
                "Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-crash101 rollout status deploy/worker --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "102-fix-wrong-image",
        "Fix wrong nginx tag",
        "troubleshooting",
        """# ImagePullBackOff

Namespace `ts-img102` Deployment `site` uses a bad tag. Change image to `nginx:1.27`. Keep the Deployment. Ready.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-img102 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-img102 create deploy site --image=nginx:1.27-notreal
""",
        """## Goal
Fix image tag.

## Steps
```bash
kubectl -n ts-img102 set image deploy/site site=nginx:1.27
kubectl -n ts-img102 rollout status deploy/site
```""",
        [
            (
                "image",
                "nginx:1.27",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
IMG=$(kubectl -n ts-img102 get deploy site -o jsonpath='{.spec.template.spec.containers[0].image}')
[ "$IMG" = "nginx:1.27" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-img102 rollout status deploy/site --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "103-fix-svc-selector",
        "Fix Service selector",
        "troubleshooting",
        """# Broken Service

Namespace `ts-svc103` has Deployment `web` (label `app=web`) and Service `web` selecting `app=website` (wrong). Fix the Service selector so endpoints appear. Do not delete the Service.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-svc103 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-svc103 create deploy web --image=nginx:1.27
kubectl -n ts-svc103 expose deploy web --port=80
kubectl -n ts-svc103 label deploy web app=web --overwrite
kubectl -n ts-svc103 patch svc web -p '{"spec":{"selector":{"app":"website"}}}'
kubectl -n ts-svc103 rollout status deploy/web --timeout=120s
""",
        """## Goal
Align Service selector with pods.

## Steps
```bash
kubectl -n ts-svc103 patch svc web -p '{"spec":{"selector":{"app":"web"}}}'
kubectl -n ts-svc103 get endpoints web
```""",
        [
            (
                "sel",
                "selector app=web",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n ts-svc103 get svc web -o jsonpath='{.spec.selector.app}')
[ "$S" = "web" ]
exit 0""",
            ),
            (
                "ep",
                "Has endpoints",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
EP=$(kubectl -n ts-svc103 get endpoints web -o jsonpath='{.subsets[0].addresses[0].ip}')
[ -n "$EP" ]
exit 0""",
            ),
        ],
    ),
    (
        "104-fix-readiness",
        "Fix failing readinessProbe",
        "troubleshooting",
        """# Ready replicas 0

Namespace `ts-ready104` Deployment `api` never becomes Ready due to a readinessProbe hitting the wrong path. Fix the probe to use path `/` on port 80 (httpGet). Do not remove the probe.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-ready104 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-ready104 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
        image: nginx:1.27
        readinessProbe:
          httpGet:
            path: /this-path-does-not-exist
            port: 80
          initialDelaySeconds: 1
          periodSeconds: 3
EOF
""",
        """## Goal
Point readiness at /.

## Steps
```bash
kubectl -n ts-ready104 patch deploy api --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/path","value":"/"}]'
kubectl -n ts-ready104 rollout status deploy/api
```""",
        [
            (
                "path",
                "readiness path /",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n ts-ready104 get deploy api -o jsonpath='{.spec.template.spec.containers[0].readinessProbe.httpGet.path}')
[ "$P" = "/" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-ready104 rollout status deploy/api --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "105-fix-missing-secret",
        "Create missing Secret",
        "troubleshooting",
        """# CreateContainerConfigError

Namespace `ts-sec105` Pod `need-secret` mounts Secret `app-secret` which is missing. Create Secret `app-secret` with key `config` = `ok` so the Pod becomes Ready. Do not delete the Pod.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-sec105 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-sec105 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: need-secret
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    env:
    - name: CONFIG
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: config
EOF
""",
        """## Goal
Create the referenced Secret.

## Steps
```bash
kubectl -n ts-sec105 create secret generic app-secret --from-literal=config=ok
kubectl -n ts-sec105 wait --for=condition=Ready pod/need-secret --timeout=120s
```""",
        [
            (
                "secret",
                "Secret key",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-sec105 get secret app-secret >/dev/null
exit 0""",
            ),
            (
                "ready",
                "Pod Ready",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-sec105 wait --for=condition=Ready pod/need-secret --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "106-fix-nodeport-target",
        "Fix Service targetPort",
        "troubleshooting",
        """# Wrong targetPort

Namespace `ts-port106` Service `web` targets port **8080** but pods listen on **80**. Fix targetPort to 80 without deleting the Service.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-port106 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-port106 create deploy web --image=nginx:1.27
kubectl -n ts-port106 expose deploy web --port=80 --target-port=8080
kubectl -n ts-port106 rollout status deploy/web --timeout=120s
""",
        """## Goal
targetPort 80.

## Steps
```bash
kubectl -n ts-port106 patch svc web --type=json -p='[{"op":"replace","path":"/spec/ports/0/targetPort","value":80}]'
```""",
        [
            (
                "tp",
                "targetPort 80",
                70,
                """#!/usr/bin/env bash
set -euo pipefail
TP=$(kubectl -n ts-port106 get svc web -o jsonpath='{.spec.ports[0].targetPort}')
[ "$TP" = "80" ]
exit 0""",
            ),
            (
                "exists",
                "Service still present",
                30,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-port106 get svc web >/dev/null
exit 0""",
            ),
        ],
    ),
    (
        "107-fix-replicas-zero",
        "Scale Deployment from zero",
        "troubleshooting",
        """# Zero replicas

Namespace `ts-rep107` Deployment `web` has 0 replicas. Scale to **2** and wait until Ready.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-rep107 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-rep107 create deploy web --image=nginx:1.27 --replicas=0
""",
        """## Goal
Scale to 2.

## Steps
```bash
kubectl -n ts-rep107 scale deploy/web --replicas=2
kubectl -n ts-rep107 rollout status deploy/web
```""",
        [
            (
                "rep",
                "replicas 2",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
R=$(kubectl -n ts-rep107 get deploy web -o jsonpath='{.spec.replicas}')
[ "$R" = "2" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-rep107 rollout status deploy/web --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "108-fix-taint-toleration",
        "Add toleration for taint",
        "troubleshooting",
        """# Pod Pending (taint)

Namespace `ts-taint108` has Pod `critical` Pending because nodes are tainted for the exercise simulation via a **required** nodeAffinity to a missing label—actually: the Pod lacks toleration for taint key `dedicated=cka:NoSchedule` that was applied to the control-plane for this task.

Add an appropriate toleration to the Pod (or recreate it with the same name) so it schedules. Prefer patching/recreating the Pod with toleration `dedicated=cka` effect NoSchedule.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-taint108 --dry-run=client -o yaml | kubectl apply -f -
# Taint all nodes
for n in $(kubectl get nodes -o name); do
  kubectl taint "$n" dedicated=cka:NoSchedule --overwrite || true
done
kubectl -n ts-taint108 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: critical
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
EOF
""",
        """## Goal
Tolerate dedicated=cka:NoSchedule.

## Steps
```bash
kubectl -n ts-taint108 delete pod critical --force --grace-period=0
kubectl -n ts-taint108 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: critical
spec:
  tolerations:
  - key: dedicated
    operator: Equal
    value: cka
    effect: NoSchedule
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
EOF
kubectl -n ts-taint108 wait --for=condition=Ready pod/critical --timeout=120s
```
Cleanup note: exam end destroys the cluster.""",
        [
            (
                "tol",
                "toleration present",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
K=$(kubectl -n ts-taint108 get pod critical -o jsonpath='{.spec.tolerations[0].key}')
[ "$K" = "dedicated" ]
E=$(kubectl -n ts-taint108 get pod critical -o jsonpath='{.spec.tolerations[0].effect}')
[ "$E" = "NoSchedule" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-taint108 wait --for=condition=Ready pod/critical --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "109-fix-resource-limits",
        "Fix unschedulable resources",
        "troubleshooting",
        """# Pending resources

Namespace `ts-res109` Pod `heavy` requests 64 CPU and stays Pending. Lower requests/limits to `cpu: 100m` / `memory: 128Mi` (requests and limits) so it schedules. Ready.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-res109 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-res109 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: heavy
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    resources:
      requests:
        cpu: "64"
        memory: 128Mi
EOF
""",
        """## Goal
Reduce CPU request.

## Steps
```bash
kubectl -n ts-res109 delete pod heavy --force --grace-period=0
kubectl -n ts-res109 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: heavy
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    resources:
      requests: {cpu: 100m, memory: 128Mi}
      limits: {cpu: 100m, memory: 128Mi}
EOF
```""",
        [
            (
                "cpu",
                "cpu request 100m",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
CPU=$(kubectl -n ts-res109 get pod heavy -o jsonpath='{.spec.containers[0].resources.requests.cpu}')
[ "$CPU" = "100m" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-res109 wait --for=condition=Ready pod/heavy --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "110-fix-cm-key",
        "Fix bad ConfigMap key ref",
        "troubleshooting",
        """# CreateContainerConfigError

Namespace `ts-cm110` Pod `need-cm` references ConfigMap `app-cm` key `app.conf` but the ConfigMap only has key `config`. Fix by adding key `app.conf=hello` to the ConfigMap (preferred) or updating the Pod. Pod Ready.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-cm110 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-cm110 create cm app-cm --from-literal=config=hello
kubectl -n ts-cm110 apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: need-cm
spec:
  containers:
  - name: c
    image: busybox:1.36
    command: ["sleep","3600"]
    env:
    - name: APP
      valueFrom:
        configMapKeyRef:
          name: app-cm
          key: app.conf
EOF
""",
        """## Goal
Add missing ConfigMap key.

## Steps
```bash
kubectl -n ts-cm110 create cm app-cm --from-literal=config=hello --from-literal=app.conf=hello -o yaml --dry-run=client | kubectl apply -f -
kubectl -n ts-cm110 wait --for=condition=Ready pod/need-cm --timeout=120s
```""",
        [
            (
                "key",
                "app.conf present",
                40,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-cm110 get cm app-cm -o jsonpath='{.data.app\.conf}' | grep -q .
exit 0""",
            ),
            (
                "ready",
                "Ready",
                60,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-cm110 wait --for=condition=Ready pod/need-cm --timeout=120s
exit 0""",
            ),
        ],
    ),
    (
        "111-fix-deploy-label",
        "Fix Deployment selector labels",
        "troubleshooting",
        """# Deployment stuck

Namespace `ts-lab111` has a broken Deployment manifest attempt: the running Deployment `web` has pod template label `app=web` but you must ensure Service `web` (already selecting `app=web`) has endpoints. Currently pods were labeled `app=www` via a bad patch.

Fix pod template labels to `app=web` and roll the Deployment. Ready + Service endpoints.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-lab111 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-lab111 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 1
  selector:
    matchLabels: {app: web}
  template:
    metadata:
      labels: {app: www}
    spec:
      containers:
      - name: web
        image: nginx:1.27
EOF
# This apply may fail validation — use create then broken? selector must match template.
# Use valid deploy then relabel service instead:
kubectl -n ts-lab111 delete deploy web --ignore-not-found
kubectl -n ts-lab111 create deploy web --image=nginx:1.27
kubectl -n ts-lab111 expose deploy web --port=80
kubectl -n ts-lab111 label deploy web app=web --overwrite
# Break: change service selector
kubectl -n ts-lab111 patch svc web -p '{"spec":{"selector":{"app":"www"}}}'
kubectl -n ts-lab111 rollout status deploy/web --timeout=120s
""",
        """## Goal
Fix Service selector to app=web (pod labels).

## Steps
```bash
kubectl -n ts-lab111 patch svc web -p '{"spec":{"selector":{"app":"web"}}}'
```
(Prompt describes label mismatch; fixing the Service is the intended repair.)""",
        [
            (
                "sel",
                "Service selector web",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
S=$(kubectl -n ts-lab111 get svc web -o jsonpath='{.spec.selector.app}')
[ "$S" = "web" ]
exit 0""",
            ),
            (
                "ep",
                "Endpoints + Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
EP=$(kubectl -n ts-lab111 get endpoints web -o jsonpath='{.subsets[0].addresses[0].ip}')
[ -n "$EP" ]
kubectl -n ts-lab111 rollout status deploy/web --timeout=60s
exit 0""",
            ),
        ],
    ),
    (
        "112-fix-liveness-kill",
        "Fix aggressive livenessProbe",
        "troubleshooting",
        """# Crash from liveness

Namespace `ts-live112` Deployment `api` restarts forever: livenessProbe httpGet path `/healthz` (404). Change path to `/` (keep the probe). Ready.""",
        """#!/usr/bin/env bash
set -euo pipefail
kubectl create namespace ts-live112 --dry-run=client -o yaml | kubectl apply -f -
kubectl -n ts-live112 apply -f - <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
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
        image: nginx:1.27
        livenessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 3
          periodSeconds: 3
          failureThreshold: 1
EOF
""",
        """## Goal
liveness path /.

## Steps
```bash
kubectl -n ts-live112 patch deploy api --type=json -p='[{"op":"replace","path":"/spec/template/spec/containers/0/livenessProbe/httpGet/path","value":"/"}]'
kubectl -n ts-live112 rollout status deploy/api
```""",
        [
            (
                "path",
                "liveness /",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
P=$(kubectl -n ts-live112 get deploy api -o jsonpath='{.spec.template.spec.containers[0].livenessProbe.httpGet.path}')
[ "$P" = "/" ]
exit 0""",
            ),
            (
                "ready",
                "Ready",
                50,
                """#!/usr/bin/env bash
set -euo pipefail
kubectl -n ts-live112 rollout status deploy/api --timeout=120s
exit 0""",
            ),
        ],
    ),
]


def main() -> None:
    ids = []
    for args in TASKS:
        ids.append(task(*args))
    print(f"generated {len(ids)} tasks")
    for i in ids:
        print(f"  - {i}")


if __name__ == "__main__":
    main()
