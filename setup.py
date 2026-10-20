import os
from glob import glob
from setuptools import find_packages, setup

package_name = "launch_inspector"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    data_files=[
        (
            "share/ament_index/resource_index/packages",
            ["resource/" + package_name],
        ),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools", "pyyaml"],
    zip_safe=True,
    maintainer="tanay",
    maintainer_email="tanay@todo.todo",
    description="Static dry-run analyzer, linter, and architecture visualizer for ROS 2 launch files.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "launch-inspector = launch_inspector.cli:main",
            "launch_inspector = launch_inspector.cli:main",
            "inspector = launch_inspector.cli:main",
        ],
    },
)
