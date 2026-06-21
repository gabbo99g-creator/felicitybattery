from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

from .const import DOMAIN, LOGGER
from .api import FelicityBmsApiClient, FelicityBmsApiError

class FelicityBmsDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching data from felicity-bms-bridge REST API."""

    def __init__(self, hass: HomeAssistant, api_client: FelicityBmsApiClient, update_interval_seconds: int):
        """Initialize coordinator."""
        self.api_client = api_client
        
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval_seconds),
        )

    async def _async_update_data(self):
        """Fetch telemetry from the bridge API."""
        try:
            data = await self.api_client.get_latest()
            LOGGER.debug(f"Successfully polled Felicity BMS data: {data}")
            return data
        except FelicityBmsApiError as e:
            # Raise UpdateFailed to let Home Assistant mark entities as unavailable
            raise UpdateFailed(f"Error updating Felicity BMS data: {e}") from e
