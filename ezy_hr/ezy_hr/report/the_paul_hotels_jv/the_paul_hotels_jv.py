# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

# import frappe


# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe import _
from frappe.utils import flt

import erpnext
import pandas as pd
import numpy as np
from datetime import datetime

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")


def execute(filters=None):
	if not filters:
		filters = {}

	currency = None
	if filters.get("currency"):
		currency = filters.get("currency")
	company_currency = erpnext.get_company_currency(filters.get("company"))

	salary_slips = get_salary_slips(filters, company_currency)
	if not salary_slips:
		return [], []

	earning_types, ded_types = get_earning_and_deduction_types(salary_slips)
	columns = get_columns(earning_types, ded_types,filters)

	ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

	doj_map = get_employee_doj_map()

	data = []
	start_date = None

	for ss in salary_slips:
		start_date = ss.start_date
		row = {
			"salary_slip_id": ss.name,
			"employee": ss.employee,
			"employee_name": ss.employee_name,
			"data_of_joining": doj_map.get(ss.employee),
			"branch": ss.branch,
			"department": ss.department,
			"designation": ss.designation,
			"company": ss.company,
			"start_date": ss.start_date,
			"end_date": ss.end_date,
			"leave_without_pay": ss.leave_without_pay,
			"payment_days": ss.payment_days,
			"currency": currency or company_currency,
			"total_loan_repayment": ss.total_loan_repayment,
			"custom_payroll_cost_center_":ss.custom_payroll_cost_center_,
		}

		update_column_width(ss, columns)

		for e in earning_types:
			row.update({frappe.scrub(e): ss_earning_map.get(ss.name, {}).get(e)})

		for d in ded_types:
			row.update({frappe.scrub(d): ss_ded_map.get(ss.name, {}).get(d)})

		if currency == company_currency:
			row.update(
				{
					"gross_pay": flt(ss.gross_pay) * flt(ss.exchange_rate),
					"total_deduction": flt(ss.total_deduction) * flt(ss.exchange_rate),
					"net_pay": flt(ss.net_pay) * flt(ss.exchange_rate),
				}
			)

		else:
			row.update(
				{"gross_pay": ss.gross_pay, "total_deduction": ss.total_deduction, "net_pay": ss.net_pay}
			)

		data.append(row)


	if not filters.get("each_employee"):

		dataframe = pd.DataFrame.from_records(data)

		filters_df = dataframe.loc[:,"payment_days":"net_pay"].copy()

		filters_df.drop(columns=["payment_days","currency", "total_deduction", "net_pay", "gross_pay", "total_loan_repayment"], inplace=True)

		filters_df.replace(np.nan, 0.0, inplace=True)
		
		result = filters_df.groupby(by="custom_payroll_cost_center_",as_index=True).sum().reset_index()
		result['Basic'] = result['basic'] + result['dearness_allowance']
		del result['basic']
		del result['dearness_allowance']
		melted_result = result.melt(id_vars=["custom_payroll_cost_center_"], var_name="component", value_name="amount")
		
		
		final_data = melted_result.to_dict("records")

		gl_codes = get_gl_code(final_data,filters)

		columns = group_colunms(filters)
		
		return columns, gl_codes
			
	if filters.get("each_employee"): 
		return columns, data

def get_gl_code(final_data,filters):

	all_results = []
	filters_data = final_data.copy()
	gl_code_data = frappe.db.get_list("GL Code Maping", fields=['name'])
	for gl_code in gl_code_data:
		holiday_query = """ 
			SELECT component, gl_code, acc_code, transaction_types, narration, gl_description,account_code
			FROM `tabGL Codes`
			WHERE parent = %s AND parentfield = 'gl_code_table'
		"""
		results = frappe.db.sql(holiday_query, gl_code['name'], as_dict=True)
		all_results.extend(results)

	for each in filters_data:
		map_gl = each.get('component').title().replace("_", " ").strip()
		company = frappe.db.get_value("Company",{"name":filters.get("company")},['abbr'])
		each.update({"company":company})
		if 'Pf Employee' == map_gl:
			each.update({'component': "PF-Employee"})
		elif 'Pf Employer' == map_gl:
			each.update({'component': "PF-Employer"})
		elif 'Esi' == map_gl:
			each.update({'component': "ESI"})
		elif map_gl == 'Esie':
			each.update({'component': "ESIE"})        
		else:
			each.update({'component': map_gl})
	

		for gl in all_results:
			if gl["component"] == each['component']:
				narration = None
				month = filters.get("from_date")
				date_obj = datetime.strptime(month, "%Y-%m-%d")
				formatted_date = date_obj.strftime("%B-%Y")
	
				if "Salary for the month of" in str(gl.narration):
					# print(";;;;;;;;;;;;;;;;;;;;;;")
					# narration = f'{gl.narration} April-2024'
					narration = f'{gl.narration} {formatted_date}'
					# print(";;;;;;;;;;;;;;;;;;;;;;",narration)
				else:
					narration = gl.narration
					
				
				# print(narration,"ppppppppppppppppp")
				each.update({
					'gl_code': gl.gl_code,
					'acc_code': gl.acc_code,
					'transaction_types': gl.transaction_types,
					'narration': narration,
					'gl_description': gl.gl_description,
					"account_code":gl.account_code,
				})
				map_gl = None
				break
	staff_dill_debit = 0.0
	staff_dill_credit = 0.0

	for each in filters_data:

		if each["transaction_types"] == "Expense":
			each['debit'] = each['amount']
			staff_dill_debit += round(each['debit'])

		elif each["transaction_types"] == "Asses" or each["transaction_types"] == "liability":
			each['credit'] = round(each['amount'])
			staff_dill_credit += round(each['credit'])
		elif each["transaction_types"] == "Salary payable":
			each['credit'] = round(each['amount'])
			staff_dill_credit += round(each['credit'])
			each['debit'] = round(each['amount'])
			staff_dill_debit += round(each['debit'])
		else:
			each['credit'] = 0
			each['debit'] = 0

	# new_dict = {"component":"",'credit': round(staff_dill_debit-staff_dill_credit)}
	new_dict = {"company":company,"deptcode":00,"custom_payroll_cost_center_":"Balance Sheet","narration":"SALARY PAYABLE",'credit': round(staff_dill_debit-staff_dill_credit)}

	# filters_data.append(new_dict)
	# print(staff_dill_debit,"/////////////////////////////////////",staff_dill_credit,"....",staff_dill_debit-staff_dill_credit)


	sorted_final_data = sorted(filters_data, key=lambda x: x["component"],reverse=False)
	for entry in sorted_final_data:
		deptcode = entry['custom_payroll_cost_center_'].split(' ')[0]
			# Add the deptcode to the dictionary
		entry['deptcode'] = deptcode
		deptname = entry['custom_payroll_cost_center_'].split(' - ')[1]
		entry['deptname'] = deptname
	sorted_final_data.append(new_dict)	
			
	return sorted_final_data



def get_earning_and_deduction_types(salary_slips):
	salary_component_and_type = {_("Earning"): [], _("Deduction"): []}

	for salary_compoent in get_salary_components(salary_slips):
		component_type = get_salary_component_type(salary_compoent)
		salary_component_and_type[_(component_type)].append(salary_compoent)

	return sorted(salary_component_and_type[_("Earning")]), sorted(
		salary_component_and_type[_("Deduction")]
	)


def update_column_width(ss, columns):
	if ss.branch is not None:
		columns[3].update({"width": 120})
	if ss.department is not None:
		columns[4].update({"width": 120})
	if ss.designation is not None:
		columns[5].update({"width": 120})
	if ss.leave_without_pay is not None:
		columns[9].update({"width": 120})


def get_columns(earning_types, ded_types,filters):
	columns = [
		{
			"label": _("Salary Slip ID"),
			"fieldname": "salary_slip_id",
			"fieldtype": "Link",
			"options": "Salary Slip",
			"width": 150,
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120,
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("Date of Joining"),
			"fieldname": "data_of_joining",
			"fieldtype": "Date",
			"width": 80,
		},
		{
			"label": _("Branch"),
			"fieldname": "branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": -1,
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department",
			"width": -1,
		},
		{
			"label": _("Designation"),
			"fieldname": "designation",
			"fieldtype": "Link",
			"options": "Designation",
			"width": 120,
		},
		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 120,
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Data",
			"width": 80,
		},
		{
			"label": _("Leave Without Pay"),
			"fieldname": "leave_without_pay",
			"fieldtype": "Float",
			"width": 50,
		},
		{
			"label": _("Payment Days"),
			"fieldname": "payment_days",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Payroll Cost center"),
			"fieldname": "custom_payroll_cost_center_",
			"fieldtype": "Data",
			"width": 120,
		},
	]

	for earning in earning_types:
		columns.append(
			{
				"label": earning,
				"fieldname": frappe.scrub(earning),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)

	columns.append(
		{
			"label": _("Gross Pay"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}
	)

	for deduction in ded_types:
		columns.append(
			{
				"label": deduction,
				"fieldname": frappe.scrub(deduction),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)

	columns.extend(
		[
			{
				"label": _("Loan Repayment"),
				"fieldname": "total_loan_repayment",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Total Deduction"),
				"fieldname": "total_deduction",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Net Pay"),
				"fieldname": "net_pay",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			},
			{
				"label": _("Currency"),
				"fieldtype": "Data",
				"fieldname": "currency",
				"options": "Currency",
				"hidden": 1,
			},
		]
	)
	
	return columns

def group_colunms(filters):
	columns = [ 
		{
		"label": _("Currency"),
		"fieldtype": "Data",
		"fieldname": "currency",
		"options": "Currency",
		"hidden": 1,
		},
		{
		"label": _("Company Id"),
		"fieldtype": "Link",
		"fieldname": "company",
		"options": "Company"
		},
		{
		"label": _("Dept Code"),
		"fieldtype": "Data",
		"fieldname": "deptcode",
		"width": 120,
		},
		{
		"label": _("Dept Name"),
		"fieldtype": "Data",
		"fieldname": "deptname",
		"width": 120,
		},
		
		{
		"label": _("Dept Name"),
		"fieldtype": "Data",
		"fieldname": "custom_payroll_cost_center_",
		"width": 120,
		"hidden": 1,
		},
		{
		"label": _("Account Code"),
		"fieldtype": "Data",
		"fieldname": "account_code",
		"width": 120,
		},
		
		{
		"label": _("Component"),
		"fieldtype": "Data",
		"fieldname": "component",
		"width": 120,
		"hidden": 1,
		},
		{
		"label": _("Amount"),
		"fieldtype": "Currency",
		"fieldname": "amount",
		"hidden": 1,
		},
		{
		"label": _("Expense Code"),
		"fieldtype": "Data",
		"fieldname": "gl_code",
		"hidden": 1,
		},
		{
		"label": _("Acc Code"),
		"fieldtype": "Data",
		"fieldname": "acc_code",
		"hidden": 1,
		},
		{
		"label": _("Narration"),
		"fieldtype": "Data",
		"fieldname": "narration",
		},
		{
		"label": _("GL Description"),
		"fieldtype": "Data",
		"fieldname": "gl_description",
		"width": 120,
		"hidden": 1,
		},
		{
		"label": _("Transaction Types"),
		"fieldtype": "Data",
		"fieldname": "transaction_types",
		"width": 140,
		"hidden": 1,
		},
		{
		"label": _("Debit"),
		"fieldtype": "Currency",
		"fieldname": "debit",
		"width": 140,
		},
		{
		"label": _("Credit"),
		"fieldtype": "Currency",
		"fieldname": "credit",
		"width": 140,
		},
	]

	return columns




def get_salary_components(salary_slips):
	return (
		frappe.qb.from_(salary_detail)
		.where((salary_detail.amount != 0) & (salary_detail.parent.isin([d.name for d in salary_slips])))
		.select(salary_detail.salary_component)
		.distinct()
	).run(pluck=True)


def get_salary_component_type(salary_component):
	return frappe.db.get_value("Salary Component", salary_component, "type", cache=True)


def get_salary_slips(filters, company_currency):
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	query = frappe.qb.from_(salary_slip).select(salary_slip.star)

	if filters.get("docstatus"):
		query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])

	if filters.get("from_date"):
		query = query.where(salary_slip.start_date >= filters.get("from_date"))

	if filters.get("to_date"):
		query = query.where(salary_slip.end_date <= filters.get("to_date"))

	if filters.get("company"):
		query = query.where(salary_slip.company == filters.get("company"))

	if filters.get("employee"):
		query = query.where(salary_slip.employee == filters.get("employee"))

	if filters.get("currency") and filters.get("currency") != company_currency:
		query = query.where(salary_slip.currency == filters.get("currency"))

	salary_slips = query.run(as_dict=1)

	return salary_slips or []


def get_employee_doj_map():
	employee = frappe.qb.DocType("Employee")

	result = (frappe.qb.from_(employee).select(employee.name, employee.date_of_joining)).run()

	return frappe._dict(result)


def get_salary_slip_details(salary_slips, currency, company_currency, component_type):
	salary_slips = [ss.name for ss in salary_slips]

	result = (
		frappe.qb.from_(salary_slip)
		.join(salary_detail)
		.on(salary_slip.name == salary_detail.parent)
		.where((salary_detail.parent.isin(salary_slips)) & (salary_detail.parentfield == component_type))
		.select(
			salary_detail.parent,
			salary_detail.salary_component,
			salary_detail.amount,
			salary_slip.exchange_rate,
		)
	).run(as_dict=1)

	ss_map = {}

	for d in result:
		ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
		if currency == company_currency:
			ss_map[d.parent][d.salary_component] += flt(d.amount) * flt(
				d.exchange_rate if d.exchange_rate else 1
			)
		else:
			ss_map[d.parent][d.salary_component] += flt(d.amount)

	return ss_map
