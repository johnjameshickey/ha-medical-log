from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_CHILD_NAME, DOMAIN, PLATFORMS
from .model import MedicalLogData

CARD_URL = "/medical_log/medical-log-card.js"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register bundled frontend assets."""
    card_path = Path(__file__).parent / "www" / "medical-log-card.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(card_path), False)]
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    data = MedicalLogData(hass, entry.entry_id, entry.data[CONF_CHILD_NAME])
    await data.async_load()
    hass.data[DOMAIN][entry.entry_id] = data
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
