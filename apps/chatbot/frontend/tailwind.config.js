/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "./styles/**/*.{css}",
    "../../shared/**/*.ts"
  ],
  theme: {
    extend: {}
  },
  plugins: []
};
