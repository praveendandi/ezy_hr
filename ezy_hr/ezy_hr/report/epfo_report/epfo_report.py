# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate
from datetime import datetime

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns(filters) if data else []
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": _("EMP Code"),
			"fieldname": "employee",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("UAN"),
			"fieldname": "pf_account",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Member Name"),
			"fieldname": "employee_name",
			"width": 160,
		},
		{
			"label": _("Gross Wages"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("EPF Wages"),
			"fieldname": "epf_wages",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("EPS Wages"),
			"fieldname": "eps_wages",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("EDLI Wages"),
			"fieldname": "edli_wages",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("EPF Contri Remitted"),
			"fieldname": "epf_contri_remitted",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("EPS Contri Remitted"),
			"fieldname": "eps_contri_remitted",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("EPF EPS Diff Remitted"),
			"fieldname": "epf_eps_diff_remitted",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("NCP Days"),
			"fieldname": "absent_days",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Working Days"),
			"fieldname": "payment_days",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Admin"),
			"fieldname": "admin",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("EDLI Admin"),
			"fieldname": "edli_admin",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Total Contribution"),
			"fieldname": "total_contribution",
			"fieldtype": "Currency",
			"width": 120
		},
	]
	
	return columns

def get_conditions(filters):
	conditions = ["1=1"]

	if filters.get("department"):
		conditions.append("sal.department = '%s'" % filters["department"])

	if filters.get("branch"):
		conditions.append("sal.branch = '%s'" % filters["branch"])

	if filters.get("company"):
		conditions.append("sal.company = '%s'" % filters["company"])

	if filters.get("from_date"):
		conditions.append("sal.start_date >= '%s'" % filters["from_date"])

	if filters.get("to_date"):
		conditions.append("sal.end_date <= '%s'" % filters["to_date"])

	if filters.get("employee"):
		conditions.append("sal.employee = '%s'" % filters["employee"])

	if filters.get("mode_of_payment"):
		conditions.append("sal.mode_of_payment = '%s'" % filters["mode_of_payment"])

	return " AND ".join(conditions)

def prepare_data(entry, component_type_dict):
	data_list = {}

	employee_account_dict = frappe._dict(
		(employee.name, {"provident_fund_account": employee.provident_fund_account,"custom_applicable_for_actual_pf":employee.custom_applicable_for_actual_pf,"date_of_birth":employee.date_of_birth})
		for employee in frappe.db.sql(
			"""SELECT name, provident_fund_account, custom_applicable_for_actual_pf,date_of_birth FROM `tabEmployee`""",
			as_dict=True,
		)
	)

	for d in entry:
		component_type = component_type_dict.get(d.salary_component)
		if data_list.get(d.name):
			data_list[d.name][component_type] = d.amount
		else:
			data_list[d.name] = {
				"employee": d.employee,
				"employee_name": d.employee_name,
				"pf_account": employee_account_dict.get(d.employee, {}).get("provident_fund_account"),
				"custom_applicable_for_actual_pf":employee_account_dict.get(d.employee, 0).get("custom_applicable_for_actual_pf"),
				"date_of_birth":employee_account_dict.get(d.employee, 0).get("date_of_birth"),
				component_type: d.amount,
				"gross_pay": round(d.gross_pay),
				"absent_days": d.absent_days, 
				"payment_days" : d.payment_days,
			}
	return data_list

def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	salary_slips = frappe.db.sql(
		f"""SELECT sal.name FROM `tabSalary Slip` sal
		WHERE docstatus = 1 AND {conditions}""",
		as_dict=1,
	)

	component_type_dict = frappe._dict(
		frappe.db.sql(
			"""SELECT name, component_type FROM `tabSalary Component`
			WHERE component_type IN ('Provident Fund', 'Provident Fund Account')"""
		)
	)

	if not component_type_dict:
		return []

	entry = frappe.db.sql(
		f"""SELECT sal.name, sal.employee, sal.employee_name, sal.payment_days, sal.gross_pay, sal.absent_days, ded.salary_component, ded.amount
		FROM `tabSalary Slip` sal, `tabSalary Detail` ded
		WHERE sal.name = ded.parent
		AND ded.parentfield = 'deductions'
		AND ded.parenttype = 'Salary Slip'
		AND sal.docstatus = 1
		AND {conditions}
		AND ded.salary_component IN ({", ".join(["%s"] * len(component_type_dict))})""",
		tuple(component_type_dict.keys()),
		as_dict=1,
	)

	data_list = prepare_data(entry, component_type_dict)

	for d in salary_slips:
		if d.name in data_list:
			employee = data_list[d.name]

			earning_data = frappe.db.sql(
				"""SELECT sal.name, ear.salary_component, ear.amount, ear.abbr
				FROM `tabSalary Slip` sal, `tabSalary Detail` ear
				WHERE sal.name = ear.parent
				AND ear.parentfield = 'earnings'
				AND ear.parenttype = 'Salary Slip'
				AND sal.docstatus = 1
				AND ear.parent=%s""", (d.name,),
				as_dict=1,
			)
			is_applicable = False

			if employee.get("custom_applicable_for_actual_pf"):
				is_applicable = True


			basic = 0
			da = 0
			hra = 0
			inc = 0

			for i in earning_data:
				if i.abbr == "B":
					basic = i.amount
				if i.abbr == "DA":
					da = i.amount
				if i.abbr == "HRA":
					hra = i.amount
				if i.abbr == "INC":
					inc = i.amount

			gross_pay = employee["gross_pay"]

			without_inc_gross = gross_pay - inc

			if is_applicable:
				epf_wages = round(basic+da)
			elif without_inc_gross - hra > 15000:
				epf_wages = 15000
			else:
				epf_wages = round(without_inc_gross - hra)
			
			if without_inc_gross - hra > 15000:
				eps_wages = 15000 
			else:
				eps_wages = round(without_inc_gross - hra)
		
			if without_inc_gross - hra > 15000:
				edli_wages = 15000
			else:
				edli_wages = round(without_inc_gross - hra)
			
			# eps_wages = epf_wages
			# edli_wages = epf_wages
			def calculate_birth_year(age):
				current_year = datetime.now().year
				birth_year = current_year - age
				return birth_year

			epf_contri_remitted = round((epf_wages * 12.0) / 100)
			eps_contri_remitted = None
   
			if calculate_birth_year(employee["date_of_birth"].year) >= 58:
				eps_contri_remitted = 0
			else:
				eps_contri_remitted = round((eps_wages * 8.33) / 100)
	
			epf_eps_diff_remitted = round(epf_contri_remitted - eps_contri_remitted)
			admin = round((epf_wages * 0.5) / 100)
			edli_admin = round((edli_wages * 0.5) / 100)
			total_contribution = round(epf_contri_remitted + eps_contri_remitted + epf_eps_diff_remitted + admin + edli_admin)

			employee["epf_wages"] = epf_wages
			employee["eps_wages"] = eps_wages
			employee["edli_wages"] = edli_wages
			employee["epf_contri_remitted"] = epf_contri_remitted
			employee["eps_contri_remitted"] = eps_contri_remitted
			employee["epf_eps_diff_remitted"] = epf_eps_diff_remitted
			employee["admin"] = admin
			employee["edli_admin"] = edli_admin
			employee["total_contribution"] = total_contribution
			employee['gross_pay'] = without_inc_gross

			data.append(employee)

	return data

@frappe.whitelist()
def get_years():
	year_list = frappe.db.sql_list(
		"""SELECT DISTINCT YEAR(end_date) FROM `tabSalary Slip` ORDER BY YEAR(end_date) DESC"""
	)
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)
