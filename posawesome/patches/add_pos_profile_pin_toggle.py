import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field


CUSTOM_FIELDS = {
	"POS Profile": [
		{
			"fieldname": "posa_section_terminal_security",
			"label": "Terminal Security",
			"fieldtype": "Section Break",
			"insert_after": "posa_ignore_mandatory_fields",
		},
		{
			"fieldname": "posa_enable_cashier_pin",
			"label": "Enable Cashier PIN",
			"fieldtype": "Check",
			"default": "1",
			"description": "When enabled, the POS asks for a cashier PIN to unlock and switch terminals. When disabled, the signed-in user operates the POS without a PIN.",
			"insert_after": "posa_section_terminal_security",
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

	# Existing terminals must keep their current PIN-protected behaviour.  The
	# checkbox defaults to 1; an administrator can uncheck it per POS Profile.
	if frappe.db.has_column("POS Profile", "posa_enable_cashier_pin"):
		frappe.db.sql(
			"update `tabPOS Profile` set posa_enable_cashier_pin = 1 "
			"where posa_enable_cashier_pin is null or posa_enable_cashier_pin = 0"
		)

	frappe.clear_cache()
