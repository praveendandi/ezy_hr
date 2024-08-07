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
	},
    refresh(frm) {
        frm.add_custom_button(__('Generate Absents'), function() {
            frappe.prompt([
                {'fieldname': 'unit', 'fieldtype': 'Link', 'label': 'Select Unit', 'options': 'Company'},
                {'fieldname': 'from_date', 'fieldtype': 'Date', 'label': 'From Date'},
                {'fieldname': 'to_date', 'fieldtype': 'Date', 'label': 'To Date'},
            ], function(values) {
                let unit = values.unit;
                let from_date = values.from_date;
                let to_date = values.to_date;

                // Fetch employees within the selected unit
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: "Employee",
                        filters: {
                            "company": unit,
                            "status":"Active"
                        },
                        fields: ['name']
                    },
                    callback: function(data) {
                        if (data.message) {
                            // Call the server-side method to create absents for all employees in the unit
                            frappe.call({
                                method: 'ezy_hr.ezy_hr.custom_script.attendance.absen_attendance.create_absents',
                                args: {
                                    "data":data.message,
                                    // unit: unit,
                                    "from_date": from_date,
                                    "to_date": to_date,
                                    // employee_ids: employee_ids
                                },
                                callback: function(response) {
                                    if (response.message) {
                                        frappe.msgprint(__('Response: ' + response.message));
                                    }
                                }
                            });
                        } else {
                            frappe.msgprint(__('No employees found for the selected unit.'));
                        }
                    }
                });
            }, __('Generate Absents'), __('Submit'));
        },);
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
