/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    fontSize: {
      sm: '0.75rem',
      base: '0.95rem',
      xl: '1.25rem',
      '2xl': '1.563rem',
      '3xl': '1.953rem',
      '4xl': '2.441rem',
      '5xl': '3.052rem',
      '6xl': '4.82rem',
    },
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        border: "rgb(145 187 255 / 30%)",
        primary: "#1865e3",
        secondary: "#939fad",
        tertiary: "#FFF",
        success: "#08E56B",
        "success-dark": "#02b753",
        warning: "#FFE625",
        "background-secondary": "rgb(239 239 239)",
        "background-tertiary": "rgb(239 239 239)",
      }
    },
  },
  plugins: [],
};
