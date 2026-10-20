import { describe, expect, it } from "vitest";

import {
	DATA_TABLE_EXPAND_COLUMN,
	buildFinalVisibleColumns,
	getItemSelectorVisibleHeaders,
	getResponsiveVisibleHeaders,
} from "../src/posapp/composables/pos/items/useItemsTableResponsive";

const headers = [
	{ key: "item_name", title: "Name", required: true },
	{ key: "qty", title: "QTY", required: true },
	{ key: "uom", title: "UOM" },
	{ key: "price_list_rate", title: "Price List Rate" },
	{ key: "discount_percentage", title: "Discount %" },
	{ key: "discount_amount", title: "Discount Amount" },
	{ key: "rate", title: "Rate", required: true },
	{ key: "amount", title: "Amount", required: true },
	{ key: "posa_is_offer", title: "Offer?" },
	{ key: "actions", title: "Actions", required: true },
];

describe("items table final visible columns", () => {
	it("keeps the body column order aligned with the responsive header order and appends expand", () => {
		const visible = buildFinalVisibleColumns(headers, 1200);

		expect(visible.map((column) => column.key)).toEqual([
			"item_name",
			"qty",
			"uom",
			"price_list_rate",
			"discount_percentage",
			"discount_amount",
			"rate",
			"amount",
			"posa_is_offer",
			"actions",
			"data-table-expand",
		]);
	});

	it("keeps selected optional columns visible in normal POS pane widths", () => {
		const responsive = getResponsiveVisibleHeaders(headers, 600);
		const finalColumns = buildFinalVisibleColumns(headers, 600);

		expect(responsive.map((column) => column.key)).toEqual([
			"item_name",
			"qty",
			"uom",
			"price_list_rate",
			"discount_percentage",
			"discount_amount",
			"rate",
			"amount",
			"posa_is_offer",
			"actions",
		]);
		expect(finalColumns.slice(0, -1)).toEqual(responsive);
		expect(finalColumns.at(-1)?.key).toBe("data-table-expand");
		expect(
			responsive.find((column) => column.key === "item_name")?.minWidth,
		).toBe(160);
		expect(
			responsive.find((column) => column.key === "qty")?.minWidth,
		).toBe(92);
		expect(
			responsive.find((column) => column.key === "actions")?.minWidth,
		).toBe(68);
	});

	it("fits every selected column inside a standard desktop invoice pane", () => {
		const paneWidth = 1020;
		const responsive = getResponsiveVisibleHeaders(headers, paneWidth);
		const occupiedWidth = responsive.reduce(
			(total, column) => total + Number(column.width || 0),
			Number(DATA_TABLE_EXPAND_COLUMN.width),
		);

		expect(responsive).toHaveLength(headers.length);
		expect(occupiedWidth).toBeLessThanOrEqual(paneWidth);
		expect(
			responsive.find((column) => column.key === "item_name")?.minWidth,
		).toBe(148);
		expect(
			responsive.find((column) => column.key === "actions")?.minWidth,
		).toBe(56);
	});

	it("keeps the expand column even when the responsive layout collapses optional fields", () => {
		const finalColumns = buildFinalVisibleColumns(headers, 420);

		expect(finalColumns.map((column) => column.key)).toEqual([
			"item_name",
			"qty",
			"rate",
			"amount",
			"actions",
			"data-table-expand",
		]);
	});

	it("prioritizes name, rate and stock in the compact item picker", () => {
		const pickerHeaders = [
			{ key: "item_name", title: "Name" },
			{ key: "item_code", title: "Code" },
			{ key: "rate", title: "Rate" },
			{ key: "actual_qty", title: "Available QTY" },
			{ key: "stock_uom", title: "UOM" },
		];

		const compact = getItemSelectorVisibleHeaders(pickerHeaders, 360);

		expect(compact.map((column) => column.key)).toEqual([
			"item_name",
			"rate",
			"actual_qty",
		]);
		expect(compact.find((column) => column.key === "item_name")?.minWidth).toBe(0);
		expect(compact.find((column) => column.key === "rate")).toMatchObject({
			align: "end",
			width: 112,
			minWidth: 112,
			nowrap: true,
		});
		expect(compact.find((column) => column.key === "actual_qty")).toMatchObject({
			title: "Qty",
			align: "end",
			width: 80,
			minWidth: 80,
			nowrap: true,
		});
	});

	it("does not hide picker columns when the container is wide", () => {
		const pickerHeaders = [
			{ key: "item_name", title: "Name" },
			{ key: "item_code", title: "Code" },
			{ key: "rate", title: "Rate" },
			{ key: "actual_qty", title: "Available QTY" },
			{ key: "stock_uom", title: "UOM" },
		];

		expect(getItemSelectorVisibleHeaders(pickerHeaders, 900)).toEqual(
			pickerHeaders,
		);
	});
});
