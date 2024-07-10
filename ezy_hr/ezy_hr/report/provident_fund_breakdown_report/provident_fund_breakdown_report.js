// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["Provident Fund Breakdown Report"] = {
	"filters": [
		{
			fieldname: "company",
			label: "Unit",
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "employee",
			label: "Employee ID",
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "department",
			label: "Department",
			fieldtype: "Link",
			options: "Department",
		},
	]
};
