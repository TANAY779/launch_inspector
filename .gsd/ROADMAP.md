# ROADMAP.md — Launch Inspector

> **Current Phase**: Phase 1: Foundation & Static Launch Resolver Engine
> **Milestone**: v0.1.0

## Must-Haves (from SPEC)
- [ ] Safe evaluation of Python, XML, and YAML launch files without launching processes.
- [ ] Complete extraction of resolved node names, namespaces, package/executable names, parameters, and topic remappings.
- [ ] Detection of parameter inconsistencies (`use_sim_time` splits, duplicate node names, parameter typos).
- [ ] Detection of topic wiring errors (QoS incompatibilities, type conflicts, orphan topics).
- [ ] Mermaid diagram and SARIF report generation.
- [ ] Clean CLI with rich terminal output and CI exit codes.

## Phases

### Phase 1: Foundation & Static Launch Resolver Engine
**Status**: ⏳ In Progress
**Objective**: Build the core launch visitor and interceptor engine that safely executes `generate_launch_description()` in an isolated dry-run context, capturing all `Node`, `ComposableNode`, and `IncludeLaunchDescription` declarations into a clean typed System Model without executing binaries.
**Deliverables**:
- Typed data models: `ResolvedNode`, `ResolvedTopic`, `ResolvedParam`, `LaunchSystemModel`
- Launch interceptor that patches/intercepts `ExecuteProcess`, `Node`, and container actions
- Support for launch arguments, substitutions, and conditional actions (`IfCondition`, `UnlessCondition`)
- Unit tests verifying dry-run resolution of synthetic and real launch files

### Phase 2: Static Rule Checker & Linter Engine
**Status**: ⬜ Not Started
**Objective**: Implement an extensible rules engine that analyzes the `LaunchSystemModel` for configuration and communication defects.
**Deliverables**:
- Rule `TIME-001`: `use_sim_time` consistency across all nodes
- Rule `NAME-001`: Duplicate node and namespace collisions
- Rule `PARAM-001`: Unknown/misspelled parameter keys (Levenshtein distance suggestions)
- Rule `REMAP-001`: Dangling/unmatched topic remappings
- Rule `QOS-001`: Topic QoS incompatibility (Reliable subscriber paired with Best Effort publisher)
- Rule `TYPE-001`: Message type mismatch on identical topic paths

### Phase 3: Visualizer & CI Export Formatter
**Status**: ⬜ Not Started
**Objective**: Build visual graph exporters and machine-readable output formats for local development and CI pipelines.
**Deliverables**:
- Rich terminal UI with colorized diagnostics table and summary card
- Mermaid flowchart generator (`.mmd` and embedded markdown)
- Graphviz DOT exporter
- SARIF (Static Analysis Results Interchange Format) exporter for GitHub PR annotations
- Standard JSON schema export

### Phase 4: CLI Ergonomics & End-to-End Integration
**Status**: ⬜ Not Started
**Objective**: Package the tool as a standalone CLI (`launch-inspector`) and standard ROS 2 command verb (`ros2 launch inspect`), verifying against real-world robot stacks.
**Deliverables**:
- `pyproject.toml` / `setup.py` packaging with console entrypoints
- `ros2 launch inspect` sub-command extension
- Integration tests against `two_dof_arm` and `custom_controllers` packages
- Documentation, README, and GitHub Action template
