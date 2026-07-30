#!/usr/bin/env python3
"""Low-memory sequential download of Qwen2.5-14B-Instruct via HF mirror + wget/curl."""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path

REPO = "Qwen/Qwen2.5-14B-Instruct"
ENDPOINT = os.environ.get("HF_ENDPOINT", "https://hf-mirror.com")
LOCAL = Path("/root/autodl-tmp/time-series-agent/models/Qwen2.5-14B-Instruct")


def list_files() -> list[str]:
    url = f"{ENDPOINT}/api/models/{REPO}/tree/main"
    req = urllib.request.Request(url, headers={"User-Agent": "ts-agent/0.1"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    files = []
    for item in data:
        if item.get("type") == "file":
            files.append(item["path"])
    return files


def download_one(rel: str) -> None:
    LOCAL.mkdir(parents=True, exist_ok=True)
    dest = LOCAL / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{ENDPOINT}/{REPO}/resolve/main/{rel}"
    # Prefer fresh download for small files; resume for large ones.
    cmd = ["curl", "-L", "--fail", "--retry", "5", "--retry-delay", "2", "-o", str(dest), url]
    if dest.exists() and dest.stat().st_size > 10_000_000:
        cmd = ["curl", "-L", "--retry", "5", "--retry-delay", "2", "-C", "-", "-o", str(dest), url]
    print(f"Downloading {rel} ...", flush=True)
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        # If resume got HTTP 416 (already complete), keep existing file.
        if dest.exists() and dest.stat().st_size > 0:
            print(f"Keep existing {rel} ({dest.stat().st_size} bytes)", flush=True)
            return
        raise


def main():
    print(f"Endpoint={ENDPOINT}", flush=True)
    files = list_files()
    print(f"Found {len(files)} files", flush=True)
    for rel in files:
        download_one(rel)
    files_meta = []
    for p in LOCAL.rglob("*"):
        if p.is_file() and ".cache" not in p.parts:
            files_meta.append({"path": str(p.relative_to(LOCAL)), "size": p.stat().st_size})
    manifest = {
        "repo_id": REPO,
        "local_dir": str(LOCAL),
        "hf_endpoint": ENDPOINT,
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_files": len(files_meta),
        "total_bytes": sum(x["size"] for x in files_meta),
        "has_weights": any(x["path"].endswith(".safetensors") for x in files_meta),
        "files": files_meta,
    }
    Path(str(LOCAL) + ".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in manifest if k != "files"}, indent=2))
    if not manifest["has_weights"]:
        raise SystemExit("Download incomplete: no safetensors")
    print("Model download validated.")


if __name__ == "__main__":
    main()
