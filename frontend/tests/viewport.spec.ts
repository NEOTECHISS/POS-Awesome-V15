// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest";

const originalContent =
	"width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no, minimal-ui";

function installViewportMeta(content = originalContent) {
	document.head.innerHTML = "";
	const meta = document.createElement("meta");
	meta.name = "viewport";
	meta.content = content;
	document.head.appendChild(meta);
	return meta;
}

async function loadViewportModule() {
	vi.resetModules();
	return import("../src/posapp/utils/viewport");
}

describe("POS viewport contract", () => {
	beforeEach(() => {
		installViewportMeta();
	});

	it("enables zoom and safe-area insets while the POS is mounted", async () => {
		const { applyPosViewport } = await loadViewportModule();
		const meta = document.querySelector('meta[name="viewport"]') as HTMLMetaElement;

		applyPosViewport();

		expect(meta.content).toContain("viewport-fit=cover");
		expect(meta.content).toContain("maximum-scale=5");
		expect(meta.content).not.toContain("user-scalable=no");
	});

	it("restores the desk viewport on unmount", async () => {
		const { applyPosViewport, restorePosViewport } = await loadViewportModule();
		const meta = document.querySelector('meta[name="viewport"]') as HTMLMetaElement;

		applyPosViewport();
		restorePosViewport();

		expect(meta.content).toBe(originalContent);
	});

	it("is idempotent across repeated mounts", async () => {
		const { applyPosViewport, restorePosViewport } = await loadViewportModule();
		const meta = document.querySelector('meta[name="viewport"]') as HTMLMetaElement;

		applyPosViewport();
		applyPosViewport();
		restorePosViewport();

		expect(meta.content).toBe(originalContent);
	});

	it("does nothing when the shell has no viewport meta", async () => {
		document.head.innerHTML = "";
		const { applyPosViewport, restorePosViewport } = await loadViewportModule();

		expect(() => {
			applyPosViewport();
			restorePosViewport();
		}).not.toThrow();
	});
});
