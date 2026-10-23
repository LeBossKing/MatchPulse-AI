"""Export the contract from Pydantic and FastAPI; no server or Azure is needed."""

import argparse
import json
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402
from app.models.event import MatchEvent  # noqa: E402
from app.models.insight import ProcessEventRequest, ProcessEventResponse  # noqa: E402
from app.models.match import DemoFixture  # noqa: E402


def contract_documents() -> dict[Path, dict]:
    models = {
        "event": MatchEvent,
        "demo-fixture": DemoFixture,
        "process-request": ProcessEventRequest,
        "process-response": ProcessEventResponse,
    }
    documents = {ROOT / "docs" / "openapi.json": app.openapi()}
    for name, model in models.items():
        documents[ROOT / "docs" / "schemas" / f"{name}.schema.json"] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            **model.model_json_schema(
                mode="serialization" if model is ProcessEventResponse else "validation"
            ),
        }
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if exported schemas are stale.")
    args = parser.parse_args()
    stale = []
    for path, document in contract_documents().items():
        content = json.dumps(document, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"Exported {path.relative_to(ROOT)}")
    if stale:
        parser.exit(1, "Stale contracts: " + ", ".join(stale) + "\n")
    if args.check:
        print("OpenAPI and JSON Schemas match the backend models.")


if __name__ == "__main__":
    main()
