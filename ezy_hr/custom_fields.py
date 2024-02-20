CUSTOM_FIELDS = {
    "Payroll Settings": [
        {
            "fieldname": "custom_year",
            "fieldtype": "Select",
            "label": "Year",
            "options": "\n2022\n2023\n2024",
            "insert_after": "define_opening_balance_for_earning_and_deductions",
        },
        {
            "fieldname": "custom_month",
            "fieldtype": "Select",
            "label": "Month",
            "options": "\nJan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSept\nOct\nNov\nDec",
            "insert_after": "custom_year"
        },
        {
            "fieldname": "groupwise_salary_summary",
            "fieldtype": "Button",
            "label": "Get Groupwise salary Summary",
            "insert_after": "custom_month"
        }
    ]
}
