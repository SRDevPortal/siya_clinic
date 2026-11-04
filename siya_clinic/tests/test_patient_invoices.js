const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
let refresh;
const requests = [];
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../public/js/patient/patient_invoices.js'), 'utf8'), {
    frappe: {ui: {form: {on(dt, events) {refresh = events.refresh;}}}, call(options) {requests.push(options);}}
});
const rows = [];
const frm = {doc: {name: 'PAT-A'}, is_new: () => false,
    clear_table() {rows.length = 0;}, add_child() {const row = {}; rows.push(row); return row;}, refresh_field() {}};
refresh({...frm, is_new: () => true});
assert.equal(requests.length, 0);
refresh(frm);
assert.equal(requests[0].method, 'siya_clinic.api.patient_invoices.get_patient_invoices');
assert.equal(requests[0].args.patient, 'PAT-A');
refresh(frm);
requests[0].callback({message: [{name: 'OLD'}]});
assert.equal(rows.length, 0, 'Ignore stale response after a newer refresh');
requests[1].callback({message: [{name: 'INV-A', posting_date: '2026-11-04', grand_total: 100, outstanding_amount: 25}]});
assert.equal(rows[0].sr_invoice_no, 'INV-A');
assert.equal(rows[0].sr_grand_total, 100);
assert.equal(rows[0].sr_outstanding, 25);
frm.doc.name = 'PAT-B';
requests[1].callback({message: [{name: 'WRONG-PATIENT'}]});
assert.equal(rows[0].sr_invoice_no, 'INV-A', 'Old patient response cannot modify the new form');
console.log('Patient invoice UI passed: existing fields, no new-document request and stale-response isolation.');
