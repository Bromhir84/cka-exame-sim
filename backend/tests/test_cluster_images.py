"""Cluster image cache: install pulls once, kind load reuses them."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.cluster_images import (  # noqa: E402
    CACHED_IMAGES,
    CALICO_VERSION,
    image_inspect_cmd,
    images_to_load,
    pull_plan,
    strip_image_digests,
)
from app.config import KIND_IMAGE  # noqa: E402


class ClusterImageCacheTests(unittest.TestCase):
    def test_pull_plan_includes_node_image_and_digest_pins(self):
        plan = pull_plan()
        refs = [item.ref for item in plan]
        self.assertEqual(refs[0], KIND_IMAGE)
        self.assertNotIn(KIND_IMAGE, [image.name for image in CACHED_IMAGES])

        by_tag = {item.tag_as: item.ref for item in plan if item.tag_as}
        controller = "registry.k8s.io/ingress-nginx/controller:v1.11.3"
        certgen = "registry.k8s.io/ingress-nginx/kube-webhook-certgen:v1.4.4"
        self.assertTrue(by_tag[controller].startswith(controller + "@sha256:"))
        self.assertTrue(by_tag[certgen].startswith(certgen + "@sha256:"))

    def test_cached_set_matches_cluster_manifests_and_task_images(self):
        names = {image.name for image in CACHED_IMAGES}
        self.assertIn(f"docker.io/calico/node:{CALICO_VERSION}", names)
        self.assertIn(f"docker.io/calico/cni:{CALICO_VERSION}", names)
        self.assertIn(f"docker.io/calico/kube-controllers:{CALICO_VERSION}", names)
        self.assertIn("nginx:1.27", names)
        self.assertIn("busybox:1.36", names)
        # These tags are supposed to fail image pull in troubleshooting tasks.
        self.assertNotIn("nginx:1.27-notreal", names)
        self.assertNotIn("nginx:1.27-this-tag-does-not-exist", names)

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
