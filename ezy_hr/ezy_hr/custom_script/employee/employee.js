frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        frm.add_custom_button(__('Update Fields'), function() {
            frappe.route_options = {
                "employee_id":frm.doc.name
            };
            frappe.set_route('Form', 'Employee Fields Update','new_employee_fields_update');
        }).addClass('btn-primary');
    },
    custom_leave_policy: function(frm) {       
        frappe.call({
            method: "ezy_hr.ezy_hr.custom_script.employee.employee.assign_leave_policy",
            args: { doc: cur_frm.doc },
            callback: function(r) {
                if (r.message.success) {
                    frappe.msgprint(r.message.reason);
                } else {
                    frappe.msgprint(r.message.reason);
                }
            }
        });
    },
    reports_to: function(frm) {
        frappe.db.get_value("Employee", {"name": frm.doc.reports_to}, "user_id")
            .then(r => {
                let report_user_id = r.message.user_id;
                console.log(report_user_id);
                frm.set_value('leave_approver', report_user_id);
                frm.set_value('shift_request_approver', report_user_id);
            });
    }

});
