"""Images every question cluster needs, cached on the Docker host.

kind nodes keep their own containerd store. A host ``docker pull`` is invisible
to them, so each new cluster would download Calico, ingress-nginx, and the
workload images again. Install pulls this list once; cluster setup copies the
local images in with ``kind load`` before those pods are created.
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

    The ingress manifest pins a multi-arch index digest. ``kind load`` imports
    the single platform image, whose digest is different, and a pin that does
    not match is pulled again. The tag still names the digest we pulled.
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


async def _image_present(name: str) -> bool:
    code, _ = await _run(image_inspect_cmd(name), timeout=30)
    return code == 0


async def load_cached_images(cluster_name: str) -> None:
    """Copy host-cached images into this cluster's nodes.

    Images that were never pulled are skipped; kubelet then pulls those as
    before. A failed load of an image that *is* present is fatal so a broken
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
    print(
        f"loading {len(names)} cached images into {cluster_name}",
        flush=True,
    )
    code, out = await _run(
        ["kind", "load", "docker-image", "--name", cluster_name, *names],
        timeout=900,
    )
    if code != 0:
        raise RuntimeError(f"kind load docker-image failed:\n{out}")
