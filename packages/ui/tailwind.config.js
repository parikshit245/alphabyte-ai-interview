const config = require("@repo/tailwind-config/tailwind.config");

/** @type {import('tailwindcss').Config} */
module.exports = {
  presets: [config],
  content: ["./src/**/*.{ts,tsx}"],
};
