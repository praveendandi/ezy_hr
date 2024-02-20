import frappe
from frappe.utils import cstr
from hrms.payroll.report.salary_register.salary_register import execute as execute_
from calendar import monthrange
from datetime import date, datetime
import pandas as pd
import numpy as np
import sys
import traceback


@frappe.whitelist()
def get_monthly_excel_report():

    year = 2023
    month = 1
    begin = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])
   
    site_name = cstr(frappe.local.site)
    folder_path = frappe.utils.get_bench_path()
    
    path = (
        folder_path
        + "/sites/"
        + site_name
    )
    file_name = "/private/files/Groupby_Salary_Summary_DEC.xlsx"
    file_path = path+file_name
    company = frappe.defaults.get_user_default("Company")
    filters = {
       "from_date":"2024-01-01",
        "to_date":"2024-01-31",
        "currency":"INR",
        "company":company,
        "docstatus":"Submitted"
    }
    
    write_excel(filters,file_path,company)
    
def write_excel(filters,filename,company):
    try:
        address = company_address(company)
        join_detail = joining_details(company)
        exit_details =resignee_details(company)
        salary_slip=salary_slip_details(filters)
        cost_details = cost_report_details(filters)
        designation_detail= groupby_designation_details(filters)
        individual_desig_detail = individual_designation_details(filters)
        department_details = groupby_department_details(filters)
        individual_dep_detail = individual_department_details(filters)
        cost_center_summ = cost_center_wise_cost_summary(filters)
        cost_center_details = cost_center_wise_report(filters)
        
        with pd.ExcelWriter(filename, engine='xlsxwriter', mode='w') as writer:
            
            
            workBook = writer.book
            header_format_other = workBook.add_format({
                'bold': True,            # Bold text
                'text_wrap': True,       # Wrap text
                'valign': 'vcenter',     # Vertical centering
                'align': 'left',         # Left-align text
                'border': 1,
                'fg_color': '#D7E4BC',
            })
            # Head count
            join_detail.to_excel(writer, sheet_name="Head Count",startrow=8,index=False)
            
            worksheet = writer.sheets['Head Count']
            header_format = workBook.add_format({
                            'bold': True,
                            # 'text_wrap': True,
                            # 'valign': 'top',
                            'valign': 'vcenter',
                            'fg_color': '#D7E4BC',
                            'border': 1,
                            'align': 'center',
                            }
                        )

            # worksheet.set_row(0, 30)
            # worksheet.write('A1', 'Header 1', header_format)
            worksheet.write(f"B8","New Joining Details",header_format)
            # Write the column headers with the defined format.
            for col_num, value in enumerate(join_detail.columns.values):
                column_width = max(join_detail[value].astype(str).map(len).max(), len(value))+2
                worksheet.set_column(col_num, col_num, column_width)
                worksheet.write(8, col_num, value, header_format)
                
            worksheet.write('B1', company,header_format)
            worksheet.write('B2', address,header_format)
            worksheet.write('B3', "Head Count Report For JUN 2023",header_format)
        
            exit_details.to_excel(writer, sheet_name="Head Count",startrow=(8+len(join_detail)+3),index=False)

            # Write the column headers with the defined format.
            num_rows, num_cols = join_detail.shape
            for col_num, value in enumerate(exit_details.columns.values):
                worksheet.write((8+num_rows+3), col_num, value, header_format)
            
            worksheet.write(f"B{(8+num_rows+3)}","Resignee Details",header_format)
            
            # prs details
            salary_slip.to_excel(writer, sheet_name="PRS JUN 2023",startrow=0,index=False)
            worksheet = writer.sheets['PRS JUN 2023']
            for col_num, value in enumerate(salary_slip.columns.values):
                column_width = max(salary_slip[value].astype(str).map(len).max(), len(value))+2
                worksheet.set_column(col_num, col_num, column_width)
                worksheet.write(0, col_num, value, header_format)
            
            cost_details.to_excel(writer, sheet_name="Cost Report JUN 2023",startrow=0,index=False)
            
            # cost report
            worksheet = writer.sheets['Cost Report JUN 2023']
            for col_num, value in enumerate(cost_details.columns.values):
                column_width = max(cost_details[value].astype(str).map(len).max(), len(value))+2
                worksheet.set_column(col_num, col_num, column_width)
                worksheet.write(0, col_num, value, header_format)

            # function wise cost summary
            designation_detail.to_excel(writer, sheet_name="Function wise cost summary",startrow=0,index=False)
            worksheet = writer.sheets['Function wise cost summary']
            for col_num, value in enumerate(designation_detail.columns.values):
                column_width = max(designation_detail[value].astype(str).map(len).max(), len(value))+2
                worksheet.set_column(col_num, col_num, column_width)
                worksheet.write(0, col_num, value, header_format)
            
            # Function wise report
            previous_df = 0
            is_first_dataframe = True
            for each in individual_desig_detail:
                
                emp = employee_details(each)
                dataframe = pd.DataFrame.from_records(each)
                filters_df = dataframe.loc[:,"company":"net_pay"]
            
                filters_df['salary_slip_id'] = dataframe['salary_slip_id']
                
                final = pd.concat([emp,filters_df],join="inner",axis=1)
                del final['salary_slip_id']
                
                num_rows, num_cols = final.shape
                
                final.columns = final.columns.str.replace("_"," ")
                final.columns = final.columns.str.title()
                
                startrow = 0 + previous_df
                if is_first_dataframe:
                    final.to_excel(writer, sheet_name="Function wise report",startrow=0,index=False)
                    is_first_dataframe = False
                else:
                    final.to_excel(writer, sheet_name="Function wise report",startrow=startrow,header=False,index=False)

                previous_df+= num_rows + 2
                
                # desig = list(final['Department'])[0]
                worksheet = writer.sheets['Function wise report']
                # worksheet.write("A2",desig,header_format)
                
                for col_num, value in enumerate(final.columns.values):
                    column_width = max(final[value].astype(str).map(len).max(), len(value))+2
                    worksheet.set_column(col_num, col_num, column_width)
                    worksheet.write(0, col_num, value, header_format)

            # Dept Wise Cost Summary
            department_details.to_excel(writer, sheet_name="Dept Wise Cost Summary",startrow=0,index=False)
            
            worksheet = writer.sheets['Dept Wise Cost Summary']
            for col_num, value in enumerate(department_details.columns.values):
                column_width = max(department_details[value].astype(str).map(len).max(), len(value))+2
                worksheet.set_column(col_num, col_num, column_width)
                worksheet.write(0, col_num, value, header_format)
            
            # Dept wise Report
            previous_df = 0
            is_first_dataframe = True
            for each in individual_dep_detail:
                
                emp = employee_details(each)
                dataframe = pd.DataFrame.from_records(each)
                filters_df = dataframe.loc[:,"company":"net_pay"]
            
                filters_df['salary_slip_id'] = dataframe['salary_slip_id']
                
                final = pd.concat([emp,filters_df],join="inner",axis=1)
                del final['salary_slip_id']
                
                num_rows, num_cols = final.shape
                
                final.columns = final.columns.str.replace("_"," ")
                final.columns = final.columns.str.title()
                startrow = 0 + previous_df
                
                if is_first_dataframe:
                    final.to_excel(writer, sheet_name="Dept wise Report",startrow=0,index=False)
                    is_first_dataframe = False
                else:
                    final.to_excel(writer, sheet_name="Dept wise Report",startrow=startrow,header=False,index=False)
                    
                previous_df+= num_rows+2
                
                worksheet = writer.sheets['Dept wise Report']
                for col_num, value in enumerate(final.columns.values):
                    column_width = max(final[value].astype(str).map(len).max(), len(value))+2
                    worksheet.set_column(col_num, col_num, column_width)
                    worksheet.write(0, col_num, value, header_format)
            
            # Cost Center wise cost summary
            cost_center_summ.to_excel(writer, sheet_name="Cost Center wise cost summary",startrow=0,index=False)
    
            worksheet = writer.sheets['Cost Center wise cost summary']
            for col_num, value in enumerate(cost_center_summ.columns.values):
                column_width = max(cost_center_summ[value].astype(str).map(len).max(), len(value))+2
                worksheet.set_column(col_num, col_num, column_width)
                worksheet.write(0, col_num, value, header_format)

            # Cost Center Report
            previous_df = 0
            is_first_dataframe = True
            
            for each_cost in cost_center_details:
                
                dataframe = pd.DataFrame.from_records(each_cost)
                dataframe.columns = dataframe.columns.str.replace("_"," ")
                dataframe.columns = dataframe.columns.str.title()
                
                startrow = 0 + previous_df
                num_rows, num_cols = dataframe.shape
                
                if is_first_dataframe:
                    dataframe.to_excel(writer, sheet_name="Cost Center wise Report",startrow=0,index=False)
                    is_first_dataframe = False
                else:
                    dataframe.to_excel(writer, sheet_name="Cost Center wise Report",startrow=startrow,header=False,index=False)
                
                previous_df+= num_rows+2
                
                worksheet = writer.sheets['Cost Center wise Report']
                
                for col_num, value in enumerate(dataframe.columns.values):
                    column_width = max(dataframe[value].astype(str).map(len).max(), len(value))+2
                    worksheet.set_column(col_num, col_num, column_width)
                    worksheet.write(0, col_num, value, header_format)


            # workBook.save(filename)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "write_excel")  
                

def salary_slip_details(filters):
    
    row_data = execute_(filters)

    if len(row_data[1]) >0:
        
        final_employee_details = employee_details(row_data[1])
        
        dataframe = pd.DataFrame.from_records(row_data[1])
        
        filters_df = dataframe.loc[:,"company":"net_pay"]
        
        filters_df['salary_slip_id'] = dataframe['salary_slip_id']
        
        final = pd.concat([final_employee_details,filters_df],join="inner",axis=1)
        del final['salary_slip_id']
        
        final.columns = final.columns.str.replace("_"," ")
        final.columns = final.columns.str.title()
        
        return final
    
def cost_report_details(filters):
    
    row_data = execute_(filters)
     
    if len(row_data[1]) >0:
        
        final_employee_details = employee_details(row_data[1])
        
        empl_colunms = list(final_employee_details.columns)
        
        empl_colunms.remove("salary_slip_id")
          
        dataframe = pd.DataFrame.from_records(row_data[1])
        
        filters_df = dataframe.loc[:,"company":"net_pay"]
        
        colunms = list(filters_df.columns)
        
        colunms.remove("company")
        colunms.remove("start_date")
        colunms.remove("end_date")
        colunms.remove("currency")
        
        # data type columns
        empl_colunms.extend(["company","start_date","end_date","currency"])
        
        filters_df['salary_slip_id'] = dataframe['salary_slip_id']
        
        agg_functions = {}
        for each_cat in empl_colunms:
            agg_functions.update({each_cat:"first","employee_number":"count"})
        
        for each_num in colunms:
            agg_functions.update({
                each_num:"sum"
            })
                
        final = pd.concat([final_employee_details,filters_df],join="inner",axis=1)
        
        del final['salary_slip_id']
        
        result = final.groupby(by=['company'],as_index=False).agg(agg_functions)
        
        result[empl_colunms].fillna(value=np.nan, inplace=True)
        # empl_colunms.remove("cost_center")
        # empl_colunms.remove("employee_number")
        
        # result.drop(columns=empl_colunms, inplace=True)
        result.rename(columns={
            "employee_number":"employee_count"
        },inplace=True)
        
        result.columns = result.columns.str.replace("_"," ")
        result.columns = result.columns.str.title()
       
        return result
    
    

def groupby_designation_details(filters):
    
    row_data = execute_(filters)
    
    if len(row_data[1]) >0:
        dataframe = pd.DataFrame.from_records(row_data[1])
        
        first_data = dataframe.loc[:,"employee":"company"]
        get_first_col = list(first_data.columns)
      
        filters_df = dataframe.loc[:,"company":"net_pay"]
        get_second_col = list(filters_df.columns)
       
        get_second_col.remove("company")
        get_second_col.remove("start_date")
        get_second_col.remove("end_date")
        get_second_col.remove("currency")
        
        get_first_col.extend(['start_date',"end_date","currency"])
        
        agg_functions = {}
        for each_cat in get_first_col:
            agg_functions.update({each_cat:"first","employee":"count"})
        
        for each_num in get_second_col:
            agg_functions.update({
                each_num:"sum"
            })
            
        group_data = dataframe.groupby(by=["designation"],as_index=False).agg(agg_functions)
        get_first_col.remove("designation")
        get_first_col.remove("employee")
        group_data.drop(columns=get_first_col, inplace=True)
        
        group_data.rename(columns={
            "employee":"employee_count"
        },inplace=True)
        
        group_data.columns = group_data.columns.str.replace("_"," ")
        group_data.columns = group_data.columns.str.title()
        
        return group_data

def individual_designation_details(filters):
    
    row_data = execute_(filters)
    
    if len(row_data[1]) >0:
        
        inital_data = {}
        
        for each in row_data[1]:
            designation_value = each.get("designation") if each.get("designation") else "Other"
  
            if designation_value not in inital_data:
                inital_data[designation_value]={
                    'designation':[]
                }
            each.update({
                "designation":designation_value
            })
            inital_data[designation_value]['designation'].append(each)
            
        final_data  = inital_data.values()
        second_final_data = []
        
        for i in final_data:
            k = list(i.values())
            second_final_data += k
        
        return second_final_data

def groupby_department_details(filters):
    
    row_data = execute_(filters)
    
    if len(row_data[1]) >0:
        dataframe = pd.DataFrame.from_records(row_data[1])
        
        first_data = dataframe.loc[:,"employee":"company"]
        get_first_col = list(first_data.columns)
      
        filters_df = dataframe.loc[:,"company":"net_pay"]
        get_second_col = list(filters_df.columns)
       
        get_second_col.remove("company")
        get_second_col.remove("start_date")
        get_second_col.remove("end_date")
        get_second_col.remove("currency")
        
        get_first_col.extend(['start_date',"end_date","currency"])
        
        agg_functions = {}
        for each_cat in get_first_col:
            agg_functions.update({each_cat:"first","employee":"count"})
        
        for each_num in get_second_col:
            agg_functions.update({
                each_num:"sum"
            })
            
        group_data = dataframe.groupby(by=["department"],as_index=False).agg(agg_functions)
        get_first_col.remove("department")
        get_first_col.remove("employee")
        group_data.drop(columns=get_first_col, inplace=True)
        
        group_data.rename(columns={
            "employee":"employee_count"
        },inplace=True)
        
        group_data.columns = group_data.columns.str.replace("_"," ")
        group_data.columns = group_data.columns.str.title()
        
        return group_data

def individual_department_details(filters):
   
    row_data = execute_(filters)
    
    if len(row_data[1]) >0:
        inital_data = {}
        for each in row_data[1]:
            department_value = each.get("department") if each.get("department") else "Other"
            
            if department_value not in inital_data:
                inital_data[department_value]={
                    'department':[]
                }
            each.update({
                "department":department_value
            })
            inital_data[department_value]['department'].append(each)
            
        final_data  = inital_data.values()
        second_final_data = []
        
        for i in final_data:
            k = list(i.values())
            second_final_data += k
        
        return second_final_data

def cost_center_wise_cost_summary(filters):
    
    row_data = execute_(filters)
     
    if len(row_data[1]) >0:
        
        final_employee_details = employee_details(row_data[1])
        
        empl_colunms = list(final_employee_details.columns)
        
        empl_colunms.remove("salary_slip_id")
          
        dataframe = pd.DataFrame.from_records(row_data[1])
        
        filters_df = dataframe.loc[:,"company":"net_pay"]
        
        colunms = list(filters_df.columns)
        
        colunms.remove("company")
        colunms.remove("start_date")
        colunms.remove("end_date")
        colunms.remove("currency")
        
        # data type columns
        empl_colunms.extend(["company","start_date","end_date","currency"])
        
        filters_df['salary_slip_id'] = dataframe['salary_slip_id']
        
        agg_functions = {}
        for each_cat in empl_colunms:
            agg_functions.update({each_cat:"first","employee_number":"count"})
        
        for each_num in colunms:
            agg_functions.update({
                each_num:"sum"
            })
                
        final = pd.concat([final_employee_details,filters_df],join="inner",axis=1)
        
        del final['salary_slip_id']
        
        result = final.groupby(by=['cost_center'],as_index=False).agg(agg_functions)
        
        empl_colunms.remove("cost_center")
        empl_colunms.remove("employee_number")
        
        result.drop(columns=empl_colunms, inplace=True)
        result.rename(columns={
            "employee_number":"employee_count"
        },inplace=True)
        
        result.columns = result.columns.str.replace("_"," ")
        result.columns = result.columns.str.title()
       
        return result
    

def cost_center_wise_report(filters):
    
    row_data = execute_(filters)
     
    if len(row_data[1]) >0:
        
        final_employee_details = employee_details(row_data[1])
        
        dataframe = pd.DataFrame.from_records(row_data[1])
        
        filters_df = dataframe.loc[:,"company":"net_pay"]
        
        filters_df['salary_slip_id'] = dataframe['salary_slip_id']
                
        final = pd.concat([final_employee_details,filters_df],join="inner",axis=1)
        
        del final['salary_slip_id']
  
        row_data_ = final.to_dict("records")
  
        inital_data = {}
        for each in row_data_:
            cost_center = each.get("cost_center") if each.get("cost_center") else "Other"
            
            if cost_center not in inital_data:
                inital_data[cost_center]={
                    'cost_center':[]
                }
            each.update({
                "cost_center":cost_center
            })
            inital_data[cost_center]['cost_center'].append(each)
            
        final_data  = inital_data.values()
        second_final_data = []
        
        for i in final_data:
            k = list(i.values())
            second_final_data.extend(k)
       
        return second_final_data

def company_address(company):
    
    get_address = frappe.db.sql(
        """
        SELECT ad.address_line1,ad.address_line2,ad.city,ad.state,pincode
        FROM 
        `tabAddress` as ad,
        `tabDynamic Link` as dl
        WHERE 
        dl.link_doctype= "Company" AND dl.link_name = %s
        """,(company)
    )
    
    completed_add = ",".join(get_address[0])
    
    return completed_add

def joining_details(company):
    
    row_data = frappe.db.sql(
        """
        SELECT employee as employee_number,employee_name,date_of_joining,gender,branch,
        department,designation,payroll_cost_center as cost_centre
        FROM `tabEmployee`
        WHERE date_of_joining BETWEEN "2024-01-01" AND "2024-01-31"
        AND company = %s
        """,(company),as_dict=True
    )
    
    df = pd.DataFrame.from_records(row_data)
    
    df.rename(columns={
        "employee_number":"Employee Number",
        "employee_name":"Employee Name",
        "date_of_joining":"Date Of Joining",
        "gender":"Gender",
        "branch":"Location",
        "department":"Department",
        "designation":"Designation",
        "cost_centre":"Cost Centre"
    },inplace=True)
    
    return df


def resignee_details(company):
    
    row_data = frappe.db.sql(
        """
        SELECT employee as employee_number,employee_name,relieving_date as exit_date,
        gender,branch,designation,department,payroll_cost_center as cost_centre
        FROM `tabEmployee`
        WHERE relieving_date BETWEEN "2024-01-01" AND "2024-01-31"
        AND company = %s
        """,(company),as_dict=True
    )
    
    df = pd.DataFrame.from_records(row_data)
    
    df.rename(columns={
        "employee_number":"Employee Number",
        "employee_name":"Employee Name",
        "exit_date":"Exit Date",
        "gender":"Gender",
        "branch":"Location",
        "department":"Department",
        "designation":"Designation",
        "cost_centre":"Cost Centre"
    },inplace=True)
    
    return df

def employee_details(row_data):
    
    employee_data  = []
    
    for each in row_data:
        inital = {}
        employee_details = frappe.db.sql(
            """
            SELECT date_of_birth,employment_type,default_shift,pan_number,provident_fund_account,salary_mode,
            bank_name,bank_ac_no,ifsc_code,gender,payroll_cost_center
            FROM `tabEmployee`
            WHERE employee = %s
            """,
            (each['employee']),
            as_dict=True    
        )
        if len(employee_details)>0:
            inital.update({
                "salary_slip_id":each['salary_slip_id'],
                "employee_number":each['employee'],
                "employee_name":each['employee_name'],
                "data_of_joining":each['data_of_joining'],
                "gender":employee_details[0].get("gender",None),
                "date_of_birth":employee_details[0].get("date_of_birth",None),
                "pan_number":employee_details[0].get("pan_number",None),
                "worker_type":employee_details[0].get("employment_type",None),
                "time_type":employee_details[0].get("default_shift",None),
                "designation":each.get('designation',None),
                "department":each.get('department',None),
                "location":each.get("branch",None),
                "bank_name":employee_details[0].get("bank_name",None),
                "bank_account_no":employee_details[0].get("bank_ac_no",None),
                "salary_payment_mode":employee_details[0].get("salary_mode",None),
                "ifsc_code":employee_details[0].get("ifsc_code",None),
                "pf_number":employee_details[0].get("pf_number",None),
                "provident_fund_account":employee_details[0].get("provident_fund_account",None),
                "cost_center":employee_details[0].get("payroll_cost_center",None)
            })
            inital.update({
                    
            })
            
            employee_data.append(inital)

    df_employee = pd.DataFrame.from_records(employee_data)
    
    return df_employee