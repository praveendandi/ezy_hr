from datetime import date,datetime
import frappe

@frappe.whitelist()
def flexi_weekoff():
    try:
        # Retrieve leave types with the custom flexible week off enabled
        weekoff_leave_types = frappe.db.sql("""
            SELECT lt.name, fl.unit, fl.holiday_list, fl.unit_holiday_list, fl.select_holiday_type
            FROM `tabLeave Type` as lt
            JOIN `tabFlexi Weekoff list` as fl ON lt.name = fl.parent
            WHERE lt.custom_flexi_week_off = 1
        """, as_dict=True)
        
        if not weekoff_leave_types:
            frappe.log_error(message="No leave types with custom_flexi_week_off found", title="Flexi Weekoff Error")
            return

        today = date.today()

        for weekoff in weekoff_leave_types:
            weekoff_type = weekoff["select_holiday_type"]
            unit_holiday_list = weekoff["unit_holiday_list"]
            
            if not unit_holiday_list:
                frappe.log_error(message=f"No unit holiday list found for {weekoff['name']}", title="Flexi Weekoff Error")
                continue

            # Prepare and execute the holiday query based on the type of holiday
            holiday_query = """
                SELECT holiday_date, description
                FROM `tabHoliday`
                WHERE parent = %s AND parentfield = 'holidays' AND parenttype = 'Holiday List' AND weekly_off = %s
            """
            holiday_type_flag = 1 if weekoff_type == "For Week Off" else 0
            holiday_dates = frappe.db.sql(holiday_query, (unit_holiday_list, holiday_type_flag), as_dict=True)

            for holiday in holiday_dates:
                if today == holiday['holiday_date']:
                    date_and_description = f"{holiday['holiday_date']}, {holiday['description']}"
                    
                    # Retrieve employee ids and their leave allocations
                    employee_leaves = frappe.db.sql("""
                        SELECT emp.name as employee_name, la.name as leave_allocation_name, la.total_leaves_allocated, la.new_leaves_allocated
                        FROM `tabEmployee` as emp
                        JOIN `tabLeave Allocation` as la ON la.employee = emp.name
                        WHERE emp.company = %s AND emp.holiday_list = %s AND la.leave_type = %s
                    """, (weekoff["unit"], weekoff["holiday_list"], weekoff["name"]), as_dict=True)

                    for leave in employee_leaves:
                        update_leave_allocation(leave, date_and_description)

    except Exception as e:
        frappe.log_error(message=str(e), title="Error in flexi_weekoff function")
        print(f"Error in flexi_weekoff function: {str(e)}")

def update_leave_allocation(allocation, date_and_description):
    try:
       
        leave_allocation_doc = frappe.get_doc("Leave Allocation", {"name":allocation['leave_allocation_name'],"docstatus":1})
        old_value_allocation = leave_allocation_doc.new_leaves_allocated
        leave_allocation_doc.new_leaves_allocated = old_value_allocation + 1

        leave_allocation_doc.save()
        leave_allocation_doc.submit()

        frappe.db.commit()

        # Update or create a Leave Ledger Entry with the current holiday information
        leave_ledger_entry_name = frappe.db.get_value("Leave Ledger Entry", {"transaction_name": leave_allocation_doc.name}, "name")
        
        if leave_ledger_entry_name:
            frappe.db.set_value("Leave Ledger Entry", leave_ledger_entry_name, "custom_reason_date_", date_and_description)
            frappe.db.commit()
        else:
            new_leave_ledger_entry = frappe.get_doc({
                "doctype": "Leave Ledger Entry",
                "transaction_name": leave_allocation_doc.name,
                "custom_reason_date_": date_and_description,
                "leave_type": leave_allocation_doc.leave_type,
                "employee": leave_allocation_doc.employee
            })
            new_leave_ledger_entry.insert()
            new_leave_ledger_entry.submit()

        print(f"Updated leave allocation: {allocation['leave_allocation_name']}, new leaves allocated: {leave_allocation_doc.new_leaves_allocated}")
    except Exception as e:
        frappe.log_error(message=str(e), title="Error updating leave allocation")
        print(f"Error updating leave allocation: {allocation['leave_allocation_name']} - {str(e)}")
