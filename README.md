# Launch Inspector (`launch-inspector`)

> **Static launch dry-run analyzer, linter, and architecture visualizer for ROS 2.**

[![Tests](https://img.shields.io/badge/tests-20%20passed-brightgreen.svg)]()
[![ROS 2](https://img.shields.io/badge/ROS%202-Humble%20%7C%20Jazzy-blue.svg)]()
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)]()

`launch-inspector` safely evaluates ROS 2 launch files (Python, XML, and YAML) **without spawning any OS processes or requiring physical hardware**. It reconstructs the intended node computation graph, validates parameters and remappings, flags silent wiring bugs in CI before deployment, and generates interactive Mermaid and Graphviz architecture diagrams.

---

## Why Launch Inspector?

In web and cloud engineering, static analyzers and linters catch configuration and contract errors in CI within seconds. In robotics, launch and communication errors frequently fail **silently at runtime**:
- **QoS Mismatch:** A sensor publishes `BEST_EFFORT` while a SLAM node requires `RELIABLE`. DDS silently drops all packets with zero errors.
- **`use_sim_time` Desynchronization:** Some nodes run on simulation time while others run on wall-clock time, corrupting the TF buffer with "extrapolation into the future" errors.
- **Parameter Typos:** Writing `wheel_seperation: 0.5` instead of `wheel_separation` is silently ignored by the parameter server, causing uncalibrated odometry.
- **Node Collisions:** Duplicate node names in multi-robot bringup cause silent node evictions during DDS discovery.

`launch-inspector` intercepts launch evaluation in a mock visitor context, capturing the entire system topology in milliseconds and providing rich feedback.

---

## Features

- 🚀 **100% Zero-Process Dry Run:** Resolves nodes, namespaces, launch arguments, and parameter files without executing node binaries.
- 🔍 **Static Rule Engine:** Catches silent DDS QoS mismatches, type conflicts, parameter typos, duplicate node names, and time drift.
- 📊 **Architecture Visualizer:** Generates clean [Mermaid](https://mermaid.js.org/) flowcharts and Graphviz DOT diagrams grouped by namespace.
- 🛡️ **CI & PR Annotations:** Exports standard OASIS SARIF v2.1.0 reports for native GitHub Code Scanning annotations on Pull Requests.
- ⚡ **Ultra Fast:** Validates complex multi-node launch files in under 200 ms.

---

## Installation

```bash
git clone https://github.com/ros-project/launch-inspector.git
cd launch-inspector
pip install -e .
```

*Requires Python 3.10+ and a standard ROS 2 environment (Humble or Jazzy).*

---

## CLI Usage

### Basic Audit
```bash
launch-inspector path/to/my_robot.launch.py
```

### Passing Launch Arguments
```bash
launch-inspector path/to/my_robot.launch.py use_sim_time:=true rviz:=false
```

### Exporting Visual Diagrams & Reports
```bash
# Export Mermaid diagram (renders directly on GitHub markdown)
launch-inspector bringup.launch.py --mermaid architecture.mmd

# Export Graphviz DOT graph
launch-inspector bringup.launch.py --dot graph.dot

# Export SARIF for GitHub Actions
launch-inspector bringup.launch.py --sarif report.sarif

# Export complete system model as JSON
launch-inspector bringup.launch.py --json model.json
```

---

## Built-In Static Rules

| Rule ID | Name | Severity | Description |
|---|---|---|---|
| `TIME-001` | **Sim Time Consistency** | `ERROR` | Flags desynchronized `use_sim_time` values across nodes. |
| `NAME-001` | **Duplicate Node Names** | `ERROR` | Flags multiple nodes with identical fully qualified names. |
| `QOS-001` | **QoS Compatibility** | `ERROR` | Detects DDS QoS incompatibilities (e.g. Best Effort pub vs Reliable sub). |
| `TYPE-001` | **Message Type Agreement** | `ERROR` | Flags conflicting message types connected to the same topic path. |
| `PARAM-001` | **Parameter Typo Checker** | `WARN` | Uses fuzzy matching to catch misspelled standard ROS 2 parameters. |
| `REMAP-001` | **Dangling Remap** | `WARN` | Detects remappings that match no topic advertised by the node package. |
| `ORPHAN-001` | **Orphaned Topics** | `INFO/WARN` | Identifies topics with zero publishers or zero subscribers. |

---

## GitHub Actions CI Workflow

Add this to `.github/workflows/launch-check.yml` to automatically lint launch files on every PR:

```yaml
name: Launch Inspector CI

on:
  pull_request:
    paths:
      - '**/*.launch.py'
      - '**/*.yaml'

jobs:
  inspect:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: ros-tooling/setup-ros@v0.7
        with:
          required-ros-distributions: jazzy

      - name: Install Launch Inspector
        run: pip install launch-inspector

      - name: Run Launch Audit
        run: |
          launch-inspector src/my_robot/launch/bringup.launch.py \
            --sarif results.sarif \
            --fail-on-warning

      - name: Upload SARIF report
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

---

## License

Apache-2.0
