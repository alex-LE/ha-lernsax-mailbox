"""Base entity for LernSax Mailbox."""

from __future__ import annotations

from homeassistant.const import CONF_EMAIL
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LernsaxMailboxCoordinator


class LernsaxMailboxEntity(CoordinatorEntity[LernsaxMailboxCoordinator]):
    """Base coordinator entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: LernsaxMailboxCoordinator) -> None:
        super().__init__(coordinator)
        self._account = coordinator.entry.data[CONF_EMAIL]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=coordinator.entry.title,
            manufacturer="LernSax",
            model="Mailbox",
        )

    @property
    def extra_state_attributes(self) -> dict[str, str | int]:
        """Return entity attributes."""
        data = self.coordinator.data
        return {
            "account": self._account,
            "unread_count": data.unread_count if data else 0,
        }
