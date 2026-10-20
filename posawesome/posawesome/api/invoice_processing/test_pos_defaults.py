import unittest
from types import SimpleNamespace
from unittest.mock import patch

from posawesome.posawesome.api.invoice_processing import pos_defaults


class FakeMeta:
	def __init__(self, fields=()):
		self.fields = list(fields)

	def has_field(self, fieldname):
		return any(field.fieldname == fieldname for field in self.fields)

	def get_field(self, fieldname):
		for field in self.fields:
			if field.fieldname == fieldname:
				return field
		return None


class FakeRow(dict):
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__


class FakeDoc:
	def __init__(self, doctype="Sales Invoice", **data):
		self.doctype = doctype
		self._data = dict(data)
		self.flags = SimpleNamespace()
		self.name = data.get("name")
		self._new = data.get("_new", True)
		self.meta = data.get("meta") or FakeMeta()

	def get(self, key, default=None):
		return self._data.get(key, default)

	def set(self, key, value):
		self._data[key] = value

	def __getattr__(self, key):
		try:
			return self._data[key]
		except KeyError as exc:
			raise AttributeError(key) from exc

	def __setattr__(self, key, value):
		if key in {"doctype", "_data", "flags", "name", "_new", "meta"}:
			object.__setattr__(self, key, value)
		else:
			self._data[key] = value

	def is_new(self):
		return self._new


def _field(fieldname, fieldtype="Data", options="", reqd=0):
	return SimpleNamespace(
		fieldname=fieldname,
		fieldtype=fieldtype,
		options=options,
		reqd=reqd,
	)


def _cost_center_lookup(values):
	"""Build a fake frappe.db.get_value for Customer / Group / Company / Cost Center."""

	def get_value(doctype, name, fields=None, as_dict=False):
		key = (doctype, name)
		if doctype == "Cost Center":
			value = values.get(key)
			if not value:
				return None
			return value if as_dict else value.get("company")
		value = values.get(key, {})
		if isinstance(fields, str):
			return value.get(fields)
		if as_dict:
			return {field: value.get(field) for field in fields}
		return None

	return get_value


class TestCostCenterResolution(unittest.TestCase):
	def setUp(self):
		self.profile = FakeDoc(
			doctype="POS Profile",
			name="POS-1",
			company="C",
			cost_center=None,
			posa_invoice_field_defaults=[],
		)

	@patch.object(pos_defaults, "frappe")
	def test_customer_value_wins(self, frappe_module):
		frappe_module.get_meta.side_effect = lambda doctype: FakeMeta(
			[_field("posa_cost_center")] if doctype in ("Customer", "Customer Group") else []
		)
		frappe_module.db.get_value.side_effect = _cost_center_lookup(
			{
				("Customer", "CUST"): {
					"posa_cost_center": "CC-CUST",
					"customer_group": "Group A",
				},
				("Customer Group", "Group A"): {"posa_cost_center": "CC-GROUP"},
				("Cost Center", "CC-CUST"): {
					"company": "C",
					"is_group": 0,
					"disabled": 0,
				},
				("Cost Center", "CC-GROUP"): {
					"company": "C",
					"is_group": 0,
					"disabled": 0,
				},
			}
		)

		doc = FakeDoc(company="C", customer="CUST")
		self.assertEqual(pos_defaults.resolve_cost_center(doc, self.profile), "CC-CUST")

	@patch.object(pos_defaults, "frappe")
	def test_group_walks_up_parents(self, frappe_module):
		frappe_module.get_meta.return_value = FakeMeta([_field("posa_cost_center")])
		frappe_module.db.get_value.side_effect = _cost_center_lookup(
			{
				("Customer", "CUST"): {
					"posa_cost_center": None,
					"customer_group": "Child",
				},
				("Customer Group", "Child"): {
					"posa_cost_center": None,
					"parent_customer_group": "Parent",
				},
				("Customer Group", "Parent"): {
					"posa_cost_center": "CC-GROUP",
					"parent_customer_group": None,
				},
				("Cost Center", "CC-GROUP"): {
					"company": "C",
					"is_group": 0,
					"disabled": 0,
				},
			}
		)

		doc = FakeDoc(company="C", customer="CUST")
		self.assertEqual(pos_defaults.resolve_cost_center(doc, self.profile), "CC-GROUP")

	@patch.object(pos_defaults, "frappe")
	def test_profile_then_company_fallback(self, frappe_module):
		frappe_module.get_meta.return_value = FakeMeta()
		frappe_module.db.get_value.side_effect = _cost_center_lookup(
			{
				("Cost Center", "CC-PROFILE"): {
					"company": "C",
					"is_group": 0,
					"disabled": 0,
				},
				("Cost Center", "CC-COMPANY"): {
					"company": "C",
					"is_group": 0,
					"disabled": 0,
				},
			}
		)
		self.profile.cost_center = "CC-PROFILE"

		self.assertEqual(
			pos_defaults.resolve_cost_center(FakeDoc(company="C"), self.profile),
			"CC-PROFILE",
		)

		self.profile.cost_center = None
		frappe_module.db.get_value.side_effect = _cost_center_lookup(
			{
				("Company", "C"): {"cost_center": "CC-COMPANY"},
				("Cost Center", "CC-COMPANY"): {
					"company": "C",
					"is_group": 0,
					"disabled": 0,
				},
			}
		)
		self.assertEqual(
			pos_defaults.resolve_cost_center(FakeDoc(company="C"), self.profile),
			"CC-COMPANY",
		)

	@patch.object(pos_defaults, "frappe")
	def test_ambiguous_leaves_are_not_guessed(self, frappe_module):
		frappe_module.get_meta.return_value = FakeMeta()
		frappe_module.db.get_value.return_value = None
		frappe_module.get_all.return_value = ["Branch A", "Branch B"]

		self.assertIsNone(
			pos_defaults.resolve_cost_center(FakeDoc(company="C"), self.profile)
		)

	@patch.object(pos_defaults, "frappe")
	def test_item_rows_follow_invoice_cost_center(self, frappe_module):
		frappe_module.get_meta.return_value = FakeMeta()
		frappe_module.db.get_value.side_effect = _cost_center_lookup(
			{
				("Cost Center", "CC-PROFILE"): {
					"company": "C",
					"is_group": 0,
					"disabled": 0,
				},
			}
		)
		self.profile.cost_center = "CC-PROFILE"
		doc = FakeDoc(
			company="C",
			cost_center=None,
			items=[FakeRow(cost_center="ITEM-DEFAULT")],
		)

		pos_defaults._apply_cost_center(doc, self.profile)

		self.assertEqual(doc.cost_center, "CC-PROFILE")
		self.assertEqual(doc.items[0].cost_center, "CC-PROFILE")

	@patch.object(pos_defaults, "frappe")
	def test_customer_change_replaces_derived_cost_center(self, frappe_module):
		frappe_module.get_meta.return_value = FakeMeta([_field("posa_cost_center")])
		frappe_module.db.get_value.side_effect = _cost_center_lookup(
			{
				("Customer", "CUST-B"): {
					"posa_cost_center": "CC-B",
					"customer_group": None,
				},
				("Cost Center", "CC-B"): {
					"company": "C",
					"is_group": 0,
					"disabled": 0,
				},
			}
		)
		doc = FakeDoc(
			company="C",
			customer="CUST-B",
			cost_center="CC-A",
			items=[FakeRow(cost_center="CC-A")],
		)

		pos_defaults._apply_cost_center(
			doc,
			self.profile,
			previous={"customer": "CUST-A", "cost_center": "CC-A"},
		)

		self.assertEqual(doc.cost_center, "CC-B")
		self.assertEqual(doc.items[0].cost_center, "CC-B")


class TestPaymentMethodMapping(unittest.TestCase):
	def setUp(self):
		self.profile = FakeDoc(
			doctype="POS Profile",
			name="POS-1",
			company="C",
			cost_center=None,
			posa_invoice_field_defaults=[],
		)

	def _doc(self, mode, amount=100):
		return FakeDoc(
			company="C",
			customer="CUST",
			meta=FakeMeta(
				[
					_field(
						"custom_payment_method",
						"Select",
						"نقدي\nمدى\nفيزا\nماستر كارد\nتمارا\nتابي\nتحويل بنكي\nAMERICAN EXPRESS",
						reqd=1,
					),
					_field("notes", "Select", "نقدي\nتمارا", reqd=0),
				]
			),
			payments=[FakeRow(mode_of_payment=mode, amount=amount)],
		)

	def test_cash_maps_to_arabic_option(self):
		doc = self._doc("Cash")
		pos_defaults._apply_payment_method(doc, self.profile)
		self.assertEqual(doc.get("custom_payment_method"), "نقدي")
		self.assertIsNone(doc.get("notes"))

	def test_tamara_and_master_card(self):
		doc = self._doc("Tamara")
		pos_defaults._apply_payment_method(doc, self.profile)
		self.assertEqual(doc.get("custom_payment_method"), "تمارا")

		doc = self._doc("Master Card")
		pos_defaults._apply_payment_method(doc, self.profile)
		self.assertEqual(doc.get("custom_payment_method"), "ماستر كارد")

	def test_configured_field_is_not_overwritten(self):
		self.profile.posa_invoice_field_defaults = [
			FakeRow(fieldname="custom_payment_method", source="Static Value", value="مدى")
		]
		doc = self._doc("Cash")
		doc.set("custom_payment_method", "مدى")

		pos_defaults._apply_payment_method(doc, self.profile)

		self.assertEqual(doc.get("custom_payment_method"), "مدى")

	def test_payment_mode_change_updates_derived_value(self):
		doc = self._doc("Tamara")
		doc.set("custom_payment_method", "نقدي")

		pos_defaults._apply_payment_method(doc, self.profile, previous_modes=["Cash"])

		self.assertEqual(doc.get("custom_payment_method"), "تمارا")

	def test_manual_value_survives_payment_mode_change(self):
		doc = self._doc("Tamara")
		doc.set("custom_payment_method", "تحويل بنكي")

		pos_defaults._apply_payment_method(doc, self.profile, previous_modes=["Cash"])

		self.assertEqual(doc.get("custom_payment_method"), "تحويل بنكي")


class TestApplyPosInvoiceDefaults(unittest.TestCase):
	@patch.object(pos_defaults, "_apply_payment_method")
	@patch.object(pos_defaults, "_apply_cost_center")
	@patch.object(pos_defaults, "_get_profile")
	def test_ignore_mandatory_is_enabled_for_pos_docs(
		self, get_profile, apply_cost_center, apply_payment_method
	):
		get_profile.return_value = FakeDoc(
			doctype="POS Profile",
			name="POS-1",
			company="C",
			posa_ignore_mandatory_fields=1,
			posa_invoice_field_defaults=[],
		)
		doc = FakeDoc(
			company="C",
			customer="CUST",
			posting_date="2026-10-20",
			items=[FakeRow(item_code="ITEM")],
			pos_profile="POS-1",
		)

		pos_defaults.apply_pos_invoice_defaults(doc)

		self.assertTrue(doc.flags.ignore_mandatory)

	@patch.object(pos_defaults, "_apply_payment_method")
	@patch.object(pos_defaults, "_apply_cost_center")
	@patch.object(pos_defaults, "_get_profile")
	def test_non_pos_documents_are_untouched(
		self, get_profile, apply_cost_center, apply_payment_method
	):
		doc = FakeDoc(doctype="Purchase Invoice", company="C")

		pos_defaults.apply_pos_invoice_defaults(doc)

		get_profile.assert_not_called()
		self.assertFalse(getattr(doc.flags, "ignore_mandatory", False))

	@patch.object(pos_defaults, "_apply_payment_method")
	@patch.object(pos_defaults, "_apply_cost_center")
	@patch.object(pos_defaults, "_get_profile")
	def test_core_fields_are_still_required(
		self, get_profile, apply_cost_center, apply_payment_method
	):
		get_profile.return_value = FakeDoc(
			doctype="POS Profile",
			name="POS-1",
			company="C",
			posa_ignore_mandatory_fields=1,
			posa_invoice_field_defaults=[],
		)
		doc = FakeDoc(
			company="C",
			customer="CUST",
			posting_date="2026-10-20",
			items=[],
			pos_profile="POS-1",
		)

		with patch.object(pos_defaults.frappe, "throw", side_effect=ValueError("core")):
			with self.assertRaises(ValueError):
				pos_defaults.apply_pos_invoice_defaults(doc)

		self.assertFalse(getattr(doc.flags, "ignore_mandatory", False))


if __name__ == "__main__":
	unittest.main()
