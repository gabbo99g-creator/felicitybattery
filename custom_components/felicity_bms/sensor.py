from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Callable, Any, Optional

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
    SensorEntityDescription,
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
class FelicityBmsSensorEntityDescription(SensorEntityDescription):
    """Class describing Felicity BMS sensor entities."""
    value_fn: Optional[Callable[[dict], Any]] = None

# List of sensor entity definitions
SENSORS = [
    FelicityBmsSensorEntityDescription(
        key="soc_percent",
        name="State of Charge",
        native_unit_of_measurement="%",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("soc_percent"),
    ),
    FelicityBmsSensorEntityDescription(
        key="soh_percent",
        name="State of Health",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("soh_percent"),
    ),
    FelicityBmsSensorEntityDescription(
        key="battery_voltage_v",
        name="Voltage",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery_voltage_v"),
    ),
    FelicityBmsSensorEntityDescription(
        key="battery_current_a",
        name="Current",
        native_unit_of_measurement="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("battery_current_a"),
    ),
    FelicityBmsSensorEntityDescription(
        key="cycle_count",
        name="Cycle Count",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("cycle_count"),
    ),
    FelicityBmsSensorEntityDescription(
        key="cell_min_v",
        name="Cell Min Voltage",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("cell_min_v"),
    ),
    FelicityBmsSensorEntityDescription(
        key="cell_max_v",
        name="Cell Max Voltage",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("cell_max_v"),
    ),
    FelicityBmsSensorEntityDescription(
        key="cell_delta_mv",
        name="Cell Delta",
        native_unit_of_measurement="mV",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("cell_delta_mv"),
    ),
    FelicityBmsSensorEntityDescription(
        key="charge_energy_wh",
        name="Charge Energy",
        native_unit_of_measurement="Wh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("charge_energy_wh"),
    ),
    FelicityBmsSensorEntityDescription(
        key="discharge_energy_wh",
        name="Discharge Energy",
        native_unit_of_measurement="Wh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("discharge_energy_wh"),
    ),
    FelicityBmsSensorEntityDescription(
        key="timestamp",
        name="Last Update",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: parse_timestamp(data.get("timestamp")),
    ),
]

def parse_timestamp(timestamp_str: Optional[str]) -> Optional[datetime]:
    """Safely parse ISO timestamp string into datetime object."""
    if not timestamp_str:
        return None
    try:
        # Standard fromisoformat handles YYYY-MM-DDTHH:MM:SS
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError) as e:
        _LOGGER.warning(f"Failed to parse timestamp '{timestamp_str}': {e}")
        return None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Felicity Solar BMS sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Create and register the sensor entities
    entities = [
        FelicityBmsSensor(coordinator, entry, description)
        for description in SENSORS
    ]
    async_add_entities(entities)

class FelicityBmsSensor(CoordinatorEntity[FelicityBmsDataUpdateCoordinator], SensorEntity):
    """Representation of a Felicity Solar BMS Sensor."""
    
    entity_description: FelicityBmsSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: FelicityBmsDataUpdateCoordinator, entry: ConfigEntry, description: FelicityBmsSensorEntityDescription):
        """Initialize the sensor."""
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
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        # Handle cases where coordinator has no data or structure is empty
        if not self.coordinator.data or not isinstance(self.coordinator.data, dict):
            return None
            
        value_fn = self.entity_description.value_fn
        if value_fn:
            try:
                return value_fn(self.coordinator.data)
            except Exception as e:
                _LOGGER.error(f"Error extracting value for sensor {self.entity_description.key}: {e}")
                return None
        return None
