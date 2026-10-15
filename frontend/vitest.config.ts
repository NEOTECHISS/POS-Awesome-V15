import { defineConfig } from "vitest/config";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath } from "node:url";

// Tests compile real Vue templates, without build-only style writes or
// production/browser defines from the Frappe bundle configuration.
export default defineConfig({
	plugins: [vue()],
	resolve: {
		alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) },
	},
	define: { __BUILD_VERSION__: JSON.stringify("test") },
	test: {
		include: [
			"tests/**/*.spec.{js,ts}",
			"tests/**/*.test.{js,ts}",
			"src/**/__tests__/**/*.{js,ts}",
		],
		exclude: ["tests/smoke/**", "tests/e2e/**", "tests/performance/TTI.spec.ts"],
	},
});
