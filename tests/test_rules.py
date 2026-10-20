"""Unit tests for Phase 2: Static Rule Checker & Linter Engine."""

import pytest

from launch_inspector.models import (
    DurabilityPolicy,
    EndpointDirection,
    LaunchSystemModel,
    QoSProfile,
    ReliabilityPolicy,
    ResolvedNode,
    Severity,
    TopicEndpoint,
)
from launch_inspector.rules import get_default_rule_engine


def test_time_001_sim_time_split():
    model = LaunchSystemModel(
        nodes=[
            ResolvedNode(
                name="node_a",
                namespace="robot",
                parameters={"use_sim_time": True},
            ),
            ResolvedNode(
                name="node_b",
                namespace="robot",
                parameters={"use_sim_time": False},
            ),
        ]
    )

    engine = get_default_rule_engine()
    findings = engine.analyze(model)

    time_findings = [f for f in findings if f.rule_id == "TIME-001"]
    assert len(time_findings) == 1
    assert time_findings[0].severity == Severity.ERROR
    assert "Inconsistent use_sim_time" in time_findings[0].message


def test_name_001_duplicate_nodes():
    model = LaunchSystemModel(
        nodes=[
            ResolvedNode(name="camera", namespace="front"),
            ResolvedNode(name="camera", namespace="front"),
        ]
    )

    engine = get_default_rule_engine()
    findings = engine.analyze(model)

    name_findings = [f for f in findings if f.rule_id == "NAME-001"]
    assert len(name_findings) == 1
    assert name_findings[0].severity == Severity.ERROR
    assert "/front/camera" in name_findings[0].message


def test_param_001_typo_detection():
    model = LaunchSystemModel(
        nodes=[
            ResolvedNode(
                name="diff_drive",
                namespace="",
                parameters={
                    "wheel_seperation": 0.45,  # typo for wheel_separation
                    "publish_rate": 20.0,
                },
            )
        ]
    )

    engine = get_default_rule_engine()
    findings = engine.analyze(model)

    param_findings = [f for f in findings if f.rule_id == "PARAM-001"]
    assert len(param_findings) == 1
    assert param_findings[0].severity == Severity.WARNING
    assert "wheel_separation" in param_findings[0].message


def test_qos_001_incompatibility():
    pub_ep = TopicEndpoint(
        topic="/scan",
        node_full_name="/lidar",
        direction=EndpointDirection.PUBLISHER,
        qos=QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT),
    )
    sub_ep = TopicEndpoint(
        topic="/scan",
        node_full_name="/slam",
        direction=EndpointDirection.SUBSCRIBER,
        qos=QoSProfile(reliability=ReliabilityPolicy.RELIABLE),
    )

    model = LaunchSystemModel(
        nodes=[
            ResolvedNode(name="lidar", namespace="", endpoints=[pub_ep]),
            ResolvedNode(name="slam", namespace="", endpoints=[sub_ep]),
        ]
    )

    engine = get_default_rule_engine()
    findings = engine.analyze(model)

    qos_findings = [f for f in findings if f.rule_id == "QOS-001"]
    assert len(qos_findings) == 1
    assert qos_findings[0].severity == Severity.ERROR
    assert "Publisher offers BEST_EFFORT but Subscriber requests RELIABLE" in qos_findings[0].message


def test_type_001_message_conflict():
    ep1 = TopicEndpoint(
        topic="/cmd_vel",
        node_full_name="/teleop",
        direction=EndpointDirection.PUBLISHER,
        message_type="geometry_msgs/msg/Twist",
    )
    ep2 = TopicEndpoint(
        topic="/cmd_vel",
        node_full_name="/controller",
        direction=EndpointDirection.SUBSCRIBER,
        message_type="geometry_msgs/msg/TwistStamped",
    )

    model = LaunchSystemModel(
        nodes=[
            ResolvedNode(name="teleop", namespace="", endpoints=[ep1]),
            ResolvedNode(name="controller", namespace="", endpoints=[ep2]),
        ]
    )

    engine = get_default_rule_engine()
    findings = engine.analyze(model)

    type_findings = [f for f in findings if f.rule_id == "TYPE-001"]
    assert len(type_findings) == 1
    assert type_findings[0].severity == Severity.ERROR
    assert "geometry_msgs/msg/Twist" in type_findings[0].message
    assert "geometry_msgs/msg/TwistStamped" in type_findings[0].message


def test_dangling_remap_detection():
    # robot_state_publisher known stub has joint_states, robot_description, tf
    node = ResolvedNode(
        name="rsp",
        namespace="",
        package="robot_state_publisher",
        executable="robot_state_publisher",
        remappings=[("nonexistent_sensor", "/custom_sensor")],
        endpoints=[
            TopicEndpoint(
                topic="/joint_states",
                node_full_name="/rsp",
                direction=EndpointDirection.SUBSCRIBER,
                original_name="joint_states",
            )
        ],
    )

    model = LaunchSystemModel(nodes=[node])
    engine = get_default_rule_engine()
    findings = engine.analyze(model)

    remap_findings = [f for f in findings if f.rule_id == "REMAP-001"]
    assert len(remap_findings) == 1
    assert "nonexistent_sensor" in remap_findings[0].message
