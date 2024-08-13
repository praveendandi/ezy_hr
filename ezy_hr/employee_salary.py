import frappe

@frappe.whitelist()
def get_user_employee_id(data):
   try:
       resutl = frappe.db.get_list('User Permission',  fields= ['for_value'],
                   filters= {
                       'user': frappe.session.user,
                       'allow': "Employee"
                   },
                   ignore_permissions = True
               )
       
       return resutl
   except Exception as e:
       frappe.log_error("get_user_employee_id",str(e))
       
       