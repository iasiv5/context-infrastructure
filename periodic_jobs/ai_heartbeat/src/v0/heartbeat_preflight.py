from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import heartbeat_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Heartbeat preflight reminder checker")
    parser.add_argument(
        "--state-path",
        help="Override the default heartbeat status file path.",
    )
    parser.add_argument(
        "--mark-prompted",
        nargs="+",
        choices=tuple(heartbeat_state.TASK_INTERVALS.keys()),
        help="Record that the listed tasks were prompted today without running them.",
    )
    parser.add_argument(
        "--hook-mode",
        action="store_true",
        help="Emit a concise pre-session hook message and mark due reminders as prompted.",
    )
    return parser


def run_preflight(
    *,
    state_path: str | Path | None = None,
    now: datetime | None = None,
) -> list[dict[str, Any]]:
    state = heartbeat_state.load_or_init_state(state_path)
    return heartbeat_state.collect_due_tasks(state, now=now)


def mark_prompted(
    tasks: Sequence[str],
    *,
    state_path: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    state = heartbeat_state.load_or_init_state(state_path)
    for task_name in tasks:
        heartbeat_state.record_prompted(state, task_name, now=now)
    heartbeat_state.save_state(state, state_path)
    return state


def _format_elapsed(delta: Any) -> str:
    if delta is None:
        return "last success: never"

    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        total_seconds = 0

    days, remainder = divmod(total_seconds, 86400)
    hours, _ = divmod(remainder, 3600)
    if days:
        return f"overdue by {days}d {hours}h"
    return f"overdue by {hours}h"


def format_reminder(reminder: dict[str, Any]) -> str:
    task_name = reminder["task"]
    last_success_at = reminder.get("last_success_at") or "never"
    overdue_by = _format_elapsed(reminder.get("overdue_by"))
    return f"{task_name}: {overdue_by}; last success at {last_success_at}"


def build_hook_message(
    reminders: Sequence[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> str:
    current_time = now or datetime.now(timezone.utc)
    lines = ["AI Heartbeat 会前提醒："]

    for reminder in reminders:
        task_name = reminder["task"]
        last_success_at = reminder.get("last_success_at")
        if last_success_at:
            due_text = _format_elapsed(reminder.get("overdue_by"))
            lines.append(f"- {task_name}：{due_text}；上次成功时间 {last_success_at}")
        else:
            lines.append(f"- {task_name}：还没有成功执行记录")

    lines.append("如果你现在要补跑，请在终端手动执行：")
    for reminder in reminders:
        task_name = reminder["task"]
        if task_name == "observer":
            lines.append("- observer（L1，当天观测）")
            lines.append(
                f"  python periodic_jobs/ai_heartbeat/src/v0/observer.py {current_time.date().isoformat()}"
            )
        elif task_name == "reflector":
            lines.append("- reflector（L2，每周反思）")
            lines.append("  python periodic_jobs/ai_heartbeat/src/v0/reflector.py")

    lines.append("如果你使用本仓库的本地虚拟环境，可把 python 替换成 .\\.venv\\Scripts\\python.exe。")
    lines.append("如果这次先不执行，本次提示已记为今天已提醒，不会在同一天重复弹出。")
    return "\n".join(lines)


def run_hook(
    *,
    state_path: str | Path | None = None,
    now: datetime | None = None,
) -> str | None:
    current_time = now or datetime.now(timezone.utc)
    reminders = run_preflight(state_path=state_path, now=current_time)
    if not reminders:
        return None

    mark_prompted([item["task"] for item in reminders], state_path=state_path, now=current_time)
    return build_hook_message(reminders, now=current_time)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.hook_mode:
        message = run_hook(state_path=args.state_path)
        if message:
            print(message)
        return 0

    if args.mark_prompted:
        mark_prompted(args.mark_prompted, state_path=args.state_path)
        print("Marked prompted:", ", ".join(args.mark_prompted))
        return 0

    reminders = run_preflight(state_path=args.state_path)
    if not reminders:
        print("No heartbeat reminders due.")
        return 0

    print("Heartbeat reminders due:")
    for reminder in reminders:
        print(f"- {format_reminder(reminder)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())