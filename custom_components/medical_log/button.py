from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
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
            MedicationLogButton(entry, data, "medication_1", entry.data[CONF_MEDICATION_1]),
            MedicationLogButton(entry, data, "medication_2", entry.data[CONF_MEDICATION_2]),
            TemperatureLogButton(entry, data),
        ]
    )


class MedicationLogButton(MedicalLogEntity, ButtonEntity):
    def __init__(self, entry, data, medication_key, medication_name):
        super().__init__(entry, data, f"log_{medication_key}")
        self.medication_key = medication_key
        self.medication_name = medication_name
        self._attr_name = f"Log {medication_name}"
        self._attr_icon = "mdi:medication"

    async def async_press(self) -> None:
        await self.data.async_log_medication(self.medication_key, self.medication_name)


class TemperatureLogButton(MedicalLogEntity, ButtonEntity):
    _attr_name = "Log temperature"
    _attr_icon = "mdi:thermometer-check"

    def __init__(self, entry, data):
        super().__init__(entry, data, "log_temperature")

    async def async_press(self) -> None:
        await self.data.async_log_temperature()
