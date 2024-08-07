frappe.ui.form.on('Compensatory Leave Request', {
    refresh: function(frm) {
        hide_add_row_button(frm);
        update_table_visibility(frm);
 
 
        frm.fields_dict.work_from_date.df.onchange = async function() {
            await update_compensatory_days(frm);
        };
        frm.fields_dict.work_end_date.df.onchange = async function() {
            await update_compensatory_days(frm);
        };
    }
 });
 
 
 async function update_compensatory_days(frm) {
    if (frm.doc.work_from_date && frm.doc.work_end_date) {
        let from_date = new Date(frm.doc.work_from_date);
        let end_date = new Date(frm.doc.work_end_date);
        if (from_date > end_date) {
            frappe.throw(__("'Work From Date' cannot be after 'Work End Date'"));
            return;
        }
        frm.clear_table('custom_attendance_logs');
        let data_found = false;
        for (let date = from_date; date <= end_date; date.setDate(date.getDate() + 1)) {
            let date_str = frappe.datetime.get_datetime_as_string(date, true);
            let attendance_data = (
                await frappe.db.get_value(
                    "Attendance",
                    {
                        employee: frm.doc.employee,
                        attendance_date: date_str,
                    },
                    ["in_time", "out_time", "working_hours", "attendance_date"]
                )
            ).message;
            if (attendance_data && attendance_data.in_time && attendance_data.out_time) {
                let child_row = frm.add_child('custom_attendance_logs');
                if (child_row) {
                    let in_time = attendance_data.in_time ? attendance_data.in_time.split(" ")[1] : "";
                    let out_time = attendance_data.out_time ? attendance_data.out_time.split(" ")[1] : "";
                    frappe.model.set_value(child_row.doctype, child_row.name, 'attendance_date', attendance_data.attendance_date);
                    frappe.model.set_value(child_row.doctype, child_row.name, 'in_time', in_time);
                    frappe.model.set_value(child_row.doctype, child_row.name, 'out_time', out_time);
                    frappe.model.set_value(child_row.doctype, child_row.name, 'working_hour', attendance_data.working_hours);
                    data_found = true;
                } else {
                    frappe.throw(__("Unable to add child row to 'custom_attendance_logs'"));
                }
            }
        }
        frm.refresh_field('custom_attendance_logs');
        update_table_visibility(frm);
    }
 }
 
 
 function hide_add_row_button(frm) {
    $(frm.fields_dict.custom_attendance_logs.grid.wrapper).find('.grid-add-row').hide();
 }
 
 
 function update_table_visibility(frm) {
    let has_data = frm.doc.custom_attendance_logs && frm.doc.custom_attendance_logs.length > 0;
    frm.fields_dict.custom_attendance_logs.df.hidden = !has_data;
    frm.refresh_field('custom_attendance_logs');
 
 
   
    if (has_data) {
        hide_add_row_button(frm);
    }
 }
 