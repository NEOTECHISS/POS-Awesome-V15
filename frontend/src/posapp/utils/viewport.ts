/**
 * Viewport contract for the POS shell.
 *
 * `/app/posapp` is rendered inside Frappe's desk shell
 * (`apps/frappe/frappe/www/app.html`), whose viewport meta disables zoom and
 * omits `viewport-fit=cover`. Both are wrong for a POS:
 *
 * - `user-scalable=no` / `maximum-scale=1.0` break WCAG 1.4.4 and make small
 *   quantity fields hard to operate on a phone.
 * - Without `viewport-fit=cover`, every `env(safe-area-inset-*)` resolves to
 *   `0px`, so notch / home-indicator handling never activates.
 *
 * We patch the meta while the POS is mounted and restore the desk value on
 * unmount, so the rest of the desk is untouched.
 */

const POS_VIEWPORT_CONTENT =
	"width=device-width, initial-scale=1, maximum-scale=5, viewport-fit=cover";

let previousContent: string | null = null;

function findViewportMeta(): HTMLMetaElement | null {
	if (typeof document === "undefined") return null;
	return document.querySelector<HTMLMetaElement>('meta[name="viewport"]');
}

export function applyPosViewport(): void {
	const meta = findViewportMeta();
	if (!meta) return;
	if (previousContent === null) {
		previousContent = meta.getAttribute("content") || "";
	}
	meta.setAttribute("content", POS_VIEWPORT_CONTENT);
}

export function restorePosViewport(): void {
	if (previousContent === null) return;
	const meta = findViewportMeta();
	if (meta) {
		meta.setAttribute("content", previousContent);
	}
	previousContent = null;
}

export { POS_VIEWPORT_CONTENT };
