"""Sensor platform for LernSax Mailbox."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    """Set up sensor entities."""
    coordinator: LernsaxMailboxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LernsaxUnreadCountSensor(coordinator)])


class LernsaxUnreadCountSensor(LernsaxMailboxEntity, SensorEntity):
    """Unread message count sensor."""

    _attr_name = "Unread messages"
    _attr_icon = "mdi:email-outline"
    _attr_native_unit_of_measurement = "messages"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: LernsaxMailboxCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_unread_messages"

    @property
    def native_value(self) -> int:
        """Return unread message count."""
        return self.coordinator.data.unread_count
