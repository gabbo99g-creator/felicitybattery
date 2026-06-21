import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL
from .api import FelicityBmsApiClient, FelicityBmsApiConnectionError, FelicityBmsApiError

class FelicityBmsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Felicity Solar BMS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the user setup step."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            # Reject duplicate configuration for the same host and port
            self._async_abort_entries_match({CONF_HOST: host, CONF_PORT: port})

            try:
                # Test connection by making a call to GET /api/v1/bms/felicity/latest
                session = async_get_clientsession(self.hass)
                client = FelicityBmsApiClient(host, port, session)
                await client.get_latest()
                
                # Connection successful, create the config entry
                return self.async_create_entry(
                    title=f"Felicity Solar BMS ({host}:{port})",
                    data=user_input,
                )
            except FelicityBmsApiConnectionError:
                errors["base"] = "cannot_connect"
            except FelicityBmsApiError:
                errors["base"] = "invalid_bridge_response"
            except Exception:
                errors["base"] = "unknown"

        # Schema definition
        data_schema = vol.Schema({
            vol.Required(CONF_HOST, default="localhost"): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
