# Medical Log for Home Assistant

A local-first Home Assistant custom integration for recording medication administration and temperature readings for multiple child profiles.

> **Development status:** early private test build. Do not rely on Medical Log as a medical record or for dosing decisions. It records information entered by the user and does not recommend medicines, doses, or dosing intervals.

## Model

**Household → Child profiles → Medicines → Logged entries**

Each child is an independent Home Assistant config entry with separate persistent history. Medicines are configurable rather than hard-coded to brands.

## v0.1 private test scope

- Multiple child profiles
- Two configurable medicines per child in the first setup UI
- Dose entry controls
- Temperature entry control
- Explicit Log buttons: changing a value alone never creates a record
- Last medication and temperature sensors
- Persistent local storage across Home Assistant restarts
- Events fired for logged entries
- Local-only operation

The underlying records identify both the child profile and medicine so histories cannot be mixed between profiles. The data model is intended to expand to arbitrary medicines after the first test build.

## Installation for private testing

Add this repository to HACS as a custom **Integration** repository, install **Medical Log**, restart Home Assistant, then go to **Settings → Devices & services → Add integration → Medical Log**.

Keep any existing medication helpers/scripts/dashboard in place while testing this build.

## Safety

Medical Log is a logging utility, not a medical device. It does not calculate or recommend medicines, doses, dosing intervals, or treatment decisions. Follow the medicine label and appropriate professional medical advice.

## Licence

MIT
