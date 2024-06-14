// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Information Details"] = {
	// "filters": [
	// 	{
	// 		"fieldname": "company",
	// 		"label": "Company",
	// 		"fieldtype": "Link",
	// 		"options": "Company",
	// 		"default": frappe.defaults.get_user_default("Company")
	// 	},
	// 	{
	// 		"fieldname": "department",
	// 		"label": "Department",
	// 		"fieldtype": "Link",
	// 		"options": "Department"
	// 	},
		
	// 	{
	// 		"fieldname": "gender",
	// 		"label": "Gender",
	// 		"fieldtype": "Link",
	// 		"options": "Gender"
	// 	},
	// 	{
	// 		"fieldname": "employee_type",
	// 		"label": "Employee Type",
	// 		"fieldtype": "Link",
	// 		"options": "Employment Type"
	// 	},
	// 	{
	// 		"fieldname": "branch",
	// 		"label": "Branch",
	// 		"fieldtype": "Link",
	// 		"options": "Branch"
	// 	},
	// 	{
	// 		"field_name": "payroll_cost_center",
	// 		"label": "Payroll Cost Center",
	// 		"fieldtype": "Link",
	// 		"options": "Cost Center"
	// 	},

	// ]
	"filters": [
		{
			"label": (__("Company")),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{   "label": (__("Status")),
			"fieldname": "status",
			"fieldtype": "Select",
			"options": ["Active","Left","Inactive","Suspended"],
			"default":"Active"
		},
		{
			"label": (__("Department")),
			"fieldname": "department",
			"fieldtype": "Link",
			"options": "Department"
		},
		
		{
			"label": (__("Gender")),
			"fieldname": "gender",
			"fieldtype": "Link",
			"options": "Gender"
		},
		{
			
			"label": (__("Employee Type")),
			"fieldname": "employee_type",
			"fieldtype": "Link",
			"options": "Employment Type"
		},
		{
			"label": (__("Branch")),
			"fieldname": "branch",
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"label": (__("Payroll Cost Center")),
			"field_name": "payroll_cost_center",
			"fieldtype": "Link",
			"options": "Cost Center"
		},
 
	]

};


 