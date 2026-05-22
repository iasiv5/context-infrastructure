from __future__ import annotations

import importlib.util
import json
import sys
import types
from contextlib import contextmanager
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
SRC_DIR = TESTS_DIR.parent / "src" / "v0"
OBSERVER_PATH = SRC_DIR / "observer.py"
REFLECTOR_PATH = SRC_DIR / "reflector.py"
STATE_PATH = SRC_DIR / "heartbeat_state.py"


class _SuccessfulClient:
    def create_session(self, title: str) -> str:
        return "session-1"

    def send_message(self, session_id: str, prompt: str, model_id: str | None = None):
        return {"session_id": session_id, "model_id": model_id}

    def wait_for_session_complete(self, session_id: str) -> bool:
        return True

    def delete_session(self, session_id: str) -> bool:
        return True


class _NullSessionClient:
    def create_session(self, title: str):
        return None


def _load_heartbeat_state(state_path: Path):
    spec = importlib.util.spec_from_file_location("heartbeat_state", STATE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["heartbeat_state"] = module
    spec.loader.exec_module(module)
    module.STATE_PATH = state_path
    return module


@contextmanager
def _loaded_script(module_name: str, module_path: Path, client_cls, state_path: Path):
    originals = {
        "heartbeat_state": sys.modules.get("heartbeat_state"),
        "opencode_client": sys.modules.get("opencode_client"),
        module_name: sys.modules.get(module_name),
    }
    heartbeat_state = _load_heartbeat_state(state_path)
    client_module = types.ModuleType("opencode_client")
    client_module.OpenCodeClient = client_cls
    sys.modules["opencode_client"] = client_module

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    try:
        yield module, heartbeat_state
    finally:
        for name, original in originals.items():
            if original is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original


@contextmanager
def _patched_argv(*args: str):
    original = sys.argv[:]
    sys.argv = list(args)
    try:
        yield
    finally:
        sys.argv = original


def test_observer_skip_records_skipped_status(tmp_path: Path) -> None:
    observations_path = tmp_path / "OBSERVATIONS.md"
    observations_path.write_text("Date: 2026-05-22\n", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"

    with _loaded_script("heartbeat_observer", OBSERVER_PATH, _SuccessfulClient, state_path) as (observer, _):
        observer.OBSERVATIONS_PATH = str(observations_path)
        with _patched_argv("observer.py", "2026-05-22"):
            observer.main()

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_status"] == "skipped"
    assert state["observer"]["last_target_date"] == "2026-05-22"
    assert state["observer"]["last_success_at"] is None


def test_observer_success_records_success_status(tmp_path: Path) -> None:
    observations_path = tmp_path / "OBSERVATIONS.md"
    observations_path.write_text("", encoding="utf-8")
    state_path = tmp_path / "heartbeat_status.json"

    with _loaded_script("heartbeat_observer", OBSERVER_PATH, _SuccessfulClient, state_path) as (observer, _):
        observer.OBSERVATIONS_PATH = str(observations_path)
        with _patched_argv("observer.py", "2026-05-22"):
            observer.main()

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["observer"]["last_status"] == "success"
    assert state["observer"]["last_target_date"] == "2026-05-22"
    assert state["observer"]["last_success_at"] is not None


def test_reflector_success_records_success_status(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"

    with _loaded_script("heartbeat_reflector", REFLECTOR_PATH, _SuccessfulClient, state_path) as (reflector, _):
        with _patched_argv("reflector.py"):
            reflector.main()

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["reflector"]["last_status"] == "success"
    assert state["reflector"]["last_success_at"] is not None


def test_reflector_failure_records_failed_status(tmp_path: Path) -> None:
    state_path = tmp_path / "heartbeat_status.json"

    with _loaded_script("heartbeat_reflector", REFLECTOR_PATH, _NullSessionClient, state_path) as (reflector, _):
        with _patched_argv("reflector.py"):
            reflector.main()

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["reflector"]["last_status"] == "failed"
    assert state["reflector"]["last_success_at"] is None