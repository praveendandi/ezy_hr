
import frappe
from datetime import datetime, timedelta


# @frappe.whitelist()
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
                    frappe.db.commit()
                    attendance_id = attendance_doc.name
                    calculate_total_hours(attendance_doc.name,row_data.get("time"))

            else:
                # print("7...................................")
                previou_day = checkin_date - timedelta(1)
                attendance_prev_id = frappe.get_doc("Attendance",{"employee":row_data.get("employee"),"attendance_date":previou_day})
                if attendance_prev_id:
                    # print(attendance_prev_id.name,"pmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
                    attendance_prev_id.out_time = row_data.get("time")
                    attendance_prev_id.save()
                    frappe.db.commit()
                    attendance_id_pre = attendance_prev_id.name
                    calculate_total_hours(attendance_id_pre,previou_day)
                    update_attendance_in_checkins([row_data.get("name")],attendance_id_pre)

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
    frappe.db.commit()

# def calculate_total_hours(attendance_doc,checkin_date):

#     attendance_id = frappe.get_doc("Attendance",{"name":attendance_doc})
#     totalemp_checkins = frappe.db.get_list("Employee Checkin",{"attendance":attendance_id.name},["name","log_type","time"],order_by="time DESC")
#     frappe.log_error("empcheckin",totalemp_checkins)
#     if len(totalemp_checkins) > 2:
#         print("///////333333333333")
#         total_hour = 0
#         intime_hours = None
#         inout_hours = None

#         for each in totalemp_checkins:
#             if each.get("log_type") == "IN":
#                 intime_hours  = each.get("time")

#             if each.get("log_type") == "OUT":
#                 inout_hours  = each.get("time")

#             if  intime_hours and inout_hours:

#                 print(intime_hours,type(intime_hours),"llllllllllll",inout_hours,type(inout_hours))
#                 frappe.log_error("inandout",f"{intime_hours,type(intime_hours)},{inout_hours,type(inout_hours)}")
#                 convert_in = datetime.strftime(intime_hours, "%Y-%m-%d %H:%M:%S")
#                 convert_out = datetime.strftime(inout_hours, "%Y-%m-%d %H:%M:%S")
#                 in_time = datetime.strptime(convert_in, "%Y-%m-%d %H:%M:%S")
#                 out_time = datetime.strptime(convert_out, "%Y-%m-%d %H:%M:%S")
#                 total_hour += (out_time - in_time).total_seconds() / 3600.0
#                 print(total_hour,"//////")
#                 frappe.log_error("totalhours",total_hour)
#                 # attendance_id.working_hours = total_hour
#                 # attendance_id.save()
#                 # frappe.db.commit()
#     else:
#         convert_in = datetime.strftime(attendance_id.in_time, "%Y-%m-%d %H:%M:%S")
#         convert_out = datetime.strftime(attendance_id.out_time, "%Y-%m-%d %H:%M:%S")
#         in_time = datetime.strptime(convert_in, "%Y-%m-%d %H:%M:%S")
#         out_time = datetime.strptime(convert_out, "%Y-%m-%d %H:%M:%S")
#         total_hour = (out_time - in_time).total_seconds() / 3600.0

#     attendance_id.working_hours = total_hour
#     attendance_id.save()
#     frappe.db.commit()
def calculate_total_hours(attendance_doc, checkin_date):
    import frappe
    from datetime import datetime, timezone

    attendance_id = frappe.get_doc("Attendance", {"name": attendance_doc})
    # totalemp_checkins = frappe.db.get_("Employee Checkin", {"attendance": attendance_id.name}, ["name", "log_type", "time"])
    query = """
        SELECT name, log_type, time 
        FROM `tabEmployee Checkin` 
        WHERE attendance = %s 
        ORDER BY time ASC;
    """
    totalemp_checkins = frappe.db.sql(query, (attendance_doc,), as_dict=True)
    frappe.log_error("empcheckin", totalemp_checkins)

    total_hour = 0
    intime_hours = None
    inout_hours = None
    is_lastout = True
    if len(totalemp_checkins) > 2:
        for each in totalemp_checkins:
            if each.get("log_type") == "IN":
                intime_hours = each.get("time")
                frappe.log_error("IN Time", f"{intime_hours} ({type(intime_hours)})")

            if each.get("log_type") == "OUT" and is_lastout:
                inout_hours = each.get("time")
                is_lastout = False
                frappe.log_error("OUT Time", f"{inout_hours} ({type(inout_hours)})")
            if not is_lastout and each.get("log_type") != "OUT":
                inout_hours = datetime.strptime(checkin_date, "%Y-%m-%d %H:%M:%S")
                is_lastout = True
                
            if intime_hours and inout_hours:
        
                if intime_hours < inout_hours:
                    in_time = intime_hours
                    out_time = inout_hours

                    total_hour += (out_time - in_time).total_seconds() / 3600.0
                    frappe.log_error("totalhours", total_hour)
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
            frappe.log_error("Single IN/OUT", f"IN: {in_time} ({type(in_time)}), OUT: {out_time} ({type(out_time)})")
            total_hour = (out_time - in_time).total_seconds() / 3600.0
    frappe.log_error("toltahrafter",total_hour)

    attendance_id.working_hours = total_hour
    attendance_id.save()
    frappe.log_error("aftersave",totalemp_checkins)
    frappe.db.commit()
    
