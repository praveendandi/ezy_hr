frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        frm.add_custom_button(__('Update Fields'), function() {
            frappe.route_options = {
                "employee_id":frm.doc.name
            };
            frappe.set_route('Form', 'Employee Fields Update','new_employee_fields_update');
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
        });
    }
});
