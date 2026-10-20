"""Known node interface stubs for standard ROS 2 packages."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from launch_inspector.models import (
    EndpointDirection,
    QoSProfile,
    ReliabilityPolicy,
    DurabilityPolicy,
    TopicEndpoint,
)


def get_standard_stubs(package: str, executable: str) -> List[Tuple[str, EndpointDirection, str, QoSProfile]]:
    """
    Returns list of (topic_template, direction, message_type, QoSProfile)
    for known ROS 2 packages.
    """
    stubs: List[Tuple[str, EndpointDirection, str, QoSProfile]] = []

    # Standard QoS presets
    sensor_qos = QoSProfile(
        reliability=ReliabilityPolicy.BEST_EFFORT,
        durability=DurabilityPolicy.VOLATILE,
        depth=5,
    )
    cmd_qos = QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
        depth=10,
    )
    latched_qos = QoSProfile(
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.TRANSIENT_LOCAL,
        depth=1,
    )

    if package == "robot_state_publisher":
        stubs.extend([
            ("joint_states", EndpointDirection.SUBSCRIBER, "sensor_msgs/msg/JointState", cmd_qos),
            ("robot_description", EndpointDirection.PUBLISHER, "std_msgs/msg/String", latched_qos),
            ("tf", EndpointDirection.PUBLISHER, "tf2_msgs/msg/TFMessage", cmd_qos),
            ("tf_static", EndpointDirection.PUBLISHER, "tf2_msgs/msg/TFMessage", latched_qos),
        ])

    elif package == "joint_state_publisher" or package == "joint_state_publisher_gui":
        stubs.extend([
            ("joint_states", EndpointDirection.PUBLISHER, "sensor_msgs/msg/JointState", cmd_qos),
            ("robot_description", EndpointDirection.SUBSCRIBER, "std_msgs/msg/String", latched_qos),
        ])

    elif package == "controller_manager":
        stubs.extend([
            ("robot_description", EndpointDirection.SUBSCRIBER, "std_msgs/msg/String", latched_qos),
        ])

    elif package == "diff_drive_controller":
        stubs.extend([
            ("cmd_vel", EndpointDirection.SUBSCRIBER, "geometry_msgs/msg/TwistStamped", cmd_qos),
            ("odom", EndpointDirection.PUBLISHER, "nav_msgs/msg/Odometry", cmd_qos),
            ("tf", EndpointDirection.PUBLISHER, "tf2_msgs/msg/TFMessage", cmd_qos),
        ])

    elif package == "joint_trajectory_controller":
        stubs.extend([
            ("joint_trajectory", EndpointDirection.SUBSCRIBER, "trajectory_msgs/msg/JointTrajectory", cmd_qos),
            ("controller_state", EndpointDirection.PUBLISHER, "control_msgs/msg/JointTrajectoryControllerState", cmd_qos),
        ])

    elif package == "slam_toolbox":
        stubs.extend([
            ("scan", EndpointDirection.SUBSCRIBER, "sensor_msgs/msg/LaserScan", cmd_qos),
            ("tf", EndpointDirection.SUBSCRIBER, "tf2_msgs/msg/TFMessage", cmd_qos),
            ("map", EndpointDirection.PUBLISHER, "nav_msgs/msg/OccupancyGrid", latched_qos),
            ("map_metadata", EndpointDirection.PUBLISHER, "nav_msgs/msg/MapMetaData", latched_qos),
        ])

    elif package == "nav2_amcl" or executable == "amcl":
        stubs.extend([
            ("scan", EndpointDirection.SUBSCRIBER, "sensor_msgs/msg/LaserScan", cmd_qos),
            ("tf", EndpointDirection.SUBSCRIBER, "tf2_msgs/msg/TFMessage", cmd_qos),
            ("initialpose", EndpointDirection.SUBSCRIBER, "geometry_msgs/msg/PoseWithCovarianceStamped", cmd_qos),
            ("amcl_pose", EndpointDirection.PUBLISHER, "geometry_msgs/msg/PoseWithCovarianceStamped", cmd_qos),
            ("particle_cloud", EndpointDirection.PUBLISHER, "nav2_msgs/msg/ParticleCloud", sensor_qos),
        ])

    elif package == "teleop_twist_keyboard" or package == "teleop_twist_joy":
        stubs.extend([
            ("cmd_vel", EndpointDirection.PUBLISHER, "geometry_msgs/msg/Twist", cmd_qos),
        ])

    elif package in ("rplidar_ros", "sllidar_ros", "urg_node", "sick_scan"):
        stubs.extend([
            ("scan", EndpointDirection.PUBLISHER, "sensor_msgs/msg/LaserScan", sensor_qos),
        ])

    return stubs
