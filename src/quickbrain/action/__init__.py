"""
Base action interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Action(ABC):
    """Post-research action that can be executed on results."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable action name."""
        ...

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """Execute the action. Returns a status dict."""
        ...
