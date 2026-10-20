"""Rules QOS-001, TYPE-001, and ORPHAN-001: Communication contract validation."""

from __future__ import annotations

from typing import List

from launch_inspector.models import DiagnosticFinding, LaunchSystemModel, Severity
from launch_inspector.rules.base import BaseRule


class QoSSpecificationRule(BaseRule):
    rule_id = "QOS-001"
    name = "QoS Profile Compatibility"
    description = "Checks that publishers and subscribers on the same topic have compatible DDS QoS profiles"
    default_severity = Severity.ERROR

    def check(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        findings: List[DiagnosticFinding] = []
        topics = model.get_topics()

        for topic_name, endpoints in topics.items():
            pubs = endpoints["pubs"]
            subs = endpoints["subs"]

            for pub in pubs:
                for sub in subs:
                    compatible, reason = pub.qos.is_compatible_with(sub.qos)
                    if not compatible:
                        findings.append(
                            DiagnosticFinding(
                                rule_id=self.rule_id,
                                severity=self.default_severity,
                                entity=topic_name,
                                message=(
                                    f"QoS incompatibility on topic '{topic_name}': "
                                    f"Publisher '{pub.node_full_name}' and Subscriber '{sub.node_full_name}' are incompatible: {reason}. "
                                    "Under DDS QoS contract rules, messages will be silently discarded."
                                ),
                                fix_hint=(
                                    "Align QoS profiles between publisher and subscriber "
                                    "(e.g. set Subscriber to Best Effort, or Publisher to Reliable)."
                                ),
                            )
                        )

        return findings


class MessageTypeRule(BaseRule):
    rule_id = "TYPE-001"
    name = "Message Type Compatibility"
    description = "Checks that all publishers and subscribers on a topic agree on the message type"
    default_severity = Severity.ERROR

    def check(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        findings: List[DiagnosticFinding] = []
        topics = model.get_topics()

        for topic_name, endpoints in topics.items():
            all_eps = endpoints["pubs"] + endpoints["subs"]
            types_seen = {}
            for ep in all_eps:
                if ep.message_type is not None:
                    types_seen.setdefault(ep.message_type, []).append(ep.node_full_name)

            if len(types_seen) > 1:
                type_summary = ", ".join(
                    f"'{m_type}' by {', '.join(nodes)}"
                    for m_type, nodes in types_seen.items()
                )
                findings.append(
                    DiagnosticFinding(
                        rule_id=self.rule_id,
                        severity=self.default_severity,
                        entity=topic_name,
                        message=(
                            f"Conflicting message types on topic '{topic_name}': {type_summary}. "
                            "ROS 2 DDS middleware will reject connection between these nodes."
                        ),
                        fix_hint="Update topic remapping or node implementations so all participants use the same message type.",
                    )
                )

        return findings


class OrphanTopicRule(BaseRule):
    rule_id = "ORPHAN-001"
    name = "Orphaned Topic"
    description = "Warns when a topic has subscribers with no publishers, or publishers with no subscribers"
    default_severity = Severity.INFO

    def check(self, model: LaunchSystemModel) -> List[DiagnosticFinding]:
        findings: List[DiagnosticFinding] = []
        topics = model.get_topics()

        # Exclude standard global broadcast topics like /tf or /rosout
        ignore_topics = {"/tf", "/tf_static", "/rosout", "/diagnostics", "/parameter_events"}

        for topic_name, endpoints in topics.items():
            if topic_name in ignore_topics:
                continue

            pubs = endpoints["pubs"]
            subs = endpoints["subs"]

            if pubs and not subs:
                pub_names = ", ".join(ep.node_full_name for ep in pubs)
                findings.append(
                    DiagnosticFinding(
                        rule_id=self.rule_id,
                        severity=self.default_severity,
                        entity=topic_name,
                        message=f"Topic '{topic_name}' is published by [{pub_names}] but has 0 subscribers in this launch.",
                        fix_hint="Verify if subscriber nodes are missing from the launch file or remap to an active subscriber.",
                    )
                )
            elif subs and not pubs:
                sub_names = ", ".join(ep.node_full_name for ep in subs)
                findings.append(
                    DiagnosticFinding(
                        rule_id=self.rule_id,
                        severity=Severity.WARNING,
                        entity=topic_name,
                        message=f"Topic '{topic_name}' is subscribed by [{sub_names}] but has 0 publishers in this launch.",
                        fix_hint="Ensure the producing driver or node is launched or remap to an available topic.",
                    )
                )

        return findings
