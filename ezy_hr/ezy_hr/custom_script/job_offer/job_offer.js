frappe.ui.form.on("Job Offer", {
    refresh: function (frm) {
        if ((!frm.doc.__islocal) && (frm.doc.status == 'Accepted')
            && (frm.doc.docstatus === 1) && (!frm.doc.__onload || !frm.doc.__onload.employee)) {
            frm.add_custom_button(__('Create New Employee'), function () {
                frappe.model.with_doctype('Employee', function () {
                    // Create a new Employee document
                    var empl = frappe.model.get_new_doc('Employee');
                    var job_offer = frm.doc;
                    empl.first_name = job_offer.custom_first_name;
                    empl.last_name = job_offer.custom_last_name;
                    empl.date_of_joining = job_offer.custom_date_of_joining;
                    empl.date_of_birth = job_offer.custom_date_of_birth;
                    empl.reports_to = job_offer.custom_reports_to;
                    empl.department = job_offer.custom_department;
                    empl.grade = job_offer.custom_level;
                    empl.designation = job_offer.designation;
                    empl.company = job_offer.company;
                    empl.custom_gross_amount = job_offer.custom_gross_amount;
                    empl.job_applicant = job_offer.job_applicant;
                    empl.scheduled_confirmation_date = job_offer.offer_date
                    
                    if (job_offer.custom_earning) {
                        job_offer.custom_earning.forEach(function (earning) {
                            var em_earning = frappe.model.add_child(empl, 'custom_earnings');
                            em_earning.salary_component = earning.salary_component;
                            em_earning.abbr = earning.abbr
                            em_earning.amount = earning.amount;
                        });
                    }
                    if (job_offer.custom_deducations) {
                        job_offer.custom_deducations.forEach(function (deduction) {
                            var em_deduction = frappe.model.add_child(empl, 'custom_deductions');
                            em_deduction.salary_component = deduction.salary_component;
                            em_deduction.amount = deduction.amount;
                            em_deduction.abbr = deduction.abbr
                            em_deduction.custom_employee_condition = deduction.custom_employee_condition
                            em_deduction.condition = deduction.condition;
                            em_deduction.amount_based_on_formula = deduction.amount_based_on_formula;
                            em_deduction.formula = deduction.formula
                            em_deduction.do_not_include_in_total = deduction.do_not_include_in_total
                        });
                    }
                    if (job_offer.company != "Paul Resorts And Hotels"){
                        empl.custom_effective_date = job_offer.custom_date_of_joining
                    }
                        
                    frappe.set_route('Form', 'Employee', empl.name);
                });
            });
        }

        setTimeout(() => {
            frm.remove_custom_button('Create Employee');
        }, 10);
    },

    job_applicant: function (frm) {
       deduction_applicable(frm)
    },
    company: function (frm) {
       deduction_applicable(frm)
    },
    custom_applicant_type: function (frm) {
       deduction_applicable(frm)
    },

    validate: function (frm) {
        var total_amount = 0;

        $.each(frm.doc.custom_earning, function (i, d) {
            total_amount += flt(d.amount)
        });
        frm.set_value("custom_gross_amount", total_amount);
        frm.refresh_field('custom_gross_amount');
    }


});

frappe.ui.form.on("Salary Detail",{
    amount: function (frm, cdt, cdn) {
       update_child(frm)
            
    },
})
function update_child(frm) {
    let total_gross = 0;
        let earning_rows = frm.doc.custom_earning;

        earning_rows.forEach(function(row) {
            total_gross += row.amount;
        });

        if (total_gross > 0) {
            frm.set_value('custom_gross_amount', total_gross);
            frm.refresh_field('custom_gross_amount');
        }
}

function deduction_applicable(frm) {
    if (frm.doc.job_applicant && frm.doc.custom_applicant_type == "Employee") {
            frappe.call({
                method: 'ezy_hr.ezy_hr.custom_script.job_offer.job_offer.update_deduction_table',
                args: {
                    data: frm.doc
                },
                callback: function (r) {
                    deduction_child(frm, r.message);
                },
            });
    } else {
        frm.clear_table('custom_deducations');
        frm.refresh_field('custom_deducations');
    }
}

function deduction_child(cur_frm, data) {
    cur_frm.doc.custom_deducations = [];
    let deduction = data;
    for (let index = 0; index < deduction.length; index++) {
        let child = cur_frm.add_child('custom_deducations');
        child.salary_component = deduction[index]['salary_component'];
        child.amount = deduction[index]['amount'];
        child.custom_employee_condition = deduction[index]['custom_employee_condition'];
        child.condition = deduction[index]['condition'];
        child.amount_based_on_formula = deduction[index]['amount_based_on_formula'];
        child.formula = deduction[index]['formula'];
        child.do_not_include_in_total = deduction[index]['do_not_include_in_total']  
    }
    cur_frm.refresh_fields('custom_deducations');
}