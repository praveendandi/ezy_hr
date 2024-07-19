
import frappe
from datetime import datetime, timedelta


@frappe.whitelist()
def get_attendance(doc,method=None):
    try:
        row_data = doc.as_dict()
        # print(row_data,";pppppppppppppppppppppppppppp")
        frappe.log_error("row_data",row_data)

        if isinstance(row_data.get("time"),str):
            convert_str = row_data.get("time")
            convert_str = datetime.strptime(row_data.get("time"), "%Y-%m-%d %H:%M:%S")
            checkin_date = convert_str.date()
        else:
            convert_str = row_data.get("time")
            checkin_date = convert_str.date()

        attendance_id = None
       
        if row_data.get("log_type") == "IN":
            if not frappe.db.exists("Attendance",{"employee":row_data.get("employee"),"attendance_date":checkin_date}):
                # print("firstinP;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
                frappe.log_error("firstinP")
            # Create a new attendance record if an "IN" log is received
                attendance_id = create_attendance_record(row_data, checkin_date)
            else:
                # print("multipppp....................................")
                frappe.log_error("multipppp")
                # if already creating attendance of that day
                attendance_doc = frappe.get_doc("Attendance",{"employee":row_data.get("employee"),"attendance_date":checkin_date})
                attendance_id_in = attendance_doc.name
                update_attendance_in_checkins([row_data.get("name")], attendance_id_in)

        # print("5","///////////////////////////////////")
        
        if row_data.get("log_type") == "OUT":
            # If an "OUT" log is received, update the latest attendance record that has no "OUT" time
            if frappe.db.exists("Attendance",{"employee":row_data.get("employee"),"attendance_date":checkin_date}):
                # print("yyyyyyyyyyyyyyyyyyyyyyyy")
                frappe.log_error()
                attendance_doc = frappe.get_doc("Attendance",{"employee":row_data.get("employee"),"attendance_date":checkin_date})

                if attendance_doc:
                    attendance_doc.out_time = row_data.get("time")
                    attendance_doc.save()
                    attendance_id = attendance_doc.name
                    calculate_total_hours(attendance_id,checkin_date)

            else:
                # print("7...................................")
                previou_day = checkin_date - timedelta(1)
                attendance_prev_id = frappe.get_doc("Attendance",{"employee":row_data.get("employee"),"attendance_date":previou_day})
                if attendance_prev_id:
                    # print(attendance_prev_id.name,"pmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
                    attendance_id_pre = attendance_prev_id.name
                    attendance_prev_id.out_time = row_data.get("time")
                    attendance_prev_id.save()

                    calculate_total_hours(attendance_id_pre,previou_day)
                    update_attendance_in_checkins([row_data.get("name")], attendance_id_pre)

        if attendance_id:
            update_attendance_in_checkins([row_data.get("name")], attendance_id)
    except Exception as e:
        frappe.log_error("get_attendance",str(e))

def create_attendance_record(row_data, checkin_date):
    attendance_doc = {
        "doctype": "Attendance",
        "employee": row_data.get("employee"),
        "attendance_date": checkin_date,
        "shift": row_data.get("shift"),
        "status":"Present",
        "in_time": row_data.get("time") if row_data.get("log_type") == "IN" else None
    }
    new_attendance = frappe.get_doc(attendance_doc)
    new_attendance.insert()
    return new_attendance.name

def update_attendance_in_checkins(log_names: list, attendance_id: str):
    EmployeeCheckin = frappe.qb.DocType("Employee Checkin")
    (
        frappe.qb.update(EmployeeCheckin)
        .set("attendance", attendance_id)
        .where(EmployeeCheckin.name.isin(log_names))
    ).run()

def calculate_total_hours(attendance_doc,checkin_date):

    attendance_doc = frappe.get_doc("Attendance",{"name":attendance_doc})

    convert_in = datetime.strftime(attendance_doc.in_time, "%Y-%m-%d %H:%M:%S")
    convert_out = datetime.strftime(attendance_doc.out_time, "%Y-%m-%d %H:%M:%S")
    in_time = datetime.strptime(convert_in, "%Y-%m-%d %H:%M:%S")
    out_time = datetime.strptime(convert_out, "%Y-%m-%d %H:%M:%S")
    total_hours = (out_time - in_time).total_seconds() / 3600.0
    attendance_doc.working_hours = total_hours
    attendance_doc.save()
    frappe.db.commit()
