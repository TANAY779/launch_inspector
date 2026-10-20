# PLAN.md — Phase 4: CLI Ergonomics & End-to-End Integration

> **Phase**: 4
> **Status**: IN_PROGRESS

## Objective
Package `launch_inspector` with a fast CLI (`cli.py`), configure `pyproject.toml`, establish integration test fixtures, and create complete documentation and CI usage examples.

## Tasks
1. [x] Task 4.1: Implement CLI entrypoint (`launch_inspector/cli.py`):
   - Arguments parser supporting `file`, `key:=value` pairs, `--mermaid`, `--dot`, `--sarif`, `--json`, `--fail-on-warning`, `--no-color`
2. [ ] Task 4.2: Create package definitions (`pyproject.toml`, `setup.cfg`):
   - Entry point: `launch-inspector = launch_inspector.cli:main`
3. [ ] Task 4.3: Implement real-world integration fixtures (`tests/fixtures/`):
   - `bringup_clean.launch.py`: flawless multi-node robot bringup
   - `bringup_defects.launch.py`: containing QoS mismatch, sim_time split, parameter typo, and duplicate names
4. [ ] Task 4.4: Add CLI end-to-end integration tests (`tests/test_cli.py`):
   - Verify exit codes (0 for clean, 1 for defects), file exports, and argument passing
5. [ ] Task 4.5: Author comprehensive documentation (`README.md`):
   - Installation, CLI flags, GitHub Actions CI workflow example, supported rules

## Verification
- Run `pytest tests/ -v` and verify 100% of tests pass across all phases.
- Install in editable mode (`pip install -e .`) and verify `launch-inspector --help` runs directly from shell.
