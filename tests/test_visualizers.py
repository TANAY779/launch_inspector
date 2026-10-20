"""Unit tests for Phase 3: Visualizers & Reporters."""

import json
from launch_inspector.models import (
    DiagnosticFinding,
    EndpointDirection,
    LaunchSystemModel,
    QoSProfile,
    ReliabilityPolicy,
    ResolvedNode,
    Severity,
    TopicEndpoint,
)
from launch_inspector.reporters import ConsoleReporter, JsonReporter, SarifReporter
from launch_inspector.visualizers import DotVisualizer, MermaidVisualizer


def _create_sample_model() -> LaunchSystemModel:
    pub = TopicEndpoint(
        topic="/robot/scan",
        node_full_name="/robot/lidar",
        direction=EndpointDirection.PUBLISHER,
        message_type="sensor_msgs/msg/LaserScan",
    )
    sub = TopicEndpoint(
        topic="/robot/scan",
        node_full_name="/robot/nav",
        direction=EndpointDirection.SUBSCRIBER,
        message_type="sensor_msgs/msg/LaserScan",
    )

    node1 = ResolvedNode(
        name="lidar",
        namespace="robot",
        package="rplidar_ros",
        executable="rplidar_node",
        parameters={"use_sim_time": True},
        endpoints=[pub],
    )
    node2 = ResolvedNode(
        name="nav",
        namespace="robot",
        package="nav2_bringup",
        executable="navigation",
        parameters={"use_sim_time": True},
        endpoints=[sub],
    )

    diag = DiagnosticFinding(
        rule_id="TIME-001",
        severity=Severity.ERROR,
        message="Sim time error test",
        entity="/robot/lidar",
        fix_hint="Set use_sim_time=True uniformly",
    )

    return LaunchSystemModel(
        launch_path="/test/path/bringup.launch.py",
        nodes=[node1, node2],
        diagnostics=[diag],
    )


def test_mermaid_generation():
    model = _create_sample_model()
    vis = MermaidVisualizer(model)
    mermaid_text = vis.generate()

    assert "flowchart LR" in mermaid_text
    assert "Namespace: /robot" in mermaid_text
    assert "rplidar_ros/rplidar_node" in mermaid_text
    assert "/robot/scan" in mermaid_text
    # Style applied to error node
    assert "style node_robot_lidar" in mermaid_text


def test_dot_generation():
    model = _create_sample_model()
    vis = DotVisualizer(model)
    dot_text = vis.generate()

    assert "digraph G {" in dot_text
    assert "cluster_robot" in dot_text
    assert "rplidar_ros/rplidar_node" in dot_text
    assert "/robot/scan" in dot_text
    assert "->" in dot_text


def test_sarif_generation():
    model = _create_sample_model()
    reporter = SarifReporter(model)
    sarif_str = reporter.generate()
    sarif_data = json.loads(sarif_str)

    assert sarif_data["version"] == "2.1.0"
    assert len(sarif_data["runs"]) == 1
    assert sarif_data["runs"][0]["tool"]["driver"]["name"] == "launch-inspector"
    results = sarif_data["runs"][0]["results"]
    assert len(results) == 1
    assert results[0]["ruleId"] == "TIME-001"
    assert results[0]["level"] == "error"


def test_json_reporter():
    model = _create_sample_model()
    reporter = JsonReporter(model)
    json_str = reporter.generate()
    data = json.loads(json_str)

    assert len(data["nodes"]) == 2
    assert data["nodes"][0]["full_name"] == "/robot/lidar"
    assert len(data["diagnostics"]) == 1
    assert data["diagnostics"][0]["rule_id"] == "TIME-001"


def test_console_reporter():
    import io

    model = _create_sample_model()
    reporter = ConsoleReporter(model, use_color=False)
    buf = io.StringIO()
    exit_code = reporter.report(out=buf)

    assert exit_code == 1  # 1 error exists
    captured = buf.getvalue()
    assert "LAUNCH INSPECTOR" in captured
    assert "RESOLVED NODES:" in captured
    assert "/robot/lidar" in captured
    assert "[TIME-001]" in captured
    assert "FAILED (1 error(s)" in captured
