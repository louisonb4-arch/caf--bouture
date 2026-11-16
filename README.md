# Café Bouture — site

- `dist/` : le site prêt à publier (Vercel : dossier racine = `dist`, aucune compilation).
- `src/index.html` : source à modifier, puis `python3 src/build.py` régénère `dist/`.
  (minification via html-minifier-terser : `npm i -g html-minifier-terser` et adapter le chemin dans build.py si besoin)
- `img/`, `fonts/` : photos AVIF/WebP en 2 tailles, polices auto-hébergées et allégées.
