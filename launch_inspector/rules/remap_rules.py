"""Rule REMAP-001: Dangling or unmatched remapping rule detection."""

from __future__ import annotations

from typing import List

from launch_inspector.models import DiagnosticFinding, LaunchSystemModel, Severity
from launch_inspector.rules.base import BaseRule


class DanglingRemapRule(BaseRule):
    rule_id = "REMAP-001"
    name = "Dangling Remapping"
    description = "Warns when a remapping rule does not match any known topic advertised by the node"
    default_severity = Severity.WARNING

    def check(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        findings: List[DiagnosticFinding] = []

        for node in model.nodes:
            if not node.remappings:
                continue

            # Get all original endpoint names if known from stubs
            known_origins = {
                ep.original_name for ep in node.endpoints if ep.original_name is not None
            }

            for src, dst in node.remappings:
                # If we have stubs for this node but src is not in known_origins
                if known_origins and src not in known_origins and f"~/{src}" not in known_origins:
                    findings.append(
                        DiagnosticFinding(
                            rule_id=self.rule_id,
                            severity=self.default_severity,
                            entity=f"{node.full_name}:{src}",
                            message=(
                                f"Remapping source '{src}' -> '{dst}' on node '{node.full_name}' "
                                f"does not match any standard endpoints for package '{node.package}' "
                                f"(known endpoints: {', '.join(sorted(known_origins))})."
                            ),
                            fix_hint="Verify the exact topic name published or subscribed by the node before remapping.",
                        )
                    )

        return findings
