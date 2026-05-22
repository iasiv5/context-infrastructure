from __future__ import annotations

import importlib.util
import json
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SRC_DIR = TESTS_DIR.parent / "src" / "v0"
RUNNER_PATH = SRC_DIR / "heartbeat_local_runner.py"

runner_spec = importlib.util.spec_from_file_location("heartbeat_local_runner", RUNNER_PATH)
assert runner_spec is not None and runner_spec.loader is not None
heartbeat_local_runner = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(heartbeat_local_runner)


def test_local_observer_skips_existing_date(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("Date: 2026-05-22\n", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"

    exit_code = heartbeat_local_runner.main(
        [
            "observer",
            "--target-date",
            "2026-05-22",
            "--workspace-root",
            str(workspace_root),
            "--observations-path",
            str(observations_path),
            "--state-path",
            str(state_path),
        ]
    )

    assert exit_code == 0
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_status"] == "skipped"
    assert state["observer"]["last_target_date"] == "2026-05-22"


def test_local_observer_writes_observation_entry(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    (workspace_root / "rules").mkdir(parents=True)
    (workspace_root / "periodic_jobs" / "sample").mkdir(parents=True)
    (workspace_root / "rules" / "example.md").write_text("rule", encoding="utf-8")
    (workspace_root / "periodic_jobs" / "sample" / "task.txt").write_text("task", encoding="utf-8")
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"

    exit_code = heartbeat_local_runner.main(
        [
            "observer",
            "--target-date",
            "2026-05-22",
            "--workspace-root",
            str(workspace_root),
            "--observations-path",
            str(observations_path),
            "--state-path",
            str(state_path),
        ]
    )

    assert exit_code == 0
    observations = observations_path.read_text(encoding="utf-8")
    assert "Date: 2026-05-22" in observations
    assert "rules/example.md" in observations
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_status"] == "success"


def test_local_reflector_prunes_stale_low_priority_lines_and_writes_report(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text(
        "# Memory Observations\n\n"
        "Date: 2026-04-01\n\n"
        "🟢 Low: old routine note\n"
        "🔴 High: durable constraint\n\n"
        "Date: 2026-05-20\n\n"
        "🔴 High: recent durable constraint\n"
        "🟡 Medium: recent project note\n",
        encoding="utf-8",
    )
    state_path = tmp_path / "heartbeat_status.json"
    report_path = tmp_path / "heartbeat_reflector_report.md"
    rules_path = workspace_root / "rules" / "skills" / "ai_heartbeat_local_reflections.md"

    exit_code = heartbeat_local_runner.main(
        [
            "reflector",
            "--target-date",
            "2026-05-22",
            "--workspace-root",
            str(workspace_root),
            "--observations-path",
            str(observations_path),
            "--report-path",
            str(report_path),
            "--rules-promotion-path",
            str(rules_path),
            "--state-path",
            str(state_path),
        ]
    )

    assert exit_code == 0
    observations = observations_path.read_text(encoding="utf-8")
    assert "🟢 Low: old routine note" not in observations
    assert "🔴 High: durable constraint" in observations
    report = report_path.read_text(encoding="utf-8")
    assert "Removed stale low-priority lines: 1" in report
    assert "Promoted operational rules: 4" in report
    promoted_rules = rules_path.read_text(encoding="utf-8")
    assert "# AI Heartbeat Local Reflections" in promoted_rules
    assert "Treat AGENTS.md, rules/, docs/specs/, and docs/plans/ as a single high-priority review surface" in promoted_rules
    assert "Treat periodic_jobs/, docs/, tools/, and m/ changes as active workspace signals" in promoted_rules
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["reflector"]["last_status"] == "success"