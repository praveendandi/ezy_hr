frappe.ui.form.on("Employee Promotion", {
    refresh: function(frm) {
        console.log("Form Loaded");
    },
    validate: function(frm) {
        calculate_total_amount(frm);
    },
    custom_effective_date: function(frm) {
        on_change_value(frm);
    },
    employee: function(frm) {
        on_change_value(frm);
    },
    custom_earnings_detail: {
        on_change: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            calculate_total_amount(frm);
        }
    }
});

function on_change_value(frm) {
    if(frm.doc.employee && frm.doc.custom_effective_date){
        frappe.call({
            method: 'ezy_hr.ezy_hr.doctype.employee_salary_update.employee_salary_update.update_earning_table',
            args: {
                data: frm.doc
            },
            callback: function (r) {
                if (r.message) {
                    employee_earnings(frm, r.message);
                    // calculate_total_amount(frm);
                }
            },
            error: function(err) {
                console.error("Error fetching earnings data", err);
            }
        });
    } else {
        frm.doc.custom_earnings_detail = [];
        frm.refresh_field('custom_earnings_detail');
        frm.set_value('custom_new_gross_amount', 0);
    }
}

function employee_earnings(frm, data) {
    frm.doc.custom_earnings_detail = [];
    data.forEach(function(item) {
        let row = frm.add_child('custom_earnings_detail');
        row.salary_component = item.salary_component;
        row.amount = item.amount;
    });
    frm.refresh_field('custom_earnings_detail');
}

function calculate_total_amount(frm) {
    let total = 0;
    frm.doc.custom_earnings_detail.forEach(function(row) {
        total += flt(row.new_amount);
    });
    frm.set_value('custom_new_gross_amount', total);
    frm.refresh_field('custom_new_gross_amount');
}