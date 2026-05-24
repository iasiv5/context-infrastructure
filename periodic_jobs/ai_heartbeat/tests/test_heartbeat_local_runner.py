from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


TESTS_DIR = Path(__file__).resolve().parent
SRC_DIR = TESTS_DIR.parent / "src" / "v0"
RUNNER_PATH = SRC_DIR / "heartbeat_local_runner.py"

runner_spec = importlib.util.spec_from_file_location("heartbeat_local_runner", RUNNER_PATH)
assert runner_spec is not None and runner_spec.loader is not None
heartbeat_local_runner = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(heartbeat_local_runner)


def _assert_claude_run_artifacts(state_path: Path, *, task_name: str, status: str) -> dict[str, object]:
    artifact_root = state_path.parent / "claude_runs"
    assert artifact_root.exists()
    run_dirs = [path for path in artifact_root.iterdir() if path.is_dir()]
    assert run_dirs
    latest_run = max(run_dirs, key=lambda path: path.stat().st_mtime)

    prompt_path = latest_run / "prompt.md"
    stdout_path = latest_run / "stdout.txt"
    stderr_path = latest_run / "stderr.txt"
    metadata_path = latest_run / "metadata.json"

    assert prompt_path.exists()
    assert stdout_path.exists()
    assert stderr_path.exists()
    assert metadata_path.exists()

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["task_name"] == task_name
    assert metadata["status"] == status
    return metadata


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


def test_local_observer_writes_observation_entry(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    (workspace_root / "rules").mkdir(parents=True)
    (workspace_root / "periodic_jobs" / "sample").mkdir(parents=True)
    (workspace_root / "rules" / "example.md").write_text("rule", encoding="utf-8")
    (workspace_root / "periodic_jobs" / "sample" / "task.txt").write_text("task", encoding="utf-8")
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"
    prompt_path = tmp_path / "observer.md"
    prompt_path.write_text("Date: {target_date}\n", encoding="utf-8")

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_OBSERVER_PROMPT_PATH", prompt_path, raising=False)

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        observations_path.write_text(
            f"Date: {target_date}\n\n- rules/example.md\n",
            encoding="utf-8",
        )
        return {
            "exit_code": 0,
            "stdout": '{"status":"ok"}',
            "stderr": "",
            "parsed_output": {"status": "ok"},
        }

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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


def test_local_observer_runs_claude_prompt_and_requires_target_date_entry(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"
    prompt_path = tmp_path / "observer.md"
    prompt_path.write_text(
        "Date: {target_date}\n"
        "Workspace: {workspace_root}\n"
        "Observations: {observations_path}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_OBSERVER_PROMPT_PATH", prompt_path, raising=False)
    captured: dict[str, str] = {}

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        captured["task_name"] = task_name
        captured["prompt_text"] = prompt_text
        observations_path.write_text(
            f"Date: {target_date}\n\n- Claude observer synthesized this entry.\n",
            encoding="utf-8",
        )
        return {
            "exit_code": 0,
            "stdout": '{"status":"ok"}',
            "stderr": "",
            "parsed_output": {"status": "ok"},
        }

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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
    assert captured["task_name"] == "observer"
    assert "Date: 2026-05-22" in captured["prompt_text"]
    assert heartbeat_local_runner._path_for_prompt(observations_path, workspace_root=workspace_root) in captured["prompt_text"]
    observations = observations_path.read_text(encoding="utf-8")
    assert "Claude observer synthesized this entry." in observations
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_status"] == "success"


def test_local_observer_fails_when_claude_does_not_write_target_date(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"
    prompt_path = tmp_path / "observer.md"
    prompt_path.write_text("Date: {target_date}\n", encoding="utf-8")

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_OBSERVER_PROMPT_PATH", prompt_path, raising=False)

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        return {
            "exit_code": 0,
            "stdout": '{"status":"ok"}',
            "stderr": "",
            "parsed_output": {"status": "ok"},
        }

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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

    assert exit_code == 1
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_status"] == "failed"
    assert state["observer"]["last_target_date"] == "2026-05-22"
    metadata = _assert_claude_run_artifacts(state_path, task_name="observer", status="failed")
    assert "did not write Date: 2026-05-22" in str(metadata["error"])


def test_local_observer_fails_when_claude_cli_is_unavailable(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"
    prompt_path = tmp_path / "observer.md"
    prompt_path.write_text("Date: {target_date}\n", encoding="utf-8")

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_OBSERVER_PROMPT_PATH", prompt_path, raising=False)

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        raise RuntimeError("observer Claude CLI is unavailable: missing executable")

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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

    assert exit_code == 1
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_status"] == "failed"
    assert "Claude CLI is unavailable" in state["observer"]["last_error"]
    metadata = _assert_claude_run_artifacts(state_path, task_name="observer", status="failed")
    assert "Claude CLI is unavailable" in str(metadata["error"])


@pytest.mark.parametrize(
    ("runner_result", "expected_error"),
    [
        (
            {
                "exit_code": 1,
                "stdout": "",
                "stderr": "permission denied",
                "parsed_output": None,
                "parse_error": None,
            },
            "exited with code 1",
        ),
        (
            {
                "exit_code": 0,
                "stdout": "not-json",
                "stderr": "",
                "parsed_output": None,
                "parse_error": "observer Claude CLI returned invalid JSON output",
            },
            "invalid JSON output",
        ),
    ],
)
def test_local_observer_persists_failure_artifacts_for_claude_runner_errors(
    tmp_path: Path,
    monkeypatch,
    runner_result: dict[str, object],
    expected_error: str,
) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"
    prompt_path = tmp_path / "observer.md"
    prompt_path.write_text("Date: {target_date}\n", encoding="utf-8")

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_OBSERVER_PROMPT_PATH", prompt_path, raising=False)

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        return dict(runner_result)

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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

    assert exit_code == 1
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_status"] == "failed"
    assert expected_error in state["observer"]["last_error"]
    metadata = _assert_claude_run_artifacts(state_path, task_name="observer", status="failed")
    assert expected_error in str(metadata["error"])


def test_local_reflector_runs_claude_and_validates_report_touched_files(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text(
        "# Memory Observations\n\n"
        "Date: 2026-05-20\n\n"
        "🔴 High: recent durable constraint\n",
        encoding="utf-8",
    )
    state_path = tmp_path / "heartbeat_status.json"
    report_path = tmp_path / "heartbeat_reflector_report.md"
    rules_path = workspace_root / "rules" / "skills" / "ai_heartbeat_local_reflections.md"
    prompt_path = tmp_path / "reflector.md"
    prompt_path.write_text(
        "Date: {target_date}\n"
        "Report: {report_path}\n"
        "Rules output: {rules_promotion_path}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_REFLECTOR_PROMPT_PATH", prompt_path, raising=False)
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_prepare_reflector_git_context",
        lambda *, workspace_root, allowlist_relative_paths: {"baseline_ref": "HEAD", "checkpoint_ref": None, "pre_run_status": {}},
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_detect_unexpected_reflector_changes",
        lambda *, workspace_root, before_status, allowlist_relative_paths: [],
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_restore_reflector_paths",
        lambda *, workspace_root, baseline_ref, relative_paths, pre_run_status: (_ for _ in ()).throw(AssertionError("reflector success should not restore")),
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_drop_reflector_checkpoint",
        lambda *, workspace_root, checkpoint_ref: None,
        raising=False,
    )
    captured: dict[str, str] = {}

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        captured["task_name"] = task_name
        captured["prompt_text"] = prompt_text
        observations_path.write_text(
            "# Memory Observations\n\n"
            "Date: 2026-05-20\n\n"
            "🔴 High: recent durable constraint\n",
            encoding="utf-8",
        )
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text("# AI Heartbeat Local Reflections\n", encoding="utf-8")
        report_path.write_text(
            "# AI Heartbeat Reflector Report\n\n"
            "Date: 2026-05-22\n\n"
            "## Touched Files\n"
            "- `contexts/memory/OBSERVATIONS.md` — 垃圾回收\n"
            "- `rules/skills/ai_heartbeat_local_reflections.md` — 晋升\n",
            encoding="utf-8",
        )
        return {
            "exit_code": 0,
            "stdout": '{"status":"ok"}',
            "stderr": "",
            "parsed_output": {"status": "ok"},
            "parse_error": None,
        }

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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
    assert captured["task_name"] == "reflector"
    assert heartbeat_local_runner._path_for_prompt(report_path, workspace_root=workspace_root) in captured["prompt_text"]
    assert "When writing `## Touched Files`, use one bare repo-relative path per bullet" in captured["prompt_text"]
    assert "Do not wrap touched file paths in backticks and do not add descriptions or commentary" in captured["prompt_text"]
    report = report_path.read_text(encoding="utf-8")
    assert "Date: 2026-05-22" in report
    assert "rules/skills/ai_heartbeat_local_reflections.md" in report
    promoted_rules = rules_path.read_text(encoding="utf-8")
    assert "# AI Heartbeat Local Reflections" in promoted_rules
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["reflector"]["last_status"] == "success"


def test_local_reflector_fails_when_report_is_missing_target_date(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("Date: 2026-05-20\n", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"
    report_path = tmp_path / "heartbeat_reflector_report.md"
    rules_path = workspace_root / "rules" / "skills" / "ai_heartbeat_local_reflections.md"
    prompt_path = tmp_path / "reflector.md"
    prompt_path.write_text("Date: {target_date}\n", encoding="utf-8")

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_REFLECTOR_PROMPT_PATH", prompt_path, raising=False)
    restore_calls: list[tuple[str, tuple[str, ...]]] = []
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_prepare_reflector_git_context",
        lambda *, workspace_root, allowlist_relative_paths: {"baseline_ref": "HEAD", "checkpoint_ref": None, "pre_run_status": {}},
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_detect_unexpected_reflector_changes",
        lambda *, workspace_root, before_status, allowlist_relative_paths: [],
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_restore_reflector_paths",
        lambda *, workspace_root, baseline_ref, relative_paths, pre_run_status: restore_calls.append((baseline_ref, tuple(relative_paths))),
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_drop_reflector_checkpoint",
        lambda *, workspace_root, checkpoint_ref: None,
        raising=False,
    )

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text("# AI Heartbeat Local Reflections\n", encoding="utf-8")
        report_path.write_text(
            "# AI Heartbeat Reflector Report\n\n"
            "## Touched Files\n"
            "- contexts/memory/OBSERVATIONS.md\n",
            encoding="utf-8",
        )
        return {
            "exit_code": 0,
            "stdout": '{"status":"ok"}',
            "stderr": "",
            "parsed_output": {"status": "ok"},
            "parse_error": None,
        }

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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

    assert exit_code == 1
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["reflector"]["last_status"] == "failed"
    assert "Date: 2026-05-22" in state["reflector"]["last_error"]
    assert restore_calls
    assert restore_calls[0][0] == "HEAD"
    assert "contexts/memory/OBSERVATIONS.md" in restore_calls[0][1]


def test_local_reflector_fails_when_report_mentions_non_allowlist_file(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("Date: 2026-05-20\n", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"
    report_path = tmp_path / "heartbeat_reflector_report.md"
    rules_path = workspace_root / "rules" / "skills" / "ai_heartbeat_local_reflections.md"
    prompt_path = tmp_path / "reflector.md"
    prompt_path.write_text("Date: {target_date}\n", encoding="utf-8")

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_REFLECTOR_PROMPT_PATH", prompt_path, raising=False)
    restore_calls: list[tuple[str, tuple[str, ...]]] = []
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_prepare_reflector_git_context",
        lambda *, workspace_root, allowlist_relative_paths: {"baseline_ref": "HEAD", "checkpoint_ref": None, "pre_run_status": {}},
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_detect_unexpected_reflector_changes",
        lambda *, workspace_root, before_status, allowlist_relative_paths: [],
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_restore_reflector_paths",
        lambda *, workspace_root, baseline_ref, relative_paths, pre_run_status: restore_calls.append((baseline_ref, tuple(relative_paths))),
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_drop_reflector_checkpoint",
        lambda *, workspace_root, checkpoint_ref: None,
        raising=False,
    )

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text("# AI Heartbeat Local Reflections\n", encoding="utf-8")
        report_path.write_text(
            "# AI Heartbeat Reflector Report\n\n"
            "Date: 2026-05-22\n\n"
            "## Touched Files\n"
            "- contexts/memory/OBSERVATIONS.md\n"
            "- docs/specs/out-of-scope.md\n",
            encoding="utf-8",
        )
        return {
            "exit_code": 0,
            "stdout": '{"status":"ok"}',
            "stderr": "",
            "parsed_output": {"status": "ok"},
            "parse_error": None,
        }

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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

    assert exit_code == 1
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["reflector"]["last_status"] == "failed"
    assert "allowlist" in state["reflector"]["last_error"]
    assert restore_calls
    assert restore_calls[0][0] == "HEAD"


def test_resolve_reflector_git_context_uses_head_for_clean_surface(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    report_path = workspace_root / "periodic_jobs" / "ai_heartbeat" / "state" / "heartbeat_reflector_report.md"

    monkeypatch.setattr(
        heartbeat_local_runner,
        "_git_status_for_paths",
        lambda *, workspace_root, relative_paths: {},
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_git_status_all_paths",
        lambda *, workspace_root: {},
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_create_reflector_checkpoint",
        lambda *, workspace_root: (_ for _ in ()).throw(AssertionError("clean surface should not create a checkpoint")),
        raising=False,
    )

    git_context = heartbeat_local_runner._prepare_reflector_git_context(
        workspace_root=workspace_root,
        allowlist_relative_paths=heartbeat_local_runner._reflector_allowlist_relative_paths(
            workspace_root=workspace_root,
            report_path=report_path,
        ),
    )

    assert git_context["baseline_ref"] == "HEAD"
    assert git_context["checkpoint_ref"] is None
    assert git_context["pre_run_status"] == {}


def test_resolve_reflector_git_context_creates_checkpoint_for_dirty_surface(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    report_path = workspace_root / "periodic_jobs" / "ai_heartbeat" / "state" / "heartbeat_reflector_report.md"

    monkeypatch.setattr(
        heartbeat_local_runner,
        "_git_status_for_paths",
        lambda *, workspace_root, relative_paths: {"contexts/memory/OBSERVATIONS.md": " M"},
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_git_status_all_paths",
        lambda *, workspace_root: {},
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_create_reflector_checkpoint",
        lambda *, workspace_root: "checkpoint-123",
        raising=False,
    )

    git_context = heartbeat_local_runner._prepare_reflector_git_context(
        workspace_root=workspace_root,
        allowlist_relative_paths=heartbeat_local_runner._reflector_allowlist_relative_paths(
            workspace_root=workspace_root,
            report_path=report_path,
        ),
    )

    assert git_context["baseline_ref"] == "checkpoint-123"
    assert git_context["checkpoint_ref"] == "checkpoint-123"
    assert git_context["pre_run_status"] == {"contexts/memory/OBSERVATIONS.md": " M"}


def test_local_reflector_drops_temporary_checkpoint_on_success(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    observations_path = workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"
    observations_path.parent.mkdir(parents=True)
    observations_path.write_text("Date: 2026-05-20\n", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"
    report_path = tmp_path / "heartbeat_reflector_report.md"
    rules_path = workspace_root / "rules" / "skills" / "ai_heartbeat_local_reflections.md"
    prompt_path = tmp_path / "reflector.md"
    prompt_path.write_text("Date: {target_date}\n", encoding="utf-8")

    monkeypatch.setattr(heartbeat_local_runner, "DEFAULT_REFLECTOR_PROMPT_PATH", prompt_path, raising=False)
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_prepare_reflector_git_context",
        lambda *, workspace_root, allowlist_relative_paths: {"baseline_ref": "checkpoint-123", "checkpoint_ref": "checkpoint-123", "pre_run_status": {"contexts/memory/OBSERVATIONS.md": " M"}},
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_detect_unexpected_reflector_changes",
        lambda *, workspace_root, before_status, allowlist_relative_paths: [],
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_restore_reflector_paths",
        lambda *, workspace_root, baseline_ref, relative_paths, pre_run_status: (_ for _ in ()).throw(AssertionError("reflector success should not restore")),
        raising=False,
    )
    dropped_checkpoints: list[str] = []
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_drop_reflector_checkpoint",
        lambda *, workspace_root, checkpoint_ref: dropped_checkpoints.append(checkpoint_ref),
        raising=False,
    )

    def fake_run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str):
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text("# AI Heartbeat Local Reflections\n", encoding="utf-8")
        report_path.write_text(
            "# AI Heartbeat Reflector Report\n\n"
            "Date: 2026-05-22\n\n"
            "## Touched Files\n"
            "- contexts/memory/OBSERVATIONS.md\n"
            "- rules/skills/ai_heartbeat_local_reflections.md\n",
            encoding="utf-8",
        )
        return {
            "exit_code": 0,
            "stdout": '{"status":"ok"}',
            "stderr": "",
            "parsed_output": {"status": "ok"},
            "parse_error": None,
        }

    monkeypatch.setattr(heartbeat_local_runner, "_run_claude_cli", fake_run_claude_cli, raising=False)

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
    assert dropped_checkpoints == ["checkpoint-123"]


def test_reflector_allowlist_includes_report_path_inside_workspace(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    report_path = workspace_root / "periodic_jobs" / "ai_heartbeat" / "state" / "heartbeat_reflector_report.md"

    allowlist_relative_paths = heartbeat_local_runner._reflector_allowlist_relative_paths(
        workspace_root=workspace_root,
        report_path=report_path,
    )

    assert "periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md" in allowlist_relative_paths


def test_restore_reflector_paths_deletes_generated_report_not_in_git(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / "workspace"
    report_path = workspace_root / "periodic_jobs" / "ai_heartbeat" / "state" / "heartbeat_reflector_report.md"
    report_path.parent.mkdir(parents=True)
    report_path.write_text("generated", encoding="utf-8")

    checkout_calls: list[tuple[str, ...]] = []
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_git_path_exists_in_ref",
        lambda *, workspace_root, ref, relative_path: relative_path != "periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md",
        raising=False,
    )
    monkeypatch.setattr(
        heartbeat_local_runner,
        "_run_git_command",
        lambda *, workspace_root, args: checkout_calls.append(tuple(args)),
        raising=False,
    )

    heartbeat_local_runner._restore_reflector_paths(
        workspace_root=workspace_root,
        baseline_ref="HEAD",
        relative_paths=(
            "contexts/memory/OBSERVATIONS.md",
            "periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md",
        ),
        pre_run_status={},
    )

    assert not report_path.exists()
    assert checkout_calls == [("checkout", "HEAD", "--", "contexts/memory/OBSERVATIONS.md")]