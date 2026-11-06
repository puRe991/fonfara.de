#!/usr/bin/env python3
"""
Baut die statische Website fonfara.de nach ./public

    python3 build.py

Benötigt: Python 3.9+, Jinja2, Pillow  (pip install -r requirements.txt)

Die Seiten liegen unter src/pages, das Layout unter src/templates.
Bilder/PDFs liegen unter src/media (gleiche Pfade wie auf der alten Website,
damit alte Links und Suchmaschinen-Einträge weiter funktionieren).
Nur tatsächlich verwendete Medien werden nach public/ kopiert.
"""
import json
import os
import re
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from PIL import Image

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "public"
SITE_URL = "https://www.fonfara.de/"

# --------------------------------------------------------------------------
# Navigation
# --------------------------------------------------------------------------
MAIN_NAV = [
    ("home", "Start", "index.html"),
    ("person", "Person", "teflon/index.html"),
    ("musik", "Musik", "musik/index.html"),
    ("video", "Video", "video/index.html"),
    ("comedy", "Comedy", "kp/index.html"),
    ("meditation", "Meditation", "meditation/index.html"),
    ("buecher", "Bücher", "buecher.html"),
    ("impressum", "Kontakt", "impressum.html"),
]

SUB_NAV = {
    "person": ("Biografie", [
        ("Deutsch", "teflon/index.html"),
        ("English", "teflon/index-english.html"),
    ]),
    "musik": ("Musik", [
        ("Übersicht", "musik/index.html"),
        ("ASIAN STARS", "asianstars/index.html"),
        ("ASIAN STARS – Live-Archiv", "asianstars/mp3.html"),
        ("Sirius-Engel", "musik/siriusengel.html"),
        ("Das Summen der Honigbiene", "honigbiene/index.html"),
    ]),
    "comedy": ("Frau Kächele & Frau Peters", [
        ("Daheim", "kp/index.html"),
        ("Fakten", "kp/fakten.html"),
        ("Anhören", "kp/player/player.html"),
        ("Ansehen", "kp/video.html"),
        ("CD & Buch", "kp/cd.html"),
        ("Live-Show", "kp/live.html"),
        ("Die schwäbische Seite", "schwaebische-comedy/schwaebische-comedy.html"),
        ("Hefezopf-Rezepte", "kp/hefezopfrezept.html"),
        ("Humor", "humor.html"),
        ("Impressum", "kp/impressum.html"),
    ]),
    "meditation": ("Meditation", [
        ("Online-Meditation", "meditation/index.html"),
        ("Fragen & Tipps", "meditation/fragen.html"),
        ("Dienstagstreff", "dienstagstreff/index.html"),
        ("CD & Download", "meditation/cd.html"),
    ]),
    "creativ": ("Kreatives", [
        ("Comedy & Werbung", "creativ/index.html"),
        ("Werkbeispiel", "creativ/werkbeispiel.html"),
        ("Hauszeitung", "creativ/hauszeitung.html"),
        ("Impressum", "creativ/impressum.html"),
    ]),
}

# (Ausgabepfad, Template, Titel, Beschreibung, Hauptnavigation, Unternavigation)
PAGES = [
    ("index.html", "index.html",
     "Teflon Fonfara – Humor, Harmonie, Heilung | Künstler, Musiker, Autor",
     "Teflon Fonfara: Musiker, Performer, Autor, Grafiker. Erfinder von Frau Kächele & Frau Peters, Videos, Comedy, Musik, Bücher und kostenlose Online-Meditation.",
     "home", None),
    ("teflon/index.html", "teflon/index.html",
     "Die Teflon-Fonfara-Story – Biografie",
     "Vom Stuttgarter Sargverleih über New York und SDR3 bis zur Electric Sitar: die Biografie von Teflon Fonfara.",
     "person", "person"),
    ("teflon/index-english.html", "teflon/index-english.html",
     "The Teflon Fonfara Story – Biography (English)",
     "From Stuttgart's first coffin rental to New York, SDR3 radio cult and the electric sitar: the biography of Teflon Fonfara.",
     "person", "person"),
    ("musik/index.html", "musik/index.html",
     "Musik & Projekte – Teflon Fonfara",
     "Musik von Teflon Fonfara: Album, Einzeltitel, ASIAN STARS, Sirius-Engel, Das Summen der Honigbiene und Musik-Comedy.",
     "musik", "musik"),
    ("musik/siriusengel.html", "musik/siriusengel.html",
     "Sirius-Engel – ein Studio-Projekt von Teflon Fonfara",
     "SIRIUS-ENGEL: elektromagnetische Wechselstrom-Kapelle mit dem kosmischen Tanz zur seelischen Liebkosung. Videos und Songs.",
     "musik", "musik"),
    ("asianstars/index.html", "asianstars/index.html",
     "ASIAN STARS – Elektro-euphorische Weltmusik",
     "ASIAN STARS: elektro-euphorische Weltmusik zur harmonischen Tanz-Erheiterung mit Teflon Fonfara, Tim Ackerland und Arno Ritter.",
     "musik", "musik"),
    ("asianstars/mp3.html", "asianstars/mp3.html",
     "ASIAN STARS – ältere Live-Videos",
     "Live-Videos von ASIAN STARS: Cafe Galao, Kirchheimer Musiknacht, Goa-Party und mehr.",
     "musik", "musik"),
    ("honigbiene/index.html", "honigbiene/index.html",
     "Das Summen der Honigbiene – Musik & Bild-Installation",
     "Das Summen der Honigbiene: Musik von Teflon Fonfara, Bilder von Roland Bentz. Kunstband mit CD.",
     "musik", "musik"),
    ("video/index.html", "video/index.html",
     "Videos – TV, Musik live, Musik-Clips und Comedy | Teflon Fonfara",
     "Videos von Teflon Fonfara: Musikvideos, TV-Dokus, ASIAN STARS live, Frau Kächele & Frau Peters und Werbetrailer.",
     "video", None),
    ("kp/index.html", "kp/index.html",
     "Frau Kächele & Frau Peters – Schwäbische Comedy aus SDR3",
     "Die wilden Hefezopf-Weiber aus SDR 3: alles über Frau Kächele & Frau Peters und Eberhard Kächele.",
     "comedy", "comedy"),
    ("kp/fakten.html", "kp/fakten.html",
     "Die Fakten zu Frau Kächele & Frau Peters",
     "Fakten zur Kult-Comedy-Show Frau Kächele & Frau Peters: über 800 Folgen in SDR 3 von 1986 bis 1998.",
     "comedy", "comedy"),
    ("kp/player/player.html", "kp/player/player.html",
     "Anhören – Sketche & Songs von Frau Kächele & Frau Peters",
     "Die wildesten Sketche und Songs mit Frau Kächele & Frau Peters: Original-Folgen aus SDR3 zum Anhören.",
     "comedy", "comedy"),
    ("kp/video.html", "kp/video.html",
     "Ansehen – Videos mit Frau Kächele & Frau Peters",
     "Videos mit Frau Kächele & Frau Peters, Eberhard Kächele, Trickfilmen und Live-Auftritten.",
     "comedy", "comedy"),
    ("kp/cd.html", "kp/cd.html",
     "Der neue Bahnhof isch fertig – Hörspiel, Buch & CDs",
     "Frau Kächele & Frau Peters erleben Stuttgart 21: Hörspiel und Buch. Dazu alle CDs, LP und das Textbuch Hefezopf-Power.",
     "comedy", "comedy"),
    ("kp/live.html", "kp/live.html",
     "Live-Show – Frau Kächele & Frau Peters",
     "Die Live-Show: Frau Kächele & Frau Peters, schwäbische Comedy pur. Mit Babs Steinbock und Teflon Fonfara.",
     "comedy", "comedy"),
    ("kp/hefezopfrezept.html", "kp/hefezopfrezept.html",
     "Hefezopf-Rezepte aus der Sammlung von Frau Kächele & Frau Peters",
     "25 Original-Hefezopf-Rezepte, eingesandt von den Fans von Frau Kächele & Frau Peters.",
     "comedy", "comedy"),
    ("kp/impressum.html", "kp/impressum.html",
     "Impressum – Frau Kächele & Frau Peters",
     "Impressum des Projekts Frau Kächele & Frau Peters von Teflon Fonfara.",
     "comedy", "comedy"),
    ("schwaebische-comedy/schwaebische-comedy.html", "schwaebische-comedy/schwaebische-comedy.html",
     "Die schwäbische Seite – der andere Humor",
     "Der andere schwäbische Humor, die Kächele-Comedy-Dynastie, Schwäbisch im Tempo-Experiment und Eberhard Kächele.",
     "comedy", "comedy"),
    ("humor.html", "humor.html",
     "Humor – Schwäbische Comedy mit Frau Kächele & Frau Peters",
     "Frau Kächele & Frau Peters und weitere Radio-Serien von Teflon Fonfara bei SDR, SWF und SWR.",
     "comedy", "comedy"),
    ("meditation/index.html", "meditation/index.html",
     "Kostenlose Online-Meditation – Licht-Atem-Meditation zur Selbstheilung",
     "Die Licht-Atem-Meditation von Teflon Fonfara: kostenlos online anhören, zur Entspannung und Selbstheilung. Dauer ca. 28 Minuten.",
     "meditation", "meditation"),
    ("meditation/fragen.html", "meditation/fragen.html",
     "Fragen & Antworten zur Licht-Atem-Meditation",
     "Fragen und Antworten zur Licht-Atem-Meditation: Wozu ist sie gut, für wen ist sie, wie atme ich richtig?",
     "meditation", "meditation"),
    ("meditation/cd.html", "meditation/cd.html",
     "Licht-Atem-Meditation als MP3 – CD & Download",
     "Die Licht-Atem-Meditation in drei Varianten als MP3: geführte Übung, Sanftes Schweben und Einschlaf-Meditation.",
     "meditation", "meditation"),
    ("dienstagstreff/index.html", "dienstagstreff/index.html",
     "Meditation in Stuttgart – Dienstagstreff",
     "Dienstagstreff in Stuttgart-Süd: Meditation, Gespräch, Spaß und Selbstheilung mit Teflon Fonfara.",
     "meditation", "meditation"),
    ("buecher.html", "buecher.html",
     "Bücher & Hörspiel – Teflon Fonfara",
     "Bücher von Teflon Fonfara: Liebe in magischen Zeiten, Der neue Bahnhof isch fertig, Die Kraft der spirituellen Transformation und mehr.",
     "buecher", None),
    ("impressum.html", "impressum.html",
     "Impressum & Datenschutz – Teflon Fonfara",
     "Impressum, Kontakt, Haftungsausschluss und Datenschutzerklärung von fonfara.de.",
     "impressum", None),
    ("creativ/index.html", "creativ/index.html",
     "Comedy & Werbung – humorvolle Internet-Videos von Teflon Fonfara",
     "Humor in der Werbung: Teflon Fonfara entwickelt Idee, Konzept und Produktion für unterhaltsame Werbe-Videos.",
     "", "creativ"),
    ("creativ/werkbeispiel.html", "creativ/werkbeispiel.html",
     "Werkbeispiel – humorvolle Werbung aus einer Hand",
     "Werkbeispiel: Komplett-Realisierung für einen Schuhhersteller – Website, Shop, Kataloge, Kampagnen, Firmen-Video und Maskottchen.",
     "", "creativ"),
    ("creativ/hauszeitung.html", "creativ/hauszeitung.html",
     "Die Hauszeitung – Firmenzeitung von Teflon Fonfara",
     "Warum eine eigene Firmenzeitung? Redaktion und Gestaltung aus einer Hand.",
     "", "creativ"),
    ("creativ/impressum.html", "creativ/impressum.html",
     "Impressum – Kreatives",
     "Impressum und Haftungsausschluss für fonfara.de/creativ.",
     "", "creativ"),
]

# Alte Adressen, die nur weiterleiten (damit Lesezeichen/Backlinks funktionieren)
REDIRECTS = {
    "index.htm": "index.html",
    "meditation.html": "meditation/index.html",
    "siriusengel/index.htm": "musik/siriusengel.html",
    "siriusengel/index.html": "musik/siriusengel.html",
    "kp/kp-intro.htm": "kp/index.html",
    "kp/mp3-frameset.html": "kp/player/player.html",
    "meditation/download.htm": "meditation/cd.html",
    "meditation/impressum.html": "impressum.html",
    "buch/frameset-buecher.htm": "buecher.html",
    "frequenzladen/medi/mp3-download.html": "asianstars/index.html#cd",
}


# --------------------------------------------------------------------------
# Helfer
# --------------------------------------------------------------------------
_dims_cache = {}
used_media = set()


def rel_root(out_path):
    depth = out_path.count("/")
    return "../" * depth


def media_dims(path):
    if path not in _dims_cache:
        p = SRC / "media" / path
        if not p.exists():
            raise FileNotFoundError(f"Bild fehlt: src/media/{path}")
        with Image.open(p) as im:
            _dims_cache[path] = im.size
    return _dims_cache[path]


def make_env():
    env = Environment(
        loader=FileSystemLoader([str(SRC / "templates"), str(SRC / "pages")]),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["load_json"] = lambda name: json.loads((SRC / "data" / name).read_text("utf-8"))
    env.globals["fragment"] = lambda name: (SRC / "fragments" / name).read_text("utf-8")
    env.globals["MAIN_NAV"] = MAIN_NAV
    env.globals["SUB_NAV"] = SUB_NAV
    env.globals["SITE_URL"] = SITE_URL

    def dims(path):
        used_media.add(path)
        return media_dims(path)

    env.globals["dims"] = dims
    env.globals["media"] = lambda p: (used_media.add(p), p)[1]
    env.filters["slug"] = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")).strip("-")
    return env


def redirect_html(target, root):
    url = root + target
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<title>Weiterleitung …</title>
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{SITE_URL}{target}">
</head><body style="font-family:system-ui,sans-serif;padding:2rem">
<p>Diese Seite ist umgezogen: <a href="{url}">{url}</a></p>
</body></html>
"""


def build():
    if OUT.exists():
        # Audio-Dateien (nicht im Repository) beim Neubau erhalten
        tmp_keep = ROOT / ".audio-keep"
        if tmp_keep.exists():
            shutil.rmtree(tmp_keep)
        moved = []
        for mp3 in OUT.rglob("*.mp3"):
            dest = tmp_keep / mp3.relative_to(OUT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(mp3), dest)
            moved.append(dest)
        shutil.rmtree(OUT)
    else:
        moved, tmp_keep = [], ROOT / ".audio-keep"
    OUT.mkdir()

    env = make_env()
    sitemap = []
    for out_path, tpl, title, desc, section, sub in PAGES:
        if not (SRC / "pages" / tpl).exists():
            print(f"WARNUNG: Template fehlt: {tpl}", file=sys.stderr)
            continue
        root = rel_root(out_path)
        ctx = dict(
            root=root, page_path=out_path, title=title, description=desc,
            section=section, sub=sub,
            canonical=SITE_URL + ("" if out_path == "index.html" else out_path),
        )
        html = env.get_template(tpl).render(**ctx)
        html = re.sub(r"\n\s*\n+", "\n", html)
        dest = OUT / out_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, "utf-8")
        sitemap.append(ctx["canonical"])

    for src, target in REDIRECTS.items():
        dest = OUT / src
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(redirect_html(target, rel_root(src)), "utf-8")

    # statische Dateien
    shutil.copytree(SRC / "static", OUT / "assets")
    for extra in ("favicon.ico",):
        if (SRC / "media" / extra).exists():
            shutil.copy2(SRC / "media" / extra, OUT / extra)
    (OUT / "assets" / "img").mkdir(exist_ok=True)

    # verwendete Medien kopieren
    for p in sorted(used_media):
        s = SRC / "media" / p
        d = OUT / p
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)

    # Medien, die nur per Link (nicht per dims()) eingebunden sind: in HTML suchen
    linked = set()
    for f in OUT.rglob("*.html"):
        base = f.parent
        for m in re.finditer(r'(?:href|src|data-poster)="([^"#?]+\.(?:jpg|jpeg|png|gif|pdf|webp))"', f.read_text("utf-8")):
            ref = m.group(1)
            if ref.startswith(("http:", "https:", "mailto:")):
                continue
            target = (base / ref).resolve()
            try:
                rel = target.relative_to(OUT)
            except ValueError:
                continue
            if not target.exists():
                s = SRC / "media" / rel
                if s.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(s, target)
                    linked.add(str(rel))
                else:
                    print(f"WARNUNG: {f.relative_to(OUT)} verweist auf fehlende Datei {rel}", file=sys.stderr)

    # robots + sitemap
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", "utf-8")
    urls = "\n".join(f"  <url><loc>{u}</loc></url>" for u in sitemap)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n', "utf-8")
    (OUT / ".htaccess").write_text((SRC / "htaccess.txt").read_text("utf-8"), "utf-8")

    # Audio zurücklegen
    if tmp_keep.exists():
        for f in tmp_keep.rglob("*.mp3"):
            dest = OUT / f.relative_to(tmp_keep)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), dest)
        shutil.rmtree(tmp_keep)

    print(f"OK: {len(PAGES)} Seiten, {len(REDIRECTS)} Weiterleitungen, {len(used_media) + len(linked)} Medien -> {OUT}")


if __name__ == "__main__":
    build()
