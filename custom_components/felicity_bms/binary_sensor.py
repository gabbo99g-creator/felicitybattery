from dataclasses import dataclass
import logging
from typing import Callable, Any, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import EntityCategory

from .const import DOMAIN
from .coordinator import FelicityBmsDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass
class FelicityBmsBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Felicity BMS binary sensor entities."""
    is_on_fn: Optional[Callable[[dict], bool]] = None

# List of binary sensor definitions
BINARY_SENSORS = [
    FelicityBmsBinarySensorEntityDescription(
        key="fault",
        name="Fault Status",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.get("fault_flag", 0) > 0,
    ),
    FelicityBmsBinarySensorEntityDescription(
        key="alarm",
        name="Alarm Status",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data: data.get("alarm_flag", 0) > 0,
    ),
    FelicityBmsBinarySensorEntityDescription(
        key="stale_data",
        name="Stale Data",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: "stale_reading" in data.get("warnings", []),
    ),
    FelicityBmsBinarySensorEntityDescription(
        key="high_cell_delta_warning",
        name="High Cell Delta Warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        is_on_fn=lambda data: "high_cell_delta" in data.get("warnings", []),
    ),
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Felicity Solar BMS binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Register all binary sensors
    entities = [
        FelicityBmsBinarySensor(coordinator, entry, description)
        for description in BINARY_SENSORS
    ]
    async_add_entities(entities)

class FelicityBmsBinarySensor(CoordinatorEntity[FelicityBmsDataUpdateCoordinator], BinarySensorEntity):
    """Representation of a Felicity Solar BMS Binary Sensor."""
    
    entity_description: FelicityBmsBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: FelicityBmsDataUpdateCoordinator, entry: ConfigEntry, description: FelicityBmsBinarySensorEntityDescription):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        
        # Configure Device Info grouping
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Felicity Solar BMS",
            "model": "Low-voltage BMS (LPBF48200-P)",
            "manufacturer": "Felicity Solar",
        }

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if the binary sensor is on."""
        # Handle cases where coordinator has no data or structure is empty
        if not self.coordinator.data or not isinstance(self.coordinator.data, dict):
            return None
            
        is_on_fn = self.entity_description.is_on_fn
        if is_on_fn:
            try:
                return is_on_fn(self.coordinator.data)
            except Exception as e:
                _LOGGER.error(f"Error extracting binary state for sensor {self.entity_description.key}: {e}")
                return None
        return None
