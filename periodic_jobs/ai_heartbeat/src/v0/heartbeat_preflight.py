from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


MODULE_DIR = Path(__file__).resolve().parent
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import heartbeat_state


LOCAL_PYTHON_HINT = ".\\.venv\\Scripts\\python.exe"


def _local_runner_command(*tasks: str, target_date: str) -> str:
    task_args = " ".join(tasks)
    return (
        f"{LOCAL_PYTHON_HINT} periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py "
        f"{task_args} --target-date {target_date}"
    )


def _status_cli_command(task_name: str, target_date: str, *, status: str = "success") -> str:
    command = (
        f"{LOCAL_PYTHON_HINT} periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py "
        f"{task_name} --status {status} --target-date {target_date}"
    )
    if status == "failed":
        command += ' --error "<brief error>"'
    return command


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
    parser.add_argument(
        "--hook-dialog-spec",
        action="store_true",
        help="Emit a JSON dialog spec for SessionStart hooks and mark due reminders as prompted.",
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


def build_dialog_spec(
    reminders: Sequence[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    current_time = now or datetime.now(timezone.utc)
    due_tasks = [item["task"] for item in reminders]

    options = [
        {
            "action": "ignore",
            "label": "忽略",
            "description": "本次先不执行，继续当前会话",
        }
    ]

    if "observer" in due_tasks:
        options.append(
            {
                "action": "run_observer",
                "label": "执行 observer",
                "description": "运行 L1 当天观测",
            }
        )

    if "reflector" in due_tasks:
        options.append(
            {
                "action": "run_reflector",
                "label": "执行 reflector",
                "description": "运行 L2 每周反思",
            }
        )

    if {"observer", "reflector"}.issubset(due_tasks):
        options.append(
            {
                "action": "run_observer_and_reflector",
                "label": "执行 observer + reflector",
                "description": "先运行 observer，再运行 reflector",
            }
        )

    due_text = "、".join(due_tasks)
    question = f"检测到 AI Heartbeat 的 {due_text} 已过期，请选择处理方式。"

    return {
        "title": "AI Heartbeat 会前提醒",
        "question": question,
        "due_tasks": due_tasks,
        "target_date": current_time.date().isoformat(),
        "options": options,
    }


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

    target_date = current_time.date().isoformat()
    lines.append("如果你现在要处理，可直接运行本地执行器：")
    for reminder in reminders:
        task_name = reminder["task"]
        if task_name == "observer":
            lines.append("- observer（L1，当天观测）：更新 contexts/memory/OBSERVATIONS.md，不要修改 rules/。")
            lines.append(f"  执行命令：{_local_runner_command('observer', target_date=target_date)}")
            lines.append(f"  如需单独回写成功：{_status_cli_command('observer', target_date)}")
        elif task_name == "reflector":
            lines.append("- reflector（L2，每周反思）：基于 OBSERVATIONS.md 提炼规则并更新 rules/。")
            lines.append(f"  执行命令：{_local_runner_command('reflector', target_date=target_date)}")
            lines.append(f"  如需单独回写成功：{_status_cli_command('reflector', target_date)}")

    if {item["task"] for item in reminders} == {"observer", "reflector"}:
        lines.append(f"- 一次执行两个任务：{_local_runner_command('observer', 'reflector', target_date=target_date)}")

    lines.append("如果任务失败，可把上面的命令改成 --status failed --error \"<brief error>\"。")
    lines.append("这些提醒已经记为今天已提醒；如果这次先不执行，也不要再次调用 --mark-prompted。")
    return "\n".join(lines)


def run_hook_dialog_spec(
    *,
    state_path: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any] | None:
    current_time = now or datetime.now(timezone.utc)
    reminders = run_preflight(state_path=state_path, now=current_time)
    if not reminders:
        return None

    dialog_spec = build_dialog_spec(reminders, now=current_time)
    mark_prompted([item["task"] for item in reminders], state_path=state_path, now=current_time)
    return dialog_spec


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