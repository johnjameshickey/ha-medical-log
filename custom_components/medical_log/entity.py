from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import CONF_CHILD_NAME, DOMAIN
from .model import MedicalLogData


class MedicalLogEntity(Entity):
    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, data: MedicalLogData, key: str) -> None:
        self.entry = entry
        self.data = data
        self.key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Medical Log — {entry.data[CONF_CHILD_NAME]}",
            manufacturer="Medical Log",
            model="Child profile",
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.data.add_listener(self.async_write_ha_state))
