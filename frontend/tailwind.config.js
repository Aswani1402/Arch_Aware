/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        arch: {
          // Light Mode Palette
          bg: "#FBFBF9",
          card: "#FFFFFF",
          surface: "#F4F3EE",
          dark: "#1A1A18",
          charcoal: "#2C2C28",
          muted: "#767571",
          border: "#E8E6E0",
          terracotta: "#C86D51",
          "terracotta-dark": "#A85338",
          sage: "#5A6B5C",
          sand: "#E5DEC9",
          amber: "#D97706",

          // Dark Mode Architectural Palette
          "dark-bg": "#0E0F12",
          "dark-card": "#18191E",
          "dark-surface": "#212228",
          "dark-border": "#2C2E35",
          "dark-text": "#F3F3F1",
          "dark-muted": "#9A9AA0",
          "dark-terracotta": "#E07A5F",
        }
      },
      fontSize: {
        'brand': ['1.75rem', { lineHeight: '2.1rem', letterSpacing: '-0.02em', fontWeight: '700' }], // 28px
        'heading': ['1.625rem', { lineHeight: '2rem', letterSpacing: '-0.015em', fontWeight: '600' }], // 26px
        'cat': ['1.1875rem', { lineHeight: '1.6rem', letterSpacing: '-0.01em', fontWeight: '600' }], // 19px
        'subcat': ['1.0625rem', { lineHeight: '1.45rem', fontWeight: '500' }], // 17px
        'card-title': ['1.0625rem', { lineHeight: '1.45rem', fontWeight: '600' }], // 17px
        'body-base': ['1rem', { lineHeight: '1.5rem' }], // 16px
        'secondary': ['0.875rem', { lineHeight: '1.35rem' }], // 14px
        'xs': ['0.8125rem', { lineHeight: '1.2rem' }], // 13px - nothing below 13px
      },
      fontFamily: {
        serif: ["Cormorant Garamond", "serif"],
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
      boxShadow: {
        'card': '0 2px 10px rgba(0, 0, 0, 0.04)',
        'card-hover': '0 12px 28px rgba(0, 0, 0, 0.08)',
        'card-dark': '0 2px 10px rgba(0, 0, 0, 0.35)',
        'card-dark-hover': '0 12px 28px rgba(0, 0, 0, 0.55)',
      }
    },
  },
  plugins: [],
};
