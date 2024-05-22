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
		frm.doc.custom_uncompleted_seperations = [];
        cur_frm.refresh_fields('custom_uncompleted_seperations')
	}
	}
});

function employee_seperation(frm, data) {

    frm.doc.custom_uncompleted_seperations = [];
    let seperation = data;
    for (let j = 0; j < seperation.length; j++) {
        let c = frm.add_child('custom_uncompleted_seperations');
        c.employee = seperation[j]['employee'];
        c.employee_name = seperation[j]['employee_name'];
        c.department = seperation[j]['department'];
        c.designation = seperation[j]['designation'];
        c.custom_separation_id = seperation[j]['name'];
        c.custom_status = seperation[j]['boarding_status'];
    }
    cur_frm.refresh_fields('custom_uncompleted_seperations');
}