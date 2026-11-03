#!/usr/bin/env python3
"""Generate assessment.yaml, checks/*.sh, and answers.md for all tasks."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "tasks"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    if path.suffix == ".sh":
        path.chmod(path.stat().st_mode | 0o111)


def emit(task_id: str, checks: list[tuple[str, str, int, str]], answers: str) -> None:
    d = ROOT / task_id
    lines = ["checks:"]
    for cid, desc, weight, _script in checks:
        lines.append(f"  - id: {cid}")
        lines.append(f"    description: {desc}")
        lines.append(f"    weight: {weight}")
        lines.append(f"    script: checks/{cid}.sh")
    write(d / "assessment.yaml", "\n".join(lines))
    for cid, _desc, _w, script in checks:
        write(d / "checks" / f"{cid}.sh", "#!/usr/bin/env bash\nset -euo pipefail\n" + script)
    write(d / "answers.md", answers.strip() + "\n")
    print(f"migrated {task_id} ({len(checks)} checks)")


# --- definitions ---

emit(
    "01-rbac",
    [
        ("sa", "ServiceAccount exists", 30, 'kubectl -n rbac-lab get sa deployer >/dev/null\n'),
        ("role", "Role has pods/deployments verbs", 40, '''
NS=rbac-lab
kubectl -n "$NS" get role deployer-role >/dev/null
ROLE_JSON=$(kubectl -n "$NS" get role deployer-role -o json)
echo "$ROLE_JSON" | grep -q '"pods"'
echo "$ROLE_JSON" | grep -q '"deployments"'
for v in get list watch create update delete; do echo "$ROLE_JSON" | grep -q "\\"$v\\""; done
'''),
        ("binding", "RoleBinding links SA to Role", 30, '''
NS=rbac-lab
kubectl -n "$NS" get rolebinding deployer-binding >/dev/null
RB_JSON=$(kubectl -n "$NS" get rolebinding deployer-binding -o json)
echo "$RB_JSON" | grep -q '"deployer-role"'
echo "$RB_JSON" | grep -q '"deployer"'
echo "$RB_JSON" | grep -q '"ServiceAccount"'
'''),
    ],
    """## Solution
```bash
kubectl -n rbac-lab create sa deployer
kubectl -n rbac-lab create role deployer-role --verb=get,list,watch,create,update,delete --resource=pods,deployments.apps
kubectl -n rbac-lab create rolebinding deployer-binding --role=deployer-role --serviceaccount=rbac-lab:deployer
```""",
)

emit(
    "02-etcd-backup",
    [
        ("exists", "Snapshot file exists and is large enough", 60, '''
CP="${CLUSTER_NAME}-control-plane"
SIZE=$(docker exec "$CP" sh -c 'if [ -f /opt/cka/etcd-snapshot.db ]; then wc -c < /opt/cka/etcd-snapshot.db; else echo 0; fi' | tr -d ' ')
[ "${SIZE:-0}" -ge 1000 ]
'''),
        ("valid", "Snapshot status check if etcdctl present", 40, '''
CP="${CLUSTER_NAME}-control-plane"
docker exec "$CP" sh -c '
  if command -v etcdctl >/dev/null 2>&1; then
    ETCDCTL_API=3 etcdctl --write-out=table snapshot status /opt/cka/etcd-snapshot.db >/dev/null
  elif [ -f /opt/cka/etcd-snapshot.db ]; then
    test $(wc -c < /opt/cka/etcd-snapshot.db) -ge 1000
  else
    exit 1
  fi
'
'''),
    ],
    """## Solution
```bash
CP=${CLUSTER_NAME}-control-plane
docker exec -it $CP bash
# inside node:
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \\
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \\
  --cert=/etc/kubernetes/pki/etcd/server.crt \\
  --key=/etc/kubernetes/pki/etcd/server.key \\
  snapshot save /opt/cka/etcd-snapshot.db
```""",
)

emit(
    "03-deployment-config",
    [
        ("cm-secret", "ConfigMap and Secret correct", 30, '''
NS=workloads-lab
kubectl -n "$NS" get cm app-config -o jsonpath='{.data.APP_ENV}' | grep -qx production
TOKEN=$(kubectl -n "$NS" get secret app-secret -o jsonpath='{.data.APP_TOKEN}' | base64 -d)
[ "$TOKEN" = "s3cr3t" ]
'''),
        ("deploy-spec", "Deployment replicas/image/env/resources", 40, '''
NS=workloads-lab
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.replicas}')" = "3" ]
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ]
kubectl -n "$NS" get deploy web -o yaml | grep -q 'configMapKeyRef'
kubectl -n "$NS" get deploy web -o yaml | grep -q 'secretKeyRef'
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')" = "100m" ]
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}')" = "64Mi" ]
'''),
        ("ready", "Deployment Ready with 3 replicas", 30, '''
NS=workloads-lab
kubectl -n "$NS" rollout status deploy/web --timeout=120s
[ "$(kubectl -n "$NS" get deploy web -o jsonpath='{.status.readyReplicas}')" = "3" ]
'''),
    ],
    """## Solution
Create ConfigMap `app-config`, Secret `app-secret`, then Deployment `web` with 3 replicas of `nginx:1.27`, envFrom cm/secret keyRefs, and cpu/memory requests.""",
)

emit(
    "04-service-ingress",
    [
        ("service", "ClusterIP Service correct", 50, '''
NS=net-lab
TYPE=$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.type}')
[ "$TYPE" = "ClusterIP" ] || [ -z "$TYPE" ]
[ "$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.ports[0].port}')" = "80" ]
[ "$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.ports[0].targetPort}')" = "8080" ]
[ "$(kubectl -n "$NS" get svc hello-svc -o jsonpath='{.spec.selector.app}')" = "hello" ]
'''),
        ("ingress", "Ingress host/class/backend", 50, '''
NS=net-lab
[ "$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.rules[0].host}')" = "hello.cka.local" ]
[ "$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.rules[0].http.paths[0].backend.service.name}')" = "hello-svc" ]
[ "$(kubectl -n "$NS" get ingress hello-ing -o jsonpath='{.spec.ingressClassName}')" = "nginx" ]
'''),
    ],
    """## Solution
```bash
kubectl -n net-lab expose deploy hello --name=hello-svc --port=80 --target-port=8080
# create Ingress hello-ing with host hello.cka.local, class nginx, backend hello-svc:80
```""",
)

emit(
    "05-network-policy",
    [
        ("select", "Selects secure-db and Ingress type", 40, '''
NS=policy-lab
[ "$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.podSelector.matchLabels.app}')" = "secure-db" ]
echo "$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.policyTypes[*]}')" | grep -q Ingress
'''),
        ("rule", "Allows frontend on TCP 5432", 60, '''
NS=policy-lab
[ "$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.ingress[0].from[0].podSelector.matchLabels.role}')" = "frontend" ]
[ "$(kubectl -n "$NS" get networkpolicy db-allow-frontend -o jsonpath='{.spec.ingress[0].ports[0].port}')" = "5432" ]
'''),
    ],
    """## Solution
Create NetworkPolicy `db-allow-frontend` selecting `app=secure-db`, policyTypes Ingress, from `role=frontend`, port 5432/TCP.""",
)

emit(
    "06-persistent-volume",
    [
        ("pvc", "PVC size/mode/class", 40, '''
NS=storage-lab
[ "$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.resources.requests.storage}')" = "1Gi" ]
[ "$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.accessModes[0]}')" = "ReadWriteOnce" ]
[ "$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.spec.storageClassName}')" = "standard" ]
'''),
        ("pod", "Pod mounts PVC and Ready/Bound", 60, '''
NS=storage-lab
kubectl -n "$NS" wait --for=condition=Ready pod/data-pod --timeout=120s
[ "$(kubectl -n "$NS" get pvc data-pvc -o jsonpath='{.status.phase}')" = "Bound" ]
echo "$(kubectl -n "$NS" get pod data-pod -o jsonpath='{.spec.containers[0].volumeMounts[0].mountPath}')" | grep -q '/data'
[ "$(kubectl -n "$NS" get pod data-pod -o jsonpath='{.spec.volumes[0].persistentVolumeClaim.claimName}')" = "data-pvc" ]
'''),
    ],
    """## Solution
Create PVC `data-pvc` (1Gi, RWO, standard) and Pod `data-pod` mounting it at `/data`.""",
)

emit(
    "07-fix-workload",
    [
        ("image", "Image fixed to nginx:1.27", 40, '''
[ "$(kubectl -n broken-app get deploy frontend -o jsonpath='{.spec.template.spec.containers[0].image}')" = "nginx:1.27" ]
'''),
        ("ready", "2 Ready replicas", 60, '''
kubectl -n broken-app rollout status deploy/frontend --timeout=120s
[ "$(kubectl -n broken-app get deploy frontend -o jsonpath='{.status.readyReplicas}')" = "2" ]
'''),
    ],
    """## Solution
```bash
kubectl -n broken-app set image deploy/frontend frontend=nginx:1.27
kubectl -n broken-app rollout status deploy/frontend
```""",
)

emit(
    "08-fix-cluster",
    [
        ("corefile", "Corefile restored (has forward, no notaplugin)", 50, '''
COREFILE=$(kubectl -n kube-system get configmap coredns -o jsonpath='{.data.Corefile}')
echo "$COREFILE" | grep -q forward
echo "$COREFILE" | grep -qv notaplugin
'''),
        ("ready", "coredns Deployment Ready", 50, '''
kubectl -n kube-system rollout status deploy/coredns --timeout=180s
DESIRED=$(kubectl -n kube-system get deploy coredns -o jsonpath='{.spec.replicas}')
READY=$(kubectl -n kube-system get deploy coredns -o jsonpath='{.status.readyReplicas}')
[ "$READY" = "$DESIRED" ]
'''),
    ],
    """## Solution
Copy Corefile from ConfigMap `coredns-backup` back to `coredns`, then `kubectl -n kube-system rollout restart deploy/coredns`.""",
)

# Generated tasks 09-32 — compact helpers
RBAC_ANSWERS = "Create the requested ServiceAccount, Role/ClusterRole, and Binding with the specified verbs/resources."

emit("09-clusterrole-binding", [
    ("cr", "ClusterRole node-viewer", 40, 'kubectl get clusterrole node-viewer -o jsonpath="{.rules[0].resources[*]}" | grep -q nodes\nkubectl get clusterrole node-viewer -o jsonpath="{.rules[0].verbs[*]}" | grep -q get\n'),
    ("sa", "SA in arch-crb", 20, 'kubectl -n arch-crb get sa node-inspector >/dev/null\n'),
    ("crb", "ClusterRoleBinding", 40, '[ "$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath="{.roleRef.name}")" = "node-viewer" ]\n[ "$(kubectl get clusterrolebinding node-viewer-binding -o jsonpath="{.subjects[0].name}")" = "node-inspector" ]\n'),
], "## Solution\nCreate ClusterRole `node-viewer`, SA `node-inspector` in `arch-crb`, and ClusterRoleBinding `node-viewer-binding`.")

emit("10-rbac-secrets-reader", [
    ("sa", "SA exists", 25, 'kubectl -n arch-secrets get sa secret-reader >/dev/null\n'),
    ("role", "Role on secrets", 40, 'kubectl -n arch-secrets get role secret-reader-role -o jsonpath="{.rules[0].resources[*]}" | grep -q secrets\nfor v in get list watch; do kubectl -n arch-secrets get role secret-reader-role -o jsonpath="{.rules[0].verbs[*]}" | grep -q "$v"; done\n'),
    ("rb", "RoleBinding", 35, 'kubectl -n arch-secrets get rolebinding secret-reader-binding >/dev/null\n'),
], f"## Solution\n{RBAC_ANSWERS}")

emit("11-role-services", [
    ("sa", "SA", 25, 'kubectl -n arch-svc-rbac get sa svc-manager >/dev/null\n'),
    ("role", "Role services verbs", 45, 'kubectl -n arch-svc-rbac get role svc-manager-role -o jsonpath="{.rules[0].resources[*]}" | grep -q services\nfor v in get list create delete; do kubectl -n arch-svc-rbac get role svc-manager-role -o jsonpath="{.rules[0].verbs[*]}" | grep -q "$v"; done\n'),
    ("rb", "RoleBinding", 30, 'kubectl -n arch-svc-rbac get rolebinding svc-manager-binding >/dev/null\n'),
], f"## Solution\n{RBAC_ANSWERS}")

emit("12-clusterrole-ns-get", [
    ("cr", "ClusterRole namespaces", 50, 'kubectl get clusterrole ns-lister -o jsonpath="{.rules[0].resources[*]}" | grep -q namespaces\nkubectl get clusterrole ns-lister -o jsonpath="{.rules[0].verbs[*]}" | grep -q get\n'),
    ("bind", "SA + CRB", 50, 'kubectl -n arch-ns get sa ns-auditor >/dev/null\nkubectl get clusterrolebinding ns-lister-binding -o jsonpath="{.roleRef.name}" | grep -qx ns-lister\n'),
], f"## Solution\n{RBAC_ANSWERS}")

emit("13-sa-deploy-binding", [
    ("sa", "ServiceAccount", 25, 'kubectl -n arch-sa-deploy get sa app-sa >/dev/null\n'),
    ("deploy", "Deployment uses SA + image", 45, '[ "$(kubectl -n arch-sa-deploy get deploy sa-demo -o jsonpath="{.spec.template.spec.serviceAccountName}")" = "app-sa" ]\n[ "$(kubectl -n arch-sa-deploy get deploy sa-demo -o jsonpath="{.spec.template.spec.containers[0].image}")" = "nginx:1.27" ]\n'),
    ("ready", "Ready", 30, 'kubectl -n arch-sa-deploy rollout status deploy/sa-demo --timeout=120s\n'),
], "## Solution\nCreate SA `app-sa` and Deployment `sa-demo` with `serviceAccountName: app-sa`.")

emit("14-rbac-jobs", [
    ("sa", "SA", 25, 'kubectl -n arch-jobs get sa job-runner >/dev/null\n'),
    ("role", "Role batch jobs", 45, 'kubectl -n arch-jobs get role job-runner-role -o json | grep -q \'"jobs"\'\nkubectl -n arch-jobs get role job-runner-role -o json | grep -q \'"batch"\'\n'),
    ("rb", "RoleBinding", 30, 'kubectl -n arch-jobs get rolebinding job-runner-binding >/dev/null\n'),
], f"## Solution\n{RBAC_ANSWERS}")

emit("15-cronjob", [
    ("sched", "Schedule + concurrency", 50, '[ "$(kubectl -n wl-cron get cronjob ping-cron -o jsonpath="{.spec.schedule}")" = "*/5 * * * *" ]\n[ "$(kubectl -n wl-cron get cronjob ping-cron -o jsonpath="{.spec.concurrencyPolicy}")" = "Forbid" ]\n'),
    ("image", "Container image", 50, '[ "$(kubectl -n wl-cron get cronjob ping-cron -o jsonpath="{.spec.jobTemplate.spec.template.spec.containers[0].image}")" = "busybox:1.36" ]\n'),
], "## Solution\n`kubectl -n wl-cron create cronjob ping-cron --image=busybox:1.36 --schedule='*/5 * * * *' -- echo cka-cron` then set concurrencyPolicy=Forbid.")

emit("16-scale-deployment", [
    ("replicas", "spec.replicas=4", 40, '[ "$(kubectl -n wl-scale get deploy api -o jsonpath="{.spec.replicas}")" = "4" ]\n'),
    ("ready", "4 Ready", 60, 'kubectl -n wl-scale rollout status deploy/api --timeout=120s\n[ "$(kubectl -n wl-scale get deploy api -o jsonpath="{.status.readyReplicas}")" = "4" ]\n'),
], "## Solution\n`kubectl -n wl-scale scale deploy/api --replicas=4`")

emit("17-probes-deployment", [
    ("spec", "Replicas + probes", 50, '[ "$(kubectl -n wl-probes get deploy probed -o jsonpath="{.spec.replicas}")" = "2" ]\n[ "$(kubectl -n wl-probes get deploy probed -o jsonpath="{.spec.template.spec.containers[0].readinessProbe.httpGet.path}")" = "/" ]\n[ "$(kubectl -n wl-probes get deploy probed -o jsonpath="{.spec.template.spec.containers[0].livenessProbe.httpGet.path}")" = "/" ]\n'),
    ("ready", "Ready", 50, 'kubectl -n wl-probes rollout status deploy/probed --timeout=120s\n'),
], "## Solution\nCreate Deployment `probed` with readiness/liveness HTTP GET `/` on port 80.")

emit("18-resource-limits", [
    ("resources", "Requests and limits", 60, '''
NS=wl-limits
[ "$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.requests.cpu}')" = "50m" ]
[ "$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.requests.memory}')" = "32Mi" ]
[ "$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.limits.cpu}')" = "200m" ]
[ "$(kubectl -n "$NS" get deploy limited -o jsonpath='{.spec.template.spec.containers[0].resources.limits.memory}')" = "128Mi" ]
'''),
    ("ready", "Ready", 40, 'kubectl -n wl-limits rollout status deploy/limited --timeout=120s\n'),
], "## Solution\nCreate Deployment `limited` with the specified requests/limits.")

emit("19-nodeport-service", [
    ("type", "NodePort type + ports", 60, '[ "$(kubectl -n net-nodeport get svc web-nodeport -o jsonpath="{.spec.type}")" = "NodePort" ]\n[ "$(kubectl -n net-nodeport get svc web-nodeport -o jsonpath="{.spec.ports[0].port}")" = "80" ]\n[ "$(kubectl -n net-nodeport get svc web-nodeport -o jsonpath="{.spec.ports[0].nodePort}")" = "30080" ]\n'),
    ("sel", "Selector", 40, '[ "$(kubectl -n net-nodeport get svc web-nodeport -o jsonpath="{.spec.selector.app}")" = "web" ]\n'),
], "## Solution\nCreate Service type NodePort with nodePort 30080 selecting app=web.")

emit("20-ingress-path", [
    ("host", "Host + path", 50, '[ "$(kubectl -n net-ingpath get ingress shop-ing -o jsonpath="{.spec.rules[0].host}")" = "shop.cka.local" ]\n[ "$(kubectl -n net-ingpath get ingress shop-ing -o jsonpath="{.spec.rules[0].http.paths[0].path}")" = "/shop" ]\n'),
    ("backend", "Backend + class", 50, '[ "$(kubectl -n net-ingpath get ingress shop-ing -o jsonpath="{.spec.rules[0].http.paths[0].backend.service.name}")" = "shop" ]\n[ "$(kubectl -n net-ingpath get ingress shop-ing -o jsonpath="{.spec.ingressClassName}")" = "nginx" ]\n'),
], "## Solution\nCreate Ingress `shop-ing` with path `/shop` to Service shop:80, class nginx.")

emit("21-networkpolicy-egress", [
    ("select", "Selects client + Egress", 40, '[ "$(kubectl -n net-egress get networkpolicy client-egress -o jsonpath="{.spec.podSelector.matchLabels.app}")" = "client" ]\necho "$(kubectl -n net-egress get networkpolicy client-egress -o jsonpath="{.spec.policyTypes[*]}")" | grep -q Egress\n'),
    ("to", "To api:8080", 60, '[ "$(kubectl -n net-egress get networkpolicy client-egress -o jsonpath="{.spec.egress[0].to[0].podSelector.matchLabels.app}")" = "api" ]\n[ "$(kubectl -n net-egress get networkpolicy client-egress -o jsonpath="{.spec.egress[0].ports[0].port}")" = "8080" ]\n'),
], "## Solution\nCreate egress NetworkPolicy from app=client to app=api port 8080.")

emit("22-clusterip-multi-port", [
    ("ports", "http+metrics ports", 70, '''
NS=net-multiport
N0=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[0].name}')
N1=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[1].name}')
echo "$N0$N1" | grep -q http
echo "$N0$N1" | grep -q metrics
PORTS=$(kubectl -n "$NS" get svc dual-svc -o jsonpath='{.spec.ports[*].port}')
echo "$PORTS" | grep -q 80
echo "$PORTS" | grep -q 8080
'''),
    ("type", "ClusterIP", 30, 'TYPE=$(kubectl -n net-multiport get svc dual-svc -o jsonpath="{.spec.type}"); [ "$TYPE" = "ClusterIP" ] || [ -z "$TYPE" ]\n'),
], "## Solution\nCreate dual-port ClusterIP Service `dual-svc` with named ports http/metrics.")

emit("23-service-labels", [
    ("sel", "Both selector labels", 70, '[ "$(kubectl -n net-svclabel get svc fe-svc -o jsonpath="{.spec.selector.tier}")" = "frontend" ]\n[ "$(kubectl -n net-svclabel get svc fe-svc -o jsonpath="{.spec.selector.env}")" = "prod" ]\n'),
    ("port", "Port 80", 30, '[ "$(kubectl -n net-svclabel get svc fe-svc -o jsonpath="{.spec.ports[0].port}")" = "80" ]\n'),
], "## Solution\nCreate Service selecting tier=frontend,env=prod on port 80.")

emit("24-pvc-busybox", [
    ("pvc", "PVC fields", 40, '[ "$(kubectl -n stor-busy get pvc busy-pvc -o jsonpath="{.spec.resources.requests.storage}")" = "500Mi" ]\n[ "$(kubectl -n stor-busy get pvc busy-pvc -o jsonpath="{.spec.storageClassName}")" = "standard" ]\n'),
    ("pod", "Pod Ready Bound", 60, 'kubectl -n stor-busy wait --for=condition=Ready pod/busy-pod --timeout=120s\n[ "$(kubectl -n stor-busy get pvc busy-pvc -o jsonpath="{.status.phase}")" = "Bound" ]\n[ "$(kubectl -n stor-busy get pod busy-pod -o jsonpath="{.spec.volumes[0].persistentVolumeClaim.claimName}")" = "busy-pvc" ]\n'),
], "## Solution\nPVC busy-pvc 500Mi + Pod busy-pod mount /mnt/data.")

emit("25-pvc-storageclass", [
    ("pvc", "2Gi standard", 40, '[ "$(kubectl -n stor-sc get pvc app-data -o jsonpath="{.spec.resources.requests.storage}")" = "2Gi" ]\n[ "$(kubectl -n stor-sc get pvc app-data -o jsonpath="{.spec.storageClassName}")" = "standard" ]\n'),
    ("pod", "Mount /var/app Bound", 60, 'kubectl -n stor-sc wait --for=condition=Ready pod/app-data-pod --timeout=120s\n[ "$(kubectl -n stor-sc get pvc app-data -o jsonpath="{.status.phase}")" = "Bound" ]\n[ "$(kubectl -n stor-sc get pod app-data-pod -o jsonpath="{.spec.containers[0].volumeMounts[0].mountPath}")" = "/var/app" ]\n'),
], "## Solution\nPVC app-data 2Gi + Pod mounting at /var/app.")

emit("26-pvc-mount-subpath", [
    ("subpath", "subPath cache at /work", 50, 'kubectl -n stor-sub wait --for=condition=Ready pod/sub-pod --timeout=120s\n[ "$(kubectl -n stor-sub get pod sub-pod -o jsonpath="{.spec.containers[0].volumeMounts[0].subPath}")" = "cache" ]\n[ "$(kubectl -n stor-sub get pod sub-pod -o jsonpath="{.spec.containers[0].volumeMounts[0].mountPath}")" = "/work" ]\n'),
    ("bound", "PVC Bound", 50, '[ "$(kubectl -n stor-sub get pvc sub-pvc -o jsonpath="{.status.phase}")" = "Bound" ]\n'),
], "## Solution\nPVC sub-pvc + Pod with volumeMount subPath: cache.")

emit("27-crashloop-fix", [
    ("image", "busybox image", 30, '[ "$(kubectl -n ts-crash get deploy looper -o jsonpath="{.spec.template.spec.containers[0].image}")" = "busybox:1.36" ]\n'),
    ("ready", "Ready", 70, 'kubectl -n ts-crash rollout status deploy/looper --timeout=120s\n[ "$(kubectl -n ts-crash get deploy looper -o jsonpath="{.status.readyReplicas}")" = "1" ]\n'),
], "## Solution\nFix container command to `sleep 3600` (edit deploy/looper).")

emit("28-wrong-selector", [
    ("sel", "Selector app=backend", 50, '[ "$(kubectl -n ts-selector get svc backend-svc -o jsonpath="{.spec.selector.app}")" = "backend" ]\n'),
    ("ep", "Has endpoints", 50, 'EP=$(kubectl -n ts-selector get endpoints backend-svc -o jsonpath="{.subsets[0].addresses[0].ip}"); [ -n "$EP" ]\n'),
], "## Solution\n`kubectl -n ts-selector patch svc backend-svc -p '{\"spec\":{\"selector\":{\"app\":\"backend\"}}}'`")

emit("29-pending-nodeselector", [
    ("image", "nginx image kept", 30, '[ "$(kubectl -n ts-pending get pod stuck -o jsonpath="{.spec.containers[0].image}")" = "nginx:1.27" ]\n'),
    ("ready", "Pod Ready", 70, 'kubectl -n ts-pending wait --for=condition=Ready pod/stuck --timeout=120s\n'),
], "## Solution\nRemove the impossible nodeSelector from Pod `stuck`.")

emit("30-failing-probe", [
    ("path", "Probe path /", 40, '[ "$(kubectl -n ts-probe get deploy web -o jsonpath="{.spec.template.spec.containers[0].readinessProbe.httpGet.path}")" = "/" ]\n'),
    ("ready", "2 Ready", 60, 'kubectl -n ts-probe rollout status deploy/web --timeout=120s\n[ "$(kubectl -n ts-probe get deploy web -o jsonpath="{.status.readyReplicas}")" = "2" ]\n'),
], "## Solution\nFix readinessProbe path to `/`.")

emit("31-missing-configmap", [
    ("cm", "ConfigMap mode=online", 40, 'kubectl -n ts-cm get cm app-settings >/dev/null\n[ "$(kubectl -n ts-cm get cm app-settings -o jsonpath="{.data.mode}")" = "online" ]\n'),
    ("ready", "Deploy Ready", 60, 'kubectl -n ts-cm rollout status deploy/cfg-app --timeout=120s\n[ "$(kubectl -n ts-cm get deploy cfg-app -o jsonpath="{.status.readyReplicas}")" = "1" ]\n'),
], "## Solution\n`kubectl -n ts-cm create configmap app-settings --from-literal=mode=online`")

emit("32-service-wrong-target", [
    ("target", "targetPort 8080", 60, '[ "$(kubectl -n ts-target get svc echo-svc -o jsonpath="{.spec.ports[0].targetPort}")" = "8080" ]\n'),
    ("port-sel", "port 80 + selector", 40, '[ "$(kubectl -n ts-target get svc echo-svc -o jsonpath="{.spec.ports[0].port}")" = "80" ]\n[ "$(kubectl -n ts-target get svc echo-svc -o jsonpath="{.spec.selector.app}")" = "echo" ]\n'),
], "## Solution\nPatch Service targetPort to 8080.")

print("DONE")
