// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Salary Update", {
    employee_id: function(frm) {
        if (frm.doc.employee_id && frm.doc.previous_review_date) {
            frappe.call({
                method: 'ezy_hr.ezy_hr.doctype.employee_salary_update.employee_salary_update.update_earning_table',
                args: {
                    data: frm.doc
                },
                callback: function (r) {
                    earning_child(frm, r.message);
                },
            });
        } else {
            frm.clear_table('component_detail');
            frm.refresh_field('component_detail');
        }

        if (frm.doc.employee_id) { 
            frappe.call({
                method: 'ezy_hr.ezy_hr.doctype.employee_salary_update.employee_salary_update.update_deduction_table',
                args: {
                    data: frm.doc
                },
                callback: function (r) {
                    deduction_child(frm, r.message);
                },
            });
        } else {
            frm.clear_table('deduction_detail');
            frm.refresh_field('deduction_detail');
        }
    },
});

frappe.ui.form.on("Earning Child",{
    new_amount: function (frm, cdt, cdn) {
       update_child(frm)
            
    },
})

function update_child(frm) {
    let total_gross = 0;
        let earning_rows = frm.doc.component_detail;

        earning_rows.forEach(function(row) {
            total_gross += row.new_amount;
        });

        if (total_gross > 0) {
            frm.set_value('new_gross_amount', total_gross);
            frm.refresh_field('new_gross_amount');
        }
}


function deduction_child(cur_frm, data) {
    cur_frm.doc.deduction_detail = [];
    let deduction = data;
    for (let index = 0; index < deduction.length; index++) {
        let child = cur_frm.add_child('deduction_detail');
        child.salary_component = deduction[index]['salary_component'];
        child.amount = deduction[index]['amount'];
        child.custom_employee_condition = deduction[index]['custom_employee_condition'];
        child.condition = deduction[index]['condition'];
        child.amount_based_on_formula = deduction[index]['amount_based_on_formula'];
        child.formula = deduction[index]['formula'];
        child.do_not_include_in_total = deduction[index]['do_not_include_in_total']  
    }
    cur_frm.refresh_fields('deduction_detail');
}