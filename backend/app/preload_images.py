"""Pull cluster images onto the Docker host. Used by the installers.

Run inside the backend container (it shares the host Docker socket):

    python -m app.preload_images
"""

from __future__ import annotations

from .cluster_images import pull_images


def main() -> int:
    return pull_images()


if __name__ == "__main__":
    raise SystemExit(main())
