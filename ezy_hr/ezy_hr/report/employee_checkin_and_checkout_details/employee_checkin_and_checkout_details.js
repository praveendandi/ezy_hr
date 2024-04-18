// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Checkin And Checkout Details"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_start(),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.month_end(),
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		// {
		// 	fieldname: "shift",
		// 	label: __("Shift Type"),
		// 	fieldtype: "Link",
		// 	options: "Shift Type",
		// },
		// {
		// 	fieldname: "department",
		// 	label: __("Department"),
		// 	fieldtype: "Link",
		// 	options: "Department",
		// },
		// {
		// 	fieldname: "company",
		// 	label: __("Company"),
		// 	fieldtype: "Link",
		// 	options: "Company",
		// 	reqd: 1,
		// 	default: frappe.defaults.get_user_default("Company"),
		// },
		
	],

};
