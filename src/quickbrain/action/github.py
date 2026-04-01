"""
GitHub Actions — open issues, create PRs, etc.
Uses `gh` CLI under the hood for authentication.
"""

from __future__ import annotations

import subprocess
from typing import Any

from quickbrain.action import Action


class GitHubIssue(Action):
    """Open a GitHub issue via gh CLI."""

    @property
    def name(self) -> str:
        return "github_issue"

    def __init__(self, repo: str, labels: list[str] | None = None):
        self.repo = repo
        self.labels = labels or []

    async def execute(self, title: str, body: str, **kwargs) -> dict[str, Any]:
        cmd = [
            "gh", "issue", "create",
            "--repo", self.repo,
            "--title", title,
            "--body", body,
        ]
        for label in self.labels:
            cmd.extend(["--label", label])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"status": "error", "stderr": result.stderr}
        return {"status": "created", "url": result.stdout.strip()}


class GitHubPR(Action):
    """Create a GitHub PR via gh CLI."""

    @property
    def name(self) -> str:
        return "github_pr"

    def __init__(self, repo: str, base: str = "main"):
        self.repo = repo
        self.base = base

    async def execute(self, title: str, body: str, head: str | None = None, **kwargs) -> dict[str, Any]:
        cmd = [
            "gh", "pr", "create",
            "--repo", self.repo,
            "--base", self.base,
            "--title", title,
            "--body", body,
        ]
        if head:
            cmd.extend(["--head", head])
        if head:
            cmd.extend(["--head", head])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {"status": "error", "stderr": result.stderr}
        return {"status": "created", "url": result.stdout.strip()}
