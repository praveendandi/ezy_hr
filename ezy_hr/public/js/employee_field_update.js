frappe.ui.form.on('Employee', {
    refresh: function(frm) {
        
        frm.add_custom_button(__('Update Fields'), function() {
            frappe.route_options = {
                "employee_id":frm.doc.name
            };
            frappe.set_route('Form', 'Employee Fields Update','new_employee_fields_update');
        }).addClass('btn-primary');
        
        // frm.add_custom_button(__('Update Salary'), function() {
        //     frappe.route_options = {
        //         "employee_id":frm.doc.name
        //     };
        //     frappe.set_route('Form', 'Employee Salary Update','new_employee_salary_update');
        // }).addClass('btn-primary');

    },
});