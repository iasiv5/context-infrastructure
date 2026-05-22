from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Sequence


MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import heartbeat_state


WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
HEARTBEAT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OBSERVATIONS_PATH = WORKSPACE_ROOT / "contexts" / "memory" / "OBSERVATIONS.md"
DEFAULT_REPORT_PATH = HEARTBEAT_ROOT / "state" / "heartbeat_reflector_report.md"
DEFAULT_RULES_PROMOTION_PATH = WORKSPACE_ROOT / "rules" / "skills" / "ai_heartbeat_local_reflections.md"
EXCLUDED_DIR_NAMES = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
HIGH_PRIORITY_PREFIXES = ("rules/", "docs/specs/", "docs/plans/")
MEDIUM_PRIORITY_PREFIXES = ("periodic_jobs/", "docs/", "tools/", "m/")
HIGH_PRIORITY_FILES = {"AGENTS.md"}
MEDIUM_PRIORITY_FILES = {"README.md", "setup_guide.md"}
MAX_PATHS_PER_BUCKET = 6
LOW_PRIORITY_RETENTION_DAYS = 30
RECENT_REVIEW_DAYS = 14


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AI Heartbeat tasks locally from the SessionStart hook")
    parser.add_argument("tasks", nargs="+", choices=tuple(heartbeat_state.TASK_INTERVALS.keys()))
    parser.add_argument("--target-date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--workspace-root")
    parser.add_argument("--observations-path")
    parser.add_argument("--report-path")
    parser.add_argument("--rules-promotion-path")
    parser.add_argument("--state-path")
    return parser


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


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


def _resolve_rules_promotion_path(path: str | None) -> Path:
    return Path(path) if path else DEFAULT_RULES_PROMOTION_PATH


def _as_posix_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _iter_recent_files(workspace_root: Path, since: datetime) -> list[str]:
    results: list[tuple[datetime, str]] = []

    for current_root, dir_names, file_names in os.walk(workspace_root):
        dir_names[:] = [name for name in dir_names if name not in EXCLUDED_DIR_NAMES]
        current_path = Path(current_root)
        for file_name in file_names:
            candidate = current_path / file_name
            try:
                relative_path = _as_posix_relative(candidate, workspace_root)
            except ValueError:
                continue

            if relative_path == "contexts/memory/OBSERVATIONS.md":
                continue
            if relative_path.startswith("periodic_jobs/ai_heartbeat/state/"):
                continue

            try:
                modified_at = datetime.fromtimestamp(candidate.stat().st_mtime, tz=timezone.utc)
            except OSError:
                continue

            if modified_at < since:
                continue

            results.append((modified_at, relative_path))

    results.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [relative_path for _, relative_path in results]


def _bucket_for_path(relative_path: str) -> str:
    if relative_path in HIGH_PRIORITY_FILES or relative_path.startswith(HIGH_PRIORITY_PREFIXES):
        return "high"
    if relative_path in MEDIUM_PRIORITY_FILES or relative_path.startswith(MEDIUM_PRIORITY_PREFIXES):
        return "medium"
    return "low"


def _format_bucket_line(bucket: str, paths: Iterable[str]) -> str | None:
    collected = list(paths)
    if not collected:
        return None

    preview = ", ".join(collected[:MAX_PATHS_PER_BUCKET])
    if len(collected) > MAX_PATHS_PER_BUCKET:
        preview += f", ... (+{len(collected) - MAX_PATHS_PER_BUCKET})"

    if bucket == "high":
        return f"🔴 High: Local observer scan detected rule-surface changes in {preview}."
    if bucket == "medium":
        return f"🟡 Medium: Local observer scan detected active workspace changes in {preview}."
    return f"🟢 Low: Local observer scan detected routine workspace churn in {preview}."


def _build_observer_lines(recent_files: Iterable[str]) -> list[str]:
    buckets = {"high": [], "medium": [], "low": []}
    for relative_path in recent_files:
        buckets[_bucket_for_path(relative_path)].append(relative_path)

    lines = [
        _format_bucket_line("high", buckets["high"]),
        _format_bucket_line("medium", buckets["medium"]),
        _format_bucket_line("low", buckets["low"]),
    ]
    rendered = [line for line in lines if line]
    if rendered:
        return rendered
    return ["🟢 Low: No recent workspace changes detected during local observer scan."]


def _append_observation_entry(observations_path: Path, target_date: str, lines: Sequence[str]) -> None:
    observations_path.parent.mkdir(parents=True, exist_ok=True)
    existing = observations_path.read_text(encoding="utf-8") if observations_path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    if existing and not existing.endswith("\n\n"):
        existing += "\n"

    entry = "\n".join([f"Date: {target_date}", "", *lines]).rstrip() + "\n\n"
    observations_path.write_text(existing + entry, encoding="utf-8")


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

    state = heartbeat_state.load_or_init_state(state_path)
    last_success_at = _parse_datetime(state["observer"].get("last_success_at"))
    scan_start = _utc_now() - timedelta(days=7)
    if last_success_at is not None and last_success_at > scan_start:
        scan_start = last_success_at

    recent_files = _iter_recent_files(workspace_root, scan_start)
    observer_lines = _build_observer_lines(recent_files)
    _append_observation_entry(observations_path, target_date, observer_lines)
    heartbeat_state.persist_success("observer", path=state_path, target_date=target_date)
    print(f"[observer] Wrote Date: {target_date} entry to {observations_path}.")
    print(f"[observer] Recent files considered: {len(recent_files)}")


def _prune_observations(content: str, *, target_date: str) -> tuple[str, int, int, int, int]:
    target_day = date.fromisoformat(target_date)
    low_cutoff = target_day - timedelta(days=LOW_PRIORITY_RETENTION_DAYS)
    review_cutoff = target_day - timedelta(days=RECENT_REVIEW_DAYS)

    current_entry_date: date | None = None
    reviewed_entries = 0
    recent_high = 0
    recent_medium = 0
    removed_low = 0
    kept_lines: list[str] = []

    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("Date: "):
            try:
                current_entry_date = date.fromisoformat(stripped.split(": ", 1)[1])
                reviewed_entries += 1
            except ValueError:
                current_entry_date = None

        if current_entry_date is not None and current_entry_date >= review_cutoff:
            if stripped.startswith("🔴 High:"):
                recent_high += 1
            elif stripped.startswith("🟡 Medium:"):
                recent_medium += 1

        if current_entry_date is not None and current_entry_date < low_cutoff and stripped.startswith("🟢 Low:"):
            removed_low += 1
            continue

        kept_lines.append(raw_line)

    pruned = "\n".join(kept_lines)
    if content.endswith("\n"):
        pruned += "\n"
    return pruned, reviewed_entries, recent_high, recent_medium, removed_low


def _write_reflector_report(
    report_path: Path,
    *,
    target_date: str,
    reviewed_entries: int,
    recent_high: int,
    recent_medium: int,
    removed_low: int,
    promotion_count: int,
    rules_path: Path,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_lines = [
        "# AI Heartbeat Local Reflector Report",
        "",
        f"Date: {target_date}",
        "",
        "## Summary",
        f"- Reviewed entries: {reviewed_entries}",
        f"- Recent high-priority lines: {recent_high}",
        f"- Recent medium-priority lines: {recent_medium}",
        f"- Removed stale low-priority lines: {removed_low}",
        f"- Promoted operational rules: {promotion_count}",
        f"- Rules output: {rules_path.as_posix()}",
        "",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")


def _build_reflection_rules(recent_high: int, recent_medium: int) -> list[str]:
    promoted_rules: list[str] = []
    if recent_high:
        promoted_rules.extend(
            [
                "Treat AGENTS.md, rules/, docs/specs/, and docs/plans/ as a single high-priority review surface whenever AI Heartbeat behavior changes.",
                "When rule-surface files change, re-check SessionStart hook behavior and documentation together before considering the change complete.",
            ]
        )

    if recent_medium:
        promoted_rules.extend(
            [
                "Treat periodic_jobs/, docs/, tools/, and m/ changes as active workspace signals that should inform reflector review before promoting or pruning memory.",
                "Prefer promoting verified workflow or routing changes into rules/ before deleting the corresponding OBSERVATIONS entries.",
            ]
        )

    if not promoted_rules:
        promoted_rules.append("No promotable operational rules were detected in the current reflector window.")

    return promoted_rules


def _write_rules_promotions(
    rules_path: Path,
    *,
    target_date: str,
    reviewed_entries: int,
    recent_high: int,
    recent_medium: int,
) -> int:
    rules_path.parent.mkdir(parents=True, exist_ok=True)
    promoted_rules = _build_reflection_rules(recent_high, recent_medium)
    bullet_lines = [f"- {rule}" for rule in promoted_rules]
    lines = [
        "# AI Heartbeat Local Reflections",
        "",
        "This file is generated by `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py` during the local reflector phase.",
        "It stores the currently promoted operational rules distilled from recent OBSERVATIONS windows.",
        "",
        f"Last Updated: {target_date}",
        f"Reviewed Entries: {reviewed_entries}",
        f"Recent High Signals: {recent_high}",
        f"Recent Medium Signals: {recent_medium}",
        "",
        "## Promoted Rules",
        *bullet_lines,
        "",
        "## Scope",
        "- This is a controlled local-reflector output, not a general-purpose skill.",
        "- Update this file only through the AI Heartbeat local reflector or an intentional manual edit.",
        "",
    ]
    rules_path.write_text("\n".join(lines), encoding="utf-8")
    return 0 if promoted_rules == ["No promotable operational rules were detected in the current reflector window."] else len(promoted_rules)


def run_reflector_local(
    *,
    observations_path: Path,
    report_path: Path,
    rules_promotion_path: Path,
    state_path: str | None,
    target_date: str,
) -> None:
    content = observations_path.read_text(encoding="utf-8") if observations_path.exists() else ""
    pruned_content, reviewed_entries, recent_high, recent_medium, removed_low = _prune_observations(content, target_date=target_date)
    if pruned_content != content:
        observations_path.write_text(pruned_content, encoding="utf-8")
        print(f"[reflector] Pruned {removed_low} stale low-priority lines from {observations_path}.")
    else:
        print("[reflector] No OBSERVATIONS cleanup was needed.")

    promotion_count = _write_rules_promotions(
        rules_promotion_path,
        target_date=target_date,
        reviewed_entries=reviewed_entries,
        recent_high=recent_high,
        recent_medium=recent_medium,
    )
    print(f"[reflector] Wrote promoted operational rules to {rules_promotion_path}.")

    _write_reflector_report(
        report_path,
        target_date=target_date,
        reviewed_entries=reviewed_entries,
        recent_high=recent_high,
        recent_medium=recent_medium,
        removed_low=removed_low,
        promotion_count=promotion_count,
        rules_path=rules_promotion_path,
    )
    heartbeat_state.persist_success("reflector", path=state_path, target_date=target_date)
    print(f"[reflector] Wrote local reflector report to {report_path}.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    workspace_root = _resolve_workspace_root(args.workspace_root)
    observations_path = _resolve_observations_path(args.observations_path, workspace_root)
    report_path = _resolve_report_path(args.report_path, args.state_path)
    rules_promotion_path = _resolve_rules_promotion_path(args.rules_promotion_path)
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
                    observations_path=observations_path,
                    report_path=report_path,
                    rules_promotion_path=rules_promotion_path,
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