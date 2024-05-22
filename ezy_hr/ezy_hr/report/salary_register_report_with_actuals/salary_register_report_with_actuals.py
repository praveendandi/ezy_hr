# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils import formatdate

import erpnext
import json

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")


def get_salary_structure_earnings(salary_slip):
    # Get the salary structure linked to the salary slip
    salary_structure = frappe.db.get_value("Salary Slip", salary_slip, "salary_structure")
    
    # Construct and execute raw SQL query to fetch earnings
    sql_query = """
        SELECT sd.salary_component, sd.amount 
        FROM `tabSalary Detail` sd 
        WHERE sd.parent = %s AND sd.amount > 0 AND sd.salary_component NOT LIKE 'Deduction%%'
    """
    earnings_data = frappe.db.sql(sql_query, (salary_structure,), as_dict=True)
    print(earnings_data, 'earnings_data')
    
    earnings_list = []
    
    # Iterate through the earnings data to extract components and amounts
    for item in earnings_data:
        earnings_list.append({
            "salary_component": item.get("salary_component"),
            "amount": item.get("amount")
        })
    
    
    # Print actual earning values
    for earning in earnings_list:
        print(f"Actual earning value for {earning['salary_component']}: {earning['amount']}")
    
    return earnings_list


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
	columns = get_columns(earning_types, ded_types)

	ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
	ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

	doj_map = get_employee_doj_map()

	data = []
	for ss in salary_slips:
		employee_data = frappe.db.get_list("Employee",{"name":ss.employee},["name","bank_name","bank_ac_no","ifsc_code","custom_gross_amount","attendance_device_id"])

		for emp in employee_data:
			department_name = None
			if ss.department:
				department_name = ss.department.split(" - ")[0] if " - " in ss.department else ss.department

			actual_gross = emp.custom_gross_amount
			row = {
				"salary_slip_id": ss.name,
				"employee": ss.employee,
				"employee_name": ss.employee_name,
				"data_of_joining": formatdate(doj_map.get(ss.employee), "dd-mm-yyyy"),
				"branch": ss.branch,
				"department": department_name,
				"designation": ss.designation,
				"attendance_device_id":emp.attendance_device_id,
				"company": ss.company,
				"start_date": formatdate(ss.start_date, "dd-mm-yyyy"),
				"end_date": formatdate(ss.end_date, "dd-mm-yyyy"),
				"leave_without_pay": ss.leave_without_pay,
				"payment_days": ss.payment_days,
				"currency": currency or company_currency,
				"bank_name":ss.bank_name,
               	"bank_account_no":ss.bank_account_no,
               	"ifsc_code":emp.ifsc_code,
				"total_loan_repayment": ss.total_loan_repayment,
				"actual_gross_pay": actual_gross
			}

			update_column_width(ss, columns)

			salary_structure_earnings = get_salary_structure_earnings(ss)

			for e in earning_types:
				actual_earning_value = next(
					(item["amount"] for item in salary_structure_earnings if item.get("salary_component") == e),
					0
				)
				row.update({
					frappe.scrub(e): round(ss_earning_map.get(ss.name, {}).get(e) or 0),
					f"actual_{frappe.scrub(e)}": round(actual_earning_value)
				})

			for d in ded_types:
				row.update({frappe.scrub(d): round(ss_ded_map.get(ss.name, {}).get(d) or 0)})

			if currency == company_currency:
				row.update(
					{
						"gross_pay": round(flt(ss.gross_pay) * flt(ss.exchange_rate)),
						"total_deduction": round(flt(ss.total_deduction) * flt(ss.exchange_rate)),
						"net_pay": round(flt(ss.net_pay) * flt(ss.exchange_rate)),
					}
				)
			else:
				row.update(
					{"gross_pay": ss.gross_pay, "total_deduction": ss.total_deduction, "net_pay": ss.net_pay}
				)

			data.append(row)

	return columns, data

# ... (rest of your code remains unchanged)



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


def get_columns(earning_types, ded_types):
	not_include_net = []

	columns = [
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Data",
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
			"fieldtype": "Data",
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
			"label": _("Bank Name"),
			"fieldname": "bank_name",
			"fieldtype": "data",
			"width": 120,
		},
		{
			"label": _("Account No"),
			"fieldname": "bank_account_no",
			"fieldtype": "data",
			"width": 120,
		},
		{
			"label": _("IFSC Code"),
			"fieldname": "ifsc_code",
			"fieldtype": "data",
			"width": 120,
		},
		{
			"label": _("Start Date"),
			"fieldname": "start_date",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("End Date"),
			"fieldname": "end_date",
			"fieldtype": "Data",
			"width": 120,
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
	]

	for earning in earning_types:
		columns.append(
			{
				"label": f"Actual {earning}",
				"fieldname": f"actual_{frappe.scrub(earning)}",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 120,
			}
		)
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
			"label": _("Actual Gross Pay"),
			"fieldname": "actual_gross_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 140,
		}
	)
	columns.append(
		{
			"label": _("Earned Gross Pay"),
			"fieldname": "gross_pay",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		}
	)

	for deduction in ded_types:
		if deduction not in ["PF-Employer", "ESIE","Actual PF Employer"]:
			columns.append(
				{
					"label": deduction,
					"fieldname": frappe.scrub(deduction),
					"fieldtype": "Currency",
					"options": "currency",
					"width": 120,
				}
			)
			# columns.append(
			#     {
			#         "label": f"Actual {deduction}",
			#         "fieldname": f"actual_{frappe.scrub(deduction)}",
			#         "fieldtype": "Currency",
			#         "options": "currency",
			#         "width": 120,
			#     }
			# )
		else:
			not_include_net.append(deduction)

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
			{
				"label": _("Attendance Device Id"),
				"fieldname": "attendance_device_id",
				"fieldtype": "Data",
				"width": 100,
			},
		]
	)

	for not_in in not_include_net:
		columns.append(
			{
				"label": not_in,
				"fieldname": frappe.scrub(not_in),
				"fieldtype": "Currency",
				"options": "currency",
				"width": 100,
			}
		)
		columns.append(
			{
				"label": f"Actual {not_in}",
				"fieldname": f"actual_{frappe.scrub(not_in)}",
				"fieldtype": "Currency",
				"options": "currency",
				"width": 100,
			}
		)

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
