//  Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt


frappe.query_reports["Attendance Correction Report"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
        },
        {
            fieldname: "employee",
            label: __("Employee"),
            fieldtype: "Link",
            options: "Employee",
            get_query: function() {
                return {
                    filters: {
                        "company": frappe.query_report.get_filter_value("company")
                    }
                };
            },
            change: function() {
                var employee_id = frappe.query_report.get_filter_value("employee");
                if (employee_id) {
                    frappe.call({
                        method: "frappe.client.get_value",
                        args: {
                            doctype: "Employee",
                            filters: { name: employee_id },
                            fieldname: ["employee_name"]
                        },
                        callback: function(r) {
                            if (r.message) {
                                frappe.query_report.set_filter_value("employee_name", r.message.employee_name);
                            }
                        }
                    });
                } else {
                    frappe.query_report.set_filter_value("employee_name", "");
                }
            }
        },
        {
            fieldname: "employee_name",
            label: __("Employee Name"),
            fieldtype: "Data",
            read_only: 1
        },
        {
            fieldname: "department",
            label: __("Department"),
            fieldtype: "Link",
            options: "Department",
            get_query: function() {
                return {
                    filters: {
                        "company": frappe.query_report.get_filter_value("company")
                    }
                };
            }
        },
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_default("company")
        }
    ]
};

if (frappe.user.has_role("Report Manager")) {
    frappe.query_reports["Attendance Correction Report"].filters.push({
        fieldname: "reports",
        label: __("Reports"),
        fieldtype: "Select",
        options: "All\nMy Team",
        default:"All"
    });

}

function fetch_employee_name(employee, callback) {
    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Employee',
            fieldname: 'employee_name',
            filters: { name: employee }
        },
        callback: function(response) {
            if (response && response.message) {
                callback(response.message.employee_name);
            } else {
                frappe.msgprint('Employee not found.');
            }
        }
    });
}

function openPopup(employee, date) {
    fetch_employee_name(employee, function(employee_name) {
        var dialog = new frappe.ui.Dialog({
            title: 'Add Attendance',
            fields: [
                {
                    fieldname: 'employee',
                    label: 'Employee',
                    fieldtype: 'Link',
                    options: 'Employee',
                    default: employee,
                    change: function() {
                        var employee_id = dialog.get_value("employee");
                        fetch_employee_name(employee_id, function(employee_name) {
                            dialog.set_value("employee_name", employee_name);
                        });
                    }
                },
                {
                    fieldname: 'employee_name',
                    label: 'Employee Name',
                    fieldtype: 'Data',
                    read_only: 1,
                    default: employee_name
                },
                {
                    fieldname: 'time',
                    label: 'Time',
                    fieldtype: 'Datetime',
                    default: date + " 18:00:00"
                },
                {
                    fieldname: 'log_type',
                    label: 'Log Type',
                    fieldtype: 'Select',
                    options: ["IN", "OUT"],
                    default: ""
                },
                {
                    fieldname: 'custom_correction',
                    label: 'Correction',
                    fieldtype: 'Data',
                    read_only: 1,
                    default: "Manual"
                },
            ],
            primary_action_label: 'Submit',
            primary_action: function() {
                var values = dialog.get_values();
                if (values) {
                    frappe.call({
                        method: 'frappe.client.insert',
                        args: {
                            doc: {
                                doctype: 'Employee Checkin',
                                employee: values.employee,
                                employee_name: values.employee_name,
                                time: values.time,
                                log_type: values.log_type,
                                custom_correction: values.custom_correction
                            }
                        },
                        callback: function() {
                            frappe.msgprint('Checkout added successfully.');
                            dialog.hide();
                            frappe.query_report.refresh();
                        }
                    });
                }
            }
        });
        dialog.show();
    });
}