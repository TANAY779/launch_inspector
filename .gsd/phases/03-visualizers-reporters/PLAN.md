# PLAN.md — Phase 3: Visualizer & CI Export Formatter

> **Phase**: 3
> **Status**: IN_PROGRESS

## Objective
Build visual graph generators (Mermaid, Graphviz DOT) and report formatters (Colorized terminal console, SARIF v2.1.0 for GitHub PR annotations, and machine-readable JSON).

## Tasks
1. [x] Task 3.1: Implement Mermaid visualizer (`visualizers/mermaid.py`):
   - Namespaces grouped into Mermaid subgraphs
   - Publisher -> Topic -> Subscriber directed edge mapping
   - Node styling based on error/warning diagnostics
2. [ ] Task 3.2: Implement Graphviz DOT visualizer (`visualizers/dot.py`):
   - Clean cluster layout for namespaces, box shapes for nodes, ellipses for topics
3. [ ] Task 3.3: Implement Terminal Console reporter (`reporters/console.py`):
   - Colorized ANSI diagnostics table, entity badges, fix hints, and status scorecard
4. [ ] Task 3.4: Implement SARIF and JSON exporters (`reporters/sarif.py`, `reporters/json_reporter.py`):
   - Valid SARIF v2.1.0 JSON schema for native GitHub Actions security/linter tab integration
5. [ ] Task 3.5: Add unit tests for visualizers and reporters (`tests/test_visualizers.py`)

## Verification
- Run `pytest tests/test_visualizers.py` and verify valid Mermaid syntax, valid DOT syntax, and valid SARIF JSON structure.
