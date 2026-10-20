"""Mermaid graph generator for ROS 2 launch system models."""

from __future__ import annotations

import re
from typing import Dict, List, Set

from launch_inspector.models import LaunchSystemModel, Severity


def _sanitize_id(name: str) -> str:
    """Turn arbitrary node/topic names into valid Mermaid identifier tokens."""
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip("/"))
    return cleaned if cleaned else "root"


class MermaidVisualizer:
    """Generates Mermaid flowchart diagrams representing the resolved node graph."""

    def __init__(self, model: LaunchSystemModel):
        self.model = model

    def generate(self) -> str:
        lines: List[str] = ["flowchart LR"]

        # Group nodes by namespace
        ns_map: Dict[str, List] = {}
        for node in self.model.nodes:
            ns = node.namespace.strip("/") or "root"
            ns_map.setdefault(ns, []).append(node)

        # Build subgraphs for namespaces
        for ns, nodes in ns_map.items():
            ns_id = f"subgraph_{_sanitize_id(ns)}"
            lines.append(f"  subgraph {ns_id} [\"Namespace: /{ns if ns != 'root' else ''}\"]")
            for node in nodes:
                node_id = f"node_{_sanitize_id(node.full_name)}"
                label = f"{node.name}"
                if node.package and node.executable:
                    label += f"<br/><small>{node.package}/{node.executable}</small>"
                lines.append(f"    {node_id}[\"{label}\"]")
            lines.append("  end")

        # Topics and edges
        topic_map = self.model.get_topics()
        rendered_topics: Set[str] = set()

        for topic_name, endpoints in topic_map.items():
            topic_id = f"topic_{_sanitize_id(topic_name)}"
            
            # Determine message type label
            m_types = {ep.message_type for ep in endpoints["pubs"] + endpoints["subs"] if ep.message_type}
            type_label = f"<br/><small>{', '.join(sorted(m_types))}</small>" if m_types else ""

            if topic_name not in rendered_topics:
                lines.append(f"  {topic_id}([\"{topic_name}{type_label}\"])")
                rendered_topics.add(topic_name)

            for pub in endpoints["pubs"]:
                pub_node_id = f"node_{_sanitize_id(pub.node_full_name)}"
                lines.append(f"  {pub_node_id} --> {topic_id}")

            for sub in endpoints["subs"]:
                sub_node_id = f"node_{_sanitize_id(sub.node_full_name)}"
                lines.append(f"  {topic_id} --> {sub_node_id}")

        # Highlight nodes with findings
        error_nodes = set()
        warn_nodes = set()
        for f in self.model.diagnostics:
            if f.entity:
                target_entity = f.entity.split(":")[0]
                if f.severity == Severity.ERROR:
                    error_nodes.add(target_entity)
                elif f.severity == Severity.WARNING:
                    warn_nodes.add(target_entity)

        for err_node in error_nodes:
            n_id = f"node_{_sanitize_id(err_node)}"
            lines.append(f"  style {n_id} stroke:#e53e3e,stroke-width:3px,fill:#fff5f5")

        for warn_node in warn_nodes:
            if warn_node not in error_nodes:
                n_id = f"node_{_sanitize_id(warn_node)}"
                lines.append(f"  style {n_id} stroke:#dd6b20,stroke-width:2px,fill:#fffaf0")

        return "\n".join(lines)
