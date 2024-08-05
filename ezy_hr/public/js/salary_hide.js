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
                        console.log(frm.doc.name, "/////////// Employee ID matched or user has required role", employee_id);

                        frm.set_df_property('custom_gross_amount', 'hidden', 0);
                        frm.set_df_property('custom_earnings', 'hidden', 0);
                        frm.set_df_property('custom_deductions', 'hidden', 0);
                    } else {
                        // Hide the fields if the condition is not met
                        console.log("/////////// Hiding fields");
                        frm.set_df_property('custom_gross_amount', 'hidden', 1);
                        frm.set_df_property('custom_earnings', 'hidden', 1);
                        frm.set_df_property('custom_deductions', 'hidden', 1);
                    }
                } else {
                    // Hide the fields if no matching user permission is found
                    console.log("/////////// No matching user permission found, hiding fields");
                    frm.set_df_property('custom_gross_amount', 'hidden', 1);
                    frm.set_df_property('custom_earnings', 'hidden', 1);
                    frm.set_df_property('custom_deductions', 'hidden', 1);
                }
            }
        });
    }
});
