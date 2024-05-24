// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["Provident Fund Breakdown Report"] = {
	"filters": [
		{
			fieldname:"from_date",
			label: __("From"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			reqd: 1,
			width: "100px"
		},
		{
			fieldname:"to_date",
			label: __("To"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
			width: "100px"
		},
		{
			fieldname: "company",
			label: "Unit",
			fieldtype: "Link",
			reqd:1,
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
		// {
		// 	fieldname: "department",
		// 	label: "Department",
		// 	fieldtype: "Link",
		// 	options: "Department",
		// },
	]
};
