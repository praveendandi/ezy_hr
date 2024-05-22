// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["ESI Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Unit"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"width": "100px",
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": "100px"
		},
	]	
};
