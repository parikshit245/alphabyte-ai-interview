const config = require("@repo/tailwind-config/tailwind.config");

/** @type {import('tailwindcss').Config} */
module.exports = {
  presets: [config],
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx}",
    // Tremor content
    "../../node_modules/@tremor/**/*.{js,ts,jsx,tsx}",
  ],
};
