"""Constants for the LernSax Mailbox integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "lernsax_mailbox"
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

DEFAULT_API_URL = "https://www.lernsax.de/jsonrpc.php"
DEFAULT_SCAN_INTERVAL_MINUTES = 30
MIN_SCAN_INTERVAL_MINUTES = 5
MAX_SCAN_INTERVAL_MINUTES = 720

CONF_SCAN_INTERVAL_MINUTES = "scan_interval_minutes"
CONF_API_URL = "api_url"

OPTION_DEFAULTS = {
    CONF_SCAN_INTERVAL_MINUTES: DEFAULT_SCAN_INTERVAL_MINUTES,
    CONF_API_URL: DEFAULT_API_URL,
}
