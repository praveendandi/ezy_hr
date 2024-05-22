// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Attendance Report"] = {
	
filters: [
	{
		fieldname: "from_date",
		label: __("From Date"),
		fieldtype: "Date",
		default: frappe.datetime.month_start(),
	},
	{
		fieldname: "to_date",
		label: __("To Date"),
		fieldtype: "Date",
		default: frappe.datetime.month_end(),
	},
	{
		fieldname: "employee",
		label: __("Employee"),
		fieldtype: "Link",
		options: "Employee"
	},
	{
		fieldname: "company",
		label: __("Unit"),
		fieldtype: "Link",
		options: "Company",
		reqd: 1
	},
],
};

