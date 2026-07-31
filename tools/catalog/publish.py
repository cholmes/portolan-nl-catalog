#!/usr/bin/env python3
"""Metadata-only publisher for the Portolan NL catalog.

Reads catalog.publish.yaml and syncs everything under the configured publish_dir
(the catalog/ tree) 1:1 to S3, skipping only Portolan's internal bookkeeping (see
_is_portolan_internal). Never uploads data (*.parquet/*.pmtiles/*.gpkg/*.tif),
tools/, staging/, or config.

Objects whose bytes already match S3 are skipped. The remote side is read by listing
each directory the catalog occupies non-recursively (concurrently), and a local file
is considered unchanged when its size and MD5 match the object's size and ETag.

Caveat: a listing carries no ContentType, so a file whose bytes are unchanged but
whose content-type mapping changed is skipped. Use --force after editing
_content_type() to rewrite every object.

Usage:
  python3 tools/catalog/publish.py            # dry run (prints planned uploads)
  python3 tools/catalog/publish.py --confirm  # execute aws s3 cp
  python3 tools/catalog/publish.py --force --confirm   # re-upload even if unchanged
"""
from __future__ import annotations
import argparse
import concurrent.futures as cf
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_CT_BY_NAME = {"catalog.json": "application/json", "collection.json": "application/json",
               "versions.json": "application/json"}
_CT_BY_SUFFIX = {
    ".json": "application/geo+json",  # items; catalog/collection overridden by name
    ".md": "text/markdown; charset=utf-8",
    ".txt": "text/markdown; charset=utf-8",  # llms.txt
    ".png": "image/png",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".yaml": "text/yaml; charset=utf-8",
    ".yml": "text/yaml; charset=utf-8",
}


@dataclass(frozen=True)
class Upload:
    local: Path
    s3_uri: str
    content_type: str


def _content_type(p: Path) -> str:
    if p.name in _CT_BY_NAME:
        return _CT_BY_NAME[p.name]
    if p.name.endswith(".style.json") or (p.suffix == ".json" and "styles" in p.parts):
        return "application/json"  # MapLibre styles, not STAC/GeoJSON
    return _CT_BY_SUFFIX.get(p.suffix, "application/octet-stream")


def _is_portolan_internal(rel: str) -> bool:
    """True for Portolan's own bookkeeping, which is never published.

    Everything under any .portolan/ directory is internal, with one exception:
    the catalog root's .portolan/metadata.yaml is the hand-authored catalog
    description and does belong in the published tree. Collection-level
    .portolan/ dirs (config.yaml, metadata.yaml, extraction-report.json) are
    tooling state and stay local.
    """
    if ".portolan" not in rel.split("/"):
        return False
    return rel != ".portolan/metadata.yaml"


def collect_uploads(manifest: dict, root: Path) -> list[Upload]:
    write_prefix = manifest["write_prefix"].rstrip("/")
    pub_dir = root / manifest.get("publish_dir", "catalog")

    uploads = []
    if not pub_dir.is_dir():
        return uploads
    for p in sorted(pub_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(pub_dir).as_posix()
        if _is_portolan_internal(rel):
            continue
        uploads.append(Upload(local=p, s3_uri=f"{write_prefix}/{rel}",
                              content_type=_content_type(p)))
    return uploads


def split_s3_uri(uri: str) -> tuple[str, str]:
    """"s3://bucket/a/b" -> ("bucket", "a/b")."""
    rest = uri[len("s3://"):] if uri.startswith("s3://") else uri
    bucket, _, key = rest.partition("/")
    return bucket, key.strip("/")


def _md5_hex(p: Path) -> str:
    """MD5 of a file, to compare against an S3 ETag (not used for security)."""
    h = hashlib.md5()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def key_dirs(uploads: list[Upload]) -> list[str]:
    """The distinct S3 "directory" prefixes the uploads live in, each ending in /."""
    return sorted({split_s3_uri(u.s3_uri)[1].rsplit("/", 1)[0] + "/" for u in uploads})


def _list_dir(bucket: str, prefix: str, region: str) -> list:
    """One non-recursive listing: the objects directly under prefix."""
    out = subprocess.run(
        ["aws", "s3api", "list-objects-v2", "--bucket", bucket, "--prefix", prefix,
         "--delimiter", "/", "--region", region, "--output", "json",
         "--query", "Contents[].[Key,ETag,Size]"],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out) or []


def remote_index(uploads: list[Upload], write_prefix: str, region: str,
                 workers: int = 16) -> dict[str, tuple[str, int]]:
    """Map S3 key -> (etag, size) for objects already published.

    Lists each directory the catalog occupies *non-recursively* (--delimiter /),
    concurrently. Listing write_prefix recursively instead would walk every data
    object sharing it -- the zarr chunks and COGs alone are ~650k keys, minutes of
    pagination -- when only a couple thousand metadata objects are ever published.

    Returns {} if listing fails, so a dry run still works without credentials;
    every file then simply looks new, which errs toward uploading.
    """
    bucket, _ = split_s3_uri(write_prefix)
    dirs = key_dirs(uploads)
    index: dict[str, tuple[str, int]] = {}
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_list_dir, bucket, d, region): d for d in dirs}
        for fut in cf.as_completed(futures):
            try:
                rows = fut.result()
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                detail = (getattr(e, "stderr", "") or str(e)).strip()
                print(f"warning: could not list s3://{bucket}/{futures[fut]} ({detail}); "
                      "treating every file as changed", file=sys.stderr)
                return {}
            for key, etag, size in rows:
                index[key] = (etag.strip('"'), int(size))
    return index


def is_unchanged(u: Upload, remote: dict[str, tuple[str, int]]) -> bool:
    """True when S3 already holds these exact bytes."""
    entry = remote.get(split_s3_uri(u.s3_uri)[1])
    if entry is None:
        return False
    etag, size = entry
    etag = etag.strip('"')  # S3 quotes ETags; tolerate either form
    if "-" in etag:  # multipart ETag is not a plain MD5; re-upload to be safe
        return False
    return size == u.local.stat().st_size and etag == _md5_hex(u.local)


def _load_manifest(root: Path) -> dict:
    text = (root / "catalog.publish.yaml").read_text()
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ModuleNotFoundError:
        pass
    # Minimal YAML fallback (flat scalars + simple "- item" lists) so the
    # publisher has zero third-party dependencies.
    data: dict = {}
    key = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            item = line.lstrip()[2:].strip().strip('"')
            data.setdefault(key, []).append(item)
        elif ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            key = k.strip()
            v = v.strip()
            data[key] = json.loads(v) if v.startswith("[") else (v.strip('"') if v else [])
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--confirm", action="store_true", help="execute uploads (default: dry run)")
    ap.add_argument("--force", action="store_true",
                    help="upload every file, even if S3 already has identical bytes")
    args = ap.parse_args(argv)

    root = Path(__file__).resolve().parents[2]
    manifest = _load_manifest(root)
    region = manifest.get("region", "us-west-2")
    uploads = collect_uploads(manifest, root)

    if not uploads:
        print("No files to publish (check publish_dir in catalog.publish.yaml).")
        return 0

    remote = {} if args.force else remote_index(uploads, manifest["write_prefix"], region)
    planned = [u for u in uploads if not is_unchanged(u, remote)]
    skipped = len(uploads) - len(planned)

    for u in planned:
        if args.confirm:
            print(f"upload: {u.local.relative_to(root)} -> {u.s3_uri}")
            subprocess.run(
                ["aws", "s3", "cp", str(u.local), u.s3_uri,
                 "--region", region, "--content-type", u.content_type],
                check=True,
            )
        else:
            print(f"DRYRUN {u.s3_uri}  ({u.content_type})")

    tally = f"{len(planned)} to upload, {skipped} unchanged (skipped), {len(uploads)} total"
    if args.confirm:
        print(f"\nDone: {tally}.")
    elif planned:
        print(f"\n{tally}. Re-run with --confirm to upload.")
    else:
        print(f"\nNothing to do: {tally}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
