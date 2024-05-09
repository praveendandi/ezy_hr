// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Information Details"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": "Company",
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "department",
			"label": "Department",
			"fieldtype": "Link",
			"options": "Department"
		},
		
		{
			"fieldname": "gender",
			"label": "Gender",
			"fieldtype": "Link",
			"options": "Gender"
		},
		{
			"fieldname": "employee_type",
			"label": "Employee Type",
			"fieldtype": "Link",
			"options": "Employment Type"
		},
		{
			"fieldname": "branch",
			"label": "Branch",
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"field_name": "payroll_cost_center",
			"label": "Payroll Cost Center",
			"fieldtype": "Link",
			"options": "Cost Center"
		},

	]
};
