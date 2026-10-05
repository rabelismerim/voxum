/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef6ff',
          100: '#e0f0fe',
          200: '#bae2fd',
          300: '#7ccbfd',
          400: '#36b2fa',
          500: '#0c96eb',
          DEFAULT: '#0284c7',
          hover: '#0369a1',
          700: '#035485',
          800: '#07476f',
          900: '#0c3c5d',
        },
        // Fundo escuro (Preto e Grafite)
        dark: {
          bg: '#090d16',       // Fundo geral das páginas
          card: '#111827',     // Cards e modais
          border: '#1f2937',   // Bordas e divisores
          hover: '#1f2937',    // Estados de hover em tabelas e botões
        },
      },
    },
  },
  plugins: [],
}