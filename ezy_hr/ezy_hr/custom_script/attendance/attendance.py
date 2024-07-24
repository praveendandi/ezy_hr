
import frappe
from datetime import datetime, timedelta,timezone

# from datetime import datetime, timezone


# @frappe.whitelist()
def get_attendance(doc,method=None):
    try:
        row_data = doc.as_dict()

        if isinstance(row_data.get("time"),str):
            convert_str = row_data.get("time")
            convert_str = datetime.strptime(row_data.get("time"), "%Y-%m-%d %H:%M:%S")
            checkin_date = convert_str.date()
        else:
            convert_str = row_data.get("time")
            checkin_date = convert_str.date()

        # if frappe.db.exists("Attendance", {"employee":doc.employee, "attendance_date":checkin_date,"status":'On Leave', "docstatus":1}):
        #     attendance_doc = frappe.get_doc("Attendance", {"employee":doc.employee, "attendance_date":checkin_date,"status":'On Leave', "docstatus":1})
        #     if attendance_doc:
        #         attendance_doc.docstatus = 2
        #         attendance_doc.cancel()

        
       
        if row_data.get("log_type") == "IN":
            if not frappe.db.exists("Attendance",{"employee":row_data.get("employee"),"attendance_date":checkin_date}):
            # Create a new attendance record if an "IN" log is received
                attendance_id = create_attendance_record(row_data, checkin_date)
                update_attendance_in_checkins([row_data.get("name")], attendance_id)
            else:
                # if already creating attendance of that day
                attendance_doc = frappe.get_doc("Attendance",{"employee":row_data.get("employee"),"attendance_date":checkin_date})
                attendance_id_in = attendance_doc.name
                update_attendance_in_checkins([row_data.get("name")], attendance_id_in)
        

        
        if row_data.get("log_type") == "OUT":
            # If an "OUT" log is received, update the latest attendance record that has no "OUT" time
            if frappe.db.exists("Attendance",{"employee":row_data.get("employee"),"attendance_date":checkin_date}):
                attendance_doc = frappe.get_doc("Attendance",{"employee":row_data.get("employee"),"attendance_date":checkin_date})
                if attendance_doc.docstatus == 1:
                    frappe.db.set_value("Attendance", attendance_doc.name,{"out_time": row_data.get("time")})
                    frappe.db.commit()
                    attendance_id_out = attendance_doc.name
                    update_attendance_in_checkins([row_data.get("name")], attendance_id_out)
                    calculate_total_hours(attendance_id_out,row_data.get("time"))

                else:
                    attendance_doc.out_time = row_data.get("time")
                    attendance_doc.save()
                    frappe.db.commit()
                    attendance_id_out = attendance_doc.name
                    update_attendance_in_checkins([row_data.get("name")], attendance_id_out)
                    calculate_total_hours(attendance_id_out,row_data.get("time"))

            else:
                previou_day = checkin_date - timedelta(1)
                attendance_prev_id = frappe.get_doc("Attendance",{"employee":row_data.get("employee"),"attendance_date":previou_day})
                if attendance_prev_id.docstatus == 1:
                    frappe.db.set_value("Attendance", attendance_prev_id.name,{"out_time": row_data.get("time")})
                    frappe.db.commit()
                    attendance_id_out = attendance_prev_id.name
                    update_attendance_in_checkins([row_data.get("name")], attendance_id_out)
                    calculate_total_hours(attendance_id_out,previou_day,)

                else:
                    attendance_prev_id.out_time = row_data.get("time")
                    attendance_prev_id.save()
                    frappe.db.commit()
                    attendance_id_pre = attendance_prev_id.name
                    update_attendance_in_checkins([row_data.get("name")],attendance_id_pre)
                    calculate_total_hours(attendance_id_pre,previou_day)
                
                

        
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
    checkin_doc = frappe.get_doc("Employee Checkin", {"name":log_names[0]})
    checkin_doc.attendance =attendance_id
    checkin_doc.flags.ignore_validate = True
    checkin_doc.save(ignore_permissions=True)
    frappe.db.commit()

    check_in_list = frappe.db.get_list("Employee Checkin", {"attendance":attendance_id}, [ "time"],order_by="time")
    in_time = check_in_list[0].time
    out_time = check_in_list[-1].time

    working_hours = calculate_total_hours(attendance_id)  
    frappe.db.set_value("Attendance", attendance_id,
                {
                    "working_hours": working_hours,
                    "in_time": in_time,
                    "out_time": out_time,
                    "docstatus":1}
                )
    frappe.db.commit()
        
    # EmployeeCheckin = frappe.qb.DocType("Employee Checkin")
    # (
    #     frappe.qb.update(EmployeeCheckin)
    #     .set("attendance", attendance_id)
    #     .where(EmployeeCheckin.name.isin(log_names))
    # ).run()
    # frappe.db.commit()


def calculate_total_hours(attendance_doc, checkin_date):
    

    attendance_id = frappe.get_doc("Attendance", {"name": attendance_doc})
    # totalemp_checkins = frappe.db.get_("Employee Checkin", {"attendance": attendance_id.name}, ["name", "log_type", "time"])
    query = """
        SELECT name, log_type, time 
        FROM `tabEmployee Checkin` 
        WHERE attendance = %s 
        ORDER BY time ASC;
    """
    totalemp_checkins = frappe.db.sql(query, (attendance_doc,), as_dict=True)
    frappe.log_error("totalemp_checkins",totalemp_checkins)

    total_hour = 0
    intime_hours = None
    inout_hours = None
    is_lastout = True
    if len(totalemp_checkins) > 2:
        for each in totalemp_checkins:
            if each.get("log_type") == "IN":
                intime_hours = each.get("time")

            if each.get("log_type") == "OUT":
                inout_hours = each.get("time")
                is_lastout = False
            # if not is_lastout and each.get("log_type") != "OUT":
            #     inout_hours = datetime.strptime(checkin_date, "%Y-%m-%d %H:%M:%S")
            #     is_lastout = True

            if intime_hours and inout_hours:
        
                if intime_hours < inout_hours:
                    in_time = intime_hours
                    out_time = inout_hours
                    total_hour += (out_time - in_time).total_seconds() / 3600.0
                    intime_hours = None
                    inout_hours = None
                else:
                    frappe.log_error("time_error", f"IN time {intime_hours} is after OUT time {inout_hours}")
                    intime_hours = None
                    inout_hours = None
                    is_lastout = True

    else:
        if attendance_id.in_time and attendance_id.out_time:
            in_time = attendance_id.in_time
            out_time = attendance_id.out_time
            total_hour = (out_time - in_time).total_seconds() / 3600.0
    

    if attendance_id.docstatus == 1:
        frappe.db.set_value("Attendance", attendance_id.name,{"working_hours":total_hour})
        frappe.db.commit()

    
    if total_hour > 7:
        if attendance_id.docstatus == 1:
            pass
        else:
            attendance_id.working_hours = total_hour
            attendance_id.save()
            attendance_id.submit()
            frappe.db.commit()
    
    else:
        attendance_id.working_hours = total_hour   
        attendance_id.save()
        frappe.db.commit()
    
