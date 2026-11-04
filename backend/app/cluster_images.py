"""Images every question cluster needs, cached on the Docker host.

kind nodes keep their own containerd store. A host ``docker pull`` is invisible
to them, so each new cluster would download Calico, ingress-nginx, and the
workload images again. Install pulls this list once; cluster setup streams
each image into the node with ``ctr images import`` before those pods are
created. ``kind load`` is not used: it passes ``--all-platforms``, and current
Docker archives reference attestation blobs that are not in the tar, so
``ctr`` exits with ``content digest … not found``.
"""

from __future__ import annotations

import asyncio
import re
import subprocess
from dataclasses import dataclass

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

    ``--all-platforms`` is omitted on purpose. Docker Hub archives include an
    attestation index whose blobs are not in ``docker save``, and importing
    every platform fails with ``content digest … not found``.
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


async def _stream_save_into(image: str, import_cmd: list[str], timeout: int) -> tuple[int, str]:
    """Pipe ``docker save`` into ``ctr images import`` without buffering the tar."""
    save = await asyncio.create_subprocess_exec(
        "docker",
        "save",
        image,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    imp = await asyncio.create_subprocess_exec(
        *import_cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    async def pump() -> None:
        assert save.stdout is not None and imp.stdin is not None
        try:
            while True:
                chunk = await save.stdout.read(1024 * 1024)
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
        err_task = asyncio.create_task(_read_stream(save.stderr))
        out_task = asyncio.create_task(_read_stream(imp.stdout))
        await pump_task
        save_code = await save.wait()
        imp_code = await imp.wait()
        out = (await out_task).decode("utf-8", errors="replace")
        err = (await err_task).decode("utf-8", errors="replace")
        if imp_code != 0:
            return imp_code, out + (("\n" + err) if err else "")
        if save_code != 0:
            return save_code, err or out
        return 0, out

    try:
        return await asyncio.wait_for(finish(), timeout=timeout)
    except asyncio.TimeoutError:
        save.kill()
        imp.kill()
        await save.wait()
        await imp.wait()
        return 1, f"timed out importing {image}"


async def _import_one(node: str, image: str, snapshotter: str) -> str:
    attempts = (
        node_import_cmd(node, snapshotter, digests=True, local=False),
        node_import_cmd(node, snapshotter, digests=False, local=True),
    )
    last = ""
    for cmd in attempts:
        code, out = await _stream_save_into(image, cmd, timeout=300)
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
    print(
        f"importing {len(names)} cached images into {len(nodes)} nodes",
        flush=True,
    )
    for node in nodes:
        snapshotter = await _node_snapshotter(node)
        for image in names:
            print(f"importing {image} into {node}", flush=True)
            output = await _import_one(node, image, snapshotter)
            await _ensure_cri_name(node, image, output)
