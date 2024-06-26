
frappe.ui.form.on('Appointment Letter', {
	custom_get_salary_break_up: function(frm){
        console.log(frm.doc.custom_employee)
        
        frappe.db.get_doc('Employee', frm.doc.custom_employee)
            .then(empl_data => {
                console.log(empl_data);
                employee_earnings(frm, empl_data.custom_earnings)
                employee_deduction(frm,empl_data.custom_deductions)

            })
}});

function employee_earnings(frm, data) {

    frm.doc.custom_earning = [];
    let earning = data;
    for (let j = 0; j < earning.length; j++) {
        let c = frm.add_child('custom_earning');
        c.salary_component = earning[j]['salary_component'];
        c.amount = earning[j]['amount'];
    }
    cur_frm.refresh_fields('custom_earning');
}

function employee_deduction(frm, data) {

    frm.doc.custom_deductions = [];
    let deduction = data;
    for (let j = 0; j < deduction.length; j++) {
        let c = frm.add_child('custom_deductions');
        c.salary_component = deduction[j]['salary_component'];
        c.amount = deduction[j]['amount'];
        c.abbr = deduction[j]['abbr'];
        c.formula = deduction[j]['formula'];
        c.amount_based_on_formula = deduction[j]['amount_based_on_formula'];
        c.do_not_include_in_total = deduction[j]['do_not_include_in_total'];
        c.condition = deduction[j]['condition'];
        c.custom_employee_condition = deduction[j]['custom_employee_condition'];
    }
    cur_frm.refresh_fields('custom_deductions');
}
