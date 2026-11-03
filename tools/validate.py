#!/usr/bin/env python3
"""Checks the templates exactly like MPVPN does before it installs them.

MPVPN rejects the whole repository if one file is invalid (it keeps the
version it has), so a broken commit here never reaches a router – but it
also stops every update until it is fixed. Run before pushing:

    python3 tools/validate.py
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MAX_TEMPLATES, MAX_SERVICES, MAX_PATTERNS, MAX_FILE = 100, 2000, 20000, 512 << 10
VALID_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
VALID_FILE = re.compile(r"^templates/[a-z0-9][a-z0-9-]{0,40}\.yaml$")
LABEL = re.compile(r"^[a-z0-9*_-]+$")


def pattern_error(p):
    q = p.strip().lower().rstrip(".")
    if not q:
        return "empty domain"
    if any(c in q for c in "/: "):
        return "domain only, no URL, port or spaces (e.g. **.netflix.com)"
    for pre in ("**.", "*."):
        if q.startswith(pre):
            q = q[len(pre):]
            break
    labels = q.split(".")
    if len(labels) < 2:
        return "needs at least a name and a top-level domain"
    for l in labels:
        if not l or not LABEL.match(l) or (l == "*" and len(labels) == 2):
            return f"invalid label {l!r}"
    if "*" in labels[-1]:
        return "no wildcard in the top-level domain"
    return None


def main():
    errors = []
    idx = yaml.safe_load((ROOT / "index.yaml").read_text())
    files = idx.get("templates") or []
    if not idx.get("version"):
        errors.append("index.yaml: version missing")
    if not 1 <= len(files) <= MAX_TEMPLATES:
        errors.append(f"index.yaml: {len(files)} templates (1..{MAX_TEMPLATES})")
    listed = set(files)
    for f in sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "templates").glob("*.yaml")):
        if f not in listed:
            errors.append(f"{f}: not listed in index.yaml (MPVPN would ignore it)")
    seen, services, patterns = set(), 0, 0
    for f in files:
        if not VALID_FILE.match(f):
            errors.append(f"index.yaml: bad path {f!r} (want templates/<id>.yaml)")
            continue
        path = ROOT / f
        if not path.exists():
            errors.append(f"{f}: missing")
            continue
        if path.stat().st_size > MAX_FILE:
            errors.append(f"{f}: larger than {MAX_FILE} bytes")
        t = yaml.safe_load(path.read_text()) or {}
        tid = t.get("id", "")
        if not VALID_ID.match(str(tid)) or f"templates/{tid}.yaml" != f:
            errors.append(f"{f}: id {tid!r} must be lower-case a-z0-9- and match the file name")
        if tid in seen:
            errors.append(f"{f}: duplicate template id")
        seen.add(tid)
        name = t.get("name") or {}
        if not (name.get("de") or name.get("en")):
            errors.append(f"{f}: name missing")
        if not -100 <= int(t.get("priority", 0)) <= 100:
            errors.append(f"{f}: priority out of -100..100")
        svs = t.get("services") or []
        if not svs:
            errors.append(f"{f}: no services")
        ids = set()
        for sv in svs:
            sid = str(sv.get("id", ""))
            if not VALID_ID.match(sid) or sid in ids:
                errors.append(f"{f}: service id {sid!r} invalid or duplicate")
            ids.add(sid)
            if not str(sv.get("name", "")).strip() or len(str(sv.get("name"))) > 80:
                errors.append(f"{f}: service {sid}: name missing or too long")
            doms = sv.get("domains") or []
            if not doms:
                errors.append(f"{f}: service {sid}: no domains")
            dd = set()
            for d in doms:
                d = str(d).strip().lower()
                e = pattern_error(d)
                if e:
                    errors.append(f"{f}: service {sid}: {d!r}: {e}")
                if d in dd:
                    errors.append(f"{f}: service {sid}: duplicate {d!r}")
                dd.add(d)
            services += 1
            patterns += len(doms)
    if services > MAX_SERVICES or patterns > MAX_PATTERNS:
        errors.append(f"too large: {services} services, {patterns} patterns")
    for e in errors:
        print("ERROR", e)
    print(f"{len(files)} templates, {services} services, {patterns} patterns: " + ("FAILED" if errors else "ok"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
