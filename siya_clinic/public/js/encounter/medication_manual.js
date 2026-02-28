// siya_clinic/public/js/encounter/medication_manual.js
// Patient Encounter — Auto-fill drug_code & print name on manual row edits
// Supports Ayurvedic, Homeopathy, Allopathy child tables

// =====================================================
// 🔹 CONFIG
// =====================================================

// Add direct Item link fields from Medication doctype if present
const MED_DIRECT_ITEM_FIELDS = ["linked_item", "default_item"];

// =====================================================
// 🔹 HELPERS
// =====================================================

function parse_days(s = "") {
  const p = (s || "").toLowerCase().trim();
  const n = parseInt(p) || 0;
  if (p.includes("month")) return n * 30;
  if (p.includes("week"))  return n * 7;
  if (p.includes("day"))   return n;
  return n;
}

// "1-0-1" → 2 | BD/TDS/QID | alternate day → 0.5
function parse_per_day(s = "") {
  const d = (s || "").toLowerCase().trim();
  const nums = d.match(/\d+/g);

  if (nums && (/[-\s/]/.test(d) || nums.length > 1)) {
    return nums.map(n => parseInt(n) || 0).reduce((a, b) => a + b, 0);
  }
  if (/\b(qid|4\s*times|4x)\b/.test(d)) return 4;
  if (/\b(tds|3\s*times|3x)\b/.test(d)) return 3;
  if (/\b(bd|2\s*times|2x)\b/.test(d)) return 2;
  if (/\b(od|1\s*time|1x|hs|bed\s*time)\b/.test(d)) return 1;
  if (/\balternate\s*day\b/.test(d)) return 0.5;
  return 0;
}

function short_form(f = "") {
  const x = (f || "").toLowerCase();
  if (x.includes("tablet"))  return "Tab";
  if (x.includes("capsule")) return "Cap";
  return "";
}

// =====================================================
// 🔹 FETCH MEDICATION DOC
// =====================================================

async function get_medication_doc(name) {
  try {
    const r = await frappe.call({
      method: "frappe.client.get",
      args: { doctype: "Medication", name },
    });
    return r.message || null;
  } catch (e) {
    console.warn("Medication load failed:", name);
    return null;
  }
}

// Find linked Item from Medication doc
function find_item_from_med_doc(med_doc) {
  if (!med_doc) return "";

  // direct fields
  for (const f of MED_DIRECT_ITEM_FIELDS) {
    if (med_doc[f]) return med_doc[f];
  }

  // search children
  for (const v of Object.values(med_doc)) {
    if (Array.isArray(v)) {
      for (const r of v) {
        if (r?.item || r?.item_code) return r.item || r.item_code;
      }
    }
  }
  return "";
}

// =====================================================
// 🔹 PRINT FIELD DETECTION
// =====================================================

function resolve_print_field(cdt) {
  if (frappe.meta.has_field(cdt, "sr_medication_name_print"))
    return "sr_medication_name_print";
  return "";
}

// =====================================================
// 🔹 CORE LOGIC
// =====================================================

async function set_drug_code_from_medication(cdt, cdn) {
  const row = locals[cdt][cdn];
  if (!row?.medication) return;

  const med_doc  = await get_medication_doc(row.medication);
  const itemname = find_item_from_med_doc(med_doc);

  if (itemname && frappe.meta.has_field(cdt, "drug_code")) {
    await frappe.model.set_value(cdt, cdn, "drug_code", itemname);
  }
}

async function update_print_name(cdt, cdn) {
  const row = locals[cdt][cdn];
  if (!row) return;

  const pf = resolve_print_field(cdt);
  if (!pf) return;

  const name      = row.medication || row.drug || "";
  const per       = parse_per_day(row.dosage || "");
  const days      = parse_days(row.period || "");
  const qty       = Math.ceil(per * days);
  const sf        = short_form(row.dosage_form || "");
  const countable = ["tablet", "capsule"].includes(
    (row.dosage_form || "").toLowerCase()
  );

  const pretty = (name && countable && sf && per > 0 && days > 0)
    ? `${name} (${qty} ${sf})`
    : name;

  await frappe.model.set_value(cdt, cdn, pf, pretty);
}

async function sync_row(cdt, cdn) {
  const row = locals[cdt][cdn];
  if (!row) return;

  // Auto drug_code
  if (row.medication && !row.drug_code) {
    await set_drug_code_from_medication(cdt, cdn);
  }

  // per day calculation
  const per = parse_per_day(row.dosage || "");
  if (frappe.meta.has_field(cdt, "no_of_tablets_per_day_for_calculation")) {
    await frappe.model.set_value(
      cdt,
      cdn,
      "no_of_tablets_per_day_for_calculation",
      per
    );
  }

  // quantity calculation
  const days      = parse_days(row.period || "");
  const countable = ["tablet", "capsule"].includes(
    (row.dosage_form || "").toLowerCase()
  );

  if (
    frappe.meta.has_field(cdt, "quantity") &&
    per > 0 &&
    days > 0 &&
    countable
  ) {
    await frappe.model.set_value(cdt, cdn, "quantity", Math.ceil(per * days));
  }

  // update pretty name
  await update_print_name(cdt, cdn);
}

// =====================================================
// 🔹 CHILD TABLE BINDINGS
// =====================================================

// Bind to main child doctype (most setups use this)
bind_child("Drug Prescription");

// If you use separate doctypes, uncomment and adjust:
// bind_child("Homeopathy Drug Prescription");
// bind_child("Allopathy Drug Prescription");

function bind_child(child_doctype) {
  frappe.ui.form.on(child_doctype, {
    async medication(frm, cdt, cdn)   { await sync_row(cdt, cdn); },
    async dosage(frm, cdt, cdn)       { await sync_row(cdt, cdn); },
    async period(frm, cdt, cdn)       { await sync_row(cdt, cdn); },
    async dosage_form(frm, cdt, cdn)  { await sync_row(cdt, cdn); },
    async form_render(frm, cdt, cdn)  { await sync_row(cdt, cdn); },
  });
}

// =====================================================
// 🔹 SAFETY NET ON SAVE
// =====================================================

frappe.ui.form.on("Patient Encounter", {
  async before_save(frm) {
    const tables = [
      "drug_prescription",
      "sr_homeopathy_drug_prescription",
      "sr_allopathy_drug_prescription",
    ];

    for (const t of tables) {
      for (const r of (frm.doc[t] || [])) {
        await sync_row(r.doctype, r.name);
      }
    }
  },
});