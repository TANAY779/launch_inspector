"""SARIF (Static Analysis Results Interchange Format) v2.1.0 exporter for GitHub PR annotations."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from launch_inspector.models import LaunchSystemModel, Severity


class SarifReporter:
    """Exports diagnostic findings in standard OASIS SARIF v2.1.0 JSON format."""

    def __init__(self, model: LaunchSystemModel):
        self.model = model

    def to_dict(self) -> Dict[str, Any]:
        rules_dict: Dict[str, Dict[str, Any]] = {}
        results: List[Dict[str, Any]] = []

        file_uri = (
            f"file://{self.model.launch_path}"
            if self.model.launch_path
            else "file://launch_description.py"
        )

        for finding in self.model.diagnostics:
            # Map severity to SARIF level
            if finding.severity == Severity.ERROR:
                level = "error"
            elif finding.severity == Severity.WARNING:
                level = "warning"
            else:
                level = "note"

            if finding.rule_id not in rules_dict:
                rules_dict[finding.rule_id] = {
                    "id": finding.rule_id,
                    "name": finding.rule_id,
                    "shortDescription": {"text": finding.message[:100]},
                    "defaultConfiguration": {"level": level},
                }

            result_obj: Dict[str, Any] = {
                "ruleId": finding.rule_id,
                "level": level,
                "message": {
                    "text": finding.message
                    + (f"\nFix hint: {finding.fix_hint}" if finding.fix_hint else "")
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": file_uri},
                            "region": {"startLine": 1, "startColumn": 1},
                        }
                    }
                ],
            }
            results.append(result_obj)

        sarif_doc: Dict[str, Any] = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "launch-inspector",
                            "version": "0.1.0",
                            "informationUri": "https://github.com/ros-project/launch-inspector",
                            "rules": list(rules_dict.values()),
                        }
                    },
                    "results": results,
                }
            ],
        }
        return sarif_doc

    def generate(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
