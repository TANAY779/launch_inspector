"""Core data models for ROS 2 launch inspection and system representation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ReliabilityPolicy(str, Enum):
    RELIABLE = "RELIABLE"
    BEST_EFFORT = "BEST_EFFORT"
    UNKNOWN = "UNKNOWN"


class DurabilityPolicy(str, Enum):
    VOLATILE = "VOLATILE"
    TRANSIENT_LOCAL = "TRANSIENT_LOCAL"
    UNKNOWN = "UNKNOWN"


class HistoryPolicy(str, Enum):
    KEEP_LAST = "KEEP_LAST"
    KEEP_ALL = "KEEP_ALL"
    UNKNOWN = "UNKNOWN"


@dataclass
class QoSProfile:
    reliability: ReliabilityPolicy = ReliabilityPolicy.UNKNOWN
    durability: DurabilityPolicy = DurabilityPolicy.UNKNOWN
    history: HistoryPolicy = HistoryPolicy.UNKNOWN
    depth: Optional[int] = None
    deadline_ms: Optional[float] = None
    lifespan_ms: Optional[float] = None

    def is_compatible_with(self, sub_qos: QoSProfile) -> Tuple[bool, Optional[str]]:
        """
        Check if publisher QoS is compatible with subscriber QoS according to DDS rules:
        - Offerer (Pub) reliability must be >= Requested (Sub) reliability.
          (If sub requests RELIABLE, pub must offer RELIABLE).
        - Offerer (Pub) durability must be >= Requested (Sub) durability.
          (If sub requests TRANSIENT_LOCAL, pub must offer TRANSIENT_LOCAL).
        """
        if self.reliability == ReliabilityPolicy.BEST_EFFORT and sub_qos.reliability == ReliabilityPolicy.RELIABLE:
            return False, "Publisher offers BEST_EFFORT but Subscriber requests RELIABLE"

        if self.durability == DurabilityPolicy.VOLATILE and sub_qos.durability == DurabilityPolicy.TRANSIENT_LOCAL:
            return False, "Publisher offers VOLATILE but Subscriber requests TRANSIENT_LOCAL"

        if self.deadline_ms is not None and sub_qos.deadline_ms is not None:
            if self.deadline_ms > sub_qos.deadline_ms:
                return False, f"Publisher deadline ({self.deadline_ms}ms) > Subscriber requested deadline ({sub_qos.deadline_ms}ms)"

        return True, None


class EndpointDirection(str, Enum):
    PUBLISHER = "PUBLISHER"
    SUBSCRIBER = "SUBSCRIBER"
    SERVICE_SERVER = "SERVICE_SERVER"
    SERVICE_CLIENT = "SERVICE_CLIENT"
    ACTION_SERVER = "ACTION_SERVER"
    ACTION_CLIENT = "ACTION_CLIENT"


@dataclass
class TopicEndpoint:
    topic: str
    node_full_name: str
    direction: EndpointDirection
    message_type: Optional[str] = None
    qos: QoSProfile = field(default_factory=QoSProfile)
    original_name: Optional[str] = None
    source: str = "launch"


@dataclass
class ResolvedNode:
    name: str
    namespace: str
    package: Optional[str] = None
    executable: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    remappings: List[Tuple[str, str]] = field(default_factory=list)
    is_lifecycle: bool = False
    condition_active: bool = True
    condition_expression: Optional[str] = None
    endpoints: List[TopicEndpoint] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        ns = self.namespace.strip("/")
        if not ns:
            return f"/{self.name}"
        return f"/{ns}/{self.name}"

    @property
    def publishers(self) -> List[TopicEndpoint]:
        return [ep for ep in self.endpoints if ep.direction == EndpointDirection.PUBLISHER]

    @property
    def subscribers(self) -> List[TopicEndpoint]:
        return [ep for ep in self.endpoints if ep.direction == EndpointDirection.SUBSCRIBER]


class Severity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class DiagnosticFinding:
    rule_id: str
    severity: Severity
    message: str
    entity: Optional[str] = None
    fix_hint: Optional[str] = None


@dataclass
class LaunchSystemModel:
    launch_path: Optional[str] = None
    arguments: Dict[str, str] = field(default_factory=dict)
    nodes: List[ResolvedNode] = field(default_factory=list)
    skipped_nodes: List[ResolvedNode] = field(default_factory=list)
    unresolved_items: List[str] = field(default_factory=list)
    diagnostics: List[DiagnosticFinding] = field(default_factory=list)

    @property
    def all_nodes(self) -> List[ResolvedNode]:
        return self.nodes

    def get_node(self, full_name: str) -> Optional[ResolvedNode]:
        for n in self.nodes:
            if n.full_name == full_name:
                return n
        return None

    def get_topics(self) -> Dict[str, Dict[str, List[TopicEndpoint]]]:
        """Returns topic -> {'pubs': [...], 'subs': [...]}"""
        topic_map: Dict[str, Dict[str, List[TopicEndpoint]]] = {}
        for node in self.nodes:
            for ep in node.endpoints:
                if ep.direction in (EndpointDirection.PUBLISHER, EndpointDirection.SUBSCRIBER):
                    if ep.topic not in topic_map:
                        topic_map[ep.topic] = {"pubs": [], "subs": []}
                    if ep.direction == EndpointDirection.PUBLISHER:
                        topic_map[ep.topic]["pubs"].append(ep)
                    else:
                        topic_map[ep.topic]["subs"].append(ep)
        return topic_map
