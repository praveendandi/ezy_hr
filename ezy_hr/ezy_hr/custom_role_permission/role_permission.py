import frappe

def get_role_permissions():
    return {
        "Department": {
            "read": ["Ezy Leave Creation"],
            "export":[]
        },
        "Employee": {
            "read": ["Ezy Leave Creation"],
            "export":[]
        },
        "Leave Type": {
            "read": ["Ezy Leave Creation"],
            "export":[]
        },
        "Company": {
            "read": ["Ezy Leave Creation"],
            "export":[]
        },
        "Leave Application": {
            "select":["Ezy Leave Creation"],
            "read": ["Ezy Leave Creation"],
            "write": ["Ezy Leave Creation"],
            "create": ["Ezy Leave Creation"],
            "export":[]
        },
        "Attendance Request": {
            "select":["Ezy Leave Creation"],
            "read": ["Ezy Leave Creation"],
            "write": ["Ezy Leave Creation"],
            "create": ["Ezy Leave Creation"],
            "export":[]
        },
        'Attendance':{
            "read": ["Employee"],
            "write": ["Employee"],
            "create": ["Employee"],
            "export":[]
        }     
    }

def update_permissions():
    try:
        role_permissions = get_role_permissions()
        for doctype, permissions in role_permissions.items():
            for perm_type, roles in permissions.items():
                for role in roles:
                    get_created = frappe.permissions.add_permission(doctype,role,perm_type)
                    
    except Exception as e:
        frappe.log_error(str(e))
                
