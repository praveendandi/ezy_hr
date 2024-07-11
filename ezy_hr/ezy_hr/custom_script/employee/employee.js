frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        // Add the 'Update Fields' button
        frm.add_custom_button(__('Update Fields'), function() {
            frappe.route_options = {
                "employee_id": frm.doc.name
            };
            frappe.set_route('Form', 'Employee Fields Update', 'new_employee_fields_update');
        }).addClass('btn-primary');
        
        // Add the 'Create User' button if no user_id is set
        if (!frm.doc.user_id) {
            frm.add_custom_button(__('Create User'), function() {
                create_user_for_employee(frm);
            }).addClass('btn-secondary');
        }
    }
});

function create_user_for_employee(frm) {
    frappe.call({
        method: 'ezy_hr.ezy_hr.custom_script.employee.employee.create_employee_user',
        args: {
            employee: frm.doc.name
        },
        callback: function(r) {
            if (!r.exc) {
                frm.set_value('user_id', r.message);
                frm.refresh();
            }
        }
    });
}
