import frappe
@frappe.whitelist()
def my_profile():
   try:
       team_list = []
       user = frappe.session.user

       user_list = frappe.db.get_list("Employee",filters={'user_id':user},
                                       fields=["employee_name",'user_id','department']
                                       )
       if user == 'Administrator':
           my_team_data = frappe.db.get_all("Employee",['employee','employee_name','department',"designation",'cell_number',"date_of_joining","prefered_email","date_of_birth","gender","emergency_phone_number","image"])
           for i in my_team_data:
               team_list.append(i)
       else :
           user_department = user_list[0]['department']

           my_team_data = frappe.get_all( "Employee",fields=['employee', 'employee_name', 'department' ,"designation",'cell_number',"prefered_email", 'date_of_joining', 'date_of_birth', 'gender', 'emergency_phone_number', 'image'],
                                    filters={'user_id':user})
           for i in my_team_data:
               if user_department == i['department']:
                   team_list.append(i)
                   user_photo = frappe.db.get_all("File",filters={"attached_to_name":i.employee},fields=["file_url"])
       return team_list

   except Exception as e:
       frappe.log_error(str(e))


import frappe
@frappe.whitelist()
def my_team():
    try:
        team_list = []
        user = frappe.session.user
        # print(user)
        if user == 'Administrator':
            my_team_data = frappe.get_all("Employee", fields=['employee', 'employee_name', "designation",'department', 'cell_number', 
                                                                "date_of_joining", "prefered_email", "date_of_birth", 
                                                                "gender", "emergency_phone_number", "image"])
            for i in my_team_data:
                team_list.append(i)
           
            return team_list
        user_employee = frappe.db.get_value("Employee", {'user_id': user}, ['name', 'department'])
        if user_employee:
            employee_id, user_department = user_employee

            my_team_data = frappe.get_all("Employee", fields=['employee', 'employee_name', "designation",'department', 'cell_number', 
                                                                "prefered_email", 'date_of_joining', 'date_of_birth', 
                                                                'gender', 'emergency_phone_number', 'image'],
                                            filters={'reports_to': employee_id})
            # print(my_team_data,"-----------------------------")

        for employee in my_team_data:
            
            team_list.append(employee)
            
        return team_list
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in fetching team")
        return []




import frappe
@frappe.whitelist()
def user_manual():
    try:
        team_list = []

        my_team_data = frappe.get_all("User Manual Data", fields=['user_manual_name', 'attachment', "video","name"])
        for i in my_team_data:
            team_list.append(i)    
        return team_list
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in fetching team")
        return []
