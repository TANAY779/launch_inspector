# ROADMAP.md — Launch Inspector

> **Current Phase**: All Phases Complete
> **Milestone**: v0.1.0 (Released)

## Must-Haves (from SPEC)
- [x] Safe evaluation of Python, XML, and YAML launch files without launching processes.
- [x] Complete extraction of resolved node names, namespaces, package/executable names, parameters, and topic remappings.
- [x] Detection of parameter inconsistencies (`use_sim_time` splits, duplicate node names, parameter typos).
- [x] Detection of topic wiring errors (QoS incompatibilities, type conflicts, orphan topics).
- [x] Mermaid diagram and SARIF report generation.
- [x] Clean CLI with rich terminal output and CI exit codes.

## Phases

### Phase 1: Foundation & Static Launch Resolver Engine
**Status**: ✅ Complete
**Objective**: Build the core launch visitor and interceptor engine that safely executes `generate_launch_description()` in an isolated dry-run context, capturing all `Node`, `ComposableNode`, and `IncludeLaunchDescription` declarations into a clean typed System Model without executing binaries.
**Deliverables**:
- [x] Typed data models: `ResolvedNode`, `ResolvedTopic`, `ResolvedParam`, `LaunchSystemModel`
- [x] Launch interceptor that patches/intercepts `ExecuteProcess`, `Node`, and container actions
- [x] Support for launch arguments, substitutions, and conditional actions (`IfCondition`, `UnlessCondition`)
- [x] Unit tests verifying dry-run resolution of synthetic and real launch files

### Phase 2: Static Rule Checker & Linter Engine
**Status**: ✅ Complete
**Objective**: Implement an extensible rules engine that analyzes the `LaunchSystemModel` for configuration and communication defects.
**Deliverables**:
- [x] Rule `TIME-001`: `use_sim_time` consistency across all nodes
- [x] Rule `NAME-001`: Duplicate node and namespace collisions
- [x] Rule `PARAM-001`: Unknown/misspelled parameter keys (Levenshtein distance suggestions)
- [x] Rule `REMAP-001`: Dangling/unmatched topic remappings
- [x] Rule `QOS-001`: Topic QoS incompatibility (Reliable subscriber paired with Best Effort publisher)
- [x] Rule `TYPE-001`: Message type mismatch on identical topic paths

### Phase 3: Visualizer & CI Export Formatter
**Status**: ✅ Complete
**Objective**: Build visual graph exporters and machine-readable output formats for local development and CI pipelines.
**Deliverables**:
- [x] Rich terminal UI with colorized diagnostics table and summary card
- [x] Mermaid flowchart generator (`.mmd` and embedded markdown)
- [x] Graphviz DOT exporter
- [x] SARIF (Static Analysis Results Interchange Format) exporter for GitHub PR annotations
- [x] Standard JSON schema export

### Phase 4: CLI Ergonomics & End-to-End Integration
**Status**: ✅ Complete
**Objective**: Package the tool as a standalone CLI (`launch-inspector`) and standard ROS 2 command verb (`ros2 launch inspect`), verifying against real-world robot stacks.
**Deliverables**:
- [x] `pyproject.toml` packaging with console entrypoints
- [x] Integration fixtures (`clean_bringup.launch.py`, `defective_bringup.launch.py`)
- [x] End-to-end integration test suite (`tests/test_cli.py`)
- [x] Complete documentation (`README.md`)
