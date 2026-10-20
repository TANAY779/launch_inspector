"""Graphviz DOT generator for ROS 2 launch system models."""

from __future__ import annotations

import re
from typing import Dict, List

from launch_inspector.models import LaunchSystemModel


def _sanitize_id(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip("/"))
    return cleaned if cleaned else "root"


class DotVisualizer:
    """Generates Graphviz DOT graph strings representing the node/topic architecture."""

    def __init__(self, model: LaunchSystemModel):
        self.model = model

    def generate(self) -> str:
        lines: List[str] = [
            "digraph G {",
            "  rankdir=LR;",
            "  node [fontname=\"sans-serif\", fontsize=10];",
            "  edge [fontname=\"sans-serif\", fontsize=9];",
        ]

        # Group nodes by namespace into subgraphs
        ns_map: Dict[str, List] = {}
        for node in self.model.nodes:
            ns = node.namespace.strip("/") or "root"
            ns_map.setdefault(ns, []).append(node)

        for ns, nodes in ns_map.items():
            cluster_id = f"cluster_{_sanitize_id(ns)}"
            lines.append(f"  subgraph {cluster_id} {{")
            lines.append(f"    label = \"Namespace: /{ns if ns != 'root' else ''}\";")
            lines.append("    style = rounded;")
            lines.append("    color = lightgrey;")
            for node in nodes:
                node_id = f"node_{_sanitize_id(node.full_name)}"
                label = f"{node.name}\\n({node.package or ''}/{node.executable or ''})"
                lines.append(f"    {node_id} [label=\"{label}\", shape=box, style=filled, fillcolor=white];")
            lines.append("  }")

        # Render topics as ellipses
        topic_map = self.model.get_topics()
        for topic_name, endpoints in topic_map.items():
            topic_id = f"topic_{_sanitize_id(topic_name)}"
            m_types = {ep.message_type for ep in endpoints["pubs"] + endpoints["subs"] if ep.message_type}
            t_label = f"{topic_name}\\n[{', '.join(sorted(m_types))}]" if m_types else topic_name
            lines.append(f"  {topic_id} [label=\"{t_label}\", shape=ellipse, style=filled, fillcolor=\"#E8F0FE\", color=\"#4285F4\"];")

            for pub in endpoints["pubs"]:
                pub_id = f"node_{_sanitize_id(pub.node_full_name)}"
                lines.append(f"  {pub_id} -> {topic_id};")

            for sub in endpoints["subs"]:
                sub_id = f"node_{_sanitize_id(sub.node_full_name)}"
                lines.append(f"  {topic_id} -> {sub_id};")

        lines.append("}")
        return "\n".join(lines)
