"""Cluster image cache: install pulls once, kind load reuses them."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.cluster_images import (  # noqa: E402
    CACHED_IMAGES,
    CALICO_VERSION,
    choose_import_source,
    cri_ref,
    image_inspect_cmd,
    images_to_load,
    imported_refs,
    node_import_cmd,
    pull_plan,
    rewrite_image_archive,
    snapshotter_from_config,
    strip_image_digests,
)
from app.config import KIND_IMAGE  # noqa: E402


class ClusterImageCacheTests(unittest.TestCase):
    def test_pull_plan_includes_node_image_and_digest_pins(self):
        plan = pull_plan()
        refs = [item.ref for item in plan]
        self.assertEqual(refs[0], KIND_IMAGE)
        self.assertNotIn(KIND_IMAGE, [image.name for image in CACHED_IMAGES])

        self.assertIn("docker.io/calico/node:v3.28.2", refs)
        self.assertIn("nginx:1.27", refs)
        self.assertNotIn(
            "registry.k8s.io/ingress-nginx/controller:v1.11.3",
            [image.name for image in CACHED_IMAGES],
        )
        self.assertFalse(any(item.tag_as for item in plan))

    def test_cached_set_matches_cluster_manifests_and_task_images(self):
        names = {image.name for image in CACHED_IMAGES}
        self.assertIn(f"docker.io/calico/node:{CALICO_VERSION}", names)
        self.assertIn(f"docker.io/calico/cni:{CALICO_VERSION}", names)
        self.assertIn(f"docker.io/calico/kube-controllers:{CALICO_VERSION}", names)
        self.assertIn("nginx:1.27", names)
        self.assertIn("busybox:1.36", names)
        self.assertNotIn("registry.k8s.io/ingress-nginx/controller:v1.11.3", names)
        self.assertNotIn(
            "registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.4.4", names
        )
        # These tags are supposed to fail image pull in troubleshooting tasks.
        self.assertNotIn("nginx:1.27-notreal", names)
        self.assertNotIn("nginx:1.27-this-tag-does-not-exist", names)

    def test_cri_ref_matches_kubelet_normalization(self):
        self.assertEqual(cri_ref("nginx:1.27"), "docker.io/library/nginx:1.27")
        self.assertEqual(cri_ref("busybox:1.36"), "docker.io/library/busybox:1.36")
        self.assertEqual(
            cri_ref("docker.io/calico/node:v3.28.2"),
            "docker.io/calico/node:v3.28.2",
        )
        self.assertEqual(
            cri_ref("registry.k8s.io/ingress-nginx/controller:v1.11.3"),
            "registry.k8s.io/ingress-nginx/controller:v1.11.3",
        )

    def test_node_import_skips_other_platforms(self):
        cmd = node_import_cmd(
            "cka-node",
            "overlayfs",
            digests=True,
            local=False,
        )
        self.assertNotIn("--all-platforms", cmd)
        self.assertIn("--digests", cmd)
        self.assertIn("--snapshotter=overlayfs", cmd)
        self.assertEqual(cmd[-1], "-")
        fallback = node_import_cmd(
            "cka-node",
            "overlayfs",
            digests=False,
            local=True,
        )
        self.assertIn("--local", fallback)
        self.assertNotIn("--digests", fallback)
        self.assertNotIn("--all-platforms", fallback)

    def test_import_output_and_snapshotter(self):
        output = (
            "unpacking docker.io/library/nginx:1.27 (sha256:abc)...done\n"
            "unpacking nginx:1.27 (sha256:def)...done\n"
        )
        refs = imported_refs(output)
        self.assertEqual(
            choose_import_source(refs, "nginx:1.27"),
            "docker.io/library/nginx:1.27",
        )
        config = """
version = 2

[plugins."io.containerd.grpc.v1.cri".containerd]
  snapshotter = "overlayfs"
  disable_snapshot_annotations = true

[plugins."io.containerd.grpc.v1.cri".cni]
  bin_dir = "/opt/cni/bin"
"""
        self.assertEqual(snapshotter_from_config(config), "overlayfs")
        self.assertEqual(snapshotter_from_config("version = 2\n"), "overlayfs")

    def test_rewrite_drops_attestation_blob_missing_from_save(self):
        # The digest from a failed kind-node import of nginx:1.27. It is an
        # attestation entry whose blob docker save did not include.
        missing = "sha256:2c1ee2371c776670cebad7f4fee298ed8979fdfc18d2c1bc49f17c35754259f2"
        config = b'{"architecture":"amd64","os":"linux"}'
        layer = b"rootfs"
        config_digest = "sha256:" + hashlib.sha256(config).hexdigest()
        layer_digest = "sha256:" + hashlib.sha256(layer).hexdigest()
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": config_digest,
                "size": len(config),
            },
            "layers": [
                {
                    "mediaType": "application/vnd.oci.image.layer.v1.tar",
                    "digest": layer_digest,
                    "size": len(layer),
                }
            ],
        }
        manifest_bytes = json.dumps(manifest).encode()
        manifest_digest = "sha256:" + hashlib.sha256(manifest_bytes).hexdigest()
        index = {
            "schemaVersion": 2,
            "manifests": [
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": manifest_digest,
                    "size": len(manifest_bytes),
                    "platform": {"architecture": "amd64", "os": "linux"},
                },
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": missing,
                    "size": 100,
                    "platform": {"architecture": "unknown", "os": "unknown"},
                    "annotations": {
                        "vnd.docker.reference.type": "attestation-manifest"
                    },
                },
            ],
        }
        blobs = {
            config_digest.split(":", 1)[1]: config,
            layer_digest.split(":", 1)[1]: layer,
            manifest_digest.split(":", 1)[1]: manifest_bytes,
        }
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "image.tar"
            dst = Path(tmp) / "slim.tar"
            with tarfile.open(src, "w") as tf:
                layout = b'{"imageLayoutVersion":"1.0.0"}\n'
                info = tarfile.TarInfo("oci-layout")
                info.size = len(layout)
                tf.addfile(info, io.BytesIO(layout))
                raw_index = json.dumps(index).encode()
                info = tarfile.TarInfo("index.json")
                info.size = len(raw_index)
                tf.addfile(info, io.BytesIO(raw_index))
                for hexpart, data in blobs.items():
                    info = tarfile.TarInfo(f"blobs/sha256/{hexpart}")
                    info.size = len(data)
                    tf.addfile(info, io.BytesIO(data))
            rewrite_image_archive(src, dst, "amd64", "nginx:1.27")
            with tarfile.open(dst, "r") as tf:
                rewritten = json.load(tf.extractfile("index.json"))
            self.assertEqual(len(rewritten["manifests"]), 1)
            self.assertEqual(rewritten["manifests"][0]["digest"], manifest_digest)
            self.assertNotIn(missing, json.dumps(rewritten))
            self.assertEqual(
                rewritten["manifests"][0]["annotations"]["io.containerd.image.name"],
                "docker.io/library/nginx:1.27",
            )

    def _oci_tar(self, path: Path, index: dict, blobs: dict[str, bytes]) -> None:
        with tarfile.open(path, "w") as tf:
            layout = b'{"imageLayoutVersion":"1.0.0"}\n'
            info = tarfile.TarInfo("oci-layout")
            info.size = len(layout)
            tf.addfile(info, io.BytesIO(layout))
            raw_index = json.dumps(index).encode()
            info = tarfile.TarInfo("index.json")
            info.size = len(raw_index)
            tf.addfile(info, io.BytesIO(raw_index))
            for hexpart, data in blobs.items():
                info = tarfile.TarInfo(f"blobs/sha256/{hexpart}")
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))

    def _amd64_image(self, layer: bytes = b"rootfs") -> tuple[str, dict[str, bytes]]:
        config = b'{"architecture":"amd64","os":"linux"}'
        config_digest = "sha256:" + hashlib.sha256(config).hexdigest()
        layer_digest = "sha256:" + hashlib.sha256(layer).hexdigest()
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": config_digest,
                "size": len(config),
            },
            "layers": [
                {
                    "mediaType": "application/vnd.oci.image.layer.v1.tar",
                    "digest": layer_digest,
                    "size": len(layer),
                }
            ],
        }
        manifest_bytes = json.dumps(manifest).encode()
        manifest_digest = "sha256:" + hashlib.sha256(manifest_bytes).hexdigest()
        blobs = {
            config_digest.split(":", 1)[1]: config,
            layer_digest.split(":", 1)[1]: layer,
            manifest_digest.split(":", 1)[1]: manifest_bytes,
        }
        return manifest_digest, blobs

    def test_rewrite_drops_other_platform_from_nested_index(self):
        # nginx:1.27's linux/386 manifest. docker save lists it inside the
        # image index and does not save the blob.
        missing = (
            "sha256:2c1ee2371c776670cebad7f4fee298ed8979fdfc18d2c1bc49f17c35754259f2"
        )
        manifest_digest, blobs = self._amd64_image()
        image_index = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.index.v1+json",
            "manifests": [
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": manifest_digest,
                    "size": len(blobs[manifest_digest.split(":", 1)[1]]),
                    "platform": {"architecture": "amd64", "os": "linux"},
                },
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": missing,
                    "size": 100,
                    "platform": {"architecture": "386", "os": "linux"},
                },
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": "sha256:" + "ab" * 32,
                    "size": 50,
                    "platform": {"architecture": "unknown", "os": "unknown"},
                    "annotations": {
                        "vnd.docker.reference.type": "attestation-manifest"
                    },
                },
            ],
        }
        index_bytes = json.dumps(image_index).encode()
        index_digest = "sha256:" + hashlib.sha256(index_bytes).hexdigest()
        blobs[index_digest.split(":", 1)[1]] = index_bytes
        index = {
            "schemaVersion": 2,
            "manifests": [
                {
                    "mediaType": "application/vnd.oci.image.index.v1+json",
                    "digest": index_digest,
                    "size": len(index_bytes),
                    "annotations": {
                        "org.opencontainers.image.ref.name": "nginx:1.27"
                    },
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "image.tar"
            dst = Path(tmp) / "slim.tar"
            self._oci_tar(src, index, blobs)
            rewrite_image_archive(src, dst, "amd64", "nginx:1.27")
            with tarfile.open(dst, "r") as tf:
                rewritten = json.load(tf.extractfile("index.json"))
                names = tf.getnames()
            self.assertEqual(len(rewritten["manifests"]), 1)
            self.assertEqual(rewritten["manifests"][0]["digest"], manifest_digest)
            self.assertNotIn(missing, json.dumps(rewritten))
            self.assertNotIn(
                "blobs/sha256/" + missing.split(":", 1)[1],
                names,
            )
            self.assertNotIn(
                "blobs/sha256/" + index_digest.split(":", 1)[1],
                names,
            )
            self.assertEqual(
                rewritten["manifests"][0]["annotations"]["io.containerd.image.name"],
                "docker.io/library/nginx:1.27",
            )

    def test_rewrite_drops_saved_attestation_without_platform(self):
        manifest_digest, blobs = self._amd64_image()
        statement = b'{"payloadType":"application/vnd.in-toto+json"}'
        statement_digest = "sha256:" + hashlib.sha256(statement).hexdigest()
        empty = b"{}"
        attestation = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
                "size": len(empty),
            },
            "layers": [
                {
                    "mediaType": "application/vnd.in-toto+json",
                    "digest": statement_digest,
                    "size": len(statement),
                }
            ],
        }
        attestation_bytes = json.dumps(attestation).encode()
        attestation_digest = "sha256:" + hashlib.sha256(attestation_bytes).hexdigest()
        blobs[statement_digest.split(":", 1)[1]] = statement
        blobs[attestation_digest.split(":", 1)[1]] = attestation_bytes
        # The empty config blob is not stored; the attestation is still rejected
        # by its in-toto layer before that blob is required.
        index = {
            "schemaVersion": 2,
            "manifests": [
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": manifest_digest,
                    "size": len(blobs[manifest_digest.split(":", 1)[1]]),
                    "platform": {"architecture": "amd64", "os": "linux"},
                },
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": attestation_digest,
                    "size": len(attestation_bytes),
                    "annotations": {
                        "vnd.docker.reference.digest": manifest_digest,
                    },
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "image.tar"
            dst = Path(tmp) / "slim.tar"
            self._oci_tar(src, index, blobs)
            rewrite_image_archive(src, dst, "amd64", "nginx:1.27")
            with tarfile.open(dst, "r") as tf:
                rewritten = json.load(tf.extractfile("index.json"))
            self.assertEqual(
                [item["digest"] for item in rewritten["manifests"]],
                [manifest_digest],
            )

    def test_rewrite_refuses_a_different_architecture(self):
        config = b'{"architecture":"386","os":"linux"}'
        layer = b"rootfs"
        config_digest = "sha256:" + hashlib.sha256(config).hexdigest()
        layer_digest = "sha256:" + hashlib.sha256(layer).hexdigest()
        manifest = {
            "schemaVersion": 2,
            "mediaType": "application/vnd.oci.image.manifest.v1+json",
            "config": {
                "mediaType": "application/vnd.oci.image.config.v1+json",
                "digest": config_digest,
                "size": len(config),
            },
            "layers": [
                {
                    "mediaType": "application/vnd.oci.image.layer.v1.tar",
                    "digest": layer_digest,
                    "size": len(layer),
                }
            ],
        }
        manifest_bytes = json.dumps(manifest).encode()
        manifest_digest = "sha256:" + hashlib.sha256(manifest_bytes).hexdigest()
        blobs = {
            config_digest.split(":", 1)[1]: config,
            layer_digest.split(":", 1)[1]: layer,
            manifest_digest.split(":", 1)[1]: manifest_bytes,
        }
        index = {
            "schemaVersion": 2,
            "manifests": [
                {
                    "mediaType": "application/vnd.oci.image.manifest.v1+json",
                    "digest": manifest_digest,
                    "size": len(manifest_bytes),
                    "platform": {"architecture": "386", "os": "linux"},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "image.tar"
            dst = Path(tmp) / "slim.tar"
            self._oci_tar(src, index, blobs)
            with self.assertRaises(RuntimeError):
                rewrite_image_archive(src, dst, "amd64", "nginx:1.27")

    def test_classic_archive_without_index_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "classic.tar"
            dst = Path(tmp) / "out.tar"
            payload = b"not-an-oci-index"
            with tarfile.open(src, "w") as tf:
                info = tarfile.TarInfo("manifest.json")
                info.size = len(payload)
                tf.addfile(info, io.BytesIO(payload))
            rewrite_image_archive(src, dst, "amd64", "nginx:1.27")
            self.assertEqual(src.read_bytes(), dst.read_bytes())

    def test_local_image_check_matches_kind(self):
        cmd = image_inspect_cmd("docker.io/calico/node:v3.28.2")
        self.assertEqual(
            cmd,
            ["docker", "inspect", "--type=image", "docker.io/calico/node:v3.28.2"],
        )
        self.assertNotIn("image", cmd[1:2])

    def test_images_to_load_skips_anything_not_on_the_host(self):
        present = {"nginx:1.27", "busybox:1.36", "kindest/node:v1.31.4"}
        loaded = images_to_load(present)
        self.assertEqual(loaded, ["nginx:1.27", "busybox:1.36"])

    def test_ingress_digest_pin_strips_to_the_cached_tag(self):
        pinned = (
            "image: registry.k8s.io/ingress-nginx/controller:v1.11.3"
            "@sha256:d56f135b6462cfc476447cfe564b83a45e8bb7da2774963b00d12161112270b7"
        )
        self.assertEqual(
            strip_image_digests(pinned),
            "image: registry.k8s.io/ingress-nginx/controller:v1.11.3",
        )
        self.assertEqual(
            strip_image_digests("image: docker.io/calico/node:v3.28.2"),
            "image: docker.io/calico/node:v3.28.2",
        )
