// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt



frappe.query_reports["Employee Leave Balance Report"] = {
    "filters": [
        {
            "fieldname": "unit",
            "label": __("Unit"),
            "fieldtype": "Link",
            "options": "Company",  
            "default": frappe.defaults.get_default("company"), 
            "reqd": 1  
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "default": ""
        },
        {
            "fieldname": "leave_type",
            "label": __("Leave Type"),
            "fieldtype": "Link",
            "options": "Leave Type",
            "default": ""
        }
    ]
};

