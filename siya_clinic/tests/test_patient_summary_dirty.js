const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

for (const [script, field] of [["patient_invoices.js", "sr_sales_invoice_list"], ["patient_payments.js", "sr_payment_entry_list"]]) {
    const requests = [];
    let refresh, dirty = false, counter = 0;
    const frm = {
        doc: {doctype: "Patient", name: "PAT-A"},
        fields_dict: {[field]: {df: {options: "Summary Row"}}},
        is_new: () => false,
        clear_table(key) {this.doc[key] = [];},
        refresh_field() {},
        dirty() {dirty = true;},
        add_child() {dirty = true; throw Error("Display refresh used dirtying add_child");}
    };
    const frappe = {
        provide() {}, model: {},
        ui: {form: {on(dt, handlers) {refresh = handlers.refresh;}}},
        call(options) {requests.push(options);}
    };
    const context = vm.createContext({frappe, cur_frm: frm, $: {extend: Object.assign}});
    // Exercise the installed Frappe row constructor, not a replacement implementation.
    vm.runInContext(fs.readFileSync(path.resolve(__dirname, "../../../frappe/frappe/public/js/frappe/model/create_new.js"), "utf8"), context);
    Object.assign(frappe.model, {
        get_new_name: () => `summary-${++counter}`,
        set_default_values() {}, add_to_locals() {}
    });
    frappe.session = {user: "test"};
    vm.runInContext(fs.readFileSync(path.resolve(__dirname, "../public/js/patient", script), "utf8"), context);
    refresh(frm);
    refresh(frm);
    requests[0].callback({message: [{name: "STALE"}]});
    assert.equal((frm.doc[field] || []).length, 0);
    requests[1].callback({message: [{name: "CURRENT"}]});
    assert.equal(frm.doc[field].length, 1);
    assert.equal(dirty, false, `${script}: opening a clean Patient must remain saved`);
    refresh(frm);
    frm.dirty(); // A genuine edit made while the request is pending must survive.
    requests[2].callback({message: [{name: "LATEST"}]});
    assert.equal(dirty, true, `${script}: must preserve genuine pending edits`);
    frm.doc.name = "PAT-B";
    requests[2].callback({message: [{name: "WRONG-PATIENT"}]});
    assert.equal(frm.doc[field].length, 1);
}
console.log("Patient summaries: clean opening, real edits and stale responses verified against Frappe model.");
