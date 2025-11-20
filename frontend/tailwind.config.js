/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./pages/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0dd3c9",
          muted: "#0b9c95",
        },
        slate: {
          950: "#020617",
        },
        accent: "#f5c453",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.25rem",
        "3xl": "1.75rem",
      },
      fontFamily: {
        sans: ["Inter", "Space Grotesk", "var(--font-sans)", "sans-serif"],
      },
    },
  },
  plugins: [],
};

