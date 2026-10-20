"""POS-specific defaults for Sales Invoice / POS Invoice.

The desk allows teams to make extra fields mandatory on Sales Invoice (for
example ``custom_payment_method``, ``custom_fitting_location`` or
``cost_center``).  The POS does not render those fields, so a POS sale used to
fail with ``MandatoryError`` while the same invoice could be created from the
desk.

This module runs from ``before_validate`` for POS invoices only.  It:

1. resolves ``cost_center`` from the customer, then the customer group tree,
   then the POS Profile, then the Company default;
2. applies explicit field defaults configured on the POS Profile
   (``posa_invoice_field_defaults``);
3. infers required Select fields from the payment modes (for example
   ``custom_payment_method`` = "Cash" -> "نقدي");
4. optionally skips the remaining mandatory checks for the POS document.

The switch is the POS Profile checkbox ``posa_ignore_mandatory_fields``.  It
defaults to enabled so an existing site is not blocked by a back-office field
that the POS cannot collect.  Core POS fields (company, customer, posting
date, items) are always verified before the bypass is applied.
"""

import re

import frappe
from frappe.utils import cint, flt

# Mode of Payment names are free text.  The POS may see "Cash", "Mada",
# "Master Card", ... while the custom Select field uses Arabic labels.
# Keys are canonical, normalized names; values are accepted aliases.
PAYMENT_MODE_ALIASES = {
	"cash": {"cash", "نقدي", "نقدا", "نقداً"},
	"mada": {"mada", "مدى"},
	"visa": {"visa", "فيزا"},
	"master card": {"master card", "mastercard", "ماستر كارد", "ماستركارد"},
	"tamara": {"tamara", "تمارا"},
	"tabby": {"tabby", "تابي"},
	"bank transfer": {"bank transfer", "banktransfer", "تحويل بنكي", "تحويل"},
	"american express": {"american express", "amex", "americanexpress"},
}

POS_DOCTYPES = ("Sales Invoice", "POS Invoice")


def apply_pos_invoice_defaults(doc, method=None):
	"""Doc event: fill POS-safe defaults before Frappe validates mandatory fields."""

	if doc.doctype not in POS_DOCTYPES:
		return

	profile = _get_profile(doc.get("pos_profile"))
	if not profile:
		return

	previous = _previous_invoice_state(doc)
	previous_modes = _previous_payment_modes(doc)

	# Explicit POS Profile configuration wins over the built-in heuristics.
	_apply_configured_defaults(doc, profile)
	_apply_cost_center(
		doc,
		profile,
		previous,
		allow_customer_override=not _has_configured_field(profile, "cost_center"),
	)
	_apply_payment_method(doc, profile, previous_modes)

	if cint(profile.get("posa_ignore_mandatory_fields")):
		_assert_core_fields(doc)
		doc.flags.ignore_mandatory = True


# ---------------------------------------------------------------------------
# Cost center resolution
# ---------------------------------------------------------------------------


def resolve_cost_center(doc, profile):
	"""Resolve a usable leaf cost center for a POS invoice."""

	company = doc.get("company") or profile.get("company")

	customer = doc.get("customer")
	if customer:
		cost_center = _customer_cost_center(customer, company)
		if cost_center:
			return cost_center

	profile_cost_center = profile.get("cost_center")
	if _is_usable_cost_center(profile_cost_center, company):
		return profile_cost_center

	company_cost_center = frappe.db.get_value("Company", company, "cost_center")
	if _is_usable_cost_center(company_cost_center, company):
		return company_cost_center

	# If the company has exactly one leaf, use it.  With two or more branches
	# choosing one would silently post the sale to the wrong branch.
	leaves = frappe.get_all(
		"Cost Center",
		filters={"company": company, "is_group": 0, "disabled": 0},
		pluck="name",
		limit=2,
	)
	if len(leaves) == 1:
		return leaves[0]

	return None


def _apply_cost_center(doc, profile, previous=None, allow_customer_override=True):
	resolved = resolve_cost_center(doc, profile)
	previous_cost_center = previous.get("cost_center") if previous else None
	customer_changed = bool(
		previous and previous.get("customer") != doc.get("customer")
	)

	# A cashier can change the customer on a saved draft.  The old cost center
	# belongs to the old customer, so replace it when it is still the value we
	# derived before (a manually edited cost center is preserved).
	if (
		allow_customer_override
		and customer_changed
		and resolved
		and doc.get("cost_center") in (None, previous_cost_center)
	):
		doc.cost_center = resolved

	if not doc.get("cost_center"):
		doc.cost_center = resolved

	# ERPNext posts GL rows from the item cost center first, and it fills that
	# from the item/company default before this hook runs.  The POS has no
	# per-item cost center control, so keep every row aligned with the invoice
	# cost center; otherwise the customer's branch would be ignored by the GL.
	if doc.get("cost_center"):
		for item in doc.get("items") or []:
			item.cost_center = doc.get("cost_center")


def _customer_cost_center(customer, company):
	if not _has_field("Customer", "posa_cost_center"):
		return None

	cost_center = frappe.db.get_value("Customer", customer, "posa_cost_center")
	if _is_usable_cost_center(cost_center, company):
		return cost_center

	customer_group = frappe.db.get_value("Customer", customer, "customer_group")
	return _customer_group_cost_center(customer_group, company)


def _customer_group_cost_center(customer_group, company):
	if not customer_group or not _has_field("Customer Group", "posa_cost_center"):
		return None

	seen = set()
	for _depth in range(10):
		if not customer_group or customer_group in seen:
			break
		seen.add(customer_group)

		cost_center = frappe.db.get_value(
			"Customer Group", customer_group, "posa_cost_center"
		)
		if _is_usable_cost_center(cost_center, company):
			return cost_center

		customer_group = frappe.db.get_value(
			"Customer Group", customer_group, "parent_customer_group"
		)

	return None


def _is_usable_cost_center(cost_center, company):
	if not cost_center:
		return False

	row = frappe.db.get_value(
		"Cost Center",
		cost_center,
		["company", "is_group", "disabled"],
		as_dict=True,
	)
	return bool(
		row
		and row.get("company") == company
		and not cint(row.get("is_group"))
		and not cint(row.get("disabled"))
	)


# ---------------------------------------------------------------------------
# POS Profile field defaults
# ---------------------------------------------------------------------------


def _apply_configured_defaults(doc, profile):
	for row in profile.get("posa_invoice_field_defaults") or []:
		fieldname = (row.get("fieldname") or "").strip()
		if not fieldname or not doc.meta.has_field(fieldname):
			continue
		if doc.get(fieldname) not in (None, ""):
			continue

		value = _resolve_default_value(row, doc, profile)
		if value not in (None, ""):
			doc.set(fieldname, value)


def _has_configured_field(profile, fieldname):
	return any(
		(row.get("fieldname") or "").strip() == fieldname
		for row in profile.get("posa_invoice_field_defaults") or []
	)


def _resolve_default_value(row, doc, profile):
	source = row.get("source")
	company = doc.get("company") or profile.get("company")
	customer = doc.get("customer")

	if source == "Static Value":
		return row.get("value")

	if source == "Payment Mode":
		return _match_payment_option_for_field(doc, row.get("fieldname"))

	if source == "Customer Cost Center":
		return _customer_cost_center(customer, company) if customer else None

	if source == "Customer Group Cost Center":
		if not customer:
			return None
		group = frappe.db.get_value("Customer", customer, "customer_group")
		return _customer_group_cost_center(group, company)

	if source == "POS Profile Cost Center":
		cost_center = profile.get("cost_center")
		return cost_center if _is_usable_cost_center(cost_center, company) else None

	if source == "Company Cost Center":
		cost_center = frappe.db.get_value("Company", company, "cost_center")
		return cost_center if _is_usable_cost_center(cost_center, company) else None

	return None


# ---------------------------------------------------------------------------
# Payment mode -> required Select field
# ---------------------------------------------------------------------------


def _apply_payment_method(doc, profile=None, previous_modes=None):
	modes = _payment_modes(doc)
	if not modes:
		return

	previous_modes = previous_modes or []

	for field in doc.meta.fields:
		if field.fieldtype != "Select" or not cint(field.reqd):
			continue
		if profile and _has_configured_field(profile, field.fieldname):
			continue

		mapped_now = _match_option(field.options, modes)
		if not mapped_now:
			continue

		current = doc.get(field.fieldname)
		if not current:
			doc.set(field.fieldname, mapped_now)
			continue

		# A cashier can change the payment mode on a saved draft.  Update the
		# value only when it still matches what the previous modes produced, so
		# a manual edit is never overwritten.
		if previous_modes:
			mapped_before = _match_option(field.options, previous_modes)
			if (
				mapped_before
				and current == mapped_before
				and current != mapped_now
			):
				doc.set(field.fieldname, mapped_now)


def _match_payment_option_for_field(doc, fieldname):
	field = doc.meta.get_field(fieldname)
	if not field or field.fieldtype != "Select":
		return None
	return _match_option(field.options, _payment_modes(doc))


def _payment_modes(doc):
	rows = list(doc.get("payments") or [])
	rows.sort(key=lambda row: flt(row.get("amount")), reverse=True)

	modes = []
	for row in rows:
		mode = str(row.get("mode_of_payment") or "").strip()
		if mode:
			modes.append(mode)
	return modes


def _match_option(options, modes):
	option_list = [option.strip() for option in (options or "").splitlines() if option.strip()]
	if not option_list:
		return None

	for mode in modes:
		aliases = _aliases_for(mode)
		for option in option_list:
			if _normalize(option) in aliases:
				return option
	return None


def _aliases_for(mode):
	key = _normalize(mode)
	aliases = {key}

	for canonical, values in PAYMENT_MODE_ALIASES.items():
		group = {canonical} | values
		if key in group:
			aliases |= group
			break

	return aliases


def _normalize(value):
	return re.sub(r"\s+", " ", (value or "").strip().lower())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_profile(profile_name):
	if not profile_name:
		return None
	try:
		return frappe.get_cached_doc("POS Profile", profile_name)
	except frappe.DoesNotExistError:
		return None


def _previous_invoice_state(doc):
	"""Return the stored customer / cost center for a saved draft."""

	if not doc.get("name") or doc.is_new():
		return None

	return frappe.db.get_value(
		doc.doctype,
		doc.name,
		["customer", "cost_center"],
		as_dict=True,
	)


def _previous_payment_modes(doc):
	"""Return the stored payment modes for a saved draft."""

	if not doc.get("name") or doc.is_new():
		return []

	payments_field = doc.meta.get_field("payments")
	if not payments_field or not payments_field.options:
		return []

	return frappe.get_all(
		payments_field.options,
		filters={
			"parent": doc.name,
			"parenttype": doc.doctype,
			"parentfield": "payments",
		},
		pluck="mode_of_payment",
	)


def _has_field(doctype, fieldname):
	return frappe.get_meta(doctype).has_field(fieldname)


def _assert_core_fields(doc):
	missing = []
	if not doc.get("company"):
		missing.append("company")
	if not doc.get("customer"):
		missing.append("customer")
	if not doc.get("posting_date"):
		missing.append("posting_date")
	if not doc.get("items"):
		missing.append("items")

	if missing:
		frappe.throw(
			frappe._("POS invoice is missing required core fields: {0}").format(
				", ".join(missing)
			)
		)
