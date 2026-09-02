from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MEDICATION_1, CONF_MEDICATION_2, DOMAIN
from .entity import MedicalLogEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MedicalLogNumber(entry, data, "medication_1", entry.data[CONF_MEDICATION_1], "mL", 0, 20, 0.5),
            MedicalLogNumber(entry, data, "medication_2", entry.data[CONF_MEDICATION_2], "mL", 0, 20, 0.5),
            MedicalLogNumber(entry, data, "temperature", "Temperature entry", UnitOfTemperature.CELSIUS, 34, 42, 0.1, temperature=True),
        ]
    )


class MedicalLogNumber(MedicalLogEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, entry, data, key, name, unit, minimum, maximum, step, temperature=False):
        super().__init__(entry, data, f"{key}_entry")
        self.value_key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        if temperature:
            self._attr_device_class = NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self):
        return self.data.value(self.value_key)

    async def async_set_native_value(self, value: float) -> None:
        await self.data.async_set_value(self.value_key, value)
