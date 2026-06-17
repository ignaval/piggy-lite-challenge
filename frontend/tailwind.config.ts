import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        piggy: {
          50: "#fdf2f8",
          100: "#fce7f3",
          500: "#ec4899",
          600: "#db2777",
          700: "#be185d",
        },
      },
    },
  },
  plugins: [],
};

export default config;
