# React (Vite)

This website is built with [Vite](https://vitejs.dev/) and [React](https://react.dev/).

## Commands

### `npm start` / `npm run dev`

Runs the app in development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page reloads when you make changes.

### `npm run build`

Builds the app for production into the `build` folder (same output path as the old CRA setup, so GitHub Pages deploy scripts stay the same).

### `npm run preview`

Serves the production build locally for a quick smoke test before deploy.

## Notes

- Entry HTML lives at the repo root (`index.html`); static files stay in `public/`.
- React components use `.jsx`; plain JS (e.g. `reportWebVitals.js`) stays `.js`.
- Dynamic game gallery images use Vite's `import.meta.glob` (see `src/components/Interests/index.jsx`).
- Dashboard CSV/JSON assets are imported from `src/assets/data/**`.
