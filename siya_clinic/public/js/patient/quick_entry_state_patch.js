/* siya_clinic/public/js/patient/quick_entry_state_patch.js
   Patch Healthcare Patient Quick Entry:
   - Default Country from the site's Global Defaults
   - Use the SR State link for India
   - Use Healthcare's free-text state field for every other country
*/

(function patchPatientQE() {
  const normalize_country = value => String(value || "").trim().toLowerCase();
  const is_india = value => normalize_country(value) === "india";
  const get_default_country = () =>
    frappe.sys_defaults?.country || frappe.defaults?.get_default?.("country") || "";

  const tryPatch = () => {
    const QE = frappe.ui.form && frappe.ui.form.PatientQuickEntryForm;
    if (!QE || !QE.prototype) return setTimeout(tryPatch, 60);
    if (QE.__sr_state_patched__) return;
    QE.__sr_state_patched__ = true;

    // Add the India state master alongside Healthcare's generic state field.
    const orig_get = QE.prototype.get_standard_fields;
    QE.prototype.get_standard_fields = function () {
      const fields = orig_get.call(this) || [];
      const idx = fields.findIndex(f => f.fieldname === "state");

      if (idx > -1) {
        const india_mode = is_india(this.doc?.country || get_default_country());

        fields[idx].label = __("State/Province");
        fields[idx].hidden = india_mode ? 1 : 0;
        fields[idx].reqd = 0;

        fields.splice(idx, 0, {
          label: __("State/Province"),
          fieldname: "sr_state_link",
          fieldtype: "Link",
          options: "SR State",
          hidden: india_mode ? 0 : 1,
          reqd: india_mode ? 1 : 0
        });
      }

      return fields;
    };

    // Map the active state control to Healthcare's backend state value
    // before Quick Entry sends the document to the server.
    const orig_update_doc = QE.prototype.update_doc;
    QE.prototype.update_doc = function () {
      const doc = orig_update_doc.call(this);
      const country = this.dialog?.get_value("country");

      doc.state = is_india(country)
        ? this.dialog?.get_value("sr_state_link") || ""
        : this.dialog?.get_value("state") || "";

      return doc;
    };

    // Configure country-aware behavior after the dialog controls exist.
    const orig_render = QE.prototype.render_dialog;
    QE.prototype.render_dialog = function () {
      if (this.doc && !this.doc.country) {
        this.doc.country = get_default_country();
      }

      orig_render.call(this);

      const d = this.dialog;
      const f = d.fields_dict || {};
      if (!f.country || !f.state || !f.sr_state_link) return;

      f.sr_state_link.get_query = () => ({
        filters: { sr_country: "India" }
      });

      const set_legacy_state = () =>
        d.set_value("state", d.get_value("sr_state_link") || "");

      const orig_state_change = f.sr_state_link.df.change;
      f.sr_state_link.df.change = function (...args) {
        const result = orig_state_change && orig_state_change.apply(this, args);
        return Promise.resolve(result).then(set_legacy_state);
      };

      const refresh_state_mode = clear_state => {
        const india_mode = is_india(d.get_value("country"));

        f.sr_state_link.df.reqd = india_mode ? 1 : 0;
        f.state.df.reqd = 0;
        f.sr_state_link.toggle(india_mode);
        f.state.toggle(!india_mode);
        f.sr_state_link._filters = null;

        const clear_values = clear_state
          ? Promise.all([
              d.set_value("sr_state_link", ""),
              d.set_value("state", "")
            ])
          : Promise.resolve();

        return clear_values.then(() => {
          const state = d.get_value("state");
          if (india_mode && state && !d.get_value("sr_state_link")) {
            return d.set_value("sr_state_link", state);
          }
        });
      };

      let previous_country = normalize_country(d.get_value("country"));
      const orig_country_onchange = f.country.df.onchange;
      f.country.df.onchange = function (...args) {
        const result = orig_country_onchange && orig_country_onchange.apply(this, args);
        const current_country = normalize_country(d.get_value("country"));
        const country_changed = Boolean(
          previous_country && previous_country !== current_country
        );
        previous_country = current_country;

        return Promise.resolve(result).then(() => refresh_state_mode(country_changed));
      };

      refresh_state_mode(false);
    };
  };

  tryPatch();
})();
