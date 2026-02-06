app_name = "siya_clinic"
app_title = "Siya Clinic"
app_publisher = "SIYA"
app_description = "Clinic customizations packaged as clean installable/uninstallable app."
app_email = "webdevelopersriaas@gmail.com"
app_license = "mit"

# Installation
# before_install = "siya_clinic.install.before_install"
after_install = "siya_clinic.install.after_install"
after_migrate = "siya_clinic.install.after_migrate"

# Uninstallation
# before_uninstall = "siya_clinic.uninstall.before_uninstall"
# after_uninstall = "siya_clinic.uninstall.after_uninstall"

app_include_css = [
    "/assets/siya_clinic/css/theme_overrides.css",
]

web_include_css = "/assets/siya_clinic/css/theme_overrides.css"

doc_events = {}

doctype_js = {
    "Item Group Template": "public/js/item_group_template.js",
    "Sales Invoice": "public/js/sales_invoice.js",
}


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

