/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#f5efe4',
        panel: '#fffaf2',
        'panel-strong': '#f1e4d0',
        ink: '#20201c',
        muted: '#68624e',
        accent: '#a44b1a',
        'accent-soft': '#d77b46',
        line: 'rgba(32, 32, 28, 0.1)',
        'bucket-test': '#275d38',
        'bucket-build': '#8c641f',
        'bucket-archive': '#6e6e62',
        'bucket-ignore': '#7f2f2f',
      },
      fontFamily: {
        serif: ['Georgia', 'Times New Roman', 'serif'],
      },
    },
  },
  plugins: [],
};

export default config;
