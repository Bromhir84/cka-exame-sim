"""Name the specific mistake behind a failed grade check.

The check script already says what it expected. This module compares that with
the cluster: a mistyped name, the same object in another namespace, or a value
sitting on a neighboring field.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

_NOT_FOUND = re.compile(
    r'Error from server \(NotFound\): (\S+) "([^"]+)" not found'
)

# Short names and plurals kubectl prints in NotFound errors.
_ALIASES = {
    "sa": "serviceaccount",
    "serviceaccount": "serviceaccount",
    "serviceaccounts": "serviceaccount",
    "secret": "secret",
    "secrets": "secret",
    "cm": "configmap",
    "configmap": "configmap",
    "configmaps": "configmap",
    "deploy": "deployment",
    "deployment": "deployment",
    "deployments": "deployment",
    "ds": "daemonset",
    "daemonset": "daemonset",
    "daemonsets": "daemonset",
    "sts": "statefulset",
    "statefulset": "statefulset",
    "statefulsets": "statefulset",
    "rs": "replicaset",
    "replicaset": "replicaset",
    "replicasets": "replicaset",
    "svc": "service",
    "service": "service",
    "services": "service",
    "po": "pod",
    "pod": "pod",
    "pods": "pod",
    "ns": "namespace",
    "namespace": "namespace",
    "namespaces": "namespace",
    "pv": "persistentvolume",
    "persistentvolume": "persistentvolume",
    "persistentvolumes": "persistentvolume",
    "pvc": "persistentvolumeclaim",
    "persistentvolumeclaim": "persistentvolumeclaim",
    "persistentvolumeclaims": "persistentvolumeclaim",
    "sc": "storageclass",
    "storageclass": "storageclass",
    "storageclasses": "storageclass",
    "role": "role",
    "roles": "role",
    "rolebinding": "rolebinding",
    "rolebindings": "rolebinding",
    "clusterrole": "clusterrole",
    "clusterroles": "clusterrole",
    "clusterrolebinding": "clusterrolebinding",
    "clusterrolebindings": "clusterrolebinding",
    "gateway": "gateway",
    "gateways": "gateway",
    "httproute": "httproute",
    "httproutes": "httproute",
    "networkpolicy": "networkpolicy",
    "networkpolicies": "networkpolicy",
    "netpol": "networkpolicy",
    "ingress": "ingress",
    "ingresses": "ingress",
    "ep": "endpoints",
    "endpoints": "endpoints",
    "job": "job",
    "jobs": "job",
    "cj": "cronjob",
    "cronjob": "cronjob",
    "cronjobs": "cronjob",
    "quota": "resourcequota",
    "resourcequota": "resourcequota",
    "resourcequotas": "resourcequota",
    "limitrange": "limitrange",
    "limitranges": "limitrange",
    "pc": "priorityclass",
    "priorityclass": "priorityclass",
    "priorityclasses": "priorityclass",
    "pdb": "poddisruptionbudget",
    "poddisruptionbudget": "poddisruptionbudget",
}

_LABELS = {
    "serviceaccount": "ServiceAccount",
    "secret": "Secret",
    "configmap": "ConfigMap",
    "deployment": "Deployment",
    "daemonset": "DaemonSet",
    "statefulset": "StatefulSet",
    "replicaset": "ReplicaSet",
    "service": "Service",
    "pod": "Pod",
    "namespace": "Namespace",
    "persistentvolume": "PersistentVolume",
    "persistentvolumeclaim": "PersistentVolumeClaim",
    "storageclass": "StorageClass",
    "role": "Role",
    "rolebinding": "RoleBinding",
    "clusterrole": "ClusterRole",
    "clusterrolebinding": "ClusterRoleBinding",
    "gateway": "Gateway",
    "httproute": "HTTPRoute",
    "networkpolicy": "NetworkPolicy",
    "ingress": "Ingress",
    "endpoints": "Endpoints",
    "job": "Job",
    "cronjob": "CronJob",
    "resourcequota": "ResourceQuota",
    "limitrange": "LimitRange",
    "priorityclass": "PriorityClass",
    "poddisruptionbudget": "PodDisruptionBudget",
}

_VALUE_FLAGS = {
    "--timeout",
    "--for",
    "--field-selector",
    "--selector",
    "-l",
    "--kubeconfig",
    "--context",
    "--cluster",
    "--user",
    "--request-timeout",
    "--sort-by",
    "--cache-dir",
    "-f",
    "--filename",
    "--type",
    "-c",
    "--container",
    "--overrides",
    "--patch",
    "--subresource",
    "--chunk-size",
}


@dataclass(frozen=True)
class KubeCall:
    verb: str
    kind: str | None
    name: str | None
    namespace: str | None
    jsonpath: str | None


def describe_typo(actual: str, expected: str) -> str | None:
    """How `actual` differs from `expected`, when that difference is a typo."""
    if not actual or not expected or actual == expected:
        return None
    if len(actual) > 80 or len(expected) > 80:
        return None
    if "\n" in actual or "\n" in expected:
        return None
    if actual.isdigit() and expected.isdigit() and max(len(actual), len(expected)) <= 4:
        return None
    if actual.lower() == expected.lower():
        return f"`{actual}` differs from `{expected}` only by capitalization."
    if "".join(actual.split()) == "".join(expected.split()):
        return f"`{actual}` differs from `{expected}` only by whitespace."
    if _separators_only(actual, expected):
        actual_sep = "_" if "_" in actual else "-"
        expected_sep = "_" if "_" in expected else "-"
        return (
            f"`{actual}` uses `{actual_sep}` where `{expected}` uses `{expected_sep}`."
        )
    one = _one_edit(actual, expected)
    if one:
        return one
    if min(len(actual), len(expected)) < 5:
        return None
    if edit_distance(actual, expected) != 2:
        return None
    prefix = 0
    for left, right in zip(actual, expected):
        if left != right:
            break
        prefix += 1
    if prefix < 3:
        return None
    return f"`{actual}` is two characters off `{expected}`."


def typo_sentence(actual: str, expected: str) -> str | None:
    detail = describe_typo(actual, expected)
    if not detail:
        return None
    return f"Likely mistake: {detail}"


def blob_typo_sentence(pattern: str, blob: str) -> str | None:
    """A value in `blob` that is one edit away from a literal in `pattern`."""
    needles = _literals(pattern)
    if not needles or not blob.strip():
        return None
    values = _strings_in(blob)
    best: tuple[int, str, str] | None = None
    for needle in needles:
        if any(value == needle for value in values):
            continue
        for value in values:
            if value == needle or len(value) > 80:
                continue
            # Whole-blob scans only trust a single-character slip. A two-character
            # difference inside a large object is usually a different word.
            if _one_edit(value, needle) is None and value.lower() != needle.lower():
                if not _separators_only(value, needle):
                    continue
            detail = describe_typo(value, needle)
            if not detail:
                continue
            dist = edit_distance(value, needle)
            if best is None or dist < best[0]:
                best = (dist, value, detail)
    if best is None:
        return None
    return f"Likely mistake: {best[2]}"


def edit_distance(left: str, right: str) -> int:
    if abs(len(left) - len(right)) > 3:
        return abs(len(left) - len(right))
    previous = list(range(len(right) + 1))
    for i, ca in enumerate(left, start=1):
        current = [i]
        for j, cb in enumerate(right, start=1):
            current.append(
                min(
                    current[j - 1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (ca != cb),
                )
            )
        previous = current
    return previous[-1]


def parse_object_rows(text: str) -> list[tuple[str, str]]:
    """Parse `namespace\\tname` lines from a cluster-wide kubectl get."""
    rows: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("Error", "error:", "Warning", "warning:")):
            continue
        if "\t" in line:
            namespace, name = line.split("\t", 1)
            name = name.strip()
            if name:
                rows.append((namespace.strip(), name))
        elif " " not in line:
            rows.append(("", line))
    return rows


def kinds_to_inspect(output: str, trace: str) -> list[str]:
    """Resource kinds worth listing after a NotFound failure."""
    found = _last_not_found(output)
    if found is None:
        return []
    resource, name = found
    query = _command_for(kubectl_calls(trace), resource, name)
    kinds: list[str] = []

    def add(kind: str | None) -> None:
        if kind and kind not in kinds:
            kinds.append(kind)

    if _canon(resource) == "namespace":
        add("namespace")
        if query and query.kind and _canon(query.kind) != "namespace":
            add(query.kind)
        return kinds
    if query and query.kind:
        add(query.kind)
    else:
        add(resource)
    return kinds


def object_for_field_hint(output: str, trace: str) -> KubeCall | None:
    """The object whose fields can explain an empty or mismatched value."""
    if _last_not_found(output):
        return None
    calls = [
        call
        for call in kubectl_calls(trace)
        if call.verb == "get" and call.kind and call.name and call.jsonpath
    ]
    if not calls:
        return None
    return calls[-1]


def augment_failure(
    message: str,
    output: str,
    trace: str,
    listed: dict[str, list[tuple[str, str]] | None],
    document: dict | None = None,
    jsonpath: str | None = None,
) -> str:
    """Append concrete mistakes found by looking at the cluster."""
    notes = _not_found_notes(output, trace, listed)
    if document is not None and jsonpath and not _last_not_found(output):
        compared = _last_comparison(trace)
        actual = compared[0] if compared else None
        expected = compared[1] if compared else None
        hint = field_hint(document, jsonpath, actual, expected)
        if hint:
            notes.append(hint)
    return _append_notes(message, notes)


def field_hint(
    document: dict,
    jsonpath: str,
    actual: str | None,
    expected: str | None,
) -> str | None:
    """Explain a jsonpath that missed, when the object itself is readable."""
    tokens = parse_jsonpath(jsonpath)
    if not tokens:
        return None
    node: object = document
    walked: list[str | int] = []
    for token in tokens:
        if isinstance(token, int):
            if not isinstance(node, list):
                return None
            if token < 0 or token >= len(node):
                if actual not in (None, ""):
                    return None
                path = _join(walked + [token])
                noun = "item" if len(node) == 1 else "items"
                return f"`{path}` does not exist; that list has {len(node)} {noun}."
            walked.append(token)
            node = node[token]
            continue
        if not isinstance(node, dict) or token not in node:
            if actual not in (None, ""):
                return None
            if not isinstance(node, dict):
                return None
            return _missing_key(node, token, walked, expected)
        walked.append(token)
        node = node[token]

    if not expected:
        if actual in (None, "") and (_as_text(node) or "") == "":
            return f"`{_join(tokens)}` is empty."
        return None
    resolved = _as_text(node)
    if resolved == expected:
        return None
    parent_tokens = walked[:-1]
    parent = _at(document, parent_tokens)
    last = tokens[-1]
    if isinstance(parent, dict) and isinstance(last, str):
        holder = _sibling_with_value(parent, last, expected)
        if holder:
            return (
                f"`{expected}` is set on `{_join(parent_tokens + [holder])}`, "
                f"not `{_join(tokens)}`."
            )
    if actual in (None, "") and (resolved or "") == "":
        return f"`{_join(tokens)}` is empty."
    return None


def parse_jsonpath(text: str) -> list[str | int] | None:
    path = text.strip().strip("'\"")
    if path.startswith("jsonpath-as-json=") or path.startswith("jsonpath="):
        path = path.split("=", 1)[1].strip().strip("'\"")
    if path.startswith("{") and path.endswith("}"):
        path = path[1:-1]
    if not path.startswith(".") or any(char in path for char in "*?@,"):
        return None
    path = path[1:]
    tokens: list[str | int] = []
    buf: list[str] = []
    index = 0
    while index < len(path):
        char = path[index]
        if char == "\\" and index + 1 < len(path):
            buf.append(path[index + 1])
            index += 2
            continue
        if char == ".":
            if not buf:
                return None
            tokens.append("".join(buf))
            buf = []
            index += 1
            continue
        if char == "[":
            if buf:
                tokens.append("".join(buf))
                buf = []
            end = path.find("]", index)
            if end < 0:
                return None
            inner = path[index + 1 : end].strip()
            if not inner.isdigit():
                return None
            tokens.append(int(inner))
            index = end + 1
            continue
        buf.append(char)
        index += 1
    if buf:
        tokens.append("".join(buf))
    return tokens or None


def kubectl_calls(trace: str) -> list[KubeCall]:
    calls: list[KubeCall] = []
    for args in _commands(trace):
        call = _parse_kubectl(args)
        if call and call.kind:
            calls.append(call)
    return calls


def _commands(trace: str) -> list[list[str]]:
    from .grader import _trace_commands

    return _trace_commands(trace)


def _test_body(args: list[str]) -> list[str] | None:
    from .grader import _test_body as body

    return body(args)


def _last_not_found(output: str) -> tuple[str, str] | None:
    found = list(_NOT_FOUND.finditer(output))
    if not found:
        return None
    match = found[-1]
    return match.group(1), match.group(2)


def _canon(kind: str) -> str:
    base = kind.split(".", 1)[0].lower()
    if base in _ALIASES:
        return _ALIASES[base]
    if base.endswith("s") and base[:-1] in _LABELS:
        return base[:-1]
    return base


def kind_label(kind: str) -> str:
    canon = _canon(kind)
    if canon in _LABELS:
        return _LABELS[canon]
    text = kind.split(".", 1)[0]
    if not text:
        return "Object"
    return text[:1].upper() + text[1:]


def _command_for(
    calls: list[KubeCall], resource: str, name: str
) -> KubeCall | None:
    matched = [
        call
        for call in calls
        if (
            call.name == name
            and call.kind
            and _canon(call.kind) == _canon(resource)
        )
        or (_canon(resource) == "namespace" and call.namespace == name)
    ]
    if not matched:
        return None
    return matched[-1]


def _rows_for(
    listed: dict[str, list[tuple[str, str]] | None], kind: str
) -> list[tuple[str, str]] | None:
    want = _canon(kind)
    for key, rows in listed.items():
        if _canon(key) == want:
            return rows
    return None


def _not_found_notes(
    output: str,
    trace: str,
    listed: dict[str, list[tuple[str, str]] | None],
) -> list[str]:
    found = _last_not_found(output)
    if found is None:
        return []
    resource, name = found
    query = _command_for(kubectl_calls(trace), resource, name)
    if _canon(resource) == "namespace":
        return _missing_namespace_notes(name, query, listed)
    kind = query.kind if query and query.kind else resource
    return _object_notes(
        kind_label(kind),
        name,
        query.namespace if query else None,
        _rows_for(listed, kind),
    )


def _missing_namespace_notes(
    expected: str,
    query: KubeCall | None,
    listed: dict[str, list[tuple[str, str]] | None],
) -> list[str]:
    namespace_rows = _rows_for(listed, "namespace")
    object_rows = None
    label = "Object"
    object_name = None
    if query and query.kind and _canon(query.kind) != "namespace":
        object_rows = _rows_for(listed, query.kind)
        label = kind_label(query.kind)
        object_name = query.name

    if object_rows is not None and object_name:
        places = [
            namespace
            for namespace, found in object_rows
            if found == object_name and namespace and namespace != expected
        ]
        if places:
            sentence = (
                f"{label} `{object_name}` is in {_ns_phrase(places)}, not `{expected}`."
            )
            typo_ns = next(
                (
                    namespace
                    for namespace in places
                    if describe_typo(namespace, expected)
                ),
                None,
            )
            if typo_ns:
                detail = describe_typo(typo_ns, expected)
                if detail:
                    sentence += f" Namespace {detail}"
            return [sentence]

    if namespace_rows is None:
        return []
    close = _best_typos(
        expected, [("", found) for _namespace, found in namespace_rows]
    )
    if close:
        _found, _namespace, detail = close[0]
        return [f"Namespace {detail}"]
    names = [found for _, found in namespace_rows]
    if expected not in names:
        return [
            f"Namespace `{expected}` does not exist, and no similar namespace was found."
        ]
    return []


def _object_notes(
    label: str,
    name: str,
    expected_ns: str | None,
    rows: list[tuple[str, str]] | None,
) -> list[str]:
    if rows is None:
        return []
    exact = [(namespace, found) for namespace, found in rows if found == name]
    if expected_ns and any(namespace == expected_ns for namespace, _found in exact):
        return []
    elsewhere = [
        namespace
        for namespace, _found in exact
        if namespace and namespace != (expected_ns or "")
    ]
    if elsewhere:
        if expected_ns:
            return [
                f"{label} `{name}` is in {_ns_phrase(elsewhere)}, not `{expected_ns}`."
            ]
        return [
            f"{label} `{name}` is in {_ns_phrase(elsewhere)}, not the current namespace."
        ]
    if exact and all(not namespace for namespace, _found in exact):
        return []
    close = _best_typos(name, rows, expected_ns)
    if close:
        _found, namespace, detail = close[0]
        return [_with_location(detail, label, namespace, expected_ns)]
    return [
        f"No {label} named `{name}`, or a close spelling, exists on the cluster."
    ]


def _best_typos(
    target: str,
    rows: list[tuple[str, str]],
    expected_ns: str | None = None,
) -> list[tuple[str, str, str]]:
    scored: list[tuple[int, int, str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for namespace, found in rows:
        if not found or found == target or (found, namespace) in seen:
            continue
        detail = describe_typo(found, target)
        if not detail:
            continue
        seen.add((found, namespace))
        if expected_ns and namespace == expected_ns:
            rank = 0
        elif namespace:
            rank = 1
        else:
            rank = 2
        scored.append((edit_distance(found, target), rank, found, namespace, detail))
    scored.sort()
    return [
        (found, namespace, detail)
        for _distance, _rank, found, namespace, detail in scored
    ]


def _with_location(
    detail: str, label: str, namespace: str, expected_ns: str | None
) -> str:
    if namespace and expected_ns and namespace != expected_ns:
        return (
            f"{detail} That {label} is in namespace `{namespace}`, not `{expected_ns}`."
        )
    if namespace:
        return f"{detail} It is in namespace `{namespace}`."
    return detail


def _ns_phrase(names: list[str]) -> str:
    unique: list[str] = []
    for name in names:
        if name not in unique:
            unique.append(name)
    shown = [f"`{name}`" for name in unique[:3]]
    if len(shown) == 1:
        return f"namespace {shown[0]}"
    if len(shown) == 2:
        return f"namespaces {shown[0]} and {shown[1]}"
    return f"namespaces {', '.join(shown[:-1])}, and {shown[-1]}"


def _missing_key(
    node: dict,
    token: str,
    parent: list[str | int],
    expected: str | None,
) -> str:
    path = _join(parent + [token])
    close: list[tuple[int, str, str]] = []
    for key in node:
        if not isinstance(key, str):
            continue
        detail = describe_typo(key, token)
        if detail:
            close.append((edit_distance(key, token), key, detail))
    close.sort()
    if close:
        _distance, key, detail = close[0]
        located = _join(parent + [key])
        return f"`{path}` is not set. `{located}` is there instead. {detail}"
    if expected:
        for key, value in node.items():
            if isinstance(key, str) and key != token and _as_text(value) == expected:
                located = _join(parent + [key])
                return f"`{expected}` is set on `{located}`, not `{path}`."
    keys = [key for key in node if isinstance(key, str)]
    if 0 < len(keys) <= 4:
        shown = ", ".join(f"`{key}`" for key in keys[:4])
        return f"`{path}` is not set. Keys there: {shown}."
    return f"`{path}` is not set."


def _sibling_with_value(node: dict, skip: str, expected: str) -> str | None:
    for key, value in node.items():
        if isinstance(key, str) and key != skip and _as_text(value) == expected:
            return key
    return None


def _at(document: dict, tokens: list[str | int]) -> object:
    node: object = document
    for token in tokens:
        if isinstance(token, int):
            if not isinstance(node, list) or token >= len(node):
                return None
            node = node[token]
        else:
            if not isinstance(node, dict) or token not in node:
                return None
            node = node[token]
    return node


def _as_text(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return str(value)
    return None


def _join(tokens: list[str | int]) -> str:
    parts: list[str] = []
    for token in tokens:
        if isinstance(token, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{token}]"
            else:
                parts.append(f"[{token}]")
        else:
            parts.append(str(token))
    return ".".join(parts)


def _last_comparison(trace: str) -> tuple[str, str] | None:
    found: tuple[str, str] | None = None
    for args in _commands(trace):
        body = _test_body(args)
        if body and len(body) == 3 and body[1] in {"=", "=="}:
            found = (body[0], body[2])
    return found


def _append_notes(message: str, notes: list[str]) -> str:
    fresh: list[str] = []
    for note in notes:
        line = note if note.startswith("Likely mistake:") else f"Likely mistake: {note}"
        if line and line not in message and line not in fresh:
            fresh.append(line)
    if not fresh:
        return message
    base = message.rstrip()
    if not base:
        return "\n".join(fresh)
    return base + "\n\n" + "\n".join(fresh)


def _literals(pattern: str) -> list[str]:
    quoted = re.findall(r'"([^"\\]{2,40})"', pattern)
    if quoted:
        return quoted
    if re.fullmatch(r"[A-Za-z0-9_.:/-]{2,40}", pattern):
        return [pattern]
    return []


def _strings_in(blob: str) -> list[str]:
    text = blob.strip()
    if text[:1] in "{[":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if parsed is not None:
            found: list[str] = []
            _walk_strings(parsed, found)
            return found
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,63}", blob)


def _walk_strings(value: object, found: list[str]) -> None:
    if isinstance(value, str):
        found.append(value)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                found.append(key)
            _walk_strings(item, found)
        return
    if isinstance(value, list):
        for item in value:
            _walk_strings(item, found)


def _separators_only(actual: str, expected: str) -> bool:
    if actual == expected:
        return False

    def norm(value: str) -> str:
        return "".join("-" if char in "_-" else char for char in value)

    return norm(actual) == norm(expected)


def _one_edit(actual: str, expected: str) -> str | None:
    if min(len(actual), len(expected)) < 2:
        return None
    if len(actual) == len(expected):
        diffs = [i for i, (left, right) in enumerate(zip(actual, expected)) if left != right]
        if len(diffs) == 1:
            index = diffs[0]
            return (
                f"`{actual}` has `{actual[index]}` where `{expected}` has `{expected[index]}`."
            )
        if (
            len(diffs) == 2
            and diffs[1] == diffs[0] + 1
            and actual[diffs[0]] == expected[diffs[1]]
            and actual[diffs[1]] == expected[diffs[0]]
        ):
            index = diffs[0]
            return (
                f"`{actual}` swaps `{actual[index]}` and `{actual[index + 1]}` "
                f"compared with `{expected}`."
            )
        return None
    if abs(len(actual) - len(expected)) != 1:
        return None
    if len(actual) > len(expected):
        longer, shorter, extra = actual, expected, True
    else:
        longer, shorter, extra = expected, actual, False
    # Identical repeated characters match at more than one index. The later
    # index reads as "at the end" instead of "after the same character".
    match: int | None = None
    for index in range(len(longer)):
        if longer[:index] + longer[index + 1 :] == shorter:
            match = index
    if match is None:
        return None
    char = longer[match]
    if match == 0:
        place = "at the start"
    elif match == len(longer) - 1:
        place = "at the end"
    else:
        place = f"after `{longer[:match]}`"
    if extra:
        return f"`{actual}` has an extra `{char}` {place} compared with `{expected}`."
    return f"`{actual}` is missing `{char}` {place} compared with `{expected}`."


def _parse_kubectl(args: list[str]) -> KubeCall | None:
    if not args or args[0] != "kubectl":
        return None
    namespace = None
    output = None
    positionals: list[str] = []
    index = 1
    while index < len(args):
        arg = args[index]
        if arg in {"-n", "--namespace"} and index + 1 < len(args):
            namespace = args[index + 1]
            index += 2
            continue
        if arg.startswith("--namespace="):
            namespace = arg.split("=", 1)[1]
            index += 1
            continue
        if arg in {"-o", "--output"} and index + 1 < len(args):
            output = args[index + 1]
            index += 2
            continue
        if arg.startswith("--output=") or arg.startswith("-o="):
            output = arg.split("=", 1)[1]
            index += 1
            continue
        if arg in _VALUE_FLAGS and index + 1 < len(args):
            index += 2
            continue
        if arg.startswith("-"):
            index += 1
            continue
        positionals.append(arg)
        index += 1
    if not positionals:
        return None
    verb = positionals[0]
    rest = positionals[1:]
    if verb in {"get", "describe", "delete", "label", "annotate", "patch", "edit"}:
        kind, name = _kind_and_name(rest)
    elif verb == "rollout" and len(rest) >= 2 and rest[0] == "status":
        kind, name = _kind_and_name(rest[1:])
    elif verb == "wait":
        kind, name = _kind_and_name(rest)
    else:
        return None
    if not kind or "," in kind:
        return None
    return KubeCall(verb, kind, name, namespace, _jsonpath_of(output))


def _kind_and_name(rest: list[str]) -> tuple[str | None, str | None]:
    if not rest or rest[0].startswith("-"):
        return None, None
    target = rest[0]
    if "/" in target:
        kind, name = target.split("/", 1)
        return kind or None, name or None
    name = rest[1] if len(rest) > 1 and not rest[1].startswith("-") else None
    return target, name


def _jsonpath_of(output: str | None) -> str | None:
    if not output or "jsonpath" not in output:
        return None
    if "=" in output:
        return output.split("=", 1)[1]
    return output
