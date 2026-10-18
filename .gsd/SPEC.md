# SPEC.md — Project Specification: Launch Inspector

> **Status**: `FINALIZED`

## Vision
A high-precision, zero-overhead static analysis CLI and library for ROS 2 that resolves launch descriptions (Python, XML, YAML) *without spawning processes*, reconstructs the intended computation graph (nodes, namespaces, remaps, parameters, topics, QoS), detects silent wiring and configuration defects in CI before deployment, and renders actionable architecture diagrams and diagnostics.

## Goals
1. **Deterministic Launch Resolution**: Inspect arbitrary ROS 2 launch files with launch arguments evaluated, conditions resolved, and inclusions traversed, without executing node binaries.
2. **Configuration & Parameter Auditing**: Validate parameter merges across YAML files and launch overrides, flagging `use_sim_time` desynchronization, duplicate node names, and undeclared/misspelled parameter keys.
3. **Graph Wiring & Contract Auditing**: Cross-reference publisher and subscriber interfaces across the resolved node graph, detecting QoS incompatibilities (e.g. Reliable vs Best Effort), message type mismatches, and orphan topics.
4. **Rich Visualization & CI Integration**: Generate interactive Mermaid and Graphviz (DOT) architecture diagrams, alongside SARIF and JSON reports for seamless GitHub Actions / GitLab CI PR annotations.
5. **Ergonomic CLI Experience**: Provide both a standalone binary (`launch-inspector`) and a ROS 2 command verb (`ros2 launch inspect ...`).

## Non-Goals (Out of Scope)
- Runtime execution or DDS packet sniffing (this is purely static/pre-flight inspection).
- Simulation execution (no Gazebo, Isaac Sim, or physics engines).
- Automatic code patching/mutating (diagnostic and reporting tool first).
- Arbitrary full Python interpreter sandboxing (supports standard ROS 2 launch patterns and constructs).

## Target Users
- **Robotics Software Engineers**: Debugging launch files, parameter overrides, and topic remappings locally before launching physical robots or sim.
- **DevOps & QA Engineers**: Running pre-merge CI validation checks on PRs to prevent silent configuration regressions.
- **System Architects & Integrators**: Automatically generating live, always-accurate architecture diagrams of complex multi-node systems.

## Constraints
- Must run cleanly on Linux (primary) with ROS 2 Jazzy and Humble compatibility.
- Written in Python (leveraging native `launch` and `launch_ros` parsing engines).
- Zero hardware dependency (runs headless in standard CI containers).

## Success Criteria
- [ ] Successfully dry-run and resolve multi-node Python launch files without spawning child processes.
- [ ] Catch 100% of synthetic test suite errors: QoS mismatches, topic type mismatches, parameter typos, `use_sim_time` splits.
- [ ] Generate valid Mermaid diagram strings and SARIF diagnostic files.
- [ ] Tested and verified against real-world launch files (e.g. `two_dof_arm` and `custom_controllers` packages).
