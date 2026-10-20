"""JSON serialization for LaunchSystemModel."""

from __future__ import annotations

import json
from typing import Any, Dict

from launch_inspector.models import LaunchSystemModel


class JsonReporter:
    """Serializes the LaunchSystemModel to standard JSON."""

    def __init__(self, model: LaunchSystemModel):
        self.model = model

    def to_dict(self) -> Dict[str, Any]:
        return {
            "launch_path": self.model.launch_path,
            "arguments": self.model.arguments,
            "nodes": [
                {
                    "name": n.name,
                    "namespace": n.namespace,
                    "full_name": n.full_name,
                    "package": n.package,
                    "executable": n.executable,
                    "parameters": n.parameters,
                    "remappings": n.remappings,
                    "is_lifecycle": n.is_lifecycle,
                    "condition_active": n.condition_active,
                    "endpoints": [
                        {
                            "topic": ep.topic,
                            "direction": ep.direction.value,
                            "message_type": ep.message_type,
                            "original_name": ep.original_name,
                            "qos": {
                                "reliability": ep.qos.reliability.value,
                                "durability": ep.qos.durability.value,
                                "history": ep.qos.history.value,
                                "depth": ep.qos.depth,
                            },
                        }
                        for ep in n.endpoints
                    ],
                }
                for n in self.model.nodes
            ],
            "skipped_nodes": [
                {
                    "full_name": sk.full_name,
                    "package": sk.package,
                    "executable": sk.executable,
                }
                for sk in self.model.skipped_nodes
            ],
            "diagnostics": [
                {
                    "rule_id": d.rule_id,
                    "severity": d.severity.value,
                    "entity": d.entity,
                    "message": d.message,
                    "fix_hint": d.fix_hint,
                }
                for d in self.model.diagnostics
            ],
        }

    def generate(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
