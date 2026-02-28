/* siya_clinic/public/js/patient/quick_entry_state_patch.js
   Patch Healthcare Patient Quick Entry:
   - Replace legacy `state` text with `SR State` link
   - Keep legacy field for backend compatibility
   - Require state when Country = India
*/

(function patchPatientQE() {
  const tryPatch = () => {
    const QE = frappe.ui.form && frappe.ui.form.PatientQuickEntryForm;
    if (!QE || !QE.prototype) return setTimeout(tryPatch, 60);
    if (QE.__sr_state_patched__) return;
    QE.__sr_state_patched__ = true;

    // 🔹 Replace state field
    const orig_get = QE.prototype.get_standard_fields;
    QE.prototype.get_standard_fields = function () {
      const fields = orig_get.call(this) || [];
      const idx = fields.findIndex(f => f.fieldname === "state");

      if (idx > -1) {
        // Visible SR State Link
        fields.splice(idx, 1, {
          label: __("State/Province"),
          fieldname: "sr_state_link",
          fieldtype: "Link",
          options: "SR State"
        });

        // Hidden legacy state
        fields.splice(idx + 1, 0, {
          label: __("State Legacy"),
          fieldname: "state",
          fieldtype: "Data",
          hidden: 1
        });
      }

      return fields;
    };

    // 🔹 Behavior after dialog render
    const orig_render = QE.prototype.render_dialog;
    QE.prototype.render_dialog = function () {
      orig_render.call(this);

      const d = this.dialog;
      const f = d.fields_dict || {};

      // Mirror SR State → legacy state
      const set_legacy = () => {
        d.set_value("state", d.get_value("sr_state_link") || "");
      };

      if (f.sr_state_link) {

        // Filter by country
        f.sr_state_link.get_query = () => {
          const filters = {};
          const country = d.get_value("country");
          if (country) filters.sr_country = country;
          return { filters };
        };

        // Required if India
        const refresh_reqd = () => {
          const is_india = /india/i.test(String(d.get_value("country") || ""));
          f.sr_state_link.df.reqd = is_india;
          f.sr_state_link.refresh();
        };

        refresh_reqd();

        // When country changes
        if (f.country) {
          const orig_onchange = f.country.df.onchange;
          f.country.df.onchange = () => {
            orig_onchange && orig_onchange();
            refresh_reqd();
            f.sr_state_link._filters = null;
          };
        }

        // Initial sync
        set_legacy();

        // Mirror on change
        const orig_change = f.sr_state_link.df.change;
        f.sr_state_link.df.change = () => {
          orig_change && orig_change();
          set_legacy();
        };
      }

      // Ensure mirror before save
      const $save = d.get_primary_btn && d.get_primary_btn();
      if ($save) {
        $save.off("click._sr_state_guard").on("click._sr_state_guard", set_legacy);
      }
    };
  };

  tryPatch();
})();