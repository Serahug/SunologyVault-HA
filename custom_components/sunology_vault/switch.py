"""Switch platform for Sunology VAULT."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunologyDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches from config entry."""
    coordinator: SunologyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = []

    for serial in coordinator.data.batteries:
        entities.append(SunologyPreserveEnergySwitch(coordinator, serial))

    async_add_entities(entities)


class SunologyPreserveEnergySwitch(
    CoordinatorEntity[SunologyDataUpdateCoordinator], SwitchEntity
):
    """Switch for battery preserve energy mode."""

    _attr_has_entity_name = True
    _attr_translation_key = "preserve_energy"

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._serial = serial
        self._attr_unique_id = f"{serial}_preserve_energy"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"{coordinator.data.batteries[serial].name} ({serial})",
            "manufacturer": "Sunology",
            "model": "VAULT",
        }

    @property
    def _battery_data(self):
        """Get battery data for this switch."""
        return self.coordinator.data.batteries.get(self._serial)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        battery = self._battery_data
        return battery is not None and battery.device_state == "CONNECTED"

    @property
    def is_on(self) -> bool | None:
        """Return true if preserve energy mode is on."""
        if self._battery_data:
            return self._battery_data.preserve_energy
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on preserve energy mode."""
        await self.coordinator.async_set_preserve_energy(self._serial, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off preserve energy mode."""
        await self.coordinator.async_set_preserve_energy(self._serial, False)
