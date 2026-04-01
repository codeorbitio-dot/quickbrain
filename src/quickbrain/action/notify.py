"""
Notify action — send results via webhook, console, or message platform.
"""

from __future__ import annotations

import json
from typing import Any

import httpx

from quickbrain.action import Action
from quickbrain.sources import SearchResult


class ConsoleNotify(Action):
    """Print results to console (default behavior)."""

    @property
    def name(self) -> str:
        return "console"

    async def execute(self, summary: str, results: list[SearchResult] | None = None, **kwargs) -> dict[str, Any]:
        from rich.console import Console
        from rich.panel import Panel
        c = Console()
        c.print(Panel(summary, title="🧠 QuickBrain", border_style="blue"))
        return {"status": "printed", "length": len(summary)}


class WebhookNotify(Action):
    """POST results to a webhook URL (Slack, Discord, custom)."""

    def __init__(self, url: str):
        self.url = url

    @property
    def name(self) -> str:
        return "webhook"

    async def execute(self, summary: str, **kwargs) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.url,
                json={"text": summary},
                timeout=10,
            )
            resp.raise_for_status()
        return {"status": "sent", "code": resp.status_code}
