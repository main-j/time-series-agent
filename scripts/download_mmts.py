#!/usr/bin/env python3
"""Download MMTS-Bench anonymous repository archive with checksum manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

DEFAULT_URL = "https://anonymous.4open.science/api/repo/MMTS-BENCH-BEF7/zip"


def download(url: str, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "ts-agent-downloader/0.1"})
    with urlopen(req, timeout=120) as resp, zip_path.open("wb") as f:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument(
        "--out-dir",
        default="/root/autodl-tmp/time-series-agent/data/raw/mmts-bench",
    )
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir.parent / "MMTS-BENCH-BEF7.zip"
    print(f"Downloading {args.url} -> {zip_path}", flush=True)
    download(args.url, zip_path)
    digest = sha256_file(zip_path)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)
    files = []
    for p in out_dir.rglob("*"):
        if p.is_file():
            files.append({"path": str(p.relative_to(out_dir)), "size": p.stat().st_size})
    manifest = {
        "source_url": args.url,
        "zip_path": str(zip_path),
        "zip_sha256": digest,
        "out_dir": str(out_dir),
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_files": len(files),
        "total_bytes": sum(x["size"] for x in files),
        "has_benchmark": (out_dir / "Benchmark").exists(),
        "files": files,
    }
    (out_dir / "download_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in manifest if k != "files"}, indent=2))
    if not manifest["has_benchmark"]:
        raise SystemExit("MMTS-Bench download incomplete: Benchmark/ missing")
    # Zip is only needed for extract; remove to avoid duplicate disk use.
    try:
        zip_path.unlink(missing_ok=True)
        print(f"Removed archive {zip_path}")
    except OSError as e:
        print(f"Warning: could not remove archive {zip_path}: {e}")
    print("MMTS-Bench download validated.")


if __name__ == "__main__":
    main()
