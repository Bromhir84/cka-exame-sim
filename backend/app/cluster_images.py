"""Images every question cluster needs, cached on the Docker host.

kind nodes keep their own containerd store. A host ``docker pull`` is invisible
to them, so each new cluster would download Calico, ingress-nginx, and the
workload images again. Install pulls this list once; cluster setup streams
each image into the node with ``ctr images import`` before those pods are
created. ``kind load`` is not used. With the containerd image store, ``docker
save`` writes the full multi-arch index but only the blobs for the platform
that was pulled. ``ctr`` follows every descriptor and exits with ``content
digest … not found`` (for nginx:1.27 that digest is the linux/386 manifest).
The archive is reduced to the node’s own complete platform image before import.
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import re
import shutil
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .config import KIND_IMAGE

# Keep these in sync with the manifests applied in session.py.
CALICO_VERSION = "v3.28.2"
CALICO_MANIFEST = (
    "https://raw.githubusercontent.com/projectcalico/calico/"
    f"{CALICO_VERSION}/manifests/calico.yaml"
)

INGRESS_GIT_REF = "controller-v1.11.3"
INGRESS_MANIFEST = (
    "https://raw.githubusercontent.com/kubernetes/ingress-nginx/"
    f"{INGRESS_GIT_REF}/deploy/static/provider/kind/deploy.yaml"
)


@dataclass(frozen=True)
class CachedImage:
    """Image to pull on the host and load into each kind node.

    ``digest`` pins a manifest that references ``name@sha256``. ``kind load``
    imports digest refs (``ctr images import --digests``), so kubelet finds
    the image locally instead of pulling it.
    """

    name: str
    digest: str = ""

    @property
    def pull_ref(self) -> str:
        if self.digest:
            return f"{self.name}@{self.digest}"
        return self.name


# Pod/controller images. The kind node image itself is pulled separately and
# is not loaded into the nodes (it *is* the node).
CACHED_IMAGES: tuple[CachedImage, ...] = (
    CachedImage("docker.io/calico/cni:v3.28.2"),
    CachedImage("docker.io/calico/node:v3.28.2"),
    CachedImage("docker.io/calico/kube-controllers:v3.28.2"),
    CachedImage(
        "registry.k8s.io/ingress-nginx/controller:v1.11.3",
        "sha256:d56f135b6462cfc476447cfe564b83a45e8bb7da2774963b00d12161112270b7",
    ),
    CachedImage(
        "registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.4.4",
        "sha256:a9f03b34a3cbfbb26d103a14046ab2c5130a80c3d69d526ff8063d2b37b9fd3f",
    ),
    # Workload images used by the task bank (setup and candidate manifests).
    CachedImage("nginx:1.27"),
    CachedImage("busybox:1.36"),
)


@dataclass(frozen=True)
class Pull:
    ref: str
    tag_as: str = ""


def pull_plan() -> list[Pull]:
    """Host pulls in order. Digest pulls are also tagged with the manifest name."""
    plan = [Pull(KIND_IMAGE)]
    for image in CACHED_IMAGES:
        extra = image.name if image.digest else ""
        plan.append(Pull(image.pull_ref, extra))
    return plan


def images_to_load(present: set[str]) -> list[str]:
    """Cached image names that already exist in the host Docker daemon."""
    return [image.name for image in CACHED_IMAGES if image.name in present]


def image_inspect_cmd(name: str) -> list[str]:
    """Command that is true when ``name`` is already in the local Docker daemon.

    This is the same check kind uses before pulling the node image
    (``docker inspect --type=image``). ``docker image inspect`` does not
    accept ``--type``, so that form always fails and every kind node then
    downloads the images again.
    """
    return ["docker", "inspect", "--type=image", name]


_DIGEST_PIN = re.compile(r"@sha256:[a-f0-9]{64}")


def strip_image_digests(manifest: str) -> str:
    """Drop ``@sha256`` pins so kubelet looks the image up by tag.

    The ingress manifest pins a multi-arch index digest. The image imported
    into the node is the host platform image, whose digest is different, and a
    pin that does not match is pulled again. The tag still names the digest
    we pulled.
    """
    return _DIGEST_PIN.sub("", manifest)


def pull_images() -> int:
    """Pull the plan into the host Docker daemon. Returns 0 on success."""
    failed: list[str] = []
    for item in pull_plan():
        print(f"==> docker pull {item.ref}", flush=True)
        if subprocess.run(["docker", "pull", item.ref]).returncode != 0:
            failed.append(item.ref)
            continue
        if item.tag_as and item.tag_as != item.ref:
            print(f"==> docker tag {item.ref} {item.tag_as}", flush=True)
            if subprocess.run(["docker", "tag", item.ref, item.tag_as]).returncode != 0:
                failed.append(item.tag_as)
    if failed:
        print("Failed to cache: " + ", ".join(failed), flush=True)
        return 1
    print(
        "Cached images are on the Docker host. "
        "New clusters load them instead of pulling.",
        flush=True,
    )
    return 0


async def _run(cmd: list[str], timeout: int) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return 1, f"command timed out: {' '.join(cmd)}"
    return proc.returncode or 0, (out or b"").decode("utf-8", errors="replace")


def cri_ref(name: str) -> str:
    """Image name kubelet resolves, matching kind's ``sanitizeImage``."""
    sanitized = name
    if "/" not in sanitized:
        sanitized = "library/" + sanitized
    registry = sanitized.split("/", 1)[0]
    if ":" not in registry and "." not in registry and registry != "localhost":
        sanitized = "docker.io/" + sanitized
    if ":" not in sanitized:
        sanitized += ":latest"
    return sanitized


def node_import_cmd(
    node: str,
    snapshotter: str,
    *,
    digests: bool,
    local: bool,
) -> list[str]:
    """``ctr images import`` for one kind node.

    ``--all-platforms`` is omitted on purpose. A multi-arch ``docker save``
    lists platforms whose blobs were not saved, and importing every platform
    fails with ``content digest … not found``.
    """
    cmd = [
        "docker",
        "exec",
        "--privileged",
        "-i",
        node,
        "ctr",
        "--namespace=k8s.io",
        "images",
        "import",
        f"--snapshotter={snapshotter}",
    ]
    if local:
        cmd.append("--local")
    if digests:
        cmd.append("--digests")
    cmd.append("-")
    return cmd


def node_tag_cmd(node: str, source: str, target: str) -> list[str]:
    return [
        "docker",
        "exec",
        node,
        "ctr",
        "--namespace=k8s.io",
        "images",
        "tag",
        "--force",
        source,
        target,
    ]


_UNPACKED_REF = re.compile(r"unpacking\s+(\S+)\s+\(")


def imported_refs(output: str) -> list[str]:
    return _UNPACKED_REF.findall(output)


def choose_import_source(imported: list[str], image: str) -> str | None:
    if not imported:
        return None
    cri = cri_ref(image)
    if cri in imported:
        return cri
    tail = image.split("/")[-1]
    for ref in imported:
        if ref == image or ref.endswith("/" + tail):
            return ref
    return imported[0]


def normalize_arch(uname: str) -> str:
    """Map ``uname -m`` to the OCI architecture name."""
    name = uname.strip()
    return {
        "x86_64": "amd64",
        "amd64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
    }.get(name, name or "amd64")


_INDEX_MEDIA = {
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
}


def _normalize_oci_arch(arch: str) -> str:
    return {"x86_64": "amd64", "aarch64": "arm64"}.get(arch, arch)


def _is_attestation(desc: dict, doc: dict | None = None) -> bool:
    ann = desc.get("annotations") or {}
    if ann.get("vnd.docker.reference.type") == "attestation-manifest":
        return True
    plat = desc.get("platform") or {}
    if plat.get("architecture") == "unknown" or plat.get("os") == "unknown":
        return True
    if not doc:
        return False
    for layer in doc.get("layers") or []:
        media = layer.get("mediaType") if isinstance(layer, dict) else ""
        if media and ("in-toto" in media or "attestation" in media):
            return True
    return False


def _blob_member(members: set[str], digest: str) -> str | None:
    if not digest.startswith("sha256:"):
        return None
    hexpart = digest.split(":", 1)[1]
    for name in (f"blobs/sha256/{hexpart}", f"./blobs/sha256/{hexpart}"):
        if name in members:
            return name
    return None


def _read_member(tf: tarfile.TarFile, name: str) -> bytes:
    handle = tf.extractfile(name)
    if handle is None:
        return b""
    return handle.read()


def _read_json_blob(
    tf: tarfile.TarFile, members: set[str], digest: str
) -> tuple[str, dict] | None:
    name = _blob_member(members, digest)
    if name is None:
        return None
    try:
        doc = json.loads(_read_member(tf, name))
    except (json.JSONDecodeError, UnicodeError):
        return None
    if not isinstance(doc, dict):
        return None
    return name, doc


def _config_platform(
    doc: dict, tf: tarfile.TarFile, members: set[str]
) -> tuple[str, str]:
    config = (doc.get("config") or {}).get("digest") or ""
    found = _read_json_blob(tf, members, config)
    if found is None:
        return "", ""
    image = found[1]
    return (
        str(image.get("os") or ""),
        _normalize_oci_arch(str(image.get("architecture") or "")),
    )


def _image_blobs(
    tf: tarfile.TarFile, members: set[str], manifest_name: str, doc: dict
) -> set[str] | None:
    """Blob members for one image manifest, or None when any blob is absent."""
    if "layers" not in doc or not isinstance(doc.get("layers"), list):
        return None
    needed = {manifest_name}
    config = (doc.get("config") or {}).get("digest")
    if not config:
        return None
    config_name = _blob_member(members, config)
    if config_name is None:
        return None
    needed.add(config_name)
    for layer in doc["layers"]:
        layer_digest = layer.get("digest") if isinstance(layer, dict) else None
        if not layer_digest:
            return None
        layer_name = _blob_member(members, layer_digest)
        if layer_name is None:
            return None
        needed.add(layer_name)
    return needed


def _arch_rank(
    desc: dict,
    doc: dict,
    arch: str,
    tf: tarfile.TarFile,
    members: set[str],
) -> int | None:
    """Lower is a better match. None rejects a different platform."""
    plat = desc.get("platform") or {}
    os_name = str(plat.get("os") or "")
    got = _normalize_oci_arch(str(plat.get("architecture") or ""))
    if not os_name or not got:
        config_os, config_arch = _config_platform(doc, tf, members)
        os_name = os_name or config_os
        got = got or config_arch
    if os_name and os_name != "linux":
        return None
    if got and got != arch:
        return None
    if got == arch:
        return 0
    return 1


def _collect_images(
    desc: dict,
    tf: tarfile.TarFile,
    members: set[str],
    arch: str,
) -> list[tuple[int, dict, set[str]]]:
    """Complete linux images under ``desc``, skipping missing and other platforms."""
    if _is_attestation(desc):
        return []
    digest = desc.get("digest") or ""
    found = _read_json_blob(tf, members, digest)
    if found is None:
        return []
    name, doc = found
    media = str(desc.get("mediaType") or doc.get("mediaType") or "")
    if media in _INDEX_MEDIA or ("manifests" in doc and "layers" not in doc):
        found_images: list[tuple[int, dict, set[str]]] = []
        for child in doc.get("manifests") or []:
            if isinstance(child, dict):
                found_images.extend(_collect_images(child, tf, members, arch))
        return found_images
    if _is_attestation(desc, doc):
        return []
    blobs = _image_blobs(tf, members, name, doc)
    if blobs is None:
        return []
    rank = _arch_rank(desc, doc, arch, tf, members)
    if rank is None:
        return []
    updated = dict(desc)
    if not updated.get("mediaType") and doc.get("mediaType"):
        updated["mediaType"] = doc["mediaType"]
    return [(rank, updated, blobs)]


def rewrite_image_archive(src: Path, dst: Path, arch: str, image_name: str) -> None:
    """Write an OCI archive that contains one complete platform image.

    ``docker save`` of a multi-arch image stores the registry index, including
    other platforms and attestations, but omits blobs that were never pulled.
    ``ctr images import`` walks every descriptor and fails with ``content
    digest … not found``. The rewritten index points only at the node's
    platform manifest, and that manifest is tagged for kubelet.
    """
    arch = _normalize_oci_arch(arch)
    with tarfile.open(src, "r:*") as tf:
        members = {m.name: m for m in tf.getmembers() if m.isfile()}
        index_name = "index.json" if "index.json" in members else "./index.json"
        if index_name not in members:
            shutil.copyfile(src, dst)
            return
        index = json.loads(_read_member(tf, index_name))
        found: list[tuple[int, dict, set[str]]] = []
        for desc in index.get("manifests") or []:
            if isinstance(desc, dict):
                found.extend(_collect_images(desc, tf, set(members), arch))
        if not found:
            raise RuntimeError(
                f"{image_name} archive has no complete linux/{arch} image "
                "to load into the kind node"
            )
        found.sort(key=lambda item: item[0])
        _rank, chosen, needed = found[0]
        ann = dict(chosen.get("annotations") or {})
        ref = cri_ref(image_name)
        ann["io.containerd.image.name"] = ref
        ann["org.opencontainers.image.ref.name"] = ref
        chosen["annotations"] = ann
        payload = json.dumps(
            {
                "schemaVersion": 2,
                "mediaType": "application/vnd.oci.image.index.v1+json",
                "manifests": [chosen],
            },
            separators=(",", ":"),
        ).encode()
        with tarfile.open(dst, "w") as out:
            layout = members.get("oci-layout") or members.get("./oci-layout")
            if layout is not None:
                out.addfile(layout, io.BytesIO(_read_member(tf, layout.name)))
            else:
                data = b'{"imageLayoutVersion":"1.0.0"}\n'
                info = tarfile.TarInfo("oci-layout")
                info.size = len(data)
                out.addfile(info, io.BytesIO(data))
            info = tarfile.TarInfo("index.json")
            info.size = len(payload)
            out.addfile(info, io.BytesIO(payload))
            for name in sorted(needed):
                member = members[name]
                blob_name = name[2:] if name.startswith("./") else name
                info = tarfile.TarInfo(blob_name)
                info.size = member.size
                info.mode = member.mode
                info.mtime = member.mtime
                out.addfile(info, io.BytesIO(_read_member(tf, name)))


def snapshotter_from_config(text: str) -> str:
    """Read the CRI snapshotter from ``containerd config dump``."""
    sections = (
        r'\[plugins\."io\.containerd\.grpc\.v1\.cri"\.containerd\]',
        r'\[plugins\."io\.containerd\.cri\.v1\.images"\]',
    )
    for header in sections:
        match = re.search(rf"(?m)^{header}\s*$", text)
        if not match:
            continue
        rest = text[match.end() :]
        nxt = re.search(r"(?m)^\[", rest)
        block = rest[: nxt.start()] if nxt else rest
        found = re.search(r'(?m)^\s*snapshotter\s*=\s*"([^"]+)"', block)
        if found:
            return found.group(1)
    return "overlayfs"


async def _image_present(name: str) -> bool:
    code, _ = await _run(image_inspect_cmd(name), timeout=30)
    return code == 0


async def _kind_node_names(cluster_name: str) -> list[str]:
    code, out = await _run(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}",
            "--filter",
            f"label=io.x-k8s.kind.cluster={cluster_name}",
        ],
        timeout=30,
    )
    names = [line.strip() for line in out.splitlines() if line.strip()]
    if code != 0 or not names:
        raise RuntimeError(f"no kind nodes for cluster {cluster_name}:\n{out}")
    return names


async def _node_snapshotter(node: str) -> str:
    code, out = await _run(
        ["docker", "exec", node, "containerd", "config", "dump"],
        timeout=30,
    )
    if code != 0:
        return "overlayfs"
    return snapshotter_from_config(out)


async def _read_stream(stream: asyncio.StreamReader | None) -> bytes:
    if stream is None:
        return b""
    chunks: list[bytes] = []
    while True:
        chunk = await stream.read(1024 * 1024)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


async def _node_arch(node: str) -> str:
    code, out = await _run(["docker", "exec", node, "uname", "-m"], timeout=30)
    if code != 0:
        return "amd64"
    return normalize_arch(out)


async def _stream_file_into(path: str, import_cmd: list[str], timeout: int) -> tuple[int, str]:
    """Feed an image archive to ``ctr images import``."""
    imp = await asyncio.create_subprocess_exec(
        *import_cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    async def pump() -> None:
        assert imp.stdin is not None
        try:
            with open(path, "rb") as handle:
                while True:
                    chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    imp.stdin.write(chunk)
                    await imp.stdin.drain()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            try:
                imp.stdin.close()
                await imp.stdin.wait_closed()
            except (BrokenPipeError, ConnectionResetError, RuntimeError):
                pass

    async def finish() -> tuple[int, str]:
        pump_task = asyncio.create_task(pump())
        out_task = asyncio.create_task(_read_stream(imp.stdout))
        await pump_task
        code = await imp.wait()
        out = (await out_task).decode("utf-8", errors="replace")
        return code or 0, out

    try:
        return await asyncio.wait_for(finish(), timeout=timeout)
    except asyncio.TimeoutError:
        imp.kill()
        await imp.wait()
        return 1, f"timed out importing {path}"


async def _import_slim(node: str, image: str, archive: str, snapshotter: str) -> str:
    attempts = (
        node_import_cmd(node, snapshotter, digests=True, local=False),
        node_import_cmd(node, snapshotter, digests=False, local=True),
    )
    last = ""
    for cmd in attempts:
        code, out = await _stream_file_into(archive, cmd, timeout=300)
        last = out
        if code == 0:
            return out
    raise RuntimeError(f"failed to import {image} into {node}:\n{last}")


async def _ensure_cri_name(node: str, image: str, import_output: str) -> None:
    target = cri_ref(image)
    source = choose_import_source(imported_refs(import_output), image)
    if source and source != target:
        code, out = await _run(node_tag_cmd(node, source, target), timeout=30)
        if code != 0:
            raise RuntimeError(
                f"failed to tag {source} as {target} on {node}:\n{out}"
            )
    code, out = await _run(
        ["docker", "exec", node, "crictl", "inspecti", target],
        timeout=30,
    )
    if code != 0:
        raise RuntimeError(
            f"{target} is not visible to containerd on {node} after import:\n{out}"
        )


async def load_cached_images(cluster_name: str) -> None:
    """Copy host-cached images into this cluster's nodes.

    Images that were never pulled are skipped; kubelet then pulls those as
    before. A failed import of an image that *is* present is fatal so a broken
    cache is not silently replaced by another full download.
    """
    present: set[str] = set()
    for image in CACHED_IMAGES:
        if await _image_present(image.name):
            present.add(image.name)
    names = images_to_load(present)
    if not names:
        print(
            f"no cached cluster images in docker; {cluster_name} will pull them",
            flush=True,
        )
        return
    nodes = await _kind_node_names(cluster_name)
    arch = await _node_arch(nodes[0])
    print(
        f"importing {len(names)} cached images into {len(nodes)} {arch} nodes",
        flush=True,
    )
    snapshotters = {node: await _node_snapshotter(node) for node in nodes}
    for image in names:
        print(f"importing {image}", flush=True)
        # Save and strip attestations once, then import that archive into each node.
        tmp = tempfile.mkdtemp(prefix="cka-img-")
        raw = os.path.join(tmp, "image.tar")
        slim = os.path.join(tmp, "image.slim.tar")
        try:
            code, out = await _run(["docker", "save", "-o", raw, image], timeout=300)
            if code != 0:
                raise RuntimeError(f"docker save {image} failed:\n{out}")
            rewrite_image_archive(Path(raw), Path(slim), arch, image)
            os.remove(raw)
            for node in nodes:
                output = await _import_slim(node, image, slim, snapshotters[node])
                await _ensure_cri_name(node, image, output)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
