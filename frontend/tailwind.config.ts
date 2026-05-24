import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50:  "#F2F4F8",
          100: "#DDE2EC",
          200: "#B8C0D2",
          300: "#8C97B0",
          400: "#5D6A87",
          500: "#38456A",
          600: "#1F2B4F",
          700: "#16203E",
          800: "#11192F",
          900: "#0F1629",
        },
        green: {
          50:  "#ECFDF5",
          100: "#D1FAE5",
          200: "#A7F3D0",
          300: "#6EE7B7",
          400: "#34D399",
          500: "#10B981",
          600: "#059669",
          700: "#047857",
        },
        amber: {
          50:  "#FFFBEB",
          100: "#FEF3C7",
          200: "#FDE68A",
          300: "#FCD34D",
          400: "#FBBF24",
          500: "#F59E0B",
          600: "#D97706",
          700: "#B45309",
        },
        slate: {
          50:  "#F8FAFC",
          100: "#F1F5F9",
          200: "#E2E8F0",
          300: "#CBD5E1",
          400: "#94A3B8",
          500: "#64748B",
          600: "#475569",
          700: "#334155",
          800: "#1E293B",
          900: "#0F172A",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "sans-serif"],
      },
      boxShadow: {
        card:     "0 1px 2px rgba(15, 22, 41, 0.04)",
        elevated: "0 8px 24px -8px rgba(15, 22, 41, 0.12)",
        modal:    "0 24px 64px -16px rgba(15, 22, 41, 0.24)",
        focus:    "0 0 0 2px #FFFFFF, 0 0 0 4px #2563EB",
      },
      borderRadius: {
        sm:   "4px",
        md:   "8px",
        lg:   "12px",
        xl:   "16px",
        "2xl": "20px",
      },
    },
  },
  plugins: [],
};

export default config;
