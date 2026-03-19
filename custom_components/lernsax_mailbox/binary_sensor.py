"""Binary sensor platform for LernSax Mailbox."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import LernsaxMailboxCoordinator
from .entity import LernsaxMailboxEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensor entities."""
    coordinator: LernsaxMailboxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LernsaxHasUnreadBinarySensor(coordinator)])


class LernsaxHasUnreadBinarySensor(LernsaxMailboxEntity, BinarySensorEntity):
    """Binary sensor indicating whether unread mail exists."""

    _attr_name = "Has unread mail"
    _attr_icon = "mdi:email-alert-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: LernsaxMailboxCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_has_unread_mail"

    @property
    def is_on(self) -> bool:
        """Return whether unread mail exists."""
        return self.coordinator.data.unread_count > 0
