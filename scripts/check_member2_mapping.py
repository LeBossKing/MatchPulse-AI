"""Check research integrity and coverage references; does not execute source cases."""

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "research/member2"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def inside_root(base: Path, relative: str) -> Path:
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), f"Path leaves its root: {relative}")
    return path


def check() -> Counter:
    source = json.loads((RESEARCH / "validation/ai_test_cases.json").read_text(encoding="utf-8"))
    mapping = json.loads((ROOT / "docs/member2-rule-mapping.json").read_text(encoding="utf-8"))
    source_ids = [item["test_id"] for item in source["cases"]]
    mapped_ids = [item["test_id"] for item in mapping["cases"]]
    require(len(set(source_ids)) == len(source_ids), "Duplicate source test IDs.")
    require(len(set(mapped_ids)) == len(mapped_ids), "Duplicate mapped test IDs.")
    require(set(mapped_ids) == set(source_ids), "Coverage map must account for every source case exactly once.")
    statuses = Counter()
    for item in mapping["cases"]:
        status = item["status"]
        require(status in {"adapted_mvp", "deferred_source_integration"}, f"Unsupported status: {status}")
        require(bool(item["scope_note"]), f"Missing scope note for {item['test_id']}")
        statuses[status] += 1
        if status == "deferred_source_integration":
            require(not item["coverage"], f"Deferred case has ambiguous execution claims: {item['test_id']}")
            continue
        require(bool(item["coverage"]), f"No coverage target for {item['test_id']}")
        for reference in item["coverage"]:
            relative, selector = reference.split("::", 1)
            path = inside_root(ROOT, relative)
            require(path.is_file(), f"Missing coverage file: {relative}")
            text = path.read_text(encoding="utf-8")
            if path.suffix == ".py":
                functions = {node.name for node in ast.parse(text).body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
                require(selector.startswith("test_") and selector in functions, f"Missing pytest target: {reference}")
            else:
                require(path.suffix in {".ts", ".tsx"} and selector in text, f"Missing frontend test reference: {reference}")
    manifest = json.loads((RESEARCH / "MANIFEST.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = inside_root(RESEARCH, entry["path"])
        content = path.read_bytes()
        require(len(content) == entry["bytes"], f"Changed handoff size: {entry['path']}")
        require(hashlib.sha256(content).hexdigest() == entry["sha256"], f"Changed handoff hash: {entry['path']}")
    print(f"Member 2 coverage map: {len(mapped_ids)} cases; "
          f"{statuses['adapted_mvp']} adapted MVP controls; "
          f"{statuses['deferred_source_integration']} deferred source cases.")
    print(f"Coverage references exist; all {len(manifest['files'])} original manifest entries match.")
    print("This validates the scope map and references, not execution of the original StatsBomb specifications.")
    return statuses


def main() -> int:
    try:
        check()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Member 2 coverage check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
