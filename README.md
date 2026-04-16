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