frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        frm.add_custom_button(__('Update Info.'), function() {
            frappe.route_options = {
                "employee_id":frm.doc.name
            };
            frappe.set_route('Form', 'Employee Fields Update','new_employee_fields_update');
        }, __("Update Employee"));
        
        frm.add_custom_button(__('Update Salary'), function() {
            frappe.route_options = {
                "employee_id":frm.doc.name
            };
            frappe.set_route('Form', 'Employee Salary Update','new_employee_salary_update');
        }, __("Update Employee"));
        
        frappe.call({
            method: 'ezy_hr.employee_salary.get_user_employee_id',
            args: {
                data: frm.doc
            },
            callback: function (value) {
                if (value.message && value.message.length > 0) {
                    let employee_id = value.message[0].for_value;
                    if (employee_id === frm.doc.name || frappe.user.has_role(["System Manager", "HR Manager", "Salary Slips"])) {

                        frm.set_df_property('custom_gross_amount', 'hidden', 0);
                        frm.set_df_property('custom_earnings', 'hidden', 0);
                        frm.set_df_property('custom_deductions', 'hidden', 0);
                    } else {
                        frm.set_df_property('custom_gross_amount', 'hidden', 1);
                        frm.set_df_property('custom_earnings', 'hidden', 1);
                        frm.set_df_property('custom_deductions', 'hidden', 1);
                    }
                } else {
                    if(frappe.user.has_role(["System Manager", "HR Manager", "Salary Slips"])){
                        frm.set_df_property('custom_gross_amount', 'hidden', 0);
                        frm.set_df_property('custom_earnings', 'hidden', 0);
                        frm.set_df_property('custom_deductions', 'hidden', 0);
                    }else{
                        frm.set_df_property('custom_gross_amount', 'hidden', 1);
                        frm.set_df_property('custom_earnings', 'hidden', 1);
                        frm.set_df_property('custom_deductions', 'hidden', 1);
                    }
                }
            }
        });
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
