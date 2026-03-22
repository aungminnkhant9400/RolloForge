/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  safelist: [
    'grid',
    'grid-cols-2',
    'md:grid-cols-4',
    'gap-4',
    'flex',
    'items-center',
    'justify-between',
    'p-4',
    'rounded-xl',
    'bg-panel',
    'text-ink',
    'text-muted',
    'text-accent',
    'max-w-7xl',
    'mx-auto',
    'px-4',
    'py-6',
    'space-y-8',
    'mb-8',
    'mt-6',
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
      },
      fontFamily: {
        serif: ['Georgia', 'Times New Roman', 'serif'],
      },
    },
  },
  plugins: [],
}