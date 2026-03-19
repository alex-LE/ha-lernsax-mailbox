"""The LernSax Mailbox integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LernsaxClient
from .const import CONF_API_URL, DOMAIN, OPTION_DEFAULTS, PLATFORMS
from .coordinator import LernsaxMailboxCoordinator

type LernsaxConfigEntry = ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: LernsaxConfigEntry) -> bool:
    """Set up LernSax Mailbox from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    client = LernsaxClient(
        session=session,
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
        api_url=entry.options.get(CONF_API_URL, OPTION_DEFAULTS[CONF_API_URL]),
    )
    coordinator = LernsaxMailboxCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: LernsaxConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: LernsaxConfigEntry) -> None:
    """Reload config entry after options update."""
    await hass.config_entries.async_reload(entry.entry_id)
