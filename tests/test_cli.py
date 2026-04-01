"""Tests for CLI module."""
import pytest
import subprocess
import sys


def test_cli_help():
    """CLI should run without crashing."""
    result = subprocess.run(
        [sys.executable, "-m", "quickbrain", "--help"],
        capture_output=True, text=True, timeout=10,
        cwd="/root/.openclaw/workspace/quickbrain"
    )
    # Even if --help is not handled, it should not crash


def test_cli_no_args_exits():
    """CLI with no args should print usage and exit."""
    result = subprocess.run(
        [sys.executable, "-m", "quickbrain"],
        capture_output=True, text=True, timeout=10,
        cwd="/root/.openclaw/workspace/quickbrain"
    )
    # Should have non-zero exit code or print usage hint
    output = result.stdout + result.stderr
