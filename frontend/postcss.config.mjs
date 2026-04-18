export default {
  plugins: {
    // Tailwind v4 ships its PostCSS integration as a separate package.
    // Without this plugin, Next serves raw `@apply` and utility directives
    // instead of compiled CSS, which breaks the whole visual layer.
    "@tailwindcss/postcss": {},
  },
};
