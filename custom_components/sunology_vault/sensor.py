"""Sensor platform for Sunology VAULT."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BATTERY_CAPACITY_WH, DOMAIN
from .coordinator import SunologyDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    coordinator: SunologyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    for serial in coordinator.data.batteries:
        entities.append(SunologyBatteryLevelSensor(coordinator, serial))
        entities.append(SunologyBatteryStateSensor(coordinator, serial))
        entities.append(SunologyBatteryEnergySensor(coordinator, serial))

    async_add_entities(entities)


class SunologyBatteryLevelSensor(
    CoordinatorEntity[SunologyDataUpdateCoordinator], SensorEntity
):
    """Battery level percentage sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "battery_level"

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._serial = serial
        self._attr_unique_id = f"{serial}_battery_level"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"{coordinator.data.batteries[serial].name} ({serial})",
            "manufacturer": "Sunology",
            "model": "VAULT",
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        battery = self.coordinator.data.batteries.get(self._serial)
        return battery is not None and battery.device_state == "CONNECTED"

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        battery = self.coordinator.data.batteries.get(self._serial)
        if battery:
            return battery.battery_level
        return None


class SunologyBatteryStateSensor(
    CoordinatorEntity[SunologyDataUpdateCoordinator], SensorEntity
):
    """Battery state sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["off", "charging", "discharging"]
    _attr_translation_key = "battery_state"

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._serial = serial
        self._attr_unique_id = f"{serial}_battery_state"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"{coordinator.data.batteries[serial].name} ({serial})",
            "manufacturer": "Sunology",
            "model": "VAULT",
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        battery = self.coordinator.data.batteries.get(self._serial)
        return battery is not None and battery.device_state == "CONNECTED"

    @property
    def native_value(self) -> str | None:
        """Return the battery state."""
        battery = self.coordinator.data.batteries.get(self._serial)
        if battery and battery.battery_state:
            return battery.battery_state.lower()
        return None


class SunologyBatteryEnergySensor(
    CoordinatorEntity[SunologyDataUpdateCoordinator], SensorEntity
):
    """Battery available energy sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_translation_key = "battery_energy"

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._serial = serial
        self._attr_unique_id = f"{serial}_battery_energy"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"{coordinator.data.batteries[serial].name} ({serial})",
            "manufacturer": "Sunology",
            "model": "VAULT",
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        battery = self.coordinator.data.batteries.get(self._serial)
        return battery is not None and battery.device_state == "CONNECTED"

    @property
    def native_value(self) -> int | None:
        """Return the available energy in Wh."""
        battery = self.coordinator.data.batteries.get(self._serial)
        if battery:
            return int(battery.battery_level * BATTERY_CAPACITY_WH / 100)
        return None
