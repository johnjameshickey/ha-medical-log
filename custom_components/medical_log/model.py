from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any, Callable

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import EVENT_LOG_ENTRY, STORAGE_KEY_PREFIX, STORAGE_VERSION


class MedicalLogData:
    """Persistent data for one child profile."""

    def __init__(self, hass: HomeAssistant, entry_id: str, child_name: str) -> None:
        self.hass = hass
        self.entry_id = entry_id
        self.child_name = child_name
        self.store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{STORAGE_KEY_PREFIX}.{entry_id}"
        )
        self.data: dict[str, Any] = {
            "values": {"medication_1": 0.0, "medication_2": 0.0, "temperature": 37.0},
            "last": {"medication_1": None, "medication_2": None, "temperature": None},
            "history": [],
        }
        self._listeners: list[Callable[[], None]] = []

    async def async_load(self) -> None:
        stored = await self.store.async_load()
        if stored:
            self.data.update(stored)
            self.data.setdefault("values", {})
            self.data.setdefault("last", {})
            self.data.setdefault("history", [])
            self.data["values"].setdefault("medication_1", 0.0)
            self.data["values"].setdefault("medication_2", 0.0)
            self.data["values"].setdefault("temperature", 37.0)
            self.data["last"].setdefault("medication_1", None)
            self.data["last"].setdefault("medication_2", None)
            self.data["last"].setdefault("temperature", None)

    async def async_save(self) -> None:
        await self.store.async_save(self.data)

    def add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(listener)

        def remove() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return remove

    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    def value(self, key: str) -> float:
        return float(self.data["values"].get(key, 0.0))

    async def async_set_value(self, key: str, value: float) -> None:
        self.data["values"][key] = float(value)
        await self.async_save()
        self._notify()

    def last(self, key: str) -> dict[str, Any] | None:
        value = self.data["last"].get(key)
        return deepcopy(value) if value else None

    async def async_log_medication(self, key: str, name: str) -> None:
        await self._async_log(
            kind="medication",
            key=key,
            name=name,
            value=self.value(key),
            unit="mL",
        )

    async def async_log_temperature(self) -> None:
        await self._async_log(
            kind="temperature",
            key="temperature",
            name="Temperature",
            value=self.value("temperature"),
            unit="°C",
        )

    async def _async_log(
        self, *, kind: str, key: str, name: str, value: float, unit: str
    ) -> None:
        now: datetime = dt_util.utcnow()
        entry = {
            "timestamp": now.isoformat(),
            "profile_id": self.entry_id,
            "child_name": self.child_name,
            "kind": kind,
            "key": key,
            "name": name,
            "value": value,
            "unit": unit,
        }
        self.data["last"][key] = entry
        self.data["history"].append(entry)
        self.data["history"] = self.data["history"][-500:]
        await self.async_save()
        self.hass.bus.async_fire(EVENT_LOG_ENTRY, deepcopy(entry))
        self._notify()
