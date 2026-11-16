#!/usr/bin/env python3
"""Build Café Bouture : src/index.html -> dist/ (images <picture>, étiquettes plantes, minification)."""
import re, shutil, subprocess, os, html, hashlib, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, DIST = ROOT / 'src', ROOT / 'dist'
DIMS = {'interior': (480, 490)}  # le reste : 480x600 (4:5)

def pic(m):
    name, alt, sizes, flag = (m.group(1).split('|') + [''] * 4)[:4]
    w, h = DIMS.get(name, (480, 600))
    eager = flag.strip() == 'eager'
    srcset = lambda ext: f'img/{name}-480.{ext} 480w, img/{name}-720.{ext} 720w, img/{name}-960.{ext} 960w'
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<img src="img/{name}-720.webp" srcset="{srcset("webp")}" sizes="{sizes}" '
            f'alt="{html.escape(alt)}" width="{w}" height="{h}" {load}></picture>')

G = 'stroke="#1A9A43" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"'
PLANTS = [
 ("Monstera", "Monstera deliciosa", "La star qui prend toute la place. Généreuse, un peu envahissante, impossible à ne pas aimer.",
  [("☀", "Lumière vive, sans soleil direct"), ("💧", "Arrosage quand le terreau est sec sur 3 cm"), ("✿", "Un tuteur en mousse pour grimper")],
  '<path d="M64 170h72l-8 34H72z" fill="#F2A07E" stroke="#24402A"/><path d="M60 170h80" stroke="#24402A"/><path d="M100 170C98 130 92 100 70 80M100 170c4-40 14-70 40-88M100 170c0-40 2-80 0-110"/><path d="M70 80c-30 4-50-14-46-40 22-10 50 0 56 22l-8-14M58 52l14 10M44 62l20 6" fill="#1A9A43" fill-opacity=".14"/><path d="M140 82c28 6 48-12 44-38-22-10-50 2-54 24M152 54l-12 10M168 66l-22 4" fill="#1A9A43" fill-opacity=".14"/><path d="M100 60c-26-8-34-34-18-54 22 0 34 20 22 42M84 22l12 10M82 38l16 6M116 20l-10 12" fill="#1A9A43" fill-opacity=".14"/>'),
 ("Pothos", "Epipremnum aureum", "Le pote facile. Pousse partout, pardonne tout, même vos oublis d'arrosage.",
  [("⛅", "Mi-ombre ou lumière douce"), ("💧", "Laisser sécher entre deux arrosages"), ("✂", "Se bouture dans un verre d'eau")],
  '<path d="M62 40h76l-8 40H70z" fill="#FFF6E3" stroke="#24402A"/><path d="M58 40h84" stroke="#24402A"/><path d="M80 80c-6 30 4 60-10 90M100 80c4 40-8 70 6 110M122 80c8 26-2 50 12 70"/><g fill="#1A9A43" fill-opacity=".18"><path d="M74 106c-12-4-14-18-4-22 8 2 8 14 4 22z"/><path d="M78 140c12-2 16-14 8-20-10 0-12 12-8 20z"/><path d="M96 124c-12-2-16-16-6-20 8 2 10 12 6 20z"/><path d="M106 164c12-2 14-16 4-20-10 2-10 12-4 20z"/><path d="M128 110c12 0 16-14 6-18-10 0-10 10-6 18z"/><path d="M132 140c-12 0-14-14-4-18 8 2 8 12 4 18z"/><path d="M104 194c-12 0-14-14-4-16 8 2 8 10 4 16z"/></g>'),
 ("Strelitzia", "L'oiseau de paradis", "La diva solaire. Exige la meilleure place près de la fenêtre, et elle le mérite.",
  [("☀", "Plein soleil, même direct"), ("💧", "Arrosage régulier au printemps et en été"), ("✿", "Feuilles à dépoussiérer de temps en temps")],
  '<path d="M60 170h80l-10 34H70z" fill="#E9D3A8" stroke="#24402A"/><path d="M56 170h88" stroke="#24402A"/><path d="M90 170c-4-40-10-70-30-100M100 170V40M112 170c6-40 16-74 40-102"/><g fill="#1A9A43" fill-opacity=".16"><path d="M60 70C34 60 30 24 46 10c22 14 26 40 14 60zM60 70L46 12"/><path d="M100 40c-18-14-14-36 0-40 14 6 18 26 0 40zM100 40V2"/><path d="M152 68c24-12 26-46 10-58-20 14-24 40-10 58zM152 68l10-56"/></g>'),
 ("Maranta", "La plante qui prie", "La méditative. Replie ses feuilles le soir comme on referme un bon livre.",
  [("⛅", "Lumière douce, jamais de soleil direct"), ("💦", "Aime l'humidité : brumiser souvent"), ("💧", "Terreau toujours légèrement frais")],
  '<path d="M62 166h76l-8 38H70z" fill="#FFF6E3" stroke="#24402A"/><path d="M58 166h84" stroke="#24402A"/><path d="M100 166c-4-30-20-50-40-60M100 166c4-34 22-56 46-62M100 166c0-34 0-60-4-86"/><g fill="#1A9A43" fill-opacity=".16"><path d="M60 106c-34 6-52-14-44-34 26-8 42 10 44 34z"/><path d="M146 104c32 8 50-12 42-32-24-8-40 8-42 32z"/><path d="M96 80c-24-14-24-44-4-56 20 12 22 40 4 56z"/></g><g stroke="#B9532C" stroke-width="2"><path d="M30 84l10 6M38 76l8 8M168 82l-10 6M160 74l-8 8M88 44l8 6M88 58l8 4"/></g>'),
 ("Arête de poisson", "Epiphyllum anguliger", "L'originale. Zigzague là où on ne l'attend pas, et se bouture en un clin d'œil.",
  [("⛅", "Lumière vive mais filtrée"), ("💧", "Peu d'eau, c'est un cactus des forêts"), ("✂", "Un segment dans l'eau = une nouvelle plante")],
  '<path d="M76 120h48v70c0 8-6 14-14 14H90c-8 0-14-6-14-14z" fill="#E8F1F0" fill-opacity=".7" stroke="#24402A"/><path d="M80 112h40v8H80z" stroke="#24402A"/><path d="M100 176V20"/><path d="M100 30l-16 8 16 8-18 10 18 8-18 10 18 8-16 10 16 8M100 30l16 8-16 8 18 10-18 8 18 10-18 8 16 10-16 8" fill="#1A9A43" fill-opacity=".16"/><rect x="58" y="128" width="22" height="34" rx="3" fill="#fff" stroke="#24402A" stroke-width="2" transform="rotate(-10 69 145)"/>'),
 ("Fougère de Boston", "Nephrolepis exaltata", "La romantique. Aime l'humidité, les suspensions et les conversations à voix basse.",
  [("⛅", "Mi-ombre, loin des radiateurs"), ("💦", "Brumiser, elle adore la salle de bain"), ("💧", "Ne jamais laisser sécher complètement")],
  '<path d="M100 2v30" stroke="#C49A6C" stroke-width="2"/><path d="M66 32h68l-6 34H72z" fill="#1A9A43" fill-opacity=".9" stroke="#24402A"/><path d="M62 32h76" stroke="#24402A"/><path d="M80 66c-20 30-40 60-60 120M92 66c-8 40-14 80-30 136M108 66c8 40 14 80 30 136M120 66c20 30 40 60 60 120"/><g stroke-width="2.4"><path d="M70 90l-12-4M66 100l10 6M56 110l-12-4M52 124l10 6M40 140l-12-4M36 154l10 6M86 100l-12 0M84 120l10 4M78 140l-12 0M74 160l10 4M114 100l12 0M116 120l-10 4M122 140l12 0M126 160l-10 4M130 90l12-4M134 100l-10 6M144 110l12-4M148 124l-10 6M160 140l12-4M164 154l-10 6"/></g>'),
]

def plants():
    out = []
    FILES=['monstera', 'pothos', 'strelitzia', 'maranta', 'arete', 'fougere']
    for k, (name, lat, perso, care, svg) in enumerate(PLANTS):
        li = ''.join(f'<li><i aria-hidden="true">{ic}</i><span>{html.escape(t)}</span></li>' for ic, t in care)
        out.append(f'''<div class="ptag" data-rv style="--d:{k%3};--k:{k}"><div class="swing">
<div class="flip">
<div class="face"><img class="pimg" src="img/plantes/{FILES[k]}.webp" alt="" width="360" height="360" loading="lazy" decoding="async"><h3>{html.escape(name)}</h3><p class="lat">{html.escape(lat)}</p><p class="perso">{html.escape(perso)}</p><button class="hint" type="button" aria-pressed="false">↻ Comment l'entretenir<span class="sr"> : {html.escape(name)}</span></button></div>
<div class="face back"><h3>{html.escape(name)}, mode d'emploi</h3><ul class="care">{li}</ul><button class="hint" type="button" aria-pressed="true">↻ Revenir</button></div>
</div></div></div>''')
    return '\n'.join(out)

C,GR='#FFF6E3','#048D4F'
MASC=(f'<path d="M163 126c32-6 40 34 0 42" fill="none" stroke="{C}" stroke-width="11"/>'
 f'<path d="M28 108q72-8 144 0l-2 10c-4 32-20 60-40 68H70c-20-8-36-36-40-68z" fill="{C}"/>'
 f'<path d="M32 117q68 9 136 0" fill="none" stroke="{GR}" stroke-width="3.4" stroke-linecap="round"/>'
 f'<g class="pupils">'
 f'<g class="eye"><ellipse cx="83" cy="146" rx="10" ry="13" fill="none" stroke="{GR}" stroke-width="3.4"/><ellipse cx="84" cy="148" rx="6" ry="8.5" fill="{GR}"/><ellipse cx="81" cy="143" rx="2.2" ry="3" fill="{C}"/></g>'
 f'<g class="eye"><ellipse cx="117" cy="146" rx="10" ry="13" fill="none" stroke="{GR}" stroke-width="3.4"/><ellipse cx="118" cy="148" rx="6" ry="8.5" fill="{GR}"/><ellipse cx="115" cy="143" rx="2.2" ry="3" fill="{C}"/></g></g>'
 f'<path class="closed" d="M74 148q9 7 18 0M108 148q9 7 18 0" fill="none" stroke="{GR}" stroke-width="3.4" stroke-linecap="round"/>'
 f'<path d="M91 166q9 10 18 0" fill="none" stroke="{GR}" stroke-width="3.4" stroke-linecap="round"/>'
 f'<g fill="{GR}"><circle cx="72" cy="163" r="2"/><circle cx="76" cy="168" r="2"/><circle cx="128" cy="163" r="2"/><circle cx="124" cy="168" r="2"/></g>')

def build():
    s = (SRC / 'index.html').read_text()
    s = re.sub(r'<!--pic (.+?)-->', pic, s)
    s = s.replace('<!--PLANTS-->', plants()).replace('<!--MASC-->', MASC).replace('<!--LGT-->', (SRC/'lg-type.d').read_text().strip())
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    for d in ('img', 'fonts'): shutil.copytree(ROOT / d, DIST / d)
    for f in SRC.glob('*'):
        if f.name not in ('index.html', 'build.py', 'lg-type.d'): shutil.copy(f, DIST / f.name)
    raw = DIST / 'index.src.html'; raw.write_text(s)
    subprocess.run(['node', '/tmp/bt/node_modules/html-minifier-terser/cli.js', '--collapse-whitespace', '--conservative-collapse',
                    '--remove-comments', '--minify-css', 'true', '--minify-js', 'true', '--remove-redundant-attributes',
                    '-o', str(DIST / 'index.html'), str(raw)], check=True)
    raw.unlink()
    size = (DIST / 'index.html').stat().st_size
    print(f'index.html {size/1024:.1f} Ko', '| total dist', sum(p.stat().st_size for p in DIST.rglob('*') if p.is_file()) // 1024, 'Ko')

if __name__ == '__main__':
    build()
