"""
JSON conversion pipeline for the rule-based KYC email simplifier.

This module reads a JSON payload containing one or more templates, rewrites the
specified text field using the EmailSimplifier rules, and writes the simplified
payload back to disk. It keeps the existing JSON shape intact and merely adds
(or overwrites) the configured output field with the simplified content.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, List, MutableMapping, MutableSequence

from simplifier import EmailSimplifier


class JsonSimplifier:
    """Apply the EmailSimplifier to JSON payloads.

    The converter expects either a list of objects or a dictionary containing a
    list of objects. Each object must have a text field (``text_field``) that
    contains the template content to simplify. A new field (``output_field``)
    is added with the rewritten text, leaving the original intact.
    """

    def __init__(
        self,
        *,
        config_path: str = "config.yaml",
        text_field: str = "text",
        output_field: str = "simplified_text",
    ) -> None:
        self.simplifier = EmailSimplifier(config_path)
        self.text_field = text_field
        self.output_field = output_field

    def simplify_payload(self, payload: Any) -> Any:
        """Simplify every template inside the provided JSON payload."""
        if isinstance(payload, MutableSequence):
            return [self._simplify_entry(entry) for entry in payload]
        if isinstance(payload, MutableMapping):
            return {k: self.simplify_payload(v) if self._is_container(v) else v for k, v in payload.items()}  # type: ignore[return-value]
        return payload

    def _is_container(self, value: Any) -> bool:
        return isinstance(value, (MutableSequence, MutableMapping))

    def _simplify_entry(self, entry: Any) -> Any:
        """Simplify one entry if it looks like a template object."""
        if isinstance(entry, MutableMapping) and self.text_field in entry:
            original = entry[self.text_field]
            if not isinstance(original, str):
                raise TypeError(f"Expected '{self.text_field}' to be a string, got {type(original).__name__}")
            entry[self.output_field] = self.simplifier.simplify_text(original)
            return entry
        if isinstance(entry, MutableSequence):
            return [self._simplify_entry(item) for item in entry]
        return entry


def convert_json(
    input_path: str,
    output_path: str,
    *,
    config_path: str = "config.yaml",
    text_field: str = "text",
    output_field: str = "simplified_text",
) -> None:
    """Load a JSON file, simplify its templates, and write the result."""
    converter = JsonSimplifier(
        config_path=config_path,
        text_field=text_field,
        output_field=output_field,
    )

    payload = _load_json(input_path)
    simplified = converter.simplify_payload(payload)
    _write_json(output_path, simplified)


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, payload: Any) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simplify template text in a JSON file.")
    parser.add_argument("--input", required=True, help="Path to the source JSON file.")
    parser.add_argument("--output", required=True, help="Where to write the simplified JSON file.")
    parser.add_argument("--config", default="config.yaml", help="Path to the YAML rules file.")
    parser.add_argument("--text-field", default="text", help="JSON field name containing the template text.")
    parser.add_argument("--output-field", default="simplified_text", help="Field name for the rewritten content.")
    return parser


def main(argv: List[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    convert_json(
        args.input,
        args.output,
        config_path=args.config,
        text_field=args.text_field,
        output_field=args.output_field,
    )


if __name__ == "__main__":
    main()
