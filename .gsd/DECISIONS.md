# DECISIONS.md — Architecture Decision Records (ADRs)

# ADR-001: Dry-Run Interception Strategy
- **Context**: Running `ros2 launch` normally executes binaries using Python's subprocess mechanisms (`ExecuteProcess`). We need to resolve all parameters, arguments, conditions, and group namespaces without actually starting node processes or loading shared libraries.
- **Decision**: Walk the `LaunchDescription` tree using a custom execution context where action execution methods for process spawners (`Node`, `ExecuteProcess`, `LifecycleNode`) are mocked/intercepted to collect resolved state instead of spawning OS subprocesses.
- **Consequences**: Fast (sub-second execution), deterministic, does not require GPU, root access, or physical sensors to be plugged in.

# ADR-002: Standalone and ROS 2 Verb Hybrid Packaging
- **Context**: Users want to run both in developer environments where ROS 2 is sourced (`ros2 launch inspect ...`) and in minimal CI runners that might just want a fast CLI (`launch-inspector ...`).
- **Decision**: Provide both a standard console script entrypoint (`launch-inspector`) and a `ros2launch.command` plugin entrypoint.
- **Consequences**: Maximum reach and flexibility.
