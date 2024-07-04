// Copyright (c) 2024, Ganu Reddy and contributors
// For license information, please see license.txt

frappe.query_reports["HR MIS Report"] = {
	"filters": [{
		"fieldname": "company",
		"label": __("Unit"),
		"fieldtype": "Link",
		"options": "Company",
		"reqd": 1
	},
	{
		"fieldname": "start_date",
		"label": __("Start Date"),
		"fieldtype": "Date",
		"default": "2024-04-01",
		"reqd": 1
	},
	{
		"fieldname": "end_date",
		"label": __("End Date"),
		"fieldtype": "Date",
		"default": frappe.datetime.month_end(),
		"reqd": 1
	},
  
	
	{
		"label": __("Report Type"),
		"fieldname": "report_type",
		"fieldtype": "Select",
		"options": ["Summary Report", "Head Count Working", "New Joinees List", "Left Employees"]
	}
	
],

"onload": function(report) {
	// Add a download button
	report.page.add_inner_button(__('Download'), function() {
		let filters = report.get_values();
		if (!filters) return;
		frappe.call({
			method: "ezy_hr.downloading.download_all_hr_mis_reports",
			args: {
				"company": filters.company,
				"start_date": filters.start_date,
				"end_date": filters.end_date,
				"employee_type": filters.employee_type
			},
			callback: function(response) {
				if (response.message){
					let url = response.message.file_name
					window.open(url)
				}
			}
		});
	});
}
};