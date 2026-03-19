"""Config flow for LernSax Mailbox."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LernsaxAuthError, LernsaxClient
from .const import (
    CONF_API_URL,
    CONF_SCAN_INTERVAL_MINUTES,
    DEFAULT_API_URL,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    MAX_SCAN_INTERVAL_MINUTES,
    MIN_SCAN_INTERVAL_MINUTES,
    OPTION_DEFAULTS,
)

_LOGGER = logging.getLogger(__name__)


class LernsaxMailboxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LernSax Mailbox."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            email = user_input[CONF_EMAIL].strip().lower()
            await self.async_set_unique_id(email)
            self._abort_if_unique_id_configured()

            client = LernsaxClient(
                session=async_get_clientsession(self.hass),
                email=email,
                password=user_input[CONF_PASSWORD],
                api_url=user_input[CONF_API_URL],
            )

            try:
                await client.async_validate_credentials()
            except LernsaxAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during LernSax login validation")
                errors["base"] = "cannot_connect"
            else:
                data = {
                    CONF_EMAIL: email,
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }
                options = {
                    CONF_API_URL: user_input[CONF_API_URL],
                    CONF_SCAN_INTERVAL_MINUTES: int(user_input[CONF_SCAN_INTERVAL_MINUTES]),
                }
                return self.async_create_entry(title=email, data=data, options=options)

        return self.async_show_form(
            step_id="user",
            data_schema=self._build_schema(user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow handler."""
        return LernsaxMailboxOptionsFlow()

    def _build_schema(self, user_input: Mapping[str, Any] | None = None) -> vol.Schema:
        """Build the setup form schema."""
        return vol.Schema(
            {
                vol.Required(
                    CONF_EMAIL,
                    default=(user_input or {}).get(CONF_EMAIL, ""),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.EMAIL)
                ),
                vol.Required(
                    CONF_PASSWORD,
                    default=(user_input or {}).get(CONF_PASSWORD, ""),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                ),
                vol.Required(
                    CONF_API_URL,
                    default=(user_input or {}).get(CONF_API_URL, DEFAULT_API_URL),
                ): selector.TextSelector(),
                vol.Required(
                    CONF_SCAN_INTERVAL_MINUTES,
                    default=(user_input or {}).get(CONF_SCAN_INTERVAL_MINUTES, DEFAULT_SCAN_INTERVAL_MINUTES),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL_MINUTES,
                        max=MAX_SCAN_INTERVAL_MINUTES,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
            }
        )


class LernsaxMailboxOptionsFlow(config_entries.OptionsFlowWithReload):
    """LernSax Mailbox options flow."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage integration options."""
        if user_input is not None:
            user_input[CONF_SCAN_INTERVAL_MINUTES] = int(user_input[CONF_SCAN_INTERVAL_MINUTES])
            return self.async_create_entry(title="", data=user_input)

        current = {**OPTION_DEFAULTS, **self.config_entry.options}

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_URL,
                    default=current[CONF_API_URL],
                ): selector.TextSelector(),
                vol.Required(
                    CONF_SCAN_INTERVAL_MINUTES,
                    default=current[CONF_SCAN_INTERVAL_MINUTES],
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL_MINUTES,
                        max=MAX_SCAN_INTERVAL_MINUTES,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
