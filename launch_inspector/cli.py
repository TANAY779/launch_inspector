"""Command-line interface for Launch Inspector."""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional

from launch_inspector.models import Severity
from launch_inspector.reporters import ConsoleReporter, JsonReporter, SarifReporter
from launch_inspector.resolver import LaunchResolver
from launch_inspector.rules import get_default_rule_engine
from launch_inspector.visualizers import DotVisualizer, MermaidVisualizer


def parse_launch_arguments(raw_args: List[str]) -> Dict[str, str]:
    """Parse key:=value launch argument pairs."""
    parsed = {}
    for arg in raw_args:
        if ":=" in arg:
            k, v = arg.split(":=", 1)
            parsed[k.strip()] = v.strip()
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="launch-inspector",
        description="Static dry-run analyzer, linter, and architecture visualizer for ROS 2 launch files.",
    )
    parser.add_argument(
        "launch_file",
        help="Path to the ROS 2 launch file to inspect (*.launch.py, *.launch.xml, *.launch.yaml).",
    )
    parser.add_argument(
        "launch_arguments",
        nargs="*",
        help="Launch arguments in key:=value format (e.g. use_sim_time:=true rviz:=false).",
    )
    parser.add_argument(
        "--mermaid",
        nargs="?",
        const="-",
        metavar="FILE",
        help="Export Mermaid diagram to specified file (or stdout if no file given).",
    )
    parser.add_argument(
        "--dot",
        nargs="?",
        const="-",
        metavar="FILE",
        help="Export Graphviz DOT graph to specified file (or stdout if no file given).",
    )
    parser.add_argument(
        "--sarif",
        nargs="?",
        const="-",
        metavar="FILE",
        help="Export SARIF v2.1.0 diagnostics report to specified file (or stdout if no file given).",
    )
    parser.add_argument(
        "--json",
        nargs="?",
        const="-",
        metavar="FILE",
        help="Export complete JSON system model to specified file (or stdout if no file given).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors in terminal report.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with non-zero status code if warnings are detected.",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress console table output (useful in automated pipelines when writing files).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    launch_args = parse_launch_arguments(args.launch_arguments)

    # 1. Resolve launch description
    resolver = LaunchResolver(
        launch_path=args.launch_file,
        launch_arguments=launch_args,
    )
    model = resolver.resolve()

    # 2. Run static rules
    engine = get_default_rule_engine()
    engine.analyze(model)

    # 3. Handle file exports
    def _write_or_print(content: str, destination: str) -> None:
        if destination == "-":
            sys.stdout.write(content + "\n")
        else:
            with open(destination, "w", encoding="utf-8") as f:
                f.write(content + "\n")

    if args.mermaid is not None:
        vis = MermaidVisualizer(model)
        _write_or_print(vis.generate(), args.mermaid)

    if args.dot is not None:
        vis = DotVisualizer(model)
        _write_or_print(vis.generate(), args.dot)

    if args.sarif is not None:
        rep = SarifReporter(model)
        _write_or_print(rep.generate(), args.sarif)

    if args.json is not None:
        rep = JsonReporter(model)
        _write_or_print(rep.generate(), args.json)

    # 4. Console report
    exit_code = 0
    if not args.silent:
        reporter = ConsoleReporter(model, use_color=not args.no_color)
        exit_code = reporter.report()
    else:
        # Determine exit code silently
        has_error = any(f.severity == Severity.ERROR for f in model.diagnostics)
        has_warn = any(f.severity == Severity.WARNING for f in model.diagnostics)
        if has_error or (args.fail_on_warning and has_warn):
            exit_code = 1

    if args.fail_on_warning:
        has_warn = any(f.severity == Severity.WARNING for f in model.diagnostics)
        if has_warn:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
