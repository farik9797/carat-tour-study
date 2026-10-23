/** Carat Tour & Study — Tailwind config (палитра снята с макета) */
module.exports = {
  content: ['./src/templates/**/*.html', './src/assets/js/**/*.js', './build.py'],
  theme: {
    extend: {
      colors: {
        navy: { DEFAULT: '#0B2A7A', 50: '#EEF3FB', 100: '#DCE6F7', 600: '#123A9A', 700: '#0B2A7A', 800: '#082061', 900: '#062958', 950: '#041B3D' },
        accent: { DEFAULT: '#FEAA23', 50: '#FFF6E6', 400: '#FFB842', 500: '#FEAA23', 600: '#F09610' },
        sky: { 50: '#F4F8FD', 100: '#E4F0FD', 200: '#C9E0FA' },
        teal: { DEFAULT: '#0FA3B1', 500: '#0FA3B1', 600: '#027F9A' },
        ink: { DEFAULT: '#1E2B4A', soft: '#5B6B8C' },
      },
      fontFamily: {
        sans: ['Montserrat', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        hand: ['Caveat', 'cursive'],
      },
      boxShadow: {
        card: '0 6px 24px -8px rgba(11,42,122,.18)',
        soft: '0 2px 12px -4px rgba(11,42,122,.12)',
        float: '0 20px 50px -18px rgba(11,42,122,.35)',
      },
      borderRadius: { xl2: '1.25rem' },
    },
  },
  corePlugins: { container: false }, // свой .container в input.css (контент 1300px)
  plugins: [],
};
