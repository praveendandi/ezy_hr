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
        console.log("Custom leave policy triggered");
        
        frappe.call({
            method: "ezy_hr.ezy_hr.custom_script.employee.employee.assign_leave_policy",
            args: { doc: cur_frm.doc },
            callback: function(r) {
                console.log(r,"//////////////")
                if (r.message.success) {
                    frappe.msgprint(r.message.reason);
                } else {
                    frappe.msgprint(r.message.reason);
                }
            }
        });
    }
});



