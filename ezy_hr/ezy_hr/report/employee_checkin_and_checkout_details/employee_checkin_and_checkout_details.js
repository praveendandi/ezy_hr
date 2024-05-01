// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Checkin And Checkout Details"] = {
    filters: [
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
            options: "Employee"
        },
        {
            fieldname: "company",
            label: __("Unit"),
            fieldtype: "Link",
            options: "Company"
        },
    ],
    
};
// frappe.ui.form.on('Employee Checkin', {
//     onload: function(frm) {
//         if (frm.doc.__islocal) { // Check if the form is new
//             frm.set_value('log_type', frm.doc.log_type || 'IN'); // Set default value for log_type
//             frm.set_value('device_id', frm.doc.device_id || ''); // Set default value for device_id

//             frm.toggle_enable('log_type', 0); // Set log_type as read-only
//             frm.toggle_enable('device_id', 0); // Set device_id as read-only
//             frm.toggle_enable('employee', 0); // Set employee as read-only
//         }
//     }
// });
// frappe.ui.form.on('Employee Checkin', {
//     onload: function(frm) {
//         frm.toggle_display('device_id', true); // Set device_id as visible
//         frm.toggle_enable('log_type', 0); // Set log_type as read-only
//         frm.toggle_enable('device_id', 0); // Set device_id as read-only
//         frm.toggle_enable('employee', 0); // Set employee as read-only
//     }
// });


frappe.ui.form.on('Employee Checkin', {
    refresh: function(frm) {
        frm.toggle_display('device_id', true); // Set device_id as visible
    }
});
