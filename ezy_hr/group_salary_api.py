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
def get_monthly_excel_report(month,year):
    try:
        year_value = int(year)
        month_num = datetime.strptime(month, '%b').month
        from_date = date(year_value, month_num, 1)
        to_date = date(year_value, month_num, monthrange(year_value, month_num)[1])
    
        site_name = cstr(frappe.local.site)
        folder_path = frappe.utils.get_bench_path()
        
        path = (
            folder_path
            + "/sites/"
            + site_name
        )
        file_path_ = f"/files/Groupby_Salary_Summary_{month}-{year_value}.xlsx"
        file_name = f"/public{file_path_}"
        file_path = path+file_name
        company = frappe.defaults.get_user_default("Company")
        
        filters = {
            "from_date":from_date,
            "to_date":to_date,
            "currency":"INR",
            "company":company,
            "docstatus":"Submitted"
        }
        
        result = write_excel(filters,file_path,company,month,year_value)
        
        if result:
            return {"message":True,"file_name":file_path_}
        else:
            return {"message":False,"file_name":file_path_}
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "write_excel")
    
def write_excel(filters,filename,company,month,year):
    try:
        address = company_address(company)
        join_detail = joining_details(company,filters)
        exit_details =resignee_details(company,filters)
        salary_slip=salary_slip_details(filters)
        cost_details = cost_report_details(filters)
        designation_detail= designation_wise_summary(filters)
        individual_desig_detail = designation_wise_report(filters)
        department_details = department_wise_summary(filters)
        individual_dep_detail = department_wise_report(filters)
        cost_center_summ = cost_center_wise_cost_summary(filters)
        cost_center_details = cost_center_wise_report(filters)
        
        total_employee = frappe.db.count("Employee",{"status":"Active","date_of_joining":("<",(filters.get("from_date").strftime('%Y-%m-%d')))})
        salary_title = f"{company} > Salary Statement for the month of {month} {year} | Currency : INR"
        
        with pd.ExcelWriter(filename, engine='xlsxwriter', mode='w') as writer:
            workBook = writer.book
            merge_format_comp = workBook.add_format({'align': 'center', 'valign': 'vcenter','bold': True,'fg_color': '#FFFFFF'})
            merge_format_join_ext_title = workBook.add_format({'align': 'center',  'border': 1,'valign': 'vcenter','bold': True,'fg_color': '#FFFFFF'})
            merge_format_dep_deg = workBook.add_format({'align': 'left','valign': 'vcenter','border': 1,'bold': True,'fg_color': '#CACACD'})


            header_format_other = workBook.add_format({
                # 'bold': True,            # Bold text
                'text_wrap': True,       # Wrap text
                'valign': 'vcenter',     # Vertical centering
                'align': 'center',         # Left-align text
                # 'border': 1,
                'fg_color': '#FFFFFF', # white color
            })
            header_format = workBook.add_format({
                            'bold': True,
                            # 'text_wrap': True,
                            # 'valign': 'top',
                            'valign': 'vcenter',
                            'fg_color': '#CACACD',
                            'border': 1,
                            'align': 'center',
                        }
            )
            
            # Head count
            join_detail.to_excel(writer, sheet_name="Head Count",startrow=13,index=False)
            exit_details.to_excel(writer, sheet_name="Head Count",startrow=(13+len(join_detail)+3),index=False)

            num_rows, num_cols = join_detail.shape
            
            worksheet_1 = writer.sheets['Head Count']
            worksheet_1.merge_range(0,num_cols-1,0,0, company, merge_format_comp)
            worksheet_1.merge_range(1,num_cols-1,1,0, address, header_format_other)
            worksheet_1.merge_range(2,num_cols-1,2,0, f"Head Count Report For {month} {year}", merge_format_comp)
            # Opening balance And
            worksheet_1.write(3, 0, None,header_format)
            worksheet_1.merge_range(3,num_cols-2,3,1,f"Opening Balance For {month} {year}",header_format)
            worksheet_1.write(3, num_cols-1, total_employee,header_format)
            # Add New Joining
            new_join_num = num_rows
            worksheet_1.write(5, 0, 'Add')
            worksheet_1.merge_range(5,num_cols-2,5,1,f"New Joinee")
            worksheet_1.write(5, num_cols-1, new_join_num)
           # white space
            worksheet_1.write(6, 0, None)
            worksheet_1.merge_range(6,num_cols-1,6,1, None)
            worksheet_1.write(6, num_cols-1, None)
            # Resigness 
            num_ex_row = exit_details.shape[0]
            worksheet_1.write(7, 0, 'Less')
            worksheet_1.merge_range(7,num_cols-2,7,1,f"Resignee")
            worksheet_1.write(7, num_cols-1, num_ex_row)
            # White space
            worksheet_1.write(8, 0, None)
            worksheet_1.merge_range(8,num_cols-1,8,1, None)
            worksheet_1.write(8, num_cols-1, None)
            # Closing balance
            closing_bala = total_employee+(new_join_num-num_ex_row)
            worksheet_1.merge_range(9,num_cols-2,9,1,f"Closing Balance For - {month} {year}")
            worksheet_1.write(9, num_cols-1, closing_bala)

            worksheet_1.set_row(13,30) # set row height
            worksheet_1.merge_range(12,num_cols-1,12,0, "New Joining Details", merge_format_join_ext_title)
                
            for col_num, value in enumerate(join_detail.columns.values):
                # Adjust the multiplier (e.g., 1.5) based on your preference for column width
                worksheet_1.set_column(col_num, col_num, len(value) * 1.5)
                worksheet_1.write(13, col_num, value, header_format)
        
            exit_details.to_excel(writer, sheet_name="Head Count",startrow=(13+len(join_detail)+3),index=False)
            worksheet_1.set_row((13+len(join_detail)+3),30)

            # Write the column headers with the defined format.
            for col_num, value in enumerate(exit_details.columns.values):
                worksheet_1.write((13+num_rows+3), col_num,value, header_format)
            
            worksheet_1.merge_range((13+num_rows+2),num_cols-1,(13+num_rows+2),0, "Resignee Details", merge_format_join_ext_title)
            
            # prs details
            salary_slip.to_excel(writer, sheet_name=f"PRS {month} {year}",startrow=1,index=False)
            worksheet_2 = writer.sheets[f'PRS {month} {year}']
            worksheet_2.set_row(1,30)
            worksheet_2.merge_range(0,salary_slip.shape[1],0,0, salary_title)
            
            for col_num, value in enumerate(salary_slip.columns.values):
                column_width = max(salary_slip[value].astype(str).map(len).max(), len(value))+2
                worksheet_2.set_column(col_num, col_num, column_width)
                worksheet_2.write(1, col_num, value, header_format)
               
            
            # cost report
            cost_details.to_excel(writer, sheet_name=f"Cost Report {month} {year}",startrow=1,index=False)
            worksheet_3 = writer.sheets[f'Cost Report {month} {year}']
            worksheet_3.set_row(1,30)
            worksheet_3.merge_range(0,cost_details.shape[1],0,0, salary_title)
            for col_num, value in enumerate(cost_details.columns.values):
                column_width = max(cost_details[value].astype(str).map(len).max(), len(value))+2
                worksheet_3.set_column(col_num, col_num, column_width)
                worksheet_3.write(1, col_num, value, header_format)
            # function wise cost summary
            designation_detail.to_excel(writer, sheet_name="Function wise cost summary",startrow=1,index=False)
            worksheet_4 = writer.sheets['Function wise cost summary']
            worksheet_4.set_row(1,30)
            worksheet_4.merge_range(0,designation_detail.shape[1],0,0, salary_title)
            for col_num, value in enumerate(designation_detail.columns.values):
                column_width = max(designation_detail[value].astype(str).map(len).max(), len(value))+2
                worksheet_4.set_column(col_num, col_num, column_width)
                worksheet_4.write(1, col_num, value, header_format)
            
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
                
                startrow = 1 + previous_df
                if is_first_dataframe:
                    final.to_excel(writer, sheet_name="Function wise report",startrow=1,index=False)
                    worksheet_5 = writer.sheets['Function wise report']
                    desig = list(final['Designation'])[0]
                    worksheet_5.set_row(1,30)
                    worksheet_5.merge_range(0,num_cols-1,0,0, salary_title)
                    worksheet_5.merge_range(2,num_cols-1,2,0, desig,merge_format_dep_deg)
                    
                    is_first_dataframe = False
                    previous_df+= 4+num_rows
                else:
                    final.to_excel(writer, sheet_name="Function wise report",startrow=startrow,header=False,index=False)
                    worksheet_5 = writer.sheets['Function wise report']
                    desig = list(final['Designation'])[0]
                    worksheet_5.merge_range(startrow-1,num_cols-1,startrow-1,0, desig,merge_format_dep_deg)
                    previous_df+= num_rows+3
                
                for col_num, value in enumerate(final.columns.values):
                    column_width = max(final[value].astype(str).map(len).max(), len(value))+2
                    worksheet_5.set_column(col_num, col_num, column_width)
                    worksheet_5.write(1, col_num, value, header_format)

            # Dept Wise Cost Summary
            department_details.to_excel(writer, sheet_name="Dept Wise Cost Summary",startrow=1,index=False)
            worksheet_6 = writer.sheets['Dept Wise Cost Summary']
            worksheet_6.set_row(1,30)
            worksheet_6.merge_range(0,department_details.shape[1],0,0, salary_title)
            for col_num, value in enumerate(department_details.columns.values):
                column_width = max(department_details[value].astype(str).map(len).max(), len(value))+2
                worksheet_6.set_column(col_num, col_num, column_width)
                worksheet_6.write(1, col_num, value, header_format)
            
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
                startrow = 1 + previous_df
                
                if is_first_dataframe:
                    final.to_excel(writer, sheet_name="Dept wise Report",startrow=1,index=False)
                    worksheet_7 = writer.sheets['Dept wise Report']
                    dep = list(final['Department'])[0]
                    worksheet_7.set_row(1,30)
                    worksheet_7.merge_range(0,num_cols-1,0,0, salary_title)
                    worksheet_7.merge_range(2,num_cols-1,2,0, dep,merge_format_dep_deg)
                    
                    is_first_dataframe = False
                    previous_df+= 4+num_rows
                else:
                    final.to_excel(writer, sheet_name="Dept wise Report",startrow=startrow,header=False,index=False)
                    worksheet_7 = writer.sheets['Dept wise Report']
                    dep = list(final['Department'])[0]
                    worksheet_7.merge_range(startrow-1,num_cols-1,startrow-1,0, dep,merge_format_dep_deg)
                    previous_df+= num_rows+3
                
                for col_num, value in enumerate(final.columns.values):
                    column_width = max(final[value].astype(str).map(len).max(), len(value))+2
                    worksheet_7.set_column(col_num, col_num, column_width)
                    worksheet_7.write(1, col_num, value, header_format)
            
            # Cost Center wise cost summary
            cost_center_summ.to_excel(writer, sheet_name="Cost Center wise cost summary",startrow=1,index=False)
    
            worksheet_8 = writer.sheets['Cost Center wise cost summary']
            worksheet_8.set_row(1,30)
            worksheet_8.merge_range(0,cost_center_summ.shape[1],0,0, salary_title)
            for col_num, value in enumerate(cost_center_summ.columns.values):
                column_width = max(cost_center_summ[value].astype(str).map(len).max(), len(value))+2
                worksheet_8.set_column(col_num, col_num, column_width)
                worksheet_8.write(1, col_num, value, header_format)

            # Cost Center Report
            previous_df = 0
            is_first_dataframe = True
            
            for each_cost in cost_center_details:
                
                dataframe = pd.DataFrame.from_records(each_cost)
                dataframe.columns = dataframe.columns.str.replace("_"," ")
                dataframe.columns = dataframe.columns.str.title()
                
                startrow = 1 + previous_df
                num_rows, num_cols = dataframe.shape
                
                if is_first_dataframe:
                    dataframe.to_excel(writer, sheet_name="Cost Center wise Report",startrow=1,index=False)
                    worksheet_9 = writer.sheets['Cost Center wise Report']
                    cost = list(final['Cost Center'])[0]
                    worksheet_9.set_row(1,30)
                    worksheet_9.merge_range(0,num_cols-1,0,0, salary_title)
                    worksheet_9.merge_range(2,num_cols-1,2,0, cost,merge_format_dep_deg)
                    
                    is_first_dataframe = False
                    previous_df+= 4+num_rows
                else:
                    dataframe.to_excel(writer, sheet_name="Cost Center wise Report",startrow=startrow,header=False,index=False)
                    worksheet_9 = writer.sheets['Cost Center wise Report']
                    cost = list(final['Cost Center'])[0]
                    worksheet_9.merge_range(startrow-1,num_cols-1,startrow-1,0, cost,merge_format_dep_deg)
                    previous_df+= num_rows+3
                    
                for col_num, value in enumerate(dataframe.columns.values):
                    column_width = max(dataframe[value].astype(str).map(len).max(), len(value))+2
                    worksheet_9.set_column(col_num, col_num, column_width)
                    worksheet_9.write(1, col_num, value, header_format)
                    
        return True
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "write_excel")
        return False
                
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
        
        result.rename(columns={
            "employee_number":"employee_count"
        },inplace=True)
        
        result.columns = result.columns.str.replace("_"," ")
        result.columns = result.columns.str.title()
       
        return result
    
def designation_wise_summary(filters):
    
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
        
        # chnage position of column
        column_to_move = "employee_count"
        column_after_which_to_insert = 'designation'
        df_copy = group_data.copy()
        df_copy.drop(columns=column_to_move, inplace=True)
        insert_index = df_copy.columns.get_loc(column_after_which_to_insert) + 1
        df_copy.insert(insert_index, column_to_move, group_data[column_to_move])
        
        df_copy.columns = df_copy.columns.str.replace("_"," ")
        df_copy.columns = df_copy.columns.str.title()
        
        return df_copy

def designation_wise_report(filters):
    
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

def department_wise_summary(filters):
    
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
        
        column_to_move = "employee_count"
        column_after_which_to_insert = 'department'
        df_copy = group_data.copy()
        df_copy.drop(columns=column_to_move, inplace=True)
        insert_index = df_copy.columns.get_loc(column_after_which_to_insert) + 1
        df_copy.insert(insert_index, column_to_move, group_data[column_to_move])
        
        df_copy.columns = df_copy.columns.str.replace("_"," ")
        df_copy.columns = df_copy.columns.str.title()
        
        return df_copy

def department_wise_report(filters):
   
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
        
        column_to_move = "employee_count"
        column_after_which_to_insert = 'cost_center'
        df_copy = result.copy()
        df_copy.drop(columns=column_to_move, inplace=True)
        insert_index = df_copy.columns.get_loc(column_after_which_to_insert) + 1
        df_copy.insert(insert_index, column_to_move, result[column_to_move])
        
        df_copy.columns = df_copy.columns.str.replace("_"," ")
        df_copy.columns = df_copy.columns.str.title()
       
        return df_copy
    

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

def joining_details(company,filters):
   
    row_data = frappe.db.sql(
        """
        SELECT employee as employee_number,employee_name,date_of_joining,gender,branch,
        department,designation,payroll_cost_center as cost_centre
        FROM `tabEmployee`
        WHERE date_of_joining BETWEEN '{}' AND '{}'
        AND company = '{}'
        """.format(filters.get("from_date").strftime('%Y-%m-%d'),filters.get("to_date").strftime('%Y-%m-%d'),company),
        as_dict=True
    )
    
    columns = ["employee_number",
        "employee_name",
        "date_of_joining",
        "gender",
        "branch",
        "department",
        "designation",
        "cost_centre"
    ]
    
    df = pd.DataFrame.from_records(row_data,columns=columns)
    
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


def resignee_details(company,filters):
    
    row_data = frappe.db.sql(
        """
        SELECT employee as employee_number,employee_name,relieving_date as exit_date,
        gender,branch,designation,department,payroll_cost_center as cost_centre
        FROM `tabEmployee`
        WHERE relieving_date BETWEEN '{}' AND '{}'
        AND company = '{}'
        """.format(filters.get("from_date").strftime('%Y-%m-%d'),filters.get("to_date").strftime('%Y-%m-%d'),company),
        as_dict=True
    )
    columns = ["employee_number",
        "employee_name",
        "exit_date",
        "gender",
        "branch",
        "department",
        "designation",
        "cost_centre"
    ]
    df = pd.DataFrame.from_records(row_data,columns=columns)
    
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

