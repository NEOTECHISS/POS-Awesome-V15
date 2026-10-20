import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const testsDir = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(testsDir, "..");
const source = (...segments: string[]) =>
	readFileSync(path.join(frontendDir, "src", "posapp", ...segments), "utf8");

describe("mobile currency and amount layout", () => {
	it("defines a shared non-wrapping price line", () => {
		const theme = source("styles", "theme.css");

		expect(theme).toContain(".posa-price-line {");
		expect(theme).toContain("flex-wrap: nowrap;");
		expect(theme).toContain("white-space: nowrap;");
		expect(theme).toContain(".posapp .currency-symbol");
	});

	it("keeps the item picker rate and amount on one line and frees mobile width", () => {
		const table = source("components", "pos", "items", "ItemsSelectorTable.vue");

		expect(table).toContain("getItemSelectorVisibleHeaders");
		expect(table).toContain("rate-value");
		expect(table).toContain("posa-price-line");
		expect(table).toContain(":cell-props=\"getCellProps\"");
		expect(table).toContain("table-layout: fixed");
	});

	it("does not allow item card prices to wrap", () => {
		const card = source("components", "pos", "items", "ItemCard.vue");

		expect(card).toMatch(/\.primary-price\s*\{[^}]*flex-wrap:\s*nowrap/s);
		expect(card).toMatch(/\.price-amount\s*\{[^}]*white-space:\s*nowrap/s);
		expect(card).toMatch(/\.secondary-price\s*\{[^}]*white-space:\s*nowrap/s);
	});

	it("keeps cart and pharmacy rate lines non-wrapping", () => {
		const cart = source("components", "pos", "invoice", "CartItemRow.vue");
		const pharmacy = source(
			"components",
			"pos",
			"items",
			"PharmacyItemSearchTable.vue",
		);

		expect(cart).toMatch(/\.currency-display\s*\{[^}]*white-space:\s*nowrap/s);
		expect(cart).toMatch(/\.currency-symbol\s*\{[^}]*flex:\s*0 0 auto/s);
		expect(pharmacy).toContain("pharmacy-rate-cell posa-price-line");
		expect(pharmacy).toMatch(
			/\.pharmacy-rate-cell\s*\{[^}]*white-space:\s*nowrap/s,
		);
	});

	it("keeps receipt rate and amount columns non-wrapping", () => {
		const receipt = readFileSync(
			path.join(frontendDir, "src", "offline_print_template.ts"),
			"utf8",
		);

		expect(receipt).toContain(
			"td.qty, td.rate, td.amount { text-align: right; white-space: nowrap; }",
		);
	});
});
