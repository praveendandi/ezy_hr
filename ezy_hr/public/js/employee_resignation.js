frappe.ui.form.on('Employee Resignation', {
    custom_employee_type: function(frm) {
        if (frm.doc.custom_employee_type) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'EzyHr Settings',
                    fieldname: ['custom_notice_period_days_for_associate', 'custom_notice_period_days_for_management']
                },
                callback: function(r) {
                    if (r.message) {
                        let custom_notice_period_days = 0;
                        if (frm.doc.custom_employee_type === 'Associate') {
                            custom_notice_period_days = r.message.custom_notice_period_days_for_associate;
                        } else if (frm.doc.custom_employee_type === 'Management') {
                            custom_notice_period_days = r.message.custom_notice_period_days_for_management;
                        }
                        frm.set_value('custom_notice_period_days', custom_notice_period_days);
                    }
                }
            });
        }
    },
 
    resignation_date: function(frm) {
        if (frm.doc.resignation_date && frm.doc.custom_employee_type) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'EzyHr Settings',
                    fieldname: ['custom_notice_period_days_for_associate', 'custom_notice_period_days_for_management']
                },
                callback: function(r) {
                    if (r.message) {
                        let custom_notice_period_days = 0;
                        if (frm.doc.custom_employee_type === 'Associate') {
                            custom_notice_period_days = r.message.custom_notice_period_days_for_associate;
                        } else if (frm.doc.custom_employee_type === 'Management') {
                            custom_notice_period_days = r.message.custom_notice_period_days_for_management;
                        }
                        let last_working_date = frappe.datetime.add_days(frm.doc.resignation_date, custom_notice_period_days);
                        frm.set_value('last_working_date', last_working_date);
                    }
                }
            });
        }
    }
});