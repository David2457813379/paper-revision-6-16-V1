"""Execute the four research notebooks as an optional reproducibility check.

This script is intentionally outside the main notebook pipeline. It sets
environment variables for quick validation when requested, executes notebooks in
the same 01 -> 02 -> 03 -> 04 order, and writes a plain-text log under
archive/validation/. It does not overwrite the notebook files.
"""

from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime
from pathlib import Path
from time import perf_counter

import nbformat
from nbclient import NotebookClient


NOTEBOOKS = [
    "01_Parametric_Simulation_Database_Construction.ipynb",
    "02_SRC_Sensitivity_and_Variable_Selection.ipynb",
    "03_ML_Model_Training_and_Evaluation.ipynb",
    "04_EUI_OCEI_Coupling_and_Carbon_Analysis.ipynb",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the four EUI-OCEI notebooks in order for validation."
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Use a small deterministic sample and skip EnergyPlus for code validation.",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=200,
        help="Sample count used with --fast. Default: 200.",
    )
    parser.add_argument(
        "--run-energyplus",
        action="store_true",
        help="Allow EnergyPlus execution. By default, --fast disables it.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Per-notebook timeout in seconds. Default: 1800.",
    )
    return parser.parse_args()


def configure_environment(args: argparse.Namespace) -> dict[str, str]:
    env_updates: dict[str, str] = {}
    if args.fast:
        env_updates["EUI_FAST_MODE"] = "1"
        env_updates["EUI_N_SAMPLES"] = str(args.samples)
        env_updates["EUI_RUN_ENERGYPLUS"] = "1" if args.run_energyplus else "0"
    elif args.run_energyplus:
        env_updates["EUI_RUN_ENERGYPLUS"] = "1"

    os.environ.update(env_updates)
    return env_updates


def log_line(handle, message: str) -> None:
    print(message)
    handle.write(message + "\n")
    handle.flush()


def main() -> int:
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    notebook_dir = project_root / "experiment_code" / "notebooks"
    log_dir = project_root / "archive" / "validation"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"validation_{datetime.now():%Y-%m-%d_%H%M%S}.log"

    env_updates = configure_environment(args)

    with log_path.open("w", encoding="utf-8") as log:
        log_line(log, "Notebook validation started")
        log_line(log, f"Project root: {project_root}")
        log_line(log, f"Notebook directory: {notebook_dir}")
        log_line(log, f"Environment overrides: {env_updates or 'none'}")

        total_start = perf_counter()
        for notebook_name in NOTEBOOKS:
            notebook_path = notebook_dir / notebook_name
            if not notebook_path.exists():
                log_line(log, f"FAIL missing notebook: {notebook_path}")
                return 1

            log_line(log, f"RUN {notebook_name}")
            start = perf_counter()
            try:
                nb = nbformat.read(notebook_path, as_version=4)
                client = NotebookClient(
                    nb,
                    timeout=args.timeout,
                    kernel_name="python3",
                    resources={"metadata": {"path": str(project_root)}},
                )
                client.execute()
            except Exception as exc:
                log_line(log, f"FAIL {notebook_name}: {type(exc).__name__}: {exc}")
                return 1

            elapsed = perf_counter() - start
            log_line(log, f"PASS {notebook_name} ({elapsed:.1f}s)")

        total_elapsed = perf_counter() - total_start
        log_line(log, f"All notebooks passed ({total_elapsed:.1f}s)")
        log_line(log, f"Log written to: {log_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
