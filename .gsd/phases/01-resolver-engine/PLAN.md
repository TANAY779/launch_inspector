# PLAN.md — Phase 1: Foundation & Static Launch Resolver Engine

> **Phase**: 1
> **Status**: IN_PROGRESS

## Objective
Implement the core data models (`models.py`) and static launch visitor (`resolver.py`) that executes launch files without starting OS processes, capturing nodes, parameters, remappings, conditions, and arguments into a typed `LaunchSystemModel`.

## Tasks
1. [x] Task 1.1: Define typed data models (`models.py`):
   - `QoSProfile` (Reliability, Durability, History, Depth, Deadline, Lifespan)
   - `ResolvedParam` (name, value, source, type)
   - `ResolvedTopic` (name, type, qos, direction: pub/sub, remap_from)
   - `ResolvedNode` (name, namespace, full_name, package, executable, parameters, remappings, topics, condition_evaluated)
   - `LaunchSystemModel` (nodes, topics, arguments, raw_actions, metadata)
2. [ ] Task 1.2: Implement `LaunchResolver` (`resolver.py`):
   - Python launch description visitor
   - Action interception: Replace process execution in `Node`, `ExecuteProcess`, `LifecycleNode` with mock visitor
   - Recursive inspection of `GroupAction`, `PushRosNamespace`, `SetParameter`, `SetRemap`, `IncludeLaunchDescription`
   - Evaluation of `LaunchConfiguration`, `PythonExpression`, `IfCondition`, `UnlessCondition`
   - Support for parameter files (YAML loading and merging)
3. [ ] Task 1.3: Add test suite for resolver (`tests/test_resolver.py`):
   - Synthetic launch descriptions testing conditional logic, parameter loading, and remappings
   - Verification of zero processes spawned during resolution

## Verification
- Run `pytest tests/test_resolver.py` and verify all tests pass with zero spawned processes.
