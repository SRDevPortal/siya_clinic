# SRIAAS Clinic

SRIAAS Clinic is a plug-and-play Frappe app that provides clinic-specific workflows, automation, and healthcare customizations directly inside ERPNext.

It enables ERPNext users to manage **patients, encounters, CRM leads, billing workflows, and clinic operations** efficiently while maintaining seamless integration with healthcare and sales processes.

---

## Features

- Custom workflow enhancements for **Patient management**
- Automation for **Patient Encounters and clinic operations**
- Enhanced **CRM Lead assignment and access control**
- Custom **Sales Invoice workflows for clinic billing**
- Integration with **external order channels (e.g., Shopify)**
- Automated **patient follow-ups and encounter tracking**
- Custom scripts for **healthcare practitioners and appointments**
- Extended UI actions and automation across ERPNext documents

---

## Requirements

- **Frappe Framework** v15+
- **ERPNext** v15+
- **Python** 3.10+
- **Bench CLI**

---

## Installation

Install the app using the **Bench CLI**.

```bash
cd $PATH_TO_YOUR_BENCH

bench get-app https://github.com/YOUR_GITHUB_USERNAME/siya_clinic.git

bench --site <your-site-name> install-app siya_clinic

bench --site <your-site-name> migrate

bench build

bench restart
```

---

## Contributing

This app uses `pre-commit` for code formatting and linting. Please install pre-commit and enable it for this repository:

```bash
cd apps/siya_clinic
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

---

## License

MIT

## Encounter print formats per site

Open **Clinic Settings** from Desk search (System Manager) and select **Domestic**
or **International**. Saving immediately selects the matching Patient Encounter
print format. Settings are stored separately on each site and are not fixtures.

- `Patient Encounter Domestic`: the previous app encounter layout, unchanged.
- `Patient Encounter International`: the approved A4 layout, with 12 mm side
  margins and 10 mm top/bottom margins.
- `Patient Encounter New`: a compatibility copy of the selected layout, so old
  print links and integrations continue to use the correct regional template.

Deploy this app version and run `bench --site <site> migrate` on each site.
Migration preserves an existing Clinic Settings choice. On the first upgrade,
existing named defaults are respected; the exact approved international template
in Patient Encounter New is recognized before templates are updated. Otherwise,
the initial selection is Domestic. Verify International in Clinic Settings on
international sites after deployment, especially if their template was edited.

The templates are app-managed: edit their files under `siya_clinic/print_formats`
for durable layout changes. Migrations refresh them from source. Do not export
Clinic Settings or the encounter default Property Setter into shared fixtures.
Python integrations can resolve the site's selection with
`siya_clinic.setup.print_formats.get_encounter_print_format()`.

Validation: `./env/bin/python -m unittest siya_clinic.tests.test_print_regions`
from the bench directory.
