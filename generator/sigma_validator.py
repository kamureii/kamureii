"""Detection-as-Code validator for Sigma bio rules."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

VALID_STATUSES = {"experimental", "test", "stable", "production"}
VALID_LEVELS = {"informational", "low", "medium", "high", "critical"}
REQUIRED_TOP_KEYS = ("title", "id", "status", "author", "logsource", "detection", "level")
CONDITION_KEYWORDS = {"and", "or", "not", "all", "of", "them", "1", "any"}


@dataclass
class SigmaValidationResult:
    passed: bool
    rule: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def validate_sigma_dict(rule: Any) -> SigmaValidationResult:
    errors: list[str] = []
    if not isinstance(rule, dict):
        return SigmaValidationResult(passed=False, errors=["Root YAML document must be a mapping."])

    for key in REQUIRED_TOP_KEYS:
        if key not in rule or rule[key] in (None, "", []):
            errors.append(f"Missing required Sigma field: '{key}'.")

    status = str(rule.get("status", "")).lower()
    if status and status not in VALID_STATUSES:
        errors.append(f"Invalid status '{status}'. Expected one of {sorted(VALID_STATUSES)}.")

    level = str(rule.get("level", "")).lower()
    if level and level not in VALID_LEVELS:
        errors.append(f"Invalid level '{level}'. Expected one of {sorted(VALID_LEVELS)}.")

    logsource = rule.get("logsource")
    if not isinstance(logsource, dict) or not any(
        k in logsource for k in ("category", "product", "service")
    ):
        errors.append("logsource must define at least one of: category, product, service.")

    detection = rule.get("detection")
    if not isinstance(detection, dict):
        errors.append("detection must be a mapping containing selections and a condition.")
    else:
        condition = detection.get("condition")
        if not isinstance(condition, str) or not condition.strip():
            errors.append("detection.condition must be a non-empty string.")
        else:
            defined_selections = {k for k in detection.keys() if k != "condition"}
            if not defined_selections:
                errors.append("detection must declare at least one selection block.")
            tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_*]*", condition)
            for tok in tokens:
                low = tok.lower()
                if low in CONDITION_KEYWORDS:
                    continue
                if "*" in tok:
                    prefix = tok.replace("*", "")
                    if not any(sel.startswith(prefix) for sel in defined_selections):
                        errors.append(f"Wildcard condition token '{tok}' matches no selection block.")
                elif tok not in defined_selections:
                    errors.append(f"Condition references undefined selection '{tok}'.")

    return SigmaValidationResult(passed=len(errors) == 0, rule=rule, errors=errors)


def validate_sigma_file(path: Path) -> SigmaValidationResult:
    try:
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
    except Exception as exc:  # noqa: BLE001
        return SigmaValidationResult(passed=False, errors=[f"Failed to parse YAML: {exc}"])
    return validate_sigma_dict(data)
