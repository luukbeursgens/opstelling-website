#!/usr/bin/env python3
"""Meldt gewijzigde pagina's aan Bing via IndexNow, direct na het publiceren.

Bing deelt de melding met de andere zoekmachines die IndexNow gebruiken. ChatGPT
zoekt grotendeels via Bing, dus zo komen nieuwe pagina's daar ook sneller in.

Gebruik in de publicatiestap:
    python3 indexnow.py <vorige commit> <nieuwe commit>
Proberen zonder iets te versturen (voor de tests):
    python3 indexnow.py --proef jo9/index.html style.css
"""
import json, pathlib, re, subprocess, sys, urllib.request

MAP = pathlib.Path(__file__).parent
BUILD = (MAP / "build.py").read_text(encoding="utf-8")
SITE = re.search(r'^SITE = "([^"]+)"', BUILD, re.M).group(1)
SLEUTEL = re.search(r'^INDEXNOW_SLEUTEL = "([^"]+)"', BUILD, re.M).group(1)
ADRES = "https://api.indexnow.org/indexnow"


def adressen_in_sitemap():
    return re.findall(r"<loc>([^<]+)</loc>", (MAP / "sitemap.xml").read_text(encoding="utf-8"))


def adressen_voor(gewijzigde_bestanden, sitemap):
    """Welke pagina's uit de sitemap horen bij de gewijzigde bestanden (dus geen bedankpagina of stijl)."""
    adressen = []
    for bestand in gewijzigde_bestanden:
        if bestand == "index.html":
            adres = SITE + "/"
        elif bestand.endswith("/index.html"):
            adres = SITE + "/" + bestand[: -len("index.html")]
        else:
            continue
        if adres in sitemap and adres not in adressen:
            adressen.append(adres)
    return adressen


def gewijzigde_bestanden(vorige, nieuwe):
    """Bestanden die tussen twee commits veranderd zijn; None als de vorige commit onbekend is."""
    if not vorige or set(vorige) == {"0"}:
        return None
    uitkomst = subprocess.run(["git", "diff", "--name-only", vorige, nieuwe], capture_output=True, text=True, cwd=MAP)
    return uitkomst.stdout.split() if uitkomst.returncode == 0 else None


def versturen(adressen):
    host = SITE.split("://", 1)[1]
    inhoud = json.dumps({"host": host, "key": SLEUTEL, "keyLocation": f"{SITE}/{SLEUTEL}.txt", "urlList": adressen}).encode()
    verzoek = urllib.request.Request(ADRES, data=inhoud, headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(verzoek, timeout=30) as antwoord:
        return antwoord.status


def main(argumenten):
    sitemap = adressen_in_sitemap()
    if argumenten[:1] == ["--proef"]:
        print("\n".join(adressen_voor(argumenten[1:], sitemap)))
        return
    bestanden = gewijzigde_bestanden(*argumenten[:2]) if len(argumenten) >= 2 else None
    adressen = sitemap if bestanden is None else adressen_voor(bestanden, sitemap)
    if not adressen:
        print("Geen pagina's gewijzigd, niets te melden.")
        return
    print("Melden bij IndexNow:", *adressen, sep="\n  ")
    try:
        print("IndexNow antwoordde met", versturen(adressen))
    except Exception as fout:
        # Een mislukte melding mag het publiceren niet laten falen: de sitemap blijft de vangnet
        print("::warning::IndexNow-melding mislukt:", fout)


if __name__ == "__main__":
    main(sys.argv[1:])
