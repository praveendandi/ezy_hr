frappe.ui.form.on('Compensatory Leave Request', {
    work_from_date: async function(frm) {
        await update_compensatory_days(frm);
    },
    work_end_date: async function(frm) {
        await update_compensatory_days(frm);
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
 
            if (attendance_data) {
                console.log("Attendance data for date", date_str, ":", attendance_data);
 
                let child_row = frm.add_child('custom_attendance_logs');
                if (child_row) {
                    
                    let in_time = attendance_data.in_time ? attendance_data.in_time.split(" ")[1] : "";
                    let out_time = attendance_data.out_time ? attendance_data.out_time.split(" ")[1] : "";
 
                    frappe.model.set_value(child_row.doctype, child_row.name, 'attendance_date', attendance_data.attendance_date);
                    frappe.model.set_value(child_row.doctype, child_row.name, 'in_time', in_time);
                    frappe.model.set_value(child_row.doctype, child_row.name, 'out_time', out_time);
                    frappe.model.set_value(child_row.doctype, child_row.name, 'working_hour', attendance_data.working_hours);
                } else {
                    frappe.throw(__("Unable to add child row to 'custom_attendance_logs'"));
                }
            }
        }
 
        frm.refresh_field('custom_attendance_logs');
    }
 }
 