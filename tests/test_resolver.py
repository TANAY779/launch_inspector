"""Unit tests for Phase 1: Launch Resolver Engine."""

import os
import tempfile
import pytest

import launch
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace, SetParameter

from launch_inspector.models import ReliabilityPolicy
from launch_inspector.resolver import LaunchResolver


def test_basic_node_resolution():
    ld = launch.LaunchDescription([
        Node(
            package="demo_nodes_cpp",
            executable="talker",
            name="talker_node",
            parameters=[{"publish_rate": 50.0, "use_sim_time": False}],
            remappings=[("chatter", "/custom/chatter")],
        )
    ])

    resolver = LaunchResolver(launch_description=ld)
    model = resolver.resolve()

    assert len(model.nodes) == 1
    node = model.nodes[0]
    assert node.name == "talker_node"
    assert node.full_name == "/talker_node"
    assert node.parameters["publish_rate"] == 50.0
    assert node.parameters["use_sim_time"] is False
    assert ("chatter", "/custom/chatter") in node.remappings


def test_conditional_execution():
    ld = launch.LaunchDescription([
        DeclareLaunchArgument("enable_rviz", default_value="false"),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz",
            condition=IfCondition(LaunchConfiguration("enable_rviz")),
        ),
        Node(
            package="demo_nodes_cpp",
            executable="listener",
            name="listener",
            condition=UnlessCondition(LaunchConfiguration("enable_rviz")),
        ),
    ])

    # Case 1: enable_rviz is default false
    resolver = LaunchResolver(launch_description=ld)
    model = resolver.resolve()
    active_names = [n.name for n in model.nodes]
    skipped_names = [n.name for n in model.skipped_nodes]

    assert "listener" in active_names
    assert "rviz" in skipped_names

    # Case 2: enable_rviz overridden to true
    resolver_true = LaunchResolver(
        launch_description=ld, launch_arguments={"enable_rviz": "true"}
    )
    model_true = resolver_true.resolve()
    active_true = [n.name for n in model_true.nodes]
    skipped_true = [n.name for n in model_true.skipped_nodes]

    assert "rviz" in active_true
    assert "listener" in skipped_true


def test_group_action_and_namespacing():
    ld = launch.LaunchDescription([
        GroupAction([
            PushRosNamespace("fleet_robot_1"),
            SetParameter(name="use_sim_time", value=True),
            Node(
                package="demo_nodes_cpp",
                executable="talker",
                name="teleop",
            ),
        ])
    ])

    resolver = LaunchResolver(launch_description=ld)
    model = resolver.resolve()

    assert len(model.nodes) == 1
    node = model.nodes[0]
    assert node.namespace == "fleet_robot_1"
    assert node.full_name == "/fleet_robot_1/teleop"
    assert node.parameters.get("use_sim_time") is True


def test_yaml_parameter_loading():
    yaml_content = """
/robot_driver:
  ros__parameters:
    wheel_radius: 0.15
    max_velocity: 2.5
/**:
  ros__parameters:
    global_timeout: 5.0
"""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_file = f.name

    try:
        ld = launch.LaunchDescription([
            Node(
                package="my_robot",
                executable="driver",
                name="robot_driver",
                parameters=[yaml_file],
            )
        ])

        resolver = LaunchResolver(launch_description=ld)
        model = resolver.resolve()

        assert len(model.nodes) == 1
        node = model.nodes[0]
        assert node.parameters.get("wheel_radius") == 0.15
        assert node.parameters.get("max_velocity") == 2.5
        assert node.parameters.get("global_timeout") == 5.0
    finally:
        os.unlink(yaml_file)


def test_standard_stubs_and_remappings():
    ld = launch.LaunchDescription([
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="rsp",
            remappings=[("joint_states", "/arm/joint_states")],
        ),
        Node(
            package="rplidar_ros",
            executable="rplidar_node",
            name="lidar",
            remappings=[("scan", "/raw_scan")],
        ),
    ])

    resolver = LaunchResolver(launch_description=ld)
    model = resolver.resolve()

    topics = model.get_topics()
    assert "/arm/joint_states" in topics
    assert "/raw_scan" in topics

    lidar_pub = topics["/raw_scan"]["pubs"][0]
    assert lidar_pub.qos.reliability == ReliabilityPolicy.BEST_EFFORT
