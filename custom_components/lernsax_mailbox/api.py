"""Async client for the LernSax JSON-RPC endpoint."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

import aiohttp

from .const import DEFAULT_API_URL
from .models import LernsaxMailboxData

_LOGGER = logging.getLogger(__name__)


class LernsaxApiError(Exception):
    """Base API error."""


class LernsaxAuthError(LernsaxApiError):
    """Authentication failed."""


@dataclass(slots=True)
class LernsaxClient:
    """Small client for accessing the LernSax mailbox status."""

    session: aiohttp.ClientSession
    email: str
    password: str
    api_url: str = DEFAULT_API_URL

    async def async_validate_credentials(self) -> None:
        """Validate credentials by reading mailbox state once."""
        await self.async_fetch_mailbox_data()

    async def async_fetch_mailbox_data(self) -> LernsaxMailboxData:
        """Fetch mailbox state in one JSON-RPC batch."""
        payload = self._jsonrpc(
            [
                (1, "login", {"login": self.email, "password": self.password, "get_miniature": False}),
                (2, "set_focus", {"object": "mailbox"}),
                (3, "get_state", {}),
            ]
        )
        response = await self._post(payload)

        login_result = self._result_by_id(response, 1)
        state_result = self._result_by_id(response, 3)

        if login_result.get("return") != "OK":
            errno = login_result.get("errno")
            raise LernsaxAuthError(f"LernSax login failed (errno={errno!r})")

        if state_result.get("return") != "OK":
            errno = state_result.get("errno")
            raise LernsaxApiError(f"LernSax mailbox.get_state failed (errno={errno!r})")

        unread_count = self._extract_unread_count(state_result)
        return LernsaxMailboxData(unread_count=unread_count, raw_state=state_result)

    async def _post(self, payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """POST JSON-RPC payload."""
        try:
            async with self.session.post(self.api_url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
        except aiohttp.ClientResponseError as err:
            raise LernsaxApiError(f"HTTP error talking to LernSax: {err.status}") from err
        except aiohttp.ClientError as err:
            raise LernsaxApiError("Network error talking to LernSax") from err
        except ValueError as err:
            raise LernsaxApiError("Invalid JSON response from LernSax") from err

        if not isinstance(data, list):
            raise LernsaxApiError("Unexpected JSON-RPC response shape from LernSax")

        return data

    @staticmethod
    def _jsonrpc(calls: list[tuple[int, str, dict[str, Any]]]) -> list[dict[str, Any]]:
        return [
            {"id": call_id, "jsonrpc": "2.0", "method": method, "params": params}
            for call_id, method, params in calls
        ]

    @staticmethod
    def _result_by_id(response: list[dict[str, Any]], request_id: int) -> dict[str, Any]:
        for item in response:
            if item.get("id") == request_id:
                result = item.get("result")
                if isinstance(result, dict):
                    return result
                break
        raise LernsaxApiError(f"Missing JSON-RPC result for id={request_id}")

    def _extract_unread_count(self, state_result: dict[str, Any]) -> int:
        """Best-effort unread counter extraction."""

        candidates = (
            "unread",
            "unread_count",
            "unread_messages",
            "unread_message_count",
            "messages_unread",
            "mail_unread",
            "mails_unread",
            "ungelesen",
        )

        def visit(value: Any) -> int | None:
            if isinstance(value, dict):
                for key, nested in value.items():
                    lowered = str(key).lower()
                    if any(candidate in lowered for candidate in candidates):
                        parsed = self._coerce_int(nested)
                        if parsed is not None:
                            return parsed
                    found = visit(nested)
                    if found is not None:
                        return found
            elif isinstance(value, list):
                for item in value:
                    found = visit(item)
                    if found is not None:
                        return found
            return None

        unread_count = visit(state_result)
        if unread_count is None:
            _LOGGER.debug("Could not determine unread counter from LernSax response: %s", state_result)
            return 0
        return unread_count

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
        return None
