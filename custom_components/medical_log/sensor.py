from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_MEDICATION_1, CONF_MEDICATION_2, DOMAIN
from .entity import MedicalLogEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            LastMedicationSensor(entry, data, "medication_1", entry.data[CONF_MEDICATION_1]),
            LastMedicationSensor(entry, data, "medication_2", entry.data[CONF_MEDICATION_2]),
            LastTemperatureSensor(entry, data),
        ]
    )


class LastMedicationSensor(MedicalLogEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, entry, data, medication_key, medication_name):
        super().__init__(entry, data, f"last_{medication_key}")
        self.medication_key = medication_key
        self._attr_name = f"Last {medication_name}"
        self._attr_icon = "mdi:medication-clock"

    @property
    def native_value(self) -> datetime | None:
        last = self.data.last(self.medication_key)
        if not last:
            return None
        return dt_util.parse_datetime(last["timestamp"])

    @property
    def extra_state_attributes(self):
        last = self.data.last(self.medication_key)
        if not last:
            return None
        return {"dose": last["value"], "unit": last["unit"], "child": last["child_name"]}


class LastTemperatureSensor(MedicalLogEntity, SensorEntity):
    _attr_name = "Last temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    def __init__(self, entry, data):
        super().__init__(entry, data, "last_temperature")

    @property
    def native_value(self) -> float | None:
        last = self.data.last("temperature")
        return float(last["value"]) if last else None

    @property
    def extra_state_attributes(self):
        last = self.data.last("temperature")
        if not last:
            return None
        return {"logged_at": last["timestamp"], "child": last["child_name"]}
