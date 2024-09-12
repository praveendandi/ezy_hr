import frappe
from frappe.utils import cstr
from ezy_hr.ezy_hr.report.hr_mis_report.hr_mis_report import execute as get_hr_mis_report_data
import random
import pandas as pd
import numpy as np

@frappe.whitelist()
def download_all_hr_mis_reports(company, start_date, end_date):
    try:
        report_types = ["Summary Report", "Head Count Working", "New Joinees List", "Left Employees"]

        site_name = cstr(frappe.local.site)
        folder_path = frappe.utils.get_bench_path()
        
        path = (
            folder_path
            + "/sites/"
            + site_name
        )
        random_num = random.randint(1,100)
        file_path_ = f"/files/HR_Mis_Report-{random_num}.xlsx"
        file_name = f"/public{file_path_}"
        file_path = path+file_name

        with pd.ExcelWriter(file_path, engine='xlsxwriter', mode='w') as writer:
            workBook = writer.book
            header_format = workBook.add_format({
                                'bold': True,
                                'text_wrap': True,
                                'valign': 'vcenter',
                                'fg_color': '#CACACD',
                                'border': 1,
                                'align': 'center'
                            }
            )
            for report_type in report_types:
                # Fetch data based on filters
                filters = {}
                filters.update({
                    'company':company,
                    "start_date":start_date,
                    "end_date":end_date,
                    "report_type":report_type
                })
                data = get_hr_mis_report_data(filters)
                if len(data[1])>0:
                    dataframe = pd.DataFrame.from_records(data[1])
                    dataframe.columns = dataframe.columns.str.replace("_"," ")
                    dataframe.columns = dataframe.columns.str.title()
                    dataframe.to_excel(writer, sheet_name=report_type,startrow=0,index=False)
                    worksheet = writer.sheets[report_type]

                    for col_num, value in enumerate(dataframe.columns.values):
                        column_width = max(dataframe[value].astype(str).map(len).max(), len(value))+2
                        worksheet.set_column(col_num, col_num, column_width)
                        worksheet.write(0, col_num, value, header_format)
        
        
        return {"message":True,"file_name":file_path_}
    except Exception as e:
        frappe.log_error(str(e))
