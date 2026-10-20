"""Rules package for launch_inspector."""

from launch_inspector.rules.base import BaseRule, RuleEngine
from launch_inspector.rules.name_rules import DuplicateNodeNameRule
from launch_inspector.rules.param_rules import ParameterTypoRule
from launch_inspector.rules.qos_type_rules import (
    MessageTypeRule,
    OrphanTopicRule,
    QoSSpecificationRule,
)
from launch_inspector.rules.remap_rules import DanglingRemapRule
from launch_inspector.rules.time_rules import SimTimeConsistencyRule


def get_default_rule_engine() -> RuleEngine:
    """Returns a RuleEngine pre-loaded with all standard audit rules."""
    engine = RuleEngine()
    engine.register(SimTimeConsistencyRule())
    engine.register(DuplicateNodeNameRule())
    engine.register(ParameterTypoRule())
    engine.register(DanglingRemapRule())
    engine.register(QoSSpecificationRule())
    engine.register(MessageTypeRule())
    engine.register(OrphanTopicRule())
    return engine


__all__ = [
    "BaseRule",
    "RuleEngine",
    "SimTimeConsistencyRule",
    "DuplicateNodeNameRule",
    "ParameterTypoRule",
    "DanglingRemapRule",
    "QoSSpecificationRule",
    "MessageTypeRule",
    "OrphanTopicRule",
    "get_default_rule_engine",
]
