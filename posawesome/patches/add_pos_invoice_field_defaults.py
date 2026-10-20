import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


CUSTOM_FIELDS = {
	"Customer": [
		{
			"fieldname": "posa_cost_center",
			"label": "POS Cost Center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"description": "Used automatically on POS invoices when the invoice has no cost center.",
			"insert_after": "posa_discount",
		}
	],
	"Customer Group": [
		{
			"fieldname": "posa_cost_center",
			"label": "POS Cost Center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"description": "Fallback cost center for POS invoices of customers in this group (child groups inherit from their parent).",
			"insert_after": "parent_customer_group",
		}
	],
	"POS Profile": [
		{
			"fieldname": "posa_section_invoice_defaults",
			"label": "Invoice Field Defaults",
			"fieldtype": "Section Break",
			"collapsible": 1,
			"insert_after": "posa_allow_item_exchange",
		},
		{
			"fieldname": "posa_invoice_field_defaults",
			"label": "Invoice Field Defaults",
			"fieldtype": "Table",
			"options": "POS Invoice Field Default",
			"description": "Fill mandatory Sales Invoice fields that the POS does not display.",
			"insert_after": "posa_section_invoice_defaults",
		},
		{
			"fieldname": "posa_ignore_mandatory_fields",
			"label": "Ignore Sales Invoice Mandatory Fields",
			"fieldtype": "Check",
			"default": "1",
			"description": "Allow POS invoices to save even when a mandatory Sales Invoice field is not collected by the POS. Core fields (company, customer, posting date, items) are always validated.",
			"insert_after": "posa_invoice_field_defaults",
		},
	],
}


def execute():
	for doctype, fields in CUSTOM_FIELDS.items():
		for field in fields:
			if frappe.db.exists(
				"Custom Field",
				{"dt": doctype, "fieldname": field["fieldname"]},
			):
				continue
			create_custom_field(doctype, field, ignore_validate=True)

	frappe.clear_cache()
