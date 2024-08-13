frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        // Add the 'Update Fields' button
        frm.add_custom_button(__('Update Fields'), function() {
            frappe.route_options = {
                "employee_id": frm.doc.name
            };
            frappe.set_route('Form', 'Employee Fields Update', 'new_employee_fields_update');
        }).addClass('btn-primary');
 
        // Add the 'Create User' button if no user_id is set and employee status is not 'Left'
        if (!frm.doc.user_id && frm.doc.employee && frm.doc.status != 'Left') {
            frm.add_custom_button(__('Create User'), function() {
                create_user_for_employee(frm);
            }).addClass('btn-secondary');
        }
 
       
        if (frm.doc.status === 'Left' && frm.doc.user_id) {
            frappe.call({
                method: 'frappe.client.set_value',
                args: {
                    doctype: 'User',
                    name: frm.doc.user_id, 
                    fieldname: 'enabled',
                    value: 0
                },
                callback: function(r) {
                    if (!r.exc) {
                        frm.set_value('user_id', null);
                        frm.refresh();
                    } else {
                        frappe.msgprint(__('Error occurred while updating the user status'));
                        frappe.log_error(r.exc);
                    }
                },
                error: function(r) {
                    frappe.msgprint(__('Error occurred while updating the user status'));
                    frappe.log_error(r);
                }
            });
        }
        frappe.call({
            method: 'ezy_hr.employee_salary.get_user_employee_id',
            args: {
                data: frm.doc
            },
            callback: function (value) {
                if (value.message && value.message.length > 0) {
                    let employee_id = value.message[0].for_value;
                    if (employee_id === frm.doc.name || frappe.user.has_role(["System Manager", "HR Manager", "Salary Slips"])) {
                        console.log("Employee ID matched or user has required role");

                        frm.set_df_property('custom_gross_amount', 'hidden', 0);
                        frm.set_df_property('custom_earnings', 'hidden', 0);
                        frm.set_df_property('custom_deductions', 'hidden', 0);
                    } else {
                        // Hide the fields if the condition is not met
                        console.log("Hiding fields");
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
                        // Hide the fields if no matching user permission is found
                        console.log("No matching user permission found, hiding fields");
                        frm.set_df_property('custom_gross_amount', 'hidden', 1);
                        frm.set_df_property('custom_earnings', 'hidden', 1);
                        frm.set_df_property('custom_deductions', 'hidden', 1);
                    }
                   
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
 
 function create_user_for_employee(frm) {
    frappe.call({
        method: 'ezy_hr.ezy_hr.custom_script.employee.employee.create_employee_user',
        args: {
            doc : frm.doc.name
        },
        callback: function(r) {
            if (!r.exc) {
                frm.set_value('user_id', r.message);
                frm.refresh();
            } else {     
                frappe.log_error(r.exc);
            }
        },
        error: function(r) {
            frappe.log_error(r);
        }
    });
 }
  