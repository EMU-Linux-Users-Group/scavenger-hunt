"""
Builds the release download for classroom computers.\n
The download bundles its own Python (from python-build-standalone, the builds
`uv` uses), so the computer doesn't need Python installed and nobody needs an
admin password to set it up.\n
Usage: `python3 tools/build_release.py [macos|linux]` (default: macos)
"""

from __future__ import annotations

import hashlib
import io
from pathlib import Path
import sys
import tarfile
import time
import urllib.request

PYTHON_RELEASE = "20261009"
PYTHON_VERSION = "3.12.15"
PYTHON_URL = ("https://github.com/astral-sh/python-build-standalone/releases/download/"
              f"{PYTHON_RELEASE}/")
# What `uname -m` prints on each kind of computer, and the Python build it needs
TARGETS = {
    "macos": {"arm64": "aarch64-apple-darwin", "x86_64": "x86_64-apple-darwin"},
    "linux": {"x86_64": "x86_64-unknown-linux-gnu"},
}

REPO_DIR = Path(__file__).resolve().parent.parent
APP_FILES = ("scavenger_hunt.py", "monitor.pyw", "folder_structure.readyplayerroot.json",
             "hint_structure.readyplayerroot.json", "README.md")
LAUNCHER = REPO_DIR / "tools" / "ready-player-root"
TOP = "ready-player-root"


def _download(url: str) -> bytes:
    """Returns the contents of `url`"""

    with urllib.request.urlopen(url) as response:
        return response.read()


def _python_build(target: str, checksums: dict[str, str]) -> bytes:
    """Downloads the Python build for `target` and checks it against `checksums`"""

    name = f"cpython-{PYTHON_VERSION}+{PYTHON_RELEASE}-{target}-install_only_stripped.tar.gz"
    data = _download(PYTHON_URL + name)
    if hashlib.sha256(data).hexdigest() != checksums[name]:
        raise SystemExit(f"{name} does not match its published checksum")
    return data


def _add(archive: tarfile.TarFile, name: str, data: bytes | None = None, mode: int = 0o644):
    """Adds a folder (when `data` is `None`) or a file to `archive`"""

    info = tarfile.TarInfo(f"{TOP}/{name}" if name else TOP)
    info.mtime = int(time.time())
    if data is None:
        info.type, info.mode = tarfile.DIRTYPE, 0o755
        archive.addfile(info)
    else:
        info.size, info.mode = len(data), mode
        archive.addfile(info, io.BytesIO(data))


def build(platform: str) -> Path:
    """Writes `dist/ready-player-root-<platform>.tar.gz` and returns its path"""

    checksums = {}
    for line in _download(PYTHON_URL + "SHA256SUMS").decode().splitlines():
        digest, name = line.split()
        checksums[name] = digest

    output = REPO_DIR / "dist" / f"ready-player-root-{platform}.tar.gz"
    output.parent.mkdir(exist_ok=True)
    with tarfile.open(output, "w:gz") as archive:
        _add(archive, "")
        _add(archive, "python")
        for arch, target in TARGETS[platform].items():
            prefix = f"{TOP}/python/{arch}"
            with tarfile.open(fileobj=io.BytesIO(_python_build(target, checksums))) as python:
                for member in python:
                    # Each build unpacks into `python/`, so move it to `python/<arch>/`
                    member.name = prefix + member.name[len("python"):]
                    if member.islnk():
                        member.linkname = prefix + member.linkname[len("python"):]
                    # Every Mac account is in the `staff` group, so only the owner may change it
                    member.mode &= ~0o022
                    member.uid = member.gid = 0
                    member.uname = member.gname = ""
                    archive.addfile(member, python.extractfile(member) if member.isfile() else None)
        for name in APP_FILES:
            _add(archive, name, (REPO_DIR / name).read_bytes())
        _add(archive, LAUNCHER.name, LAUNCHER.read_bytes(), 0o755)
    return output


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "macos"))
