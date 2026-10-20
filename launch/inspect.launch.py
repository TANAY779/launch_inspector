"""Launch file to run Launch Inspector via ros2 launch."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    target_arg = DeclareLaunchArgument(
        "target",
        description="Path to the launch file to inspect",
    )

    inspector_proc = ExecuteProcess(
        cmd=["launch-inspector", LaunchConfiguration("target")],
        output="screen",
    )

    return LaunchDescription([target_arg, inspector_proc])
