/**
 * Resolves the currency symbol shown by the POS.
 *
 * Frappe reads the symbol from the Currency master. Some sites still have an
 * incorrect SAR symbol (`§`) in that record. The POS bundles the official
 * Saudi Riyal font (U+20C1), so SAR falls back to that glyph when the master
 * value is not a usable symbol. Every other currency keeps its configured
 * symbol unchanged.
 */

const SAUDI_RIYAL_SYMBOL = "\u20C1";
const BAD_SAR_SYMBOLS = new Set(["§", "﷼", "SAR"]);

function configuredSymbol(currency: string): string | null | undefined {
	if (typeof window === "undefined") {
		return undefined;
	}
	const resolver = (window as any).get_currency_symbol;
	if (typeof resolver !== "function") {
		return undefined;
	}
	return resolver(currency);
}

function intlSymbol(currency: string): string {
	try {
		const parts = new Intl.NumberFormat("en-US", {
			style: "currency",
			currency,
			currencyDisplay: "narrowSymbol",
		}).formatToParts(0);
		return (
			parts.find((part) => part.type === "currency")?.value?.trim() || ""
		);
	} catch {
		return "";
	}
}

export function resolveCurrencySymbol(currency?: string | null): string {
	const code = String(currency || "").trim();
	if (!code) {
		return "";
	}

	const configured = configuredSymbol(code);
	if (configured === null) {
		// Respect Frappe's "hide currency symbol" setting.
		return "";
	}

	const symbol =
		typeof configured === "string" ? configured.trim() : configured;

	if (code.toUpperCase() === "SAR") {
		const display =
			symbol && !BAD_SAR_SYMBOLS.has(symbol)
				? symbol
				: SAUDI_RIYAL_SYMBOL;
		return display.endsWith(" ") ? display : `${display} `;
	}

	return symbol || intlSymbol(code) || code;
}
