from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .api import FelicityBmsApiClient
from .coordinator import FelicityBmsDataUpdateCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Felicity Solar BMS from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    # Use scan_interval from configuration, fallback to default
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    # Setup async API client using Home Assistant's shared ClientSession
    session = async_get_clientsession(hass)
    api_client = FelicityBmsApiClient(host, port, session)
    
    # Initialize coordinator
    coordinator = FelicityBmsDataUpdateCoordinator(hass, api_client, scan_interval)

    # Perform first refresh so setup fails early if bridge is completely offline
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator instance
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to sensor and binary_sensor platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
