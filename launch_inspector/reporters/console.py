"""Rich colorized console reporter for terminal execution."""

from __future__ import annotations

import sys
from typing import TextIO

from launch_inspector.models import LaunchSystemModel, Severity

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_MAGENTA = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_DIM = "\033[2m"


class ConsoleReporter:
    """Formats and prints launch inspection diagnostics to standard output."""

    def __init__(self, model: LaunchSystemModel, use_color: bool = True):
        self.model = model
        self.use_color = use_color and sys.stdout.isatty()

    def _color(self, text: str, color_code: str) -> str:
        if not self.use_color:
            return text
        return f"{color_code}{text}{COLOR_RESET}"

    def report(self, out: TextIO = sys.stdout) -> int:
        """
        Prints the report to output stream.
        Returns suggested process exit code (1 if errors exist, 0 otherwise).
        """
        out.write(self._color("━" * 68, COLOR_DIM) + "\n")
        out.write(
            f" {self._color('LAUNCH INSPECTOR', COLOR_BOLD)} "
            f"► {self._color(self.model.launch_path or 'Inline Description', COLOR_CYAN)}\n"
        )
        out.write(self._color("━" * 68, COLOR_DIM) + "\n\n")

        # System overview
        topics = self.model.get_topics()
        out.write(
            f" Nodes: {self._color(str(len(self.model.nodes)), COLOR_BOLD)} active "
            f"({len(self.model.skipped_nodes)} conditional/skipped) | "
            f"Topics: {self._color(str(len(topics)), COLOR_BOLD)} | "
            f"Arguments: {len(self.model.arguments)}\n\n"
        )

        # Print Nodes Table
        out.write(self._color("RESOLVED NODES:", COLOR_BOLD) + "\n")
        for node in self.model.nodes:
            ns_str = f"[{node.namespace}] " if node.namespace else ""
            pkg_str = f"({node.package}/{node.executable})" if node.package else ""
            out.write(
                f"  • {self._color(node.full_name, COLOR_CYAN)} "
                f"{self._color(pkg_str, COLOR_DIM)}\n"
            )
            if node.parameters:
                p_summary = ", ".join(f"{k}={v}" for k, v in list(node.parameters.items())[:4])
                if len(node.parameters) > 4:
                    p_summary += f", ... (+{len(node.parameters)-4} more)"
                out.write(f"      params: {self._color(p_summary, COLOR_DIM)}\n")
            if node.remappings:
                r_summary = ", ".join(f"{s}->{d}" for s, d in node.remappings)
                out.write(f"      remaps: {self._color(r_summary, COLOR_DIM)}\n")

        if self.model.skipped_nodes:
            out.write(self._color("\nSKIPPED / CONDITIONAL NODES:", COLOR_DIM) + "\n")
            for sk in self.model.skipped_nodes:
                out.write(f"  ⊘ {self._color(sk.full_name, COLOR_DIM)} (condition evaluated to False)\n")

        # Diagnostics Table
        out.write("\n" + self._color("DIAGNOSTICS & AUDIT FINDINGS:", COLOR_BOLD) + "\n")
        if not self.model.diagnostics:
            out.write(f"  {self._color('✓ Zero defects or configuration issues detected.', COLOR_GREEN)}\n\n")
            return 0

        errors = 0
        warnings = 0
        infos = 0

        for f in self.model.diagnostics:
            if f.severity == Severity.ERROR:
                sev_label = self._color("ERROR", COLOR_RED + COLOR_BOLD)
                errors += 1
            elif f.severity == Severity.WARNING:
                sev_label = self._color("WARN ", COLOR_YELLOW + COLOR_BOLD)
                warnings += 1
            else:
                sev_label = self._color("INFO ", COLOR_BLUE)
                infos += 1

            rule_label = self._color(f"[{f.rule_id}]", COLOR_BOLD)
            entity_str = f" on {self._color(f.entity, COLOR_CYAN)}" if f.entity else ""

            out.write(f"  {sev_label} {rule_label}{entity_str}\n")
            out.write(f"         {f.message}\n")
            if f.fix_hint:
                out.write(f"         {self._color('Hint: ' + f.fix_hint, COLOR_DIM)}\n")
            out.write("\n")

        # Summary footer
        out.write(self._color("━" * 68, COLOR_DIM) + "\n")
        verdict = f"{errors} error(s), {warnings} warning(s), {infos} info"
        if errors > 0:
            out.write(f" Result: {self._color('FAILED', COLOR_RED + COLOR_BOLD)} ({verdict})\n")
            exit_code = 1
        elif warnings > 0:
            out.write(f" Result: {self._color('PASSED WITH WARNINGS', COLOR_YELLOW + COLOR_BOLD)} ({verdict})\n")
            exit_code = 0
        else:
            out.write(f" Result: {self._color('PASSED', COLOR_GREEN + COLOR_BOLD)} ({verdict})\n")
            exit_code = 0
        out.write(self._color("━" * 68, COLOR_DIM) + "\n")

        return exit_code
