from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Sequence


MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import heartbeat_state


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
HEARTBEAT_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = MODULE_DIR / "prompts"
DEFAULT_OBSERVATIONS_PATH = WORKSPACE_ROOT / "contexts" / "memory" / "OBSERVATIONS.md"
DEFAULT_REPORT_PATH = HEARTBEAT_ROOT / "state" / "heartbeat_reflector_report.md"
DEFAULT_OBSERVER_PROMPT_PATH = PROMPTS_DIR / "observer.md"
DEFAULT_REFLECTOR_PROMPT_PATH = PROMPTS_DIR / "reflector.md"
DEFAULT_CLAUDE_RUNS_DIR = HEARTBEAT_ROOT / "state" / "claude_runs"
DEFAULT_KNOWLEDGE_BASE_PATH = HEARTBEAT_ROOT / "docs" / "KNOWLEDGE_BASE.md"
DEFAULT_PRD_PATH = HEARTBEAT_ROOT / "docs" / "PRD.md"
DEFAULT_CLAUDE_COMMAND = "claude"
DEFAULT_CLAUDE_TIMEOUT_SECONDS = 300
LOW_PRIORITY_RETENTION_DAYS = 30
RECENT_REVIEW_DAYS = 14
REFLECTOR_RETIRED_RELATIVE_PATHS = (
    "rules/skills/" + "ai_heartbeat_local_" + "reflections.md",
)
REFLECTOR_ALLOWLIST_RELATIVE_PATHS = (
    "contexts/memory/OBSERVATIONS.md",
    "rules/SOUL.md",
    "rules/USER.md",
    "rules/COMMUNICATION.md",
    "rules/WORKSPACE.md",
    "rules/skills/INDEX.md",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AI Heartbeat tasks locally from the SessionStart hook")
    parser.add_argument("tasks", nargs="+", choices=tuple(heartbeat_state.TASK_INTERVALS.keys()))
    parser.add_argument("--target-date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--workspace-root")
    parser.add_argument("--observations-path")
    parser.add_argument("--report-path")
    parser.add_argument("--state-path")
    return parser


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _resolve_workspace_root(path: str | None) -> Path:
    return Path(path) if path else WORKSPACE_ROOT


def _resolve_observations_path(path: str | None, workspace_root: Path) -> Path:
    return Path(path) if path else workspace_root / "contexts" / "memory" / "OBSERVATIONS.md"


def _resolve_report_path(path: str | None, state_path: str | None) -> Path:
    if path:
        return Path(path)
    if state_path:
        return Path(state_path).with_name("heartbeat_reflector_report.md")
    return DEFAULT_REPORT_PATH


def _resolve_claude_runs_dir(state_path: str | None) -> Path:
    if state_path:
        return Path(state_path).resolve().parent / "claude_runs"
    return DEFAULT_CLAUDE_RUNS_DIR


def _resolve_claude_timeout_seconds() -> int:
    configured = os.environ.get("AI_HEARTBEAT_CLAUDE_TIMEOUT_SECONDS")
    if not configured:
        return DEFAULT_CLAUDE_TIMEOUT_SECONDS
    try:
        return max(1, int(configured))
    except ValueError:
        return DEFAULT_CLAUDE_TIMEOUT_SECONDS


def _resolve_claude_command() -> str:
    configured = os.environ.get("AI_HEARTBEAT_CLAUDE_COMMAND")
    if os.name != "nt":
        return configured or DEFAULT_CLAUDE_COMMAND

    candidates: list[str] = []
    if configured:
        configured_path = Path(configured)
        if configured_path.suffix.lower() == ".ps1":
            cmd_candidate = configured_path.with_suffix(".cmd")
            if cmd_candidate.exists():
                return str(cmd_candidate)
        candidates.append(configured)
        if not configured_path.suffix:
            candidates.append(f"{configured}.cmd")
            candidates.append(f"{configured}.exe")
    else:
        candidates.extend(["claude.cmd", "claude.exe", DEFAULT_CLAUDE_COMMAND])

    for candidate in candidates:
        resolved = shutil.which(candidate)
        if not resolved:
            continue
        if Path(resolved).suffix.lower() == ".ps1":
            continue
        return resolved

    return configured or "claude.cmd"


def _load_prompt_template(prompt_path: Path) -> str:
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template does not exist: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def _coerce_text(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)

def _path_relative_to_workspace(path: Path, *, workspace_root: Path) -> str | None:
    try:
        return path.resolve().relative_to(workspace_root.resolve()).as_posix()
    except ValueError:
        return None


def _path_for_prompt(path: Path, *, workspace_root: Path) -> str:
    relative_path = _path_relative_to_workspace(path, workspace_root=workspace_root)
    if relative_path is not None:
        return relative_path
    return path.as_posix()


def _normalize_relative_path(relative_path: str) -> str:
    return relative_path.strip().replace("\\", "/")


def _is_retired_reflector_path(relative_path: str) -> bool:
    return _normalize_relative_path(relative_path) in REFLECTOR_RETIRED_RELATIVE_PATHS


def _is_real_skill_doc_path(relative_path: str) -> bool:
    normalized_path = _normalize_relative_path(relative_path)
    if _is_retired_reflector_path(normalized_path):
        return False
    if normalized_path == "rules/skills/INDEX.md":
        return False
    if not normalized_path.startswith("rules/skills/") or not normalized_path.endswith(".md"):
        return False
    skill_name = normalized_path.removeprefix("rules/skills/")
    return bool(skill_name) and "/" not in skill_name


def _is_allowed_reflector_path(relative_path: str, *, allowlist_relative_paths: Sequence[str]) -> bool:
    normalized_path = _normalize_relative_path(relative_path)
    if _is_retired_reflector_path(normalized_path):
        return False
    return normalized_path in allowlist_relative_paths or _is_real_skill_doc_path(normalized_path)


def _reflector_allowlist_relative_paths(*, workspace_root: Path, report_path: Path) -> tuple[str, ...]:
    allowlist_relative_paths = list(REFLECTOR_ALLOWLIST_RELATIVE_PATHS)
    report_relative_path = _path_relative_to_workspace(report_path, workspace_root=workspace_root)
    if report_relative_path and report_relative_path not in allowlist_relative_paths:
        allowlist_relative_paths.append(report_relative_path)

    skills_dir = workspace_root / "rules" / "skills"
    if skills_dir.exists():
        for skill_path in sorted(skills_dir.glob("*.md")):
            relative_path = _path_relative_to_workspace(skill_path, workspace_root=workspace_root)
            if not relative_path or not _is_real_skill_doc_path(relative_path):
                continue
            if relative_path not in allowlist_relative_paths:
                allowlist_relative_paths.append(relative_path)

    return tuple(allowlist_relative_paths)


def _render_observer_prompt(*, prompt_path: Path, workspace_root: Path, observations_path: Path, target_date: str) -> str:
    template = _load_prompt_template(prompt_path)
    prompt = template.format(
        target_date=target_date,
        workspace_root=".",
        observations_path=_path_for_prompt(observations_path, workspace_root=workspace_root),
        agents_path=_path_for_prompt(workspace_root / "AGENTS.md", workspace_root=workspace_root),
        claude_md_path=_path_for_prompt(workspace_root / "CLAUDE.md", workspace_root=workspace_root),
        knowledge_base_path=_path_for_prompt(DEFAULT_KNOWLEDGE_BASE_PATH, workspace_root=workspace_root),
        prd_path=_path_for_prompt(DEFAULT_PRD_PATH, workspace_root=workspace_root),
        soul_path=_path_for_prompt(workspace_root / "rules" / "SOUL.md", workspace_root=workspace_root),
        user_path=_path_for_prompt(workspace_root / "rules" / "USER.md", workspace_root=workspace_root),
        workspace_rules_path=_path_for_prompt(workspace_root / "rules" / "WORKSPACE.md", workspace_root=workspace_root),
        communication_path=_path_for_prompt(workspace_root / "rules" / "COMMUNICATION.md", workspace_root=workspace_root),
    )
    return (
        "All workspace paths below are repo-relative and resolved against the current working directory.\n"
        "Do not rewrite them into absolute Windows paths or 8.3 short paths.\n"
        "When using tools, prefer repo-relative paths like rules/SOUL.md and contexts/memory/OBSERVATIONS.md.\n\n"
        f"{prompt}"
    )


def _render_reflector_prompt(
    *,
    prompt_path: Path,
    workspace_root: Path,
    observations_path: Path,
    report_path: Path,
    target_date: str,
) -> str:
    template = _load_prompt_template(prompt_path)
    allowlist_paths = "\n".join(
        f"- {path}"
        for path in _reflector_allowlist_relative_paths(
            workspace_root=workspace_root,
            report_path=report_path,
        )
    )
    prompt = template.format(
        target_date=target_date,
        workspace_root=".",
        observations_path=_path_for_prompt(observations_path, workspace_root=workspace_root),
        report_path=_path_for_prompt(report_path, workspace_root=workspace_root),
        agents_path=_path_for_prompt(workspace_root / "AGENTS.md", workspace_root=workspace_root),
        claude_md_path=_path_for_prompt(workspace_root / "CLAUDE.md", workspace_root=workspace_root),
        knowledge_base_path=_path_for_prompt(DEFAULT_KNOWLEDGE_BASE_PATH, workspace_root=workspace_root),
        prd_path=_path_for_prompt(DEFAULT_PRD_PATH, workspace_root=workspace_root),
        soul_path=_path_for_prompt(workspace_root / "rules" / "SOUL.md", workspace_root=workspace_root),
        user_path=_path_for_prompt(workspace_root / "rules" / "USER.md", workspace_root=workspace_root),
        workspace_rules_path=_path_for_prompt(workspace_root / "rules" / "WORKSPACE.md", workspace_root=workspace_root),
        communication_path=_path_for_prompt(workspace_root / "rules" / "COMMUNICATION.md", workspace_root=workspace_root),
        allowlist_paths=allowlist_paths,
    )
    return (
        "All workspace paths below are repo-relative and resolved against the current working directory.\n"
        "Do not rewrite them into absolute Windows paths or 8.3 short paths.\n"
        "When using tools, prefer repo-relative paths like rules/SOUL.md, contexts/memory/OBSERVATIONS.md, and rules/skills/INDEX.md.\n\n"
        "When writing `## Touched Files`, use one bare repo-relative path per bullet in the exact form `- path/to/file.ext`.\n"
        "Do not wrap touched file paths in backticks and do not add descriptions or commentary on those lines.\n\n"
        f"{prompt}"
    )


def _run_claude_cli(*, task_name: str, prompt_text: str, workspace_root: Path, target_date: str) -> dict[str, object]:
    command_path = _resolve_claude_command()
    command = [
        command_path,
        "-p",
        "--output-format",
        "json",
        "--permission-mode",
        "bypassPermissions",
        "--dangerously-skip-permissions",
    ]
    configured_model = os.environ.get("AI_HEARTBEAT_CLAUDE_MODEL")
    if configured_model:
        command.extend(["--model", configured_model])

    timeout_seconds = _resolve_claude_timeout_seconds()
    try:
        completed = subprocess.run(
            command,
            cwd=workspace_root,
            capture_output=True,
            input=prompt_text,
            text=True,
            encoding="utf-8",
            timeout=timeout_seconds,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"{task_name} Claude CLI is unavailable: attempted {command_path}: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{task_name} Claude CLI timed out after {timeout_seconds} seconds") from exc

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    stripped_stdout = stdout.strip()
    parsed_output = None
    parse_error = None
    if stripped_stdout:
        try:
            parsed_output = json.loads(stripped_stdout)
        except json.JSONDecodeError:
            lowered_stdout = stripped_stdout.lower()
            if "requires manual approval" in lowered_stdout or "requested permissions" in lowered_stdout or "等待你批准" in stripped_stdout:
                parse_error = f"{task_name} Claude CLI requested manual approval"
            else:
                parse_error = f"{task_name} Claude CLI returned invalid JSON output"
    elif completed.returncode == 0:
        parse_error = f"{task_name} Claude CLI returned empty output"

    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "parsed_output": parsed_output,
        "parse_error": parse_error,
        "target_date": target_date,
    }


def _raise_for_failed_claude_result(task_name: str, result: dict[str, object]) -> None:
    exit_code = result.get("exit_code")
    if exit_code != 0:
        detail = _coerce_text(result.get("stderr")).strip() or _coerce_text(result.get("stdout")).strip() or "no output"
        raise RuntimeError(f"{task_name} Claude CLI exited with code {exit_code}: {detail}")

    parse_error = _coerce_text(result.get("parse_error")).strip()
    if parse_error:
        raise RuntimeError(parse_error)


def _write_claude_run_artifacts(
    *,
    task_name: str,
    target_date: str,
    state_path: str | None,
    prompt_text: str,
    result: dict[str, object] | None,
    status: str,
    error: str | None,
) -> Path:
    runs_dir = _resolve_claude_runs_dir(state_path)
    timestamp = _utc_now().strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = runs_dir / f"{target_date}-{task_name}-{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)

    (run_dir / "prompt.md").write_text(prompt_text, encoding="utf-8")
    (run_dir / "stdout.txt").write_text(_coerce_text(None if result is None else result.get("stdout")), encoding="utf-8")
    (run_dir / "stderr.txt").write_text(_coerce_text(None if result is None else result.get("stderr")), encoding="utf-8")
    metadata = {
        "task_name": task_name,
        "target_date": target_date,
        "status": status,
        "error": error,
        "created_at": _utc_now().isoformat(),
        "exit_code": None if result is None else result.get("exit_code"),
        "parse_error": None if result is None else result.get("parse_error"),
        "command": None if result is None else result.get("command"),
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return run_dir


def _run_git_command(*, workspace_root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            ["git", "-c", "core.quotepath=false", *args],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"git is unavailable: {exc}") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")

    return completed


def _parse_git_status(stdout: str) -> dict[str, str]:
    status_by_path: dict[str, str] = {}
    for raw_line in stdout.splitlines():
        if not raw_line:
            continue
        status = raw_line[:2]
        path = raw_line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        status_by_path[path] = status
    return status_by_path


def _git_status_for_paths(*, workspace_root: Path, relative_paths: Sequence[str]) -> dict[str, str]:
    completed = _run_git_command(
        workspace_root=workspace_root,
        args=["status", "--short", "--untracked-files=all", "--", *relative_paths],
    )
    return _parse_git_status(completed.stdout)


def _git_status_all_paths(*, workspace_root: Path) -> dict[str, str]:
    completed = _run_git_command(
        workspace_root=workspace_root,
        args=["status", "--short", "--untracked-files=all", "--", "."],
    )
    return _parse_git_status(completed.stdout)


def _create_reflector_checkpoint(*, workspace_root: Path) -> str:
    timestamp = _utc_now().strftime("%Y%m%dT%H%M%S%fZ")
    completed = _run_git_command(
        workspace_root=workspace_root,
        args=["stash", "create", f"ai-heartbeat-reflector-{timestamp}"],
    )
    checkpoint_ref = completed.stdout.strip()
    if not checkpoint_ref:
        raise RuntimeError("Reflector git checkpoint creation returned an empty ref")
    return checkpoint_ref


def _prepare_reflector_git_context(*, workspace_root: Path, allowlist_relative_paths: Sequence[str]) -> dict[str, object]:
    pre_run_status = _git_status_for_paths(
        workspace_root=workspace_root,
        relative_paths=allowlist_relative_paths,
    )
    git_context: dict[str, object] = {
        "baseline_ref": "HEAD",
        "checkpoint_ref": None,
        "pre_run_status": pre_run_status,
        "pre_run_repo_status": _git_status_all_paths(workspace_root=workspace_root),
    }
    if pre_run_status:
        checkpoint_ref = _create_reflector_checkpoint(workspace_root=workspace_root)
        git_context["baseline_ref"] = checkpoint_ref
        git_context["checkpoint_ref"] = checkpoint_ref
    return git_context


def _git_path_exists_in_ref(*, workspace_root: Path, ref: str, relative_path: str) -> bool:
    try:
        completed = subprocess.run(
            ["git", "-c", "core.quotepath=false", "cat-file", "-e", f"{ref}:{relative_path}"],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"git is unavailable: {exc}") from exc

    return completed.returncode == 0


def _restore_reflector_paths(
    *,
    workspace_root: Path,
    baseline_ref: str,
    relative_paths: Sequence[str],
    pre_run_status: dict[str, str],
) -> None:
    if not relative_paths:
        return

    checkout_paths: list[str] = []
    remove_paths: list[str] = []

    for relative_path in relative_paths:
        if pre_run_status.get(relative_path) == "??":
            continue
        if _git_path_exists_in_ref(workspace_root=workspace_root, ref=baseline_ref, relative_path=relative_path):
            checkout_paths.append(relative_path)
        else:
            remove_paths.append(relative_path)

    if checkout_paths:
        _run_git_command(
            workspace_root=workspace_root,
            args=["checkout", baseline_ref, "--", *checkout_paths],
        )

    for relative_path in remove_paths:
        restore_path = workspace_root / Path(relative_path)
        if restore_path.is_dir():
            shutil.rmtree(restore_path, ignore_errors=True)
        else:
            restore_path.unlink(missing_ok=True)


def _drop_reflector_checkpoint(*, workspace_root: Path, checkpoint_ref: str) -> None:
    return None


def _detect_unexpected_reflector_changes(
    *,
    workspace_root: Path,
    before_status: dict[str, str],
    allowlist_relative_paths: Sequence[str],
) -> list[str]:
    after_status = _git_status_all_paths(workspace_root=workspace_root)
    unexpected_paths: list[str] = []
    for path, status in after_status.items():
        if _is_allowed_reflector_path(path, allowlist_relative_paths=allowlist_relative_paths):
            continue
        if before_status.get(path) != status:
            unexpected_paths.append(path)
    return sorted(unexpected_paths)


def _reflector_dynamic_restore_relative_paths(
    *,
    workspace_root: Path,
    before_status: dict[str, str],
    report_path: Path,
) -> tuple[str, ...]:
    restore_relative_paths: list[str] = []
    after_status = _git_status_all_paths(workspace_root=workspace_root)

    for path, status in after_status.items():
        if before_status.get(path) == status:
            continue
        if _is_real_skill_doc_path(path) or _is_retired_reflector_path(path):
            restore_relative_paths.append(path)

    if report_path.exists():
        report_content = report_path.read_text(encoding="utf-8")
        for path in _extract_touched_files(report_content):
            normalized_path = _normalize_relative_path(path)
            if _is_real_skill_doc_path(normalized_path) or _is_retired_reflector_path(normalized_path):
                restore_relative_paths.append(normalized_path)

    return tuple(sorted(set(restore_relative_paths)))


def _extract_touched_files(report_content: str) -> list[str]:
    touched_files: list[str] = []
    in_section = False

    for raw_line in report_content.splitlines():
        stripped = raw_line.strip()
        if stripped == "## Touched Files":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith("- "):
            touched_entry = stripped[2:].strip()
            backtick_match = re.match(r"`([^`]+)`", touched_entry)
            if backtick_match:
                touched_files.append(backtick_match.group(1).strip())
                continue
            for separator in (" — ", " - "):
                if separator in touched_entry:
                    touched_entry = touched_entry.split(separator, 1)[0].strip()
                    break
            touched_files.append(touched_entry.strip("` "))

    return touched_files


def _extract_garbage_collected_entries(report_content: str) -> list[str]:
    garbage_collected_entries: list[str] = []
    in_section = False

    for raw_line in report_content.splitlines():
        stripped = raw_line.strip()
        if stripped == "## Garbage-Collected Entries":
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith("- "):
            garbage_collected_entries.append(stripped[2:].strip().strip("`"))

    if not in_section:
        raise RuntimeError("Reflector report did not include ## Garbage-Collected Entries")

    return garbage_collected_entries


def _validate_reflector_gc_entries(
    *,
    report_content: str,
    observations_before_content: str,
    observations_after_content: str,
) -> None:
    garbage_collected_entries = _extract_garbage_collected_entries(report_content)
    before_lines = observations_before_content.splitlines()
    after_lines = observations_after_content.splitlines()

    for entry in garbage_collected_entries:
        if not entry:
            raise RuntimeError("Reflector report listed an empty garbage-collected entry")

        if re.fullmatch(r"Date: \d{4}-\d{2}-\d{2}", entry):
            if entry not in before_lines:
                raise RuntimeError(f"Reflector report claimed GC for missing date block: {entry}")
            if entry in after_lines:
                raise RuntimeError(f"Reflector report claimed GC but date block still exists: {entry}")
            continue

        if entry not in before_lines:
            raise RuntimeError(f"Reflector report claimed GC for missing observation line: {entry}")
        if entry in after_lines:
            raise RuntimeError(f"Reflector report claimed GC but observation line still exists: {entry}")


def _validate_reflector_outputs(
    *,
    workspace_root: Path,
    observations_path: Path,
    report_path: Path,
    target_date: str,
    allowlist_relative_paths: Sequence[str],
    observations_before_content: str | None = None,
) -> list[str]:
    observations_after_content = observations_path.read_text(encoding="utf-8")
    if observations_before_content is None:
        observations_before_content = observations_after_content
    if not report_path.exists():
        raise RuntimeError(f"Reflector report does not exist: {report_path}")

    report_content = report_path.read_text(encoding="utf-8")
    if f"Date: {target_date}" not in report_content:
        raise RuntimeError(f"Reflector report does not contain Date: {target_date}")

    touched_files = _extract_touched_files(report_content)
    if not touched_files:
        raise RuntimeError("Reflector report did not list touched files")

    retired_files = [path for path in touched_files if _is_retired_reflector_path(path)]
    if retired_files:
        raise RuntimeError(
            "Reflector report touched retired local reflector output files: "
            + ", ".join(sorted(retired_files))
        )

    unexpected_files = [
        path for path in touched_files if not _is_allowed_reflector_path(path, allowlist_relative_paths=allowlist_relative_paths)
    ]
    if unexpected_files:
        raise RuntimeError(f"Reflector report mentioned files outside the allowlist: {', '.join(unexpected_files)}")

    touched_skill_docs = [path for path in touched_files if _is_real_skill_doc_path(path)]
    if touched_skill_docs and "rules/skills/INDEX.md" not in touched_files:
        raise RuntimeError(
            "Reflector report touched real skill docs without also touching rules/skills/INDEX.md"
        )

    _validate_reflector_gc_entries(
        report_content=report_content,
        observations_before_content=observations_before_content,
        observations_after_content=observations_after_content,
    )

    for relative_path in touched_files:
        touched_path = workspace_root / Path(relative_path)
        if not touched_path.exists():
            raise RuntimeError(f"Reflector report referenced missing touched file: {relative_path}")
        touched_path.read_text(encoding="utf-8")

    return touched_files


def run_observer_local(
    *,
    workspace_root: Path,
    observations_path: Path,
    state_path: str | None,
    target_date: str,
) -> None:
    existing = observations_path.read_text(encoding="utf-8") if observations_path.exists() else ""
    if f"Date: {target_date}" in existing:
        heartbeat_state.persist_skipped("observer", path=state_path, target_date=target_date)
        print(f"[observer] Entry for {target_date} already exists, skipping.")
        return

    prompt_text = ""
    result: dict[str, object] | None = None
    try:
        prompt_text = _render_observer_prompt(
            prompt_path=DEFAULT_OBSERVER_PROMPT_PATH,
            workspace_root=workspace_root,
            observations_path=observations_path,
            target_date=target_date,
        )
        result = _run_claude_cli(
            task_name="observer",
            prompt_text=prompt_text,
            workspace_root=workspace_root,
            target_date=target_date,
        )
        _raise_for_failed_claude_result("observer", result)

        updated = observations_path.read_text(encoding="utf-8") if observations_path.exists() else ""
        if f"Date: {target_date}" not in updated:
            raise RuntimeError(f"Observer run did not write Date: {target_date} to {observations_path}")

        _write_claude_run_artifacts(
            task_name="observer",
            target_date=target_date,
            state_path=state_path,
            prompt_text=prompt_text,
            result=result,
            status="success",
            error=None,
        )
    except Exception as exc:
        _write_claude_run_artifacts(
            task_name="observer",
            target_date=target_date,
            state_path=state_path,
            prompt_text=prompt_text,
            result=result,
            status="failed",
            error=str(exc),
        )
        raise

    heartbeat_state.persist_success("observer", path=state_path, target_date=target_date)
    print(f"[observer] Wrote Date: {target_date} entry to {observations_path}.")
    print(f"[observer] Claude CLI completed with exit code {result['exit_code']}.")


def run_reflector_local(
    *,
    workspace_root: Path,
    observations_path: Path,
    report_path: Path,
    state_path: str | None,
    target_date: str,
) -> None:
    prompt_text = ""
    result: dict[str, object] | None = None
    touched_files: list[str] = []
    observations_before_content = observations_path.read_text(encoding="utf-8") if observations_path.exists() else ""
    allowlist_relative_paths = _reflector_allowlist_relative_paths(
        workspace_root=workspace_root,
        report_path=report_path,
    )
    git_context: dict[str, object] = {
        "baseline_ref": "HEAD",
        "checkpoint_ref": None,
        "pre_run_status": {},
        "pre_run_repo_status": {},
    }
    should_restore = False
    try:
        git_context = _prepare_reflector_git_context(
            workspace_root=workspace_root,
            allowlist_relative_paths=allowlist_relative_paths,
        )
        should_restore = True
        prompt_text = _render_reflector_prompt(
            prompt_path=DEFAULT_REFLECTOR_PROMPT_PATH,
            workspace_root=workspace_root,
            observations_path=observations_path,
            report_path=report_path,
            target_date=target_date,
        )
        result = _run_claude_cli(
            task_name="reflector",
            prompt_text=prompt_text,
            workspace_root=workspace_root,
            target_date=target_date,
        )
        _raise_for_failed_claude_result("reflector", result)
        unexpected_paths = _detect_unexpected_reflector_changes(
            workspace_root=workspace_root,
            before_status=dict(git_context.get("pre_run_repo_status", git_context.get("pre_run_status", {}))),
            allowlist_relative_paths=allowlist_relative_paths,
        )
        if unexpected_paths:
            raise RuntimeError(f"Reflector modified files outside the allowlist: {', '.join(unexpected_paths)}")
        touched_files = _validate_reflector_outputs(
            workspace_root=workspace_root,
            observations_path=observations_path,
            report_path=report_path,
            target_date=target_date,
            allowlist_relative_paths=allowlist_relative_paths,
            observations_before_content=observations_before_content,
        )
        _write_claude_run_artifacts(
            task_name="reflector",
            target_date=target_date,
            state_path=state_path,
            prompt_text=prompt_text,
            result=result,
            status="success",
            error=None,
        )
        checkpoint_ref = git_context.get("checkpoint_ref")
        if checkpoint_ref:
            _drop_reflector_checkpoint(workspace_root=workspace_root, checkpoint_ref=str(checkpoint_ref))
    except Exception as exc:
        if should_restore:
            dynamic_restore_relative_paths: tuple[str, ...] = ()
            try:
                dynamic_restore_relative_paths = _reflector_dynamic_restore_relative_paths(
                    workspace_root=workspace_root,
                    before_status=dict(git_context.get("pre_run_repo_status", git_context.get("pre_run_status", {}))),
                    report_path=report_path,
                )
            except RuntimeError:
                dynamic_restore_relative_paths = ()
            restore_relative_paths = tuple(
                dict.fromkeys(
                    [
                        *allowlist_relative_paths,
                        *dynamic_restore_relative_paths,
                    ]
                )
            )
            _restore_reflector_paths(
                workspace_root=workspace_root,
                baseline_ref=str(git_context.get("baseline_ref", "HEAD")),
                relative_paths=restore_relative_paths,
                pre_run_status=dict(git_context.get("pre_run_status", {})),
            )
        _write_claude_run_artifacts(
            task_name="reflector",
            target_date=target_date,
            state_path=state_path,
            prompt_text=prompt_text,
            result=result,
            status="failed",
            error=str(exc),
        )
        raise

    heartbeat_state.persist_success("reflector", path=state_path, target_date=target_date)
    print(f"[reflector] Claude CLI completed with exit code {result['exit_code']}.")
    print(f"[reflector] Report validated with {len(touched_files)} touched files.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    workspace_root = _resolve_workspace_root(args.workspace_root)
    observations_path = _resolve_observations_path(args.observations_path, workspace_root)
    report_path = _resolve_report_path(args.report_path, args.state_path)
    exit_code = 0

    for task_name in args.tasks:
        try:
            if task_name == "observer":
                run_observer_local(
                    workspace_root=workspace_root,
                    observations_path=observations_path,
                    state_path=args.state_path,
                    target_date=args.target_date,
                )
            else:
                run_reflector_local(
                    workspace_root=workspace_root,
                    observations_path=observations_path,
                    report_path=report_path,
                    state_path=args.state_path,
                    target_date=args.target_date,
                )
        except Exception as exc:
            heartbeat_state.persist_failure(task_name, path=args.state_path, target_date=args.target_date, error=str(exc))
            print(f"[{task_name}] Failed: {exc}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())