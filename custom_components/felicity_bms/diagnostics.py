from typing import Any, Dict
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.diagnostics import async_redact_data

from .const import DOMAIN, CONF_HOST, CONF_PORT

# Set parameters to redact (e.g. host name/IP)
TO_REDACT = {CONF_HOST}

async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> Dict[str, Any]:
    """Return diagnostics for a Felicity Solar BMS config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Redact sensitive config entry data (e.g. host)
    redacted_config = async_redact_data(dict(entry.data), TO_REDACT)
    
    # Get latest data from coordinator
    latest_data = coordinator.data if isinstance(coordinator.data, dict) else {}
    
    # Assemble diagnostic info
    diagnostics_data = {
        "integration": {
            "domain": DOMAIN,
            "version": "1.0.0",
        },
        "config_entry": redacted_config,
        "bridge_telemetry": {
            "status": latest_data.get("status", "unknown"),
            "source": latest_data.get("source"),
            "read_only": latest_data.get("read_only"),
            "warnings": latest_data.get("warnings", []),
            "device_type": latest_data.get("device_type"),
            "model": latest_data.get("model"),
        }
    }
    
    return diagnostics_data
