frappe.ui.form.on('Payroll Entry', {
    custom_validate_employee_seperation(frm){
	if (frm.doc.custom_validate_employee_seperation && (frm.doc.employees?.length > 0)) {
		frappe.call({
			method: 'ezy_hr.employee_seperation_details.separation_details',
			args: {
                data:frm.doc
            },
			callback: function (r) {
				employee_seperation(frm, r.message);
			},
		});
	} else {
        var prevoius = cur_frm.doc.employees
		frm.doc.employees = [];
        for (let j = 0; j < prevoius.length; j++) {
            let c = frm.add_child('employees');
            c.employee = prevoius[j]['employee'];
            c.employee_name = prevoius[j]['employee_name'];
            c.department = prevoius[j]['department'];
            c.designation = prevoius[j]['designation'];
        }
        cur_frm.refresh_fields('employees');
	}
	}
});
 
function employee_seperation(frm, data) {
    frm.doc.employees = [];
    let seperation = data;
    for (let j = 0; j < seperation.length; j++) {
        let c = frm.add_child('employees');
        c.employee = seperation[j]['employee'];
        c.employee_name = seperation[j]['employee_name'];
        c.department = seperation[j]['department'];
        c.designation = seperation[j]['designation'];
        c.custom_separation_id = seperation[j]['custom_separation_id'];
        c.custom_status = seperation[j]['custom_status'];
    }
    cur_frm.refresh_fields('employees');
}
