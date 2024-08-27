import frappe
from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on
from datetime import date ,datetime

@frappe.whitelist()
def get_flexi_saturday_weekoff():
    
    get_leave_type = frappe.db.get_all("Leave Type",{"custom_flexi_saturday_off":1},['name'])
    
    if get_leave_type:
        
        employee_leaves = frappe.db.sql("""
                    SELECT emp.name as employee_name, la.name as leave_allocation_name, la.total_leaves_allocated, la.new_leaves_allocated
                    FROM `tabEmployee` as emp
                    JOIN `tabLeave Allocation` as la ON la.employee = emp.name
                    WHERE la.leave_type = %s
                """, (get_leave_type[0].get('name')), as_dict=True)
        
        
        for each in employee_leaves:
            
            current_date = date.today()
            date_and_description = f"{get_leave_type[0].get('name')}, {current_date}"
            get_balacnce = get_leave_balance_on(each.get("employee_name"),get_leave_type[0]["name"],current_date,consider_all_leaves_in_the_allocation_period=True)
            
            if get_balacnce == 0:
                increment_value = 2
                update_leave_allocation(each,increment_value,date_and_description)
                
            elif get_balacnce == 1:
                increment_value = 1
                update_leave_allocation(each,increment_value,date_and_description)
            else:
               pass


def update_leave_allocation(allocation,increment_value,date_and_description):
    try:
       
        leave_allocation_doc = frappe.get_doc("Leave Allocation", {"name":allocation.get('leave_allocation_name'),"docstatus":1})
        old_value_allocation = leave_allocation_doc.new_leaves_allocated + increment_value
        total_allocation = leave_allocation_doc.total_leaves_allocated + increment_value
        leave_allocation_doc.new_leaves_allocated = old_value_allocation
        leave_allocation_doc.total_leaves_allocated = total_allocation

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

    except Exception as e:
        frappe.log_error(title="Error updating leave allocation",message=str(e)) 