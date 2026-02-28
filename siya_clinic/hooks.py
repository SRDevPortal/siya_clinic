app_name = "siya_clinic"
app_title = "Siya Clinic"
app_publisher = "SIYA"
app_description = "Clinic customizations packaged as clean installable/uninstallable app."
app_email = "webdevelopersriaas@gmail.com"
app_license = "mit"

# Installation
before_install = "siya_clinic.install.before_install"
after_install = "siya_clinic.install.after_install"
after_migrate = "siya_clinic.install.after_migrate"

# Uninstallation
before_uninstall = "siya_clinic.uninstall.before_uninstall"
after_uninstall = "siya_clinic.uninstall.after_uninstall"

app_include_css = [
    "/assets/siya_clinic/css/theme_overrides.css",
    "/assets/siya_clinic/css/app_custom.css",
]
app_include_js = [
    "/assets/siya_clinic/js/patient/quick_entry_state_patch.js",
    # "/assets/siya_clinic/js/item_group_template.js",
    "/assets/siya_clinic/js/item_group_template/item_defaults.js",
]

web_include_css = "/assets/siya_clinic/css/theme_overrides.css"

# list_js = {
#     "Sales Invoice": "public/js/sales_invoice_list.js",
# }

doctype_list_js = {
    "CRM Lead": "public/js/crm_lead/list/assignment_actions.js",
}

permission_query_conditions = {
    "CRM Lead": "siya_clinic.api.crm_lead.access.crm_lead_pqc",
}

has_permission = {
    "CRM Lead": "siya_clinic.api.crm_lead.access.crm_lead_has_permission",
}

doc_events = {
    "Patient": {
        "autoname": [
            "siya_clinic.api.patient.naming.set_patient_series",
        ],
        "before_insert": [
            "siya_clinic.api.patient.patient_id.set_patient_id",
            "siya_clinic.api.patient.creator.set_patient_creator",
            "siya_clinic.api.patient.user_control.disable_invite_user",
            "siya_clinic.api.patient.followup_marker.set_followup_id",
            "siya_clinic.api.patient.followup_marker.set_followup_day",
            "siya_clinic.api.patient.followup_marker.set_default_followup_status",
            # Normalize early
            "siya_clinic.api.patient.integrity.normalize_patient_contact_numbers",
            "siya_clinic.api.patient.integrity.normalize_patient_email",
        ],
        "validate": [
            # Normalize again (safe & idempotent)
            "siya_clinic.api.patient.integrity.normalize_patient_contact_numbers",
            "siya_clinic.api.patient.integrity.normalize_patient_email",
            # Global duplicate engine (single source of truth)
            "siya_clinic.api.patient.integrity.validate_patient_global_duplicates",
        ],
        "after_save": [
            # Link Patient → Customer
            "siya_clinic.api.address.link_to_patient.link_to_customer",
        ],
    },
    "Customer": {
        # "autoname": [
        #     "siya_clinic.api.customer.naming.set_customer_series",
        # ],
        "before_insert": [
            "siya_clinic.api.customer.customer_id.set_customer_id",
            "siya_clinic.api.customer.creator.set_customer_creator",
            # Normalize early
            "siya_clinic.api.customer.integrity.normalize_customer_contact_numbers",
            "siya_clinic.api.customer.integrity.normalize_customer_email",
        ],
        "validate": [
            # Normalize again (safe)
            "siya_clinic.api.customer.integrity.normalize_customer_contact_numbers",
            "siya_clinic.api.customer.integrity.normalize_customer_email",
            # Global duplicate engine
            "siya_clinic.api.customer.integrity.validate_customer_global_duplicates",
        ],
    },
    "Contact": {
        "before_save": [
            # Normalize phone fields
            "siya_clinic.api.contact.integrity.normalize_contact_phone_fields",
            # Global duplicate engine
            "siya_clinic.api.contact.integrity.validate_contact_global_duplicates",
        ],
    },
    "Address": {
        "validate": [
            "siya_clinic.api.address.customer_links.validate_state",
            "siya_clinic.api.address.customer_links.ensure_address_has_customer_link",
        ],
    },
    "Healthcare Practitioner": {
        "before_validate": [
            "siya_clinic.api.practitioner.name.compose_full_name",
        ],
    },
    # "Patient Appointment": {
    #     "before_insert": [
    #         "siya_clinic.api.patient_appointment.set_created_by_agent",
    #     ],
    #     # "on_update": [
    #     #     "siya_clinic.api.patient_appointment.create_payment_entries_from_child_table",
    #     #     "siya_clinic.api.patient_appointment.on_update_create_payments",
    #     # ],
    # },
    "Patient Encounter": {
        "validate": [
            "siya_clinic.api.encounter.handlers.validate_agent_status_change",
            "siya_clinic.api.encounter.handlers.validate_agent_followup_online_source",
            # "siya_clinic.api.encounter.handlers.validate_encounter_workflow",
        ],
        "before_insert": [
            "siya_clinic.api.encounter.handlers.set_created_by_agent",
            "siya_clinic.api.encounter.handlers.set_default_encounter_status",
        ],
        "before_save": [
            "siya_clinic.api.encounter.handlers.enforce_agent_encounter_place",
            "siya_clinic.api.encounter.handlers.before_save_patient_encounter",
            "siya_clinic.api.encounter.handlers.clear_advance_dependent_fields",
        ],
        "before_submit": [
            "siya_clinic.api.encounter.handlers.validate_required_before_submit",
        ],
        "on_submit": [
            "siya_clinic.api.encounter.handlers.create_billing_on_submit",
        ],
    },
    "Item": {
        "validate": "siya_clinic.api.item.package_details.calculate_pkg_weights",
    },
    "Sales Invoice": {
        "before_insert": [
            "siya_clinic.api.sales_invoice.handlers.set_created_by_agent",
        ],
        "validate": [
            "siya_clinic.api.sales_invoice.guard.validate_sales_invoice_warehouse",
        ],
        "before_submit": [
            "siya_clinic.api.sales_invoice.guard.validate_sales_invoice_warehouse",
        ],
        "on_submit": [
            "siya_clinic.api.encounter.handlers.link_pending_payment_entries",
        ],
        "before_cancel": [
            "siya_clinic.api.sales_invoice.guard.validate_sales_invoice_warehouse",
        ],
        "before_amend": [
            "siya_clinic.api.sales_invoice.guard.validate_sales_invoice_warehouse",
        ],
    },
    "Payment Entry": {
        "before_insert": [
            "siya_clinic.api.payment_entry.creator.set_created_by_agent",
        ],
    },
    "CRM Lead": {
        "validate": [
            "siya_clinic.api.crm_lead.guards.guard_restricted_fields",
        ],
        "before_save": [
            "siya_clinic.api.crm_lead.controller.normalize_phoneish_fields",
        ],
        "after_save": [
            "siya_clinic.api.crm_lead.access.restore_lead_owner_after_unassign",
        ],
        "after_insert": [
            "siya_clinic.api.crm_lead.lifecycle.after_insert",
        ],
        "on_update": [
            "siya_clinic.api.crm_lead.lifecycle.on_update",
        ],
    },
    "ToDo": {
        "on_trash": [
            "siya_clinic.api.crm_lead.assign_guard.todo_on_trash",
        ],
    },
    # "File": {
    #     "after_insert": [
    #         "siya_clinic.api.s3_bucket.file_hooks.handle_file_after_insert",
    #     ],
    #     "on_trash": [
    #         "siya_clinic.api.s3_bucket.file_hooks.handle_file_on_trash",
    #     ],
    # }
}

doctype_js = {
    "Patient": [
        "public/js/patient/followup_marker.js",
        "public/js/patient/patient_invoices.js",
        "public/js/patient/patient_payments.js",
        "public/js/patient/patient_regional.js",
        "public/js/patient/pex_launcher.js",
        "public/js/common/clinical_history.js",
    ],
    "Healthcare Practitioner": [
        "public/js/practitioner/form.js",
    ],
    "Patient Encounter": [
        "public/js/encounter/patient_encounter.js",  # Linked to Patient Encounter JS
        "public/js/encounter/practitioner_filters.js",  # Linked to Practitioner Filters JS
        "public/js/encounter/medication_filters.js",  # Linked to Medication Filters JS
        "public/js/encounter/medication_template.js", # Load Medication From Template JS
        "public/js/encounter/medication_manual.js", # # Load Medication From Manual JS
        "public/js/encounter/draft_invoice.js",     # Linked to Draft Invoice JS
        "public/js/encounter/order_item.js",        # Linked to SR Order Item JS
        # "public/js/encounter_block_autosave_for_proof.js",
        # "public/js/encounter_attachments.js",
        "public/js/common/clinical_history.js",
    ],
    "CRM Lead": [
        "public/js/crm_lead/form/master_filters.js",
        "public/js/crm_lead/form/disposition_filter.js",
        "public/js/crm_lead/form/lock_fields.js",
        "public/js/crm_lead/form/pex_launcher.js",
    ],
    "Item": [
        "public/js/item/package_weight.js",
    ],
    "Sales Invoice": [
        # "public/js/sales_invoice.js",
        "public/js/sales_invoice/template_loader.js",
        "public/js/sales_invoice/actions.js",
        "public/js/sales_invoice/barcode.js",
        "public/js/sales_invoice/shipkia.js",
    ],
    "Payment Entry": [
        "public/js/payment_entry/outstanding_dialog.js",
        "public/js/payment_entry/actions.js",
        # "public/js/_payment_entry_extend.js",
    ],
    "Stock Entry": [
        "public/js/stock_entry/barcode.js",
    ],
}

override_whitelisted_methods = {
    # Allow Shopify Full Invoice API to create Sales Invoices in our system
    "siya_clinic.api.shopify.create_shopify_order": "siya_clinic.api.shopify.create_shopify_order",

    # Override default assign_to behavior to use our custom assignment logic
    "frappe.desk.form.assign_to.add": "siya_clinic.api.crm_lead.assign_guard.add",
    "frappe.desk.form.assign_to.remove": "siya_clinic.api.crm_lead.assign_guard.remove",
    "frappe.desk.form.assign_to.clear": "siya_clinic.api.crm_lead.assign_guard.clear",
}

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Client Script", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Server Script", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Workspace", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Print Format", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Report", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Dashboard Chart", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Notification", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Web Template", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Form Tour", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Form Tour Step", "filters": [["module", "=", "Siya Clinic"]]},
    {"dt": "Custom DocPerm", "filters": [["module", "=", "Siya Clinic"]]},
]


# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "siya_clinic",
# 		"logo": "/assets/siya_clinic/logo.png",
# 		"title": "Siya Clinic",
# 		"route": "/siya_clinic",
# 		"has_permission": "siya_clinic.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/siya_clinic/css/siya_clinic.css"
# app_include_js = "/assets/siya_clinic/js/siya_clinic.js"

# include js, css files in header of web template
# web_include_css = "/assets/siya_clinic/css/siya_clinic.css"
# web_include_js = "/assets/siya_clinic/js/siya_clinic.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "siya_clinic/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "siya_clinic/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "siya_clinic.utils.jinja_methods",
# 	"filters": "siya_clinic.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "siya_clinic.install.before_install"
# after_install = "siya_clinic.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "siya_clinic.uninstall.before_uninstall"
# after_uninstall = "siya_clinic.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "siya_clinic.utils.before_app_install"
# after_app_install = "siya_clinic.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "siya_clinic.utils.before_app_uninstall"
# after_app_uninstall = "siya_clinic.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "siya_clinic.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"siya_clinic.tasks.all"
# 	],
# 	"daily": [
# 		"siya_clinic.tasks.daily"
# 	],
# 	"hourly": [
# 		"siya_clinic.tasks.hourly"
# 	],
# 	"weekly": [
# 		"siya_clinic.tasks.weekly"
# 	],
# 	"monthly": [
# 		"siya_clinic.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "siya_clinic.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "siya_clinic.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "siya_clinic.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["siya_clinic.utils.before_request"]
# after_request = ["siya_clinic.utils.after_request"]

# Job Events
# ----------
# before_job = ["siya_clinic.utils.before_job"]
# after_job = ["siya_clinic.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"siya_clinic.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

