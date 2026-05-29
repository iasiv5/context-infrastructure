from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence


MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import heartbeat_state


def _resolve_now(now: datetime | None = None) -> datetime:
    if now is None:
        return datetime.now().astimezone()
    if now.tzinfo is None:
        return now.astimezone()
    return now


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
        help="Emit a concise pre-session hook message without changing prompted state.",
    )
    parser.add_argument(
        "--hook-dialog-spec",
        action="store_true",
        help="Emit a JSON dialog spec for SessionStart hooks without changing prompted state.",
    )
    parser.add_argument(
        "--command-spec",
        action="store_true",
        help="Emit a JSON command spec for /ai-heartbeat without changing prompted state.",
    )
    return parser


def run_preflight(
    *,
    state_path: str | Path | None = None,
    now: datetime | None = None,
    respect_prompted: bool = True,
) -> list[dict[str, Any]]:
    state = heartbeat_state.load_or_init_state(state_path)
    return heartbeat_state.collect_due_tasks(state, now=now, respect_prompted=respect_prompted)


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


def build_command_spec(
    reminders: Sequence[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    current_time = _resolve_now(now)
    due_tasks = [item["task"] for item in reminders]

    if due_tasks == ["observer"]:
        recommended_action = "observer"
    elif due_tasks == ["reflector"]:
        recommended_action = "reflector"
    elif due_tasks == ["observer", "reflector"]:
        recommended_action = "observer_and_reflector"
    else:
        recommended_action = "none"

    return {
        "due_tasks": due_tasks,
        "recommended_action": recommended_action,
        "target_date": current_time.date().isoformat(),
    }


def run_command_spec(
    *,
    state_path: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    current_time = _resolve_now(now)
    reminders = run_preflight(state_path=state_path, now=current_time, respect_prompted=False)
    return build_command_spec(reminders, now=current_time)


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


def build_dialog_spec(
    reminders: Sequence[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    current_time = _resolve_now(now)
    due_tasks = [item["task"] for item in reminders]

    due_text = "、".join(due_tasks)
    question = f"检测到 AI Heartbeat 的 {due_text} 已过期，请在当前 chat 中运行 /ai-heartbeat。"

    return {
        "title": "AI Heartbeat 会前提醒",
        "question": question,
        "due_tasks": due_tasks,
        "target_date": current_time.date().isoformat(),
        "recommended_command": "/ai-heartbeat",
        "options": [
            {
                "action": "dismiss",
                "label": "知道了",
                "description": "先关闭提醒；如果今天后面还有新会话，仍可能再次提醒",
            },
            {
                "action": "snooze_today",
                "label": "今天不再提醒",
                "description": "把这些任务记为今天已提醒，今天后续会话不再重复提醒",
            }
        ],
    }


def build_hook_message(
    reminders: Sequence[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> str:
    lines = ["AI Heartbeat 会前提醒："]

    for reminder in reminders:
        task_name = reminder["task"]
        last_success_at = reminder.get("last_success_at")
        if last_success_at:
            due_text = _format_elapsed(reminder.get("overdue_by"))
            lines.append(f"- {task_name}：{due_text}；上次成功时间 {last_success_at}")
        else:
            lines.append(f"- {task_name}：还没有成功执行记录")

    lines.append("如需处理，请在当前 chat 中运行 /ai-heartbeat。")
    lines.append("hook 只负责提醒，不会直接执行 observer 或 reflector。")
    return "\n".join(lines)


def run_hook_dialog_spec(
    *,
    state_path: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any] | None:
    current_time = _resolve_now(now)
    reminders = run_preflight(state_path=state_path, now=current_time)
    if not reminders:
        return None

    return build_dialog_spec(reminders, now=current_time)


def run_hook(
    *,
    state_path: str | Path | None = None,
    now: datetime | None = None,
) -> str | None:
    current_time = _resolve_now(now)
    reminders = run_preflight(state_path=state_path, now=current_time)
    if not reminders:
        return None

    return build_hook_message(reminders, now=current_time)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command_spec:
        command_spec = run_command_spec(state_path=args.state_path)
        print(json.dumps(command_spec, ensure_ascii=False))
        return 0

    if args.hook_dialog_spec:
        dialog_spec = run_hook_dialog_spec(state_path=args.state_path)
        if dialog_spec:
            print(json.dumps(dialog_spec, ensure_ascii=False))
        return 0

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