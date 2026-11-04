const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
async function scenario(policy) {
    const calls = [];
    class QuickEntry {
        constructor() { this.doc = {__islocal: 1, country: 'India'}; }
        get_standard_fields() { return [{fieldname: 'state'}, {fieldname: 'country'}, {fieldname: 'mobile'}]; }
        setup() { this.render_dialog(); return this; }
        render_dialog() {
            const fields = this.get_standard_fields();
            const doc = {...this.doc};
            const fields_dict = {};
            for (const df of fields) {
                if (!df.fieldname) continue;
                fields_dict[df.fieldname] = {df: {...df}, refresh() {}};
                if (df.default !== undefined) doc[df.fieldname] = df.default;
            }
            this.dialog = {fields_dict, doc, get_value: name => doc[name],
                set_value(name, value) {doc[name] = value;},
                set_df_property(name, key, value) {fields_dict[name].df[key] = value;},
                get_primary_btn: () => ({off() {return this;}, on() {return this;}, prop() {}})};
        }
        insert() { return 'native insert'; }
    }
    const frappe = {ui: {form: {PatientQuickEntryForm: QuickEntry, on() {}}},
        sys_defaults: {country: 'India'},
        call: async options => {calls.push(options); return {message: policy};}};
    const context = {frappe, __: s => s, setTimeout() {throw Error('unexpected missing Quick Entry');}};
    for (const file of ['quick_entry_state_patch.js', 'privacy_intake.js']) {
        vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../public/js/patient', file), 'utf8'), context);
    }
    const entry = new QuickEntry();
    await entry.setup();
    const d = entry.dialog;
    assert(calls[0].method.startsWith('siya_clinic.'), 'Intake uses the local clinic endpoint');
    assert.equal(d.fields_dict.sr_state_link.df.options, 'SR State');
    assert.equal(d.fields_dict.sr_state_link.df.reqd, true, 'India state requirement retained');
    d.set_value('sr_state_link', 'STATE-TEST');
    d.fields_dict.sr_state_link.df.change();
    assert.equal(d.get_value('state'), 'STATE-TEST', 'Legacy state mirroring retained');
    if (!policy.enabled) {
        assert.equal(d.fields_dict.mobile.df.hidden, undefined, 'Disabled privacy retains original mobile control');
        assert(!d.fields_dict.__privacy_source_lead);
    } else {
        assert.equal(d.fields_dict.mobile.df.hidden, true);
        assert.equal(d.fields_dict.mobile.df.reqd, 0);
        assert.equal(d.get_value('mask_mobile'), '******0101');
        assert.equal(d.fields_dict.mask_mobile.df.read_only, 1);
        assert.equal(d.get_value('__privacy_source_lead'), policy.source);
    }
}
(async () => {
    await scenario({enabled: false});
    await scenario({enabled: true, source: 'CRM-LEAD-2026-00014', mask_mobile: '******0101', edit_original: false, enter_new_numbers: false});
    console.log('Siya Quick Entry passed: disabled/native flow, State/Country patch and masked source intake.');
})().catch(error => {console.error(error); process.exitCode = 1;});
