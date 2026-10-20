"""Rule NAME-001: Node name uniqueness check across active nodes."""

from __future__ import annotations

from collections import Counter
from typing import List

from launch_inspector.models import DiagnosticFinding, LaunchSystemModel, Severity
from launch_inspector.rules.base import BaseRule


class DuplicateNodeNameRule(BaseRule):
    rule_id = "NAME-001"
    name = "Duplicate Node Names"
    description = "Checks that all active nodes have globally unique fully qualified names"
    default_severity = Severity.ERROR

    def check(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        findings: List[DiagnosticFinding] = []
        name_counts = Counter(node.full_name for node in model.nodes)

        for name, count in name_counts.items():
            if count > 1:
                findings.append(
                    DiagnosticFinding(
                        rule_id=self.rule_id,
                        severity=self.default_severity,
                        entity=name,
                        message=(
                            f"Duplicate node name detected: '{name}' is declared {count} times. "
                            "In ROS 2, nodes sharing the same fully qualified name will collide in DDS discovery, "
                            "leading to shutdown of one or both nodes."
                        ),
                        fix_hint=(
                            f"Rename one of the '{name}' nodes or place them in distinct namespaces "
                            "using PushRosNamespace or the namespace='...' argument."
                        ),
                    )
                )

        return findings
