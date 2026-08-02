#!/usr/bin/env python3
"""Download Qwen2.5-14B-Instruct to local data disk with resume + manifest."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

# Prefer mirror + disable xet for AutoDL-like environments.
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from huggingface_hub import snapshot_download


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-id", default="Qwen/Qwen2.5-14B-Instruct")
    parser.add_argument(
        "--local-dir",
        default="/root/autodl-tmp/time-series-agent/models/Qwen2.5-14B-Instruct",
    )
    args = parser.parse_args()
    local_dir = Path(args.local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {args.repo_id} -> {local_dir}", flush=True)
    print(f"HF_ENDPOINT={os.environ.get('HF_ENDPOINT')}", flush=True)
    path = snapshot_download(repo_id=args.repo_id, local_dir=str(local_dir))
    files = []
    for root, _, fs in os.walk(path):
        for f in fs:
            fp = os.path.join(root, f)
            files.append({"path": os.path.relpath(fp, path), "size": os.path.getsize(fp)})
    required = ["config.json", "tokenizer.json"]
    missing = [r for r in required if not (Path(path) / r).exists()]
    weight_ok = any(x["path"].endswith(".safetensors") or "pytorch_model" in x["path"] for x in files)
    manifest = {
        "repo_id": args.repo_id,
        "local_dir": path,
        "hf_endpoint": os.environ.get("HF_ENDPOINT"),
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_files": len(files),
        "total_bytes": sum(x["size"] for x in files),
        "missing_required": missing,
        "has_weights": weight_ok,
        "files": files,
    }
    manifest_path = Path(str(local_dir) + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in manifest if k != "files"}, indent=2))
    if missing or not weight_ok:
        raise SystemExit("Model download incomplete")
    print("Model download validated.")


if __name__ == "__main__":
    main()
