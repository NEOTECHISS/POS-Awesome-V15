import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const testsDir = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(testsDir, "..");
const source = (...segments: string[]) =>
	readFileSync(path.join(frontendDir, "src", "posapp", ...segments), "utf8");

describe("barcode printing handheld layout", () => {
	const printing = source(
		"components",
		"pos",
		"shell",
		"BarcodePrinting.vue",
	);

	it("switches between item picking and the print workspace on narrow screens", () => {
		expect(printing).toContain(
			"const isMobileLayout = computed(() => windowWidth.value < 960)",
		);
		expect(printing).toContain('v-model="mobilePane"');
		expect(printing).toContain("barcode-mobile-tabs");
		expect(printing).toContain("barcode-pane-hidden");
		expect(printing).toContain("barcode-mobile-items-bar");
		expect(printing).toMatch(
			/\.barcode-pane-hidden\s*\{[^}]*display:\s*none\s*!important/s,
		);
		expect(printing).not.toMatch(
			/v-show="!isMobileLayout \|\| mobilePane ===/,
		);
	});

	it("renders a touch-friendly print queue instead of the wide data table", () => {
		expect(printing).toContain(
			'<v-data-table\n\t\t\t\t\t\t\tv-if="!isMobileLayout"',
		);
		expect(printing).toContain("barcode-mobile-queue");
		expect(printing).toContain("barcode-queue-card");
		expect(printing).toContain("barcode-mobile-printbar");
		expect(printing).toContain("openPreview");
		expect(printing).toContain("downloadPdf(items)");
		expect(printing).toContain("printLabels(items)");
		expect(printing).toMatch(
			/\.barcode-queue-card__metric > strong\s*\{[^}]*white-space:\s*nowrap/s,
		);
		expect(printing).toMatch(
			/\.barcode-mobile-printbar\s*\{[^}]*grid-template-columns:\s*repeat\(4/s,
		);
		expect(printing).toContain(":id=\"'qty-input-' + item._row_id\"");
		expect(printing).not.toContain("qty-input-mobile-");
	});

	it("opens complex dialogs fullscreen and keeps setup fields compact", () => {
		expect(printing.match(/:fullscreen="isMobileLayout"/g)?.length).toBe(4);
		expect(printing).toContain("barcode-mobile-setup");
		expect(printing).toContain("barcode-settings-block");
		expect(printing).toContain("barcode-dialog-actions");
		expect(printing).toContain("barcode-sscc-actions");
		expect(printing).toMatch(
			/\.barcode-config-row :deep\(\.v-col\)[^{]*\{[^}]*padding:\s*4px/s,
		);
	});

	it("fits preview labels to the handheld viewport without changing print output", () => {
		expect(printing).toContain(
			'<meta name="viewport" content="width=device-width, initial-scale=1">',
		);
		expect(printing).toContain("fitLabels");
		expect(printing).toContain("label.style.zoom");
		expect(printing).toMatch(
			/@media screen[\s\S]*?\.label\s*\{[^}]*flex:\s*0 0 auto/,
		);
		expect(printing).toContain(
			"Barcode preview could not render every barcode",
		);
		expect(printing).toMatch(
			/\.barcode-preview-actions\s*\{[^}]*flex-wrap:\s*wrap/s,
		);
	});
});

describe("barcode designer handheld layout", () => {
	const designer = source("components", "pos", "shell", "LabelDesigner.vue");
	const panel = source(
		"components",
		"pos",
		"shell",
		"LabelDesignerPanel.vue",
	);
	const verification = source(
		"components",
		"pos",
		"shell",
		"VerificationDialog.vue",
	);

	it("wraps the designer toolbar and tool box instead of overflowing", () => {
		expect(designer).toMatch(
			/@media \(max-width: 959\.98px\)[\s\S]*\.designer-toolbar\s*\{[^}]*flex-wrap:\s*wrap/s,
		);
		expect(designer).toMatch(
			/\.designer-toolbox\s*\{[^}]*flex-wrap:\s*wrap/s,
		);
		expect(designer).toMatch(
			/\.designer-scroll\s*\{[^}]*justify-content:\s*flex-start/s,
		);
		expect(designer).toContain(':y2="canvasPx.height"');
	});

	it("stacks the properties panel and keeps the dialog usable on small screens", () => {
		expect(panel).toMatch(
			/@media \(max-width: 959\.98px\)[\s\S]*\.panel-root\s*\{[^}]*border-left:\s*0/s,
		);
		expect(verification).toContain("() => props.modelValue");
		expect(verification).toMatch(
			/@media \(max-width: 600px\)[\s\S]*\.v-list-item-title,[\s\S]*white-space:\s*normal/s,
		);
	});
});
