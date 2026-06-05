from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from rules.skills import pdf_to_markdown_cli as cli


def test_extract_message_text_prefers_content() -> None:
    data = {"choices": [{"message": {"content": "hello", "reasoning_content": "hidden"}}]}

    assert cli.extract_message_text(data) == "hello"


def test_extract_message_text_falls_back_to_reasoning_content() -> None:
    data = {"choices": [{"message": {"content": "", "reasoning_content": "ocr text"}}]}

    assert cli.extract_message_text(data) == "ocr text"


def test_extract_message_text_reads_list_content() -> None:
    data = {"choices": [{"message": {"content": [{"text": "a"}, {"text": "b"}]}}]}

    assert cli.extract_message_text(data) == "ab"


def test_extract_message_text_errors_on_empty_response() -> None:
    with pytest.raises(cli.CliError):
        cli.extract_message_text({"choices": [{"message": {"content": ""}}]})


def test_validate_page_range_rejects_invalid_values() -> None:
    with pytest.raises(cli.CliError):
        cli.validate_page_range(0, None)
    with pytest.raises(cli.CliError):
        cli.validate_page_range(3, 2)


def test_build_vlm_payload_contains_image_and_prompt() -> None:
    payload = cli.build_vlm_payload("abc123", "model-x")

    assert payload["model"] == "model-x"
    content = payload["messages"][1]["content"]
    assert content[0]["image_url"]["url"] == "data:image/jpeg;base64,abc123"
    assert content[1]["text"] == cli.OCR_USER_PROMPT


def test_run_docling_writes_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pdf_path = tmp_path / "input.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")
    output_path = tmp_path / "output.md"

    monkeypatch.setattr(cli, "convert_with_docling", lambda path: f"converted {path.name}")
    args = argparse.Namespace(command="docling", pdf=str(pdf_path), output=str(output_path), format="json")

    result = cli.run(args)

    assert output_path.read_text(encoding="utf-8") == "converted input.pdf"
    assert result["engine"] == "docling"
    assert result["chars"] == len("converted input.pdf")


def test_run_vlm_uses_page_range(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    pdf_path = tmp_path / "input.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")
    output_path = tmp_path / "output.md"
    captured = {}

    def fake_convert_with_vlm(**kwargs):
        captured.update(kwargs)
        return "vlm text"

    monkeypatch.setattr(cli, "convert_with_vlm", fake_convert_with_vlm)
    args = argparse.Namespace(
        command="vlm-ocr",
        pdf=str(pdf_path),
        output=str(output_path),
        format="json",
        api_base="http://localhost:1234/v1/",
        model="model-y",
        dpi=150,
        timeout=12,
        start_page=2,
        end_page=4,
    )

    result = cli.run(args)

    assert output_path.read_text(encoding="utf-8") == "vlm text"
    assert result["engine"] == "vlm-ocr"
    assert captured["start_page"] == 2
    assert captured["end_page"] == 4
    assert captured["dpi"] == 150


def test_doctor_reports_dependency_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "has_module", lambda name: name == "requests")

    result = cli.doctor(cli.DEFAULT_API_BASE, cli.DEFAULT_MODEL, check_lmstudio=False)

    assert result["dependencies"]["requests"] is True
    assert result["dependencies"]["docling"] is False
    assert result["lmstudio"]["checked"] is False
