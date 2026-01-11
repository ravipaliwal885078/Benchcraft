/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Xebia theme colors from the provided image
        primary: {
          DEFAULT: '#7C3AED', // Vibrant purple (main streak)
          dark: '#4C1D95',    // Deep purple (background)
          light: '#A78BFA',   // Light purple (highlight)
        },
        accent: {
          DEFAULT: '#F59E42', // Orange accent (streak)
          light: '#FDE68A',   // Light orange
        },
        background: {
          DEFAULT: '#FFFFFF', // Clean white background
          secondary: '#F8FAFC', // Very light gray for secondary backgrounds
        },
        surface: '#FFFFFF', // White surface for cards/modals
        foreground: '#0F172A', // Dark slate for text
        muted: {
          DEFAULT: '#64748B', // Muted text color
          foreground: '#94A3B8', // Even more muted
        },
        // Gradients for streaks (for use with bg-gradient-to-x)
        xebiaGradient1: 'linear-gradient(90deg, #7C3AED 0%, #A78BFA 100%)',
        xebiaGradient2: 'linear-gradient(90deg, #F59E42 0%, #7C3AED 100%)',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
