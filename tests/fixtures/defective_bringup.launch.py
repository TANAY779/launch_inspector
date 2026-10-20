"""Defective test fixture containing multiple deliberate configuration errors."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # 1. TIME-001: use_sim_time split (True on lidar, False on driver)
    # 2. PARAM-001: parameter typo (wheel_seperation)
    # 3. NAME-001: duplicate node name (/sensor_sync twice)
    lidar = Node(
        package="rplidar_ros",
        executable="rplidar_node",
        name="lidar_driver",
        parameters=[{"use_sim_time": True}],
    )

    diff_drive = Node(
        package="diff_drive_controller",
        executable="diff_drive_controller",
        name="driver_node",
        parameters=[
            {
                "use_sim_time": False,
                "wheel_seperation": 0.5,  # Typo for wheel_separation
            }
        ],
    )

    dup1 = Node(
        package="demo_nodes_cpp",
        executable="talker",
        name="sensor_sync",
    )

    dup2 = Node(
        package="demo_nodes_cpp",
        executable="listener",
        name="sensor_sync",
    )

    return LaunchDescription([lidar, diff_drive, dup1, dup2])
