// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Salary Update", {
	employee_id(cur_frm) {
        if (cur_frm.doc.employee_id != "" && cur_frm.doc.previous_review_date != "") {
            frappe.call({
                method: 'ezy_hr.ezy_hr.doctype.employee_salary_update.employee_salary_update.update_earning_table',
                args: {
                    data:cur_frm.doc
                },
                callback: function (r) {
                    earning_child(cur_frm, r.message);
                },
            });
        } else {
            cur_frm.doc.component_detail = [];
            cur_frm.refresh_fields('component_detail')
        }
	},
});

function earning_child(cur_frm, data) {

    cur_frm.doc.component_detail = [];
    let earnings = data;
    for (let index = 0; index < earnings.length; index++) {
        let child = cur_frm.add_child('component_detail');
        child.salary_component = earnings[index]['salary_component'];
        child.amount = earnings[index]['amount'];
    }
    cur_frm.refresh_fields('component_detail');
}