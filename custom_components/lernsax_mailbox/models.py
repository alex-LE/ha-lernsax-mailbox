"""Data models for LernSax Mailbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LernsaxMailboxData:
    """Mailbox state."""

    unread_count: int
    raw_state: dict[str, Any] = field(default_factory=dict)
