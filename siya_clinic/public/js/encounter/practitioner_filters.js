// siya_clinic/public/js/encounter/practitioner_filters.js

console.log("Practitioner Filters JS file loaded");

// Filter each practitioner Link by the practitioner's "Pathy"
const PATHY_FILTERS = {
	// Use your Patient Encounter link fieldnames here
	sr_ayurvedic_practitioner: ["Ayurveda"],
	sr_homeopathy_practitioner: ["Homeopathy"],
	sr_allopathy_practitioner: ["Allopathy"],
};

frappe.ui.form.on("Patient Encounter", {
	setup(frm) {
		// Iterate through each field and apply the filter based on Pathy
		Object.entries(PATHY_FILTERS).forEach(([fieldname, allowed]) => {
			// Skip if field doesn't exist on this site/customization
			if (!frm.fields_dict[fieldname]) return;

			// Apply the filter to the field based on practitioner's Pathy
			frm.set_query(fieldname, () => ({
				filters: {
					sr_pathy: ["in", allowed], // Filter practitioners by Pathy
					status: "Active", // Only show active practitioners
				},
			}));
		});
	},
});
