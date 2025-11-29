import re
import os
import yaml
from typing import Dict, Any, List

class EmailSimplifier:
    def __init__(self, config_path: str = "config.yaml") -> None:
        self.config = self._load_config(config_path)
        self.jargon_map: Dict[str, str] = self.config.get("jargon_map", {})
        self.tone_map: Dict[str, str] = self.config.get("tone_map", {})
        self.patterns: List[Dict[str, str]] = self.config.get("patterns", [])
        self.kyc_documents: Dict[str, str] = self.config.get("kyc_documents", {})
        self.sentence_length_limit: int = self.config.get("sentence_length_limit", 22)

    @staticmethod
    def _load_config(path: str) -> Dict[str, Any]:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}

    def simplify_text(self, text: str) -> str:
        if not text: return text
        text = re.sub(r"\s+", " ", text).strip()

        text = self._apply_word_map(text, self.jargon_map)
        text = self._apply_word_map(text, self.tone_map)
        text = self._apply_patterns(text, self.patterns)
        text = self._apply_kyc_doc_rules(text)
        text = self._rewrite_sentences(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _apply_word_map(self, text: str, mapping: Dict[str, str]) -> str:
        for raw, simple in mapping.items():
            text = re.sub(rf"\b{re.escape(raw)}\b", simple, text, flags=re.IGNORECASE)
        return text

    def _apply_patterns(self, text: str, patterns: List[Dict[str, str]]) -> str:
        for p in patterns:
            text = re.sub(re.escape(p["search"]), p["replace"], text, flags=re.IGNORECASE)
        return text

    def _apply_kyc_doc_rules(self, text: str) -> str:
        for raw, friendly in self.kyc_documents.items():
            text = re.sub(rf"\b{re.escape(raw)}\b", friendly, text, flags=re.IGNORECASE)
        return text

    def _rewrite_sentences(self, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        cleaned = []
        for s in sentences:
            s = s.strip()
            if not s: continue
            if len(s.split()) > self.sentence_length_limit and "," in s:
                parts = [p.strip() for p in s.split(",")]
                cleaned.append(parts[0] + ".")
                if len(parts) > 1:
                    cleaned.append(", ".join(parts[1:]) + ".")
                continue
            cleaned.append(s if s.endswith(('.', '?', '!')) else s + ".")
        return " ".join(cleaned)
