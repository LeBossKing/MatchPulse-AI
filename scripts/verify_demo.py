"""Run Task 8 checks using local dependencies, without live Azure requests."""

from pathlib import Path
import os
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    backend = ROOT / "backend"
    frontend = ROOT / "frontend"
    python = backend / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not python.is_file():
        print("Create backend/.venv and install backend/requirements-dev.txt first.", file=sys.stderr)
        return 1
    if not npm or not (frontend / "node_modules").is_dir():
        print("Install Node and run npm ci in frontend/ first.", file=sys.stderr)
        return 1

    environment = os.environ | {
        "APP_ENV": "test",
        "LLM_PROVIDER": "mock",
        "AZURE_OPENAI_ENDPOINT": "",
        "AZURE_OPENAI_DEPLOYMENT": "",
        "AZURE_OPENAI_API_KEY": "",
        "AZURE_OPENAI_TIMEOUT_SECONDS": "15",
        "AZURE_OPENAI_MAX_OUTPUT_TOKENS": "2048",
        "FRONTEND_ORIGIN": "http://localhost:5173",
        "MATCHPULSE_RUN_API_TESTS": "1",
    }
    checks = [
        ("Backend tests", backend, [str(python), "-m", "pytest", "-q"]),
        ("OpenAPI and browser schema consistency", backend, [str(python), "scripts/export_contract.py", "--check"]),
        ("Dashboard sample consistency", backend, [str(python), "scripts/export_dashboard_samples.py", "--check"]),
        ("Frontend and real HTTP demo tests", frontend, [npm, "run", "test"]),
        ("Frontend lint", frontend, [npm, "run", "lint"]),
        ("Production build", frontend, [npm, "run", "build"]),
    ]
    for index, (name, directory, command) in enumerate(checks, 1):
        print(f"\n[{index}/{len(checks)}] {name}", flush=True)
        try:
            result = subprocess.run(command, cwd=directory, env=environment, check=False)
        except OSError as error:
            print(f"Could not start {name}: {error}", file=sys.stderr)
            return 1
        if result.returncode:
            print(f"\nFAILED: {name}. Fix this check before continuing.", file=sys.stderr)
            return 1
    print("\nPASS: all automated Task 8 checks. Complete the manual demo checklist in docs/testing.md.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
