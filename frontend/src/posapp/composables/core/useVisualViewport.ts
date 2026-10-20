import { onBeforeUnmount, onMounted } from "vue";

/**
 * Mobile viewport plumbing for the POS shell.
 *
 * The POS shell is a fixed-height surface (`100dvh`, `overflow: hidden`) with
 * an inner scroller. That is the right model for a till, but it means the
 * browser cannot rely on document scroll to reveal a focused input. On
 * Android/iOS the on-screen keyboard shrinks the *visual* viewport without
 * resizing the layout viewport, so inputs and totals can end up behind the
 * keyboard.
 *
 * This composable:
 * - publishes `--posa-viewport-height` only while a keyboard is detected, so
 *   the shell can shrink to the visible area;
 * - publishes `--posa-keyboard-inset` for bottom docks / snackbars;
 * - scrolls the focused field back into view after the keyboard animation.
 *
 * It is intentionally inert on desktop: `visualViewport` matches the layout
 * viewport there, so no custom properties are set and the `100dvh` fallback
 * stays in charge.
 */

const KEYBOARD_THRESHOLD_PX = 120;
const FOCUS_SCROLL_DELAY_MS = 180;
const EDITABLE_SELECTOR = "input, textarea, select, [contenteditable='true']";

export function useVisualViewport() {
	let frame: number | null = null;
	let focusTimer: number | null = null;

	const root = () => document.documentElement;

	const clearInsetVars = () => {
		root().style.removeProperty("--posa-viewport-height");
		root().style.removeProperty("--posa-keyboard-inset");
	};

	const sync = () => {
		const viewport = window.visualViewport;
		if (!viewport) return;

		const inset = Math.max(
			0,
			window.innerHeight - viewport.height - viewport.offsetTop,
		);

		if (inset > KEYBOARD_THRESHOLD_PX) {
			root().style.setProperty(
				"--posa-viewport-height",
				`${Math.round(viewport.height)}px`,
			);
			root().style.setProperty("--posa-keyboard-inset", `${Math.round(inset)}px`);
		} else {
			clearInsetVars();
		}
	};

	const scheduleSync = () => {
		if (frame !== null) cancelAnimationFrame(frame);
		frame = requestAnimationFrame(() => {
			frame = null;
			sync();
		});
	};

	const keepFocusVisible = () => {
		const active = document.activeElement;
		if (!(active instanceof HTMLElement)) return;
		if (!active.matches(EDITABLE_SELECTOR)) return;
		if (active.closest("[data-pos-ignore-viewport]")) return;

		if (focusTimer !== null) window.clearTimeout(focusTimer);
		focusTimer = window.setTimeout(() => {
			if (document.activeElement !== active) return;
			active.scrollIntoView({ block: "center", inline: "nearest" });
		}, FOCUS_SCROLL_DELAY_MS);
	};

	onMounted(() => {
		window.visualViewport?.addEventListener("resize", scheduleSync);
		window.visualViewport?.addEventListener("scroll", scheduleSync);
		document.addEventListener("focusin", keepFocusVisible);
		sync();
	});

	onBeforeUnmount(() => {
		window.visualViewport?.removeEventListener("resize", scheduleSync);
		window.visualViewport?.removeEventListener("scroll", scheduleSync);
		document.removeEventListener("focusin", keepFocusVisible);
		if (frame !== null) cancelAnimationFrame(frame);
		if (focusTimer !== null) window.clearTimeout(focusTimer);
		clearInsetVars();
	});
}
