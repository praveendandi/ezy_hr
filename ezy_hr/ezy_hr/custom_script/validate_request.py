import frappe
from frappe import _

def restrict_self_leave_approval(doc,method=None):

    user_id = frappe.db.get_value("Employee",doc.employee, "user_id")
    if user_id:
        if frappe.session.user == user_id:
            frappe.throw(_("Self Leave Approvl Will Not Accept"))
    
