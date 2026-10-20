"""End-to-end integration tests for the CLI."""

import json
import os
import tempfile
import pytest

from launch_inspector.cli import main

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
CLEAN_LAUNCH = os.path.join(FIXTURES_DIR, "clean_bringup.launch.py")
DEFECTIVE_LAUNCH = os.path.join(FIXTURES_DIR, "defective_bringup.launch.py")


def test_cli_clean_launch():
    # Clean launch should exit with 0
    exit_code = main([CLEAN_LAUNCH, "--silent"])
    assert exit_code == 0


def test_cli_defective_launch():
    # Defective launch should exit with 1
    exit_code = main([DEFECTIVE_LAUNCH, "--silent"])
    assert exit_code == 1


def test_cli_exports_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        mermaid_path = os.path.join(tmpdir, "graph.mmd")
        dot_path = os.path.join(tmpdir, "graph.dot")
        sarif_path = os.path.join(tmpdir, "report.sarif")
        json_path = os.path.join(tmpdir, "model.json")

        exit_code = main([
            DEFECTIVE_LAUNCH,
            "--mermaid", mermaid_path,
            "--dot", dot_path,
            "--sarif", sarif_path,
            "--json", json_path,
            "--silent",
        ])

        assert exit_code == 1
        assert os.path.isfile(mermaid_path)
        assert os.path.isfile(dot_path)
        assert os.path.isfile(sarif_path)
        assert os.path.isfile(json_path)

        with open(sarif_path, "r", encoding="utf-8") as f:
            sarif_data = json.load(f)
            assert sarif_data["version"] == "2.1.0"
            results = sarif_data["runs"][0]["results"]
            rule_ids = {r["ruleId"] for r in results}
            assert "TIME-001" in rule_ids
            assert "NAME-001" in rule_ids
            assert "PARAM-001" in rule_ids


def test_cli_argument_overrides():
    # Passing use_sim_time:=false should resolve cleanly
    exit_code = main([CLEAN_LAUNCH, "use_sim_time:=false", "--silent"])
    assert exit_code == 0
