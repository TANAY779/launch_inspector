"""Base interface and registry for static linter rules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from launch_inspector.models import DiagnosticFinding, LaunchSystemModel, Severity


class BaseRule(ABC):
    """Abstract base class for static inspection rules."""

    rule_id: str = "GEN-000"
    name: str = "Generic Rule"
    description: str = ""
    default_severity: Severity = Severity.WARNING

    @abstractmethod
    def check(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        """Inspect the LaunchSystemModel and return any findings."""
        pass


class RuleEngine:
    """Orchestrates execution of static lint rules over a LaunchSystemModel."""

    def __init__(self, rules: List[BaseRule] | None = None):
        self.rules: List[BaseRule] = rules if rules is not None else []

    def register(self, rule: BaseRule) -> None:
        self.rules.append(rule)

    def analyze(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        findings: List[DiagnosticFinding] = []
        for rule in self.rules:
            try:
                results = rule.check(model)
                findings.extend(results)
            except Exception as e:
                findings.append(
                    DiagnosticFinding(
                        rule_id="RULE-FAIL",
                        severity=Severity.ERROR,
                        message=f"Rule {rule.rule_id} crashed during execution: {e}",
                    )
                )
        model.diagnostics.extend(findings)
        return findings
