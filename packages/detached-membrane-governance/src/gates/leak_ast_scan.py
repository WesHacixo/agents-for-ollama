#!/usr/bin/env python3
"""AST-based leak scanner for detached membrane Python core."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            parts: list[str] = []
            current: ast.AST = func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
                return ".".join(reversed(parts))
    return None


def _import_lines(node: ast.AST) -> list[str]:
    lines: list[str] = []
    if isinstance(node, ast.Import):
        for alias in node.names:
            lines.append(f"import {alias.name}")
    elif isinstance(node, ast.ImportFrom):
        module = node.module or ""
        lines.append(f"from {module}")
    return lines


def _iter_string_values(node: ast.AST) -> list[str]:
    values: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            values.append(child.value)
    return values


def scan_file(path: Path, rules: dict[str, Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [
            {
                "file": str(path),
                "line": exc.lineno or 1,
                "rule_id": "syntax_error",
                "snippet": str(exc),
            }
        ]

    forbidden_imports: list[str] = rules.get("forbidden_imports", [])
    forbidden_markers: list[str] = rules.get("forbidden_markers", [])
    execution_markers: list[str] = rules.get("forbidden_execution_markers", [])

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for line in _import_lines(node):
                for pattern in forbidden_imports:
                    if line.startswith(pattern) or pattern in line:
                        violations.append(
                            {
                                "file": str(path),
                                "line": node.lineno,
                                "rule_id": "forbidden_import",
                                "snippet": line.strip(),
                                "pattern": pattern,
                            }
                        )

        if isinstance(node, ast.Call):
            call_name = _call_name(node)
            if call_name:
                for marker in execution_markers:
                    key = marker.rstrip("(")
                    if call_name == key or call_name.endswith(f".{key}"):
                        violations.append(
                            {
                                "file": str(path),
                                "line": node.lineno,
                                "rule_id": "forbidden_execution_call",
                                "snippet": call_name,
                                "pattern": marker,
                            }
                        )

    for node in ast.walk(tree):
        for value in _iter_string_values(node):
            for marker in forbidden_markers:
                if marker in value:
                    violations.append(
                        {
                            "file": str(path),
                            "line": getattr(node, "lineno", 1),
                            "rule_id": "forbidden_marker_string",
                            "snippet": value[:120],
                            "pattern": marker,
                        }
                    )

    # Identifier / attribute markers outside strings (rg parity for code tokens)
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
        for name in names:
            for marker in forbidden_markers:
                if marker in name:
                    violations.append(
                        {
                            "file": str(path),
                            "line": getattr(node, "lineno", 1),
                            "rule_id": "forbidden_marker_name",
                            "snippet": name,
                            "pattern": marker,
                        }
                    )

    return violations


def scan_directory(target: Path, rules: dict[str, Any]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for py_file in sorted(target.glob("*.py")):
        violations.extend(scan_file(py_file, rules))
    return violations


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: leak_ast_scan.py <directory>", file=sys.stderr)
        return 2
    rules = json.loads(sys.stdin.read())
    target = Path(sys.argv[1])
    violations = scan_directory(target, rules)
    print(json.dumps({"violations": violations}, indent=2))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
