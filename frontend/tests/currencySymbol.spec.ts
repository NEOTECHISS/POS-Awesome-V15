// @vitest-environment jsdom

import { afterEach, describe, expect, it, vi } from "vitest";

import { resolveCurrencySymbol } from "../src/posapp/utils/currencySymbol";

describe("resolveCurrencySymbol", () => {
	afterEach(() => {
		vi.unstubAllGlobals();
	});

	it("normalizes the bad SAR master symbol to the official Riyal glyph", () => {
		vi.stubGlobal("get_currency_symbol", () => "§");

		expect(resolveCurrencySymbol("SAR")).toBe("\u20C1 ");
	});

	it("normalizes the legacy rial sign for SAR as well", () => {
		vi.stubGlobal("get_currency_symbol", () => "﷼");

		expect(resolveCurrencySymbol("SAR")).toBe("\u20C1 ");
	});

	it("preserves a valid custom SAR symbol", () => {
		vi.stubGlobal("get_currency_symbol", () => "\u20C1");

		expect(resolveCurrencySymbol("SAR")).toBe("\u20C1 ");
	});

	it("uses the official Riyal glyph when the master stores the ISO code", () => {
		vi.stubGlobal("get_currency_symbol", () => "SAR");

		expect(resolveCurrencySymbol("SAR")).toBe("\u20C1 ");
	});

	it("preserves configured symbols for other currencies", () => {
		vi.stubGlobal("get_currency_symbol", () => "$");

		expect(resolveCurrencySymbol("USD")).toBe("$");
	});

	it("respects Frappe's hide-currency-symbol setting", () => {
		vi.stubGlobal("get_currency_symbol", () => null);

		expect(resolveCurrencySymbol("SAR")).toBe("");
	});

	it("falls back to Intl when the master resolver is unavailable", () => {
		vi.stubGlobal("get_currency_symbol", undefined);

		expect(resolveCurrencySymbol("SAR")).toBe("\u20C1 ");
		expect(resolveCurrencySymbol("USD")).toBe("$");
	});

	it("returns an empty symbol when no currency is supplied", () => {
		expect(resolveCurrencySymbol("")).toBe("");
	});
});
