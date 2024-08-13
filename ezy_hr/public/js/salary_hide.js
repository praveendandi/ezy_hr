frappe.ui.form.on('Employee', {
    refresh: function(frm) {
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
                        // Hide the fields if the condition is not met
                        frm.set_df_property('custom_gross_amount', 'hidden', 1);
                        frm.set_df_property('custom_earnings', 'hidden', 1);
                        frm.set_df_property('custom_deductions', 'hidden', 1);
                    }
                } else {
                    // Hide the fields if no matching user permission is found
                    frm.set_df_property('custom_gross_amount', 'hidden', 1);
                    frm.set_df_property('custom_earnings', 'hidden', 1);
                    frm.set_df_property('custom_deductions', 'hidden', 1);
                }
            }
        });
    }
});
