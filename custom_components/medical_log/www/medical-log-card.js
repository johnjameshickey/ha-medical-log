class MedicalLogCard extends HTMLElement {
  setConfig(config) {
    if (!config.profile) throw new Error("Medical Log Card requires profile");
    this.config = config;
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() { return 8; }

  _entities() {
    const p = this.config.profile;
    return {
      med1: this.config.medication_1_entry || `number.${p}_medication_1_entry`,
      med2: this.config.medication_2_entry || `number.${p}_medication_2_entry`,
      temp: this.config.temperature_entry || `number.${p}_temperature_entry`,
      log1: this.config.log_medication_1 || `button.${p}_log_medication_1`,
      log2: this.config.log_medication_2 || `button.${p}_log_medication_2`,
      logTemp: this.config.log_temperature || `button.${p}_log_temperature`,
      last1: this.config.last_medication_1 || `sensor.${p}_last_medication_1`,
      last2: this.config.last_medication_2 || `sensor.${p}_last_medication_2`,
      lastTemp: this.config.last_temperature || `sensor.${p}_last_temperature`,
    };
  }

  _state(id) { return this._hass?.states[id]; }
  _name(id, fallback) { return this._state(id)?.attributes?.friendly_name || fallback; }
  _value(id) { return this._state(id)?.state ?? "—"; }

  _lastTime(id) {
    const state = this._state(id)?.state;
    if (!state || ["unknown", "unavailable"].includes(state)) return "—";
    const date = new Date(state);
    return Number.isNaN(date.getTime()) ? state : date.toLocaleTimeString([], {hour:"2-digit", minute:"2-digit"});
  }

  async _setNumber(entityId, delta) {
    const entity = this._state(entityId);
    if (!entity) return;
    const current = Number(entity.state);
    const step = Number(entity.attributes.step || 0.5);
    const min = Number(entity.attributes.min ?? -Infinity);
    const max = Number(entity.attributes.max ?? Infinity);
    const value = Math.min(max, Math.max(min, current + delta * step));
    await this._hass.callService("number", "set_value", { entity_id: entityId, value });
  }

  async _press(entityId) {
    if (!this._state(entityId)) return;
    await this._hass.callService("button", "press", { entity_id: entityId });
  }

  _control(entityId, accent) {
    const state = this._state(entityId);
    if (!state) return `<div class="missing">Missing: ${entityId}</div>`;
    const unit = state.attributes.unit_of_measurement || "";
    return `<div class="counter" style="--accent:${accent}">
      <button data-minus="${entityId}">−</button>
      <div><strong>${state.state}</strong><span>${unit}</span></div>
      <button data-plus="${entityId}">+</button>
    </div>`;
  }

  render() {
    if (!this._hass || !this.config || !this.shadowRoot) return;
    const e = this._entities();
    const child = this.config.title || this.config.profile.replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
    const med1Name = this.config.medication_1_name || this._name(e.med1, "Medication 1").replace(child + " ", "");
    const med2Name = this.config.medication_2_name || this._name(e.med2, "Medication 2").replace(child + " ", "");
    const dose1 = this._state(e.last1)?.attributes?.dose;
    const dose2 = this._state(e.last2)?.attributes?.dose;

    this.shadowRoot.innerHTML = `<style>
      :host{display:block;font-family:var(--paper-font-body1_-_font-family,Roboto,sans-serif)}
      ha-card{display:block;background:var(--ha-card-background,var(--card-background-color,#fff));border-radius:var(--ha-card-border-radius,12px);box-shadow:var(--ha-card-box-shadow);padding:18px;color:var(--primary-text-color)}
      h2{margin:0;font-size:22px} .sub{color:var(--secondary-text-color);font-size:13px;margin:3px 0 18px}
      .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.panel{border:1px solid var(--divider-color);border-radius:14px;padding:14px}.panel h3{margin:0 0 10px;font-size:16px}
      .counter{display:grid;grid-template-columns:44px 1fr 44px;align-items:center;text-align:center;background:color-mix(in srgb,var(--accent) 12%,transparent);border-radius:12px;overflow:hidden}.counter button{height:46px;border:0;background:transparent;color:var(--accent);font-size:25px;cursor:pointer}.counter strong{font-size:20px}.counter span{font-size:12px;margin-left:4px;color:var(--secondary-text-color)}
      .log{width:100%;margin-top:10px;border:0;border-radius:12px;padding:12px;font-weight:700;cursor:pointer;background:var(--accent);color:white}.purple{--accent:#7e57c2}.orange{--accent:#ef8c22}.green{--accent:#43a047}
      .temperature{margin-top:12px}.latest-title{margin:20px 0 9px;font-weight:700}.latest{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}.latest div{background:var(--secondary-background-color);border-radius:12px;padding:10px}.latest b{display:block;font-size:13px}.latest span{display:block;margin-top:5px;font-size:13px;color:var(--secondary-text-color)}.missing{font-size:12px;color:var(--error-color);padding:8px}
      @media(max-width:600px){.grid{grid-template-columns:1fr 1fr}.latest{grid-template-columns:1fr}.panel{padding:10px}}
    </style>
    <ha-card>
      <h2>💊 ${child} — Medical Log</h2><div class="sub">Set the value, then tap LOG</div>
      <div class="grid">
        <div class="panel purple"><h3>${med1Name}</h3>${this._control(e.med1,"#7e57c2")}<button class="log" data-press="${e.log1}">LOG ${med1Name.toUpperCase()}</button></div>
        <div class="panel orange"><h3>${med2Name}</h3>${this._control(e.med2,"#ef8c22")}<button class="log" data-press="${e.log2}">LOG ${med2Name.toUpperCase()}</button></div>
      </div>
      <div class="panel green temperature"><h3>🌡 Temperature</h3>${this._control(e.temp,"#43a047")}<button class="log" data-press="${e.logTemp}">LOG TEMPERATURE</button></div>
      <div class="latest-title">Latest</div>
      <div class="latest">
        <div><b>${med1Name}</b><span>${this._lastTime(e.last1)}${dose1 !== undefined ? ` · ${dose1} mL` : ""}</span></div>
        <div><b>${med2Name}</b><span>${this._lastTime(e.last2)}${dose2 !== undefined ? ` · ${dose2} mL` : ""}</span></div>
        <div><b>Temperature</b><span>${this._value(e.lastTemp)} ${this._state(e.lastTemp)?.attributes?.unit_of_measurement || ""}</span></div>
      </div>
    </ha-card>`;

    this.shadowRoot.querySelectorAll("[data-minus]").forEach(x => x.onclick = () => this._setNumber(x.dataset.minus,-1));
    this.shadowRoot.querySelectorAll("[data-plus]").forEach(x => x.onclick = () => this._setNumber(x.dataset.plus,1));
    this.shadowRoot.querySelectorAll("[data-press]").forEach(x => x.onclick = () => this._press(x.dataset.press));
  }
}

customElements.define("medical-log-card", MedicalLogCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "medical-log-card",
  name: "Medical Log Card",
  description: "Medication and temperature logging for a Medical Log child profile",
  preview: false,
  documentationURL: "https://github.com/johnjameshickey/ha-medical-log"
});
