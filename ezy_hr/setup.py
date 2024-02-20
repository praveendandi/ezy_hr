import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from ezy_hr.custom_fields import CUSTOM_FIELDS

# Hooks

def setup_fixtures():
    create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
