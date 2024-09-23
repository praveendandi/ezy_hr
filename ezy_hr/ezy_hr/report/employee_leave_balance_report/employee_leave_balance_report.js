// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt



frappe.query_reports["Employee Leave Balance Report"] = {
    "filters": [
        {
            fieldname: "company",
            label: __("Unit"),
            fieldtype: "Link",
            options: "Company",  
            default: frappe.defaults.get_default("company"), 
            "reqd": 1  
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
        },
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee",
            default: ""
        },
        {
            fieldname: "leave_type",
            label: __("Leave Type"),
            fieldtype: "Link",
            options: "Leave Type",
            default: ""
        }
    ]
};
