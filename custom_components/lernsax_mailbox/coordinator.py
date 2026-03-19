"""Data coordinator for LernSax Mailbox."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LernsaxApiError, LernsaxAuthError, LernsaxClient
from .const import CONF_SCAN_INTERVAL_MINUTES, DOMAIN, OPTION_DEFAULTS
from .models import LernsaxMailboxData

_LOGGER = logging.getLogger(__name__)


class LernsaxMailboxCoordinator(DataUpdateCoordinator[LernsaxMailboxData]):
    """Coordinator for mailbox polling."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: LernsaxClient,
    ) -> None:
        self.entry = entry
        self.client = client

        update_interval = timedelta(
            minutes=int(entry.options.get(CONF_SCAN_INTERVAL_MINUTES, OPTION_DEFAULTS[CONF_SCAN_INTERVAL_MINUTES]))
        )

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN}_{entry.title}",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> LernsaxMailboxData:
        """Fetch latest mailbox data."""
        try:
            return await self.client.async_fetch_mailbox_data()
        except LernsaxAuthError as err:
            raise ConfigEntryAuthFailed from err
        except LernsaxApiError as err:
            raise UpdateFailed(str(err)) from err
