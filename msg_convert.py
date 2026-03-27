"""Outlook .msg conversion pipeline for the rule-based KYC email simplifier.

This module extracts metadata and body content from Microsoft Outlook ``.msg``
files, rewrites the message body using ``EmailSimplifier``, and returns a
human-readable representation suitable for client-facing KYC communication.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional

from simplifier import EmailSimplifier


try:
    import extract_msg  # type: ignore
except ImportError as exc:  # pragma: no cover - runtime dependency check
    extract_msg = None
    _extract_msg_import_error = exc
else:
    _extract_msg_import_error = None


@dataclass
class SimplifiedMessage:
    """Structured, human-readable output for one Outlook message."""

    subject: str
    sender: str
    to: str
    cc: str
    date: str
    original_body: str
    simplified_body: str


class OutlookMsgSimplifier:
    """Extract and simplify Outlook ``.msg`` email files."""

    def __init__(self, config_path: str = "config.yaml") -> None:
        self.simplifier = EmailSimplifier(config_path)

    def simplify_msg_file(self, msg_path: str) -> SimplifiedMessage:
        """Read an Outlook .msg file path and return a simplified email."""
        self._ensure_dependency()
        message = extract_msg.Message(msg_path)
        try:
            return self._to_simplified_message(message)
        finally:
            message.close()

    def simplify_msg_bytes(self, content: bytes) -> SimplifiedMessage:
        """Read an Outlook .msg payload from bytes and return a simplified email."""
        self._ensure_dependency()
        with tempfile.NamedTemporaryFile(suffix=".msg", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            return self.simplify_msg_file(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def _to_simplified_message(self, message: Any) -> SimplifiedMessage:
        body = self._choose_body(message)
        simplified = self.simplifier.simplify_text(body)
        return SimplifiedMessage(
            subject=(getattr(message, "subject", "") or "").strip(),
            sender=(getattr(message, "sender", "") or "").strip(),
            to=(getattr(message, "to", "") or "").strip(),
            cc=(getattr(message, "cc", "") or "").strip(),
            date=str(getattr(message, "date", "") or "").strip(),
            original_body=body,
            simplified_body=simplified,
        )

    @staticmethod
    def _choose_body(message: Any) -> str:
        body = (getattr(message, "body", "") or "").strip()
        if body:
            return body
        html_body: Optional[str] = getattr(message, "htmlBody", None)
        if html_body:
            return html_body.strip()
        return ""

    @staticmethod
    def _ensure_dependency() -> None:
        if extract_msg is None:
            raise RuntimeError(
                "Missing dependency 'extract_msg'. Try: \
"
                "1) pip install 'ebcdic>=1.1.1,<2' 'extract-msg' \
"
                "2) If install still fails on Python 3.12, create a Python 3.11 virtualenv for .msg parsing."
            ) from _extract_msg_import_error


def convert_msg(
    input_path: str,
    output_path: str,
    *,
    config_path: str = "config.yaml",
) -> Dict[str, Any]:
    """Convert one Outlook .msg file into simplified JSON output."""
    converter = OutlookMsgSimplifier(config_path)
    simplified_message = converter.simplify_msg_file(input_path)
    payload = asdict(simplified_message)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return payload


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert Outlook .msg email into simplified JSON.")
    parser.add_argument("--input", required=True, help="Path to source .msg file")
    parser.add_argument("--output", required=True, help="Path to write simplified JSON")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML rules file")
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()
    convert_msg(args.input, args.output, config_path=args.config)


if __name__ == "__main__":
    main()
