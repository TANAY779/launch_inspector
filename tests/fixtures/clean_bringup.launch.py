"""Clean test fixture with zero defects."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    sim_arg = DeclareLaunchArgument("use_sim_time", default_value="true")

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
    )

    diff_drive = Node(
        package="diff_drive_controller",
        executable="diff_drive_controller",
        name="diff_drive_controller",
        parameters=[
            {
                "use_sim_time": LaunchConfiguration("use_sim_time"),
                "wheel_separation": 0.45,
                "wheel_radius": 0.1,
            }
        ],
    )

    return LaunchDescription([sim_arg, rsp, diff_drive])
