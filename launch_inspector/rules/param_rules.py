"""Rule PARAM-001: Parameter spelling and typo checking."""

from __future__ import annotations

import difflib
from typing import List

from launch_inspector.models import DiagnosticFinding, LaunchSystemModel, Severity
from launch_inspector.rules.base import BaseRule

KNOWN_STANDARD_PARAMS = [
    "use_sim_time",
    "publish_rate",
    "robot_description",
    "autostart",
    "wheel_separation",
    "wheel_radius",
    "linear.x.max_velocity",
    "linear.x.min_velocity",
    "angular.z.max_velocity",
    "laser_scan_topic",
    "odom_frame_id",
    "base_frame_id",
    "global_frame_id",
    "map_frame_id",
    "update_frequency",
    "transform_tolerance",
]


class ParameterTypoRule(BaseRule):
    rule_id = "PARAM-001"
    name = "Parameter Typo Checker"
    description = "Detects misspelled standard ROS 2 parameters using fuzzy string matching"
    default_severity = Severity.WARNING

    def check(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        findings: List[DiagnosticFinding] = []

        for node in model.nodes:
            for param_key in node.parameters.keys():
                # If it's already an exact match, skip
                if param_key in KNOWN_STANDARD_PARAMS:
                    continue

                # Fuzzy match against known standard parameters
                matches = difflib.get_close_matches(
                    param_key, KNOWN_STANDARD_PARAMS, n=1, cutoff=0.75
                )
                if matches and matches[0] != param_key:
                    best_match = matches[0]
                    findings.append(
                        DiagnosticFinding(
                            rule_id=self.rule_id,
                            severity=self.default_severity,
                            entity=f"{node.full_name}:{param_key}",
                            message=(
                                f"Suspicious parameter '{param_key}' on node '{node.full_name}'. "
                                f"Did you mean '{best_match}'?"
                            ),
                            fix_hint=f"Correct the parameter name in your launch file or YAML configuration to '{best_match}'.",
                        )
                    )

        return findings
