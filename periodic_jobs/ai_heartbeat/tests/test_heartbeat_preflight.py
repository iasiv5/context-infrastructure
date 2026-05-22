from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SRC_DIR = TESTS_DIR.parent / "src" / "v0"
STATE_MODULE_PATH = SRC_DIR / "heartbeat_state.py"
PREFLIGHT_MODULE_PATH = SRC_DIR / "heartbeat_preflight.py"

state_spec = importlib.util.spec_from_file_location("heartbeat_state", STATE_MODULE_PATH)
assert state_spec is not None and state_spec.loader is not None
heartbeat_state = importlib.util.module_from_spec(state_spec)
state_spec.loader.exec_module(heartbeat_state)

preflight_spec = importlib.util.spec_from_file_location("heartbeat_preflight", PREFLIGHT_MODULE_PATH)
assert preflight_spec is not None and preflight_spec.loader is not None
heartbeat_preflight = importlib.util.module_from_spec(preflight_spec)
preflight_spec.loader.exec_module(heartbeat_preflight)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def test_run_preflight_initializes_missing_state_and_reports_both_tasks(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    now = datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)

    reminders = heartbeat_preflight.run_preflight(state_path=state_path, now=now)

    assert [item["task"] for item in reminders] == ["observer", "reflector"]
    assert state_path.exists()


def test_run_preflight_respects_same_day_prompt_dedup(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    now = datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)
    state = heartbeat_state.default_state()
    state["observer"]["last_prompted_on"] = "2026-05-22"
    state["reflector"]["last_success_at"] = _iso(now - timedelta(days=9))
    heartbeat_state.save_state(state, state_path)

    reminders = heartbeat_preflight.run_preflight(state_path=state_path, now=now)

    assert [item["task"] for item in reminders] == ["reflector"]


def test_mark_prompted_only_updates_prompt_date(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    now = datetime(2026, 5, 22, 10, 0, tzinfo=timezone.utc)
    heartbeat_state.save_state(heartbeat_state.default_state(), state_path)

    heartbeat_preflight.mark_prompted(["observer"], state_path=state_path, now=now)

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_prompted_on"] == "2026-05-22"
    assert state["observer"]["last_attempt_at"] is None
    assert state["observer"]["last_status"] == "never"


def test_main_prints_human_readable_summary(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    heartbeat_state.save_state(heartbeat_state.default_state(), state_path)
    output = io.StringIO()

    with contextlib.redirect_stdout(output):
        exit_code = heartbeat_preflight.main(["--state-path", str(state_path)])

    rendered = output.getvalue()
    assert exit_code == 0
    assert "observer" in rendered
    assert "reflector" in rendered


def test_build_dialog_spec_shows_only_relevant_actions(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    now = datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)
    state = heartbeat_state.default_state()
    state["observer"]["last_success_at"] = _iso(now - timedelta(hours=1))
    state["reflector"]["last_success_at"] = _iso(now - timedelta(days=8))
    heartbeat_state.save_state(state, state_path)

    reminders = heartbeat_preflight.run_preflight(state_path=state_path, now=now)
    spec = heartbeat_preflight.build_dialog_spec(reminders, now=now)

    assert [option["label"] for option in spec["options"]] == ["忽略", "执行 reflector"]
    assert "commands" not in spec
    assert spec["target_date"] == "2026-05-22"


def test_run_hook_marks_prompted_and_returns_message(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    now = datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)

    message = heartbeat_preflight.run_hook(state_path=state_path, now=now)

    assert message is not None
    assert "AI Heartbeat 会前提醒" in message
    assert "observer" in message
    assert "reflector" in message
    assert "可直接运行本地执行器" in message
    assert "heartbeat_local_runner.py observer reflector --target-date 2026-05-22" in message
    assert ".\\.venv\\Scripts\\python.exe" in message

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_prompted_on"] == "2026-05-22"
    assert state["reflector"]["last_prompted_on"] == "2026-05-22"


def test_run_hook_dialog_spec_marks_prompted_and_returns_payload(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    now = datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)

    dialog_spec = heartbeat_preflight.run_hook_dialog_spec(state_path=state_path, now=now)

    assert dialog_spec is not None
    assert dialog_spec["due_tasks"] == ["observer", "reflector"]
    assert dialog_spec["target_date"] == "2026-05-22"
    assert [option["label"] for option in dialog_spec["options"]] == [
        "忽略",
        "执行 observer",
        "执行 reflector",
        "执行 observer + reflector",
    ]

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_prompted_on"] == "2026-05-22"
    assert state["reflector"]["last_prompted_on"] == "2026-05-22"


def test_hook_dialog_spec_mode_dedups_same_day(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    now = datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)
    state = heartbeat_state.default_state()
    state["observer"]["last_prompted_on"] = "2026-05-22"
    state["reflector"]["last_prompted_on"] = "2026-05-22"
    heartbeat_state.save_state(state, state_path)

    dialog_spec = heartbeat_preflight.run_hook_dialog_spec(state_path=state_path, now=now)

    assert dialog_spec is None


def test_hook_message_omits_irrelevant_actions_for_single_due_task(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"
    now = datetime(2026, 5, 22, 9, 0, tzinfo=timezone.utc)
    state = heartbeat_state.default_state()
    state["observer"]["last_success_at"] = _iso(now - timedelta(hours=1))
    state["reflector"]["last_success_at"] = _iso(now - timedelta(days=8))
    heartbeat_state.save_state(state, state_path)

    message = heartbeat_preflight.run_hook(state_path=state_path, now=now)
    assert message is not None
    assert "reflector" in message
    assert "reflector（L2，每周反思）" in message
    assert "执行 observer + reflector" not in message
