# PLAN.md — Phase 2: Static Rule Checker & Linter Engine

> **Phase**: 2
> **Status**: IN_PROGRESS

## Objective
Implement an extensible rules engine that inspects a `LaunchSystemModel` and generates standardized `DiagnosticFinding` items for silent defects (QoS mismatches, parameter typos, sim-time splits, type conflicts, and duplicate nodes).

## Tasks
1. [x] Task 2.1: Define base rule interface (`rules/base.py`):
   - `class BaseRule`: `rule_id`, `name`, `description`, `severity`, `check(model) -> List[DiagnosticFinding]`
   - `class RuleRegistry`: auto-discovers and executes all registered checks
2. [ ] Task 2.2: Implement system configuration rules:
   - `TIME-001` (`rules/time_rules.py`): Detects desynchronized `use_sim_time` flags across nodes
   - `NAME-001` (`rules/name_rules.py`): Detects duplicate full node names
   - `PARAM-001` (`rules/param_rules.py`): Detects parameter typos and known schema mismatches using Levenshtein distance
   - `REMAP-001` (`rules/remap_rules.py`): Flags dangling or unused remapping declarations
3. [ ] Task 2.3: Implement graph communication rules:
   - `QOS-001` (`rules/qos_type_rules.py`): Flags DDS QoS incompatibilities between publishers and subscribers
   - `TYPE-001` (`rules/qos_type_rules.py`): Flags message type conflicts on identical topic paths
   - `ORPHAN-001` (`rules/qos_type_rules.py`): Flags dead/orphaned topics
4. [ ] Task 2.4: Add unit tests for all rules (`tests/test_rules.py`):
   - Synthetic models testing positive and negative cases for each rule

## Verification
- Run `pytest tests/test_rules.py` and verify all rules detect their intended defects with accurate fix hints.
