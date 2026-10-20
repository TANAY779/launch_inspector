"""Rule TIME-001: use_sim_time synchronization check across nodes."""

from __future__ import annotations

from typing import List

from launch_inspector.models import DiagnosticFinding, LaunchSystemModel, Severity
from launch_inspector.rules.base import BaseRule


class SimTimeConsistencyRule(BaseRule):
    rule_id = "TIME-001"
    name = "Sim Time Consistency"
    description = "Checks that all active nodes share the same use_sim_time setting"
    default_severity = Severity.ERROR

    def check(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        findings: List[DiagnosticFinding] = []
        if len(model.nodes) < 2:
            return findings

        sim_true_nodes = []
        sim_false_or_unset_nodes = []

        for node in model.nodes:
            val = node.parameters.get("use_sim_time")
            # If explicit True
            if val is True or str(val).lower() == "true":
                sim_true_nodes.append(node.full_name)
            else:
                sim_false_or_unset_nodes.append(node.full_name)

        if sim_true_nodes and sim_false_or_unset_nodes:
            true_str = ", ".join(sim_true_nodes[:3])
            false_str = ", ".join(sim_false_or_unset_nodes[:3])
            findings.append(
                DiagnosticFinding(
                    rule_id=self.rule_id,
                    severity=self.default_severity,
                    message=(
                        f"Inconsistent use_sim_time: {len(sim_true_nodes)} nodes set to True ({true_str}...), "
                        f"but {len(sim_false_or_unset_nodes)} nodes are False/unset ({false_str}...). "
                        "This causes severe TF timing extrapolation failures and message drops."
                    ),
                    fix_hint=(
                        "Set use_sim_time uniformly across all nodes using global launch configuration "
                        "or SetParameter(name='use_sim_time', value=LaunchConfiguration('use_sim_time'))."
                    ),
                )
            )

        return findings
