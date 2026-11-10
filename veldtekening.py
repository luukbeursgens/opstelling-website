"""Veldtekeningen van een opstelling als SVG-afbeelding, zoals de app ze laat zien.

De plekken op het veld worden op dezelfde manier berekend als in de app
(positions() in js/rules.js van de app): verdediging, middenveld en aanval op
vaste hoogtes, en per linie gelijk over de breedte verdeeld.
"""

NAMEN = ["Daan", "Milan", "Noud", "Luca", "Finn", "Jesse", "Sven", "Bram", "Stijn"]
VELD_BREEDTE, VELD_LENGTE = 300, 425   # verhouding van een 6 tegen 6-veld: 30 × 42,5 meter


def linies(formatie):
    """'2-1-2' -> ['V', 'V', 'M', 'A', 'A']; zonder middenveld: '2-2' -> ['V', 'V', 'A', 'A']."""
    aantallen = [int(n) for n in formatie.split("-")]
    soorten = ["V", "A"] if len(aantallen) == 2 else ["V", "M", "A"]
    return [soort for soort, n in zip(soorten, aantallen) for _ in range(n)]


def plekken(lijnen, keeper=True):
    """Plek van elke veldspeler in procenten van het veld (x van links, y van boven)."""
    heeft_middenveld = "M" in lijnen
    hoogte = ({"V": 70, "M": 46 if heeft_middenveld else 0, "A": 20 if heeft_middenveld else 30} if keeper
              else {"V": 78, "M": 50 if heeft_middenveld else 0, "A": 22 if heeft_middenveld else 30})
    uitkomst = [None] * len(lijnen)
    for soort in "VMA":
        indexen = [i for i, l in enumerate(lijnen) if l == soort]
        n = len(indexen)
        breedte = 78 if n >= 5 else 72 if n == 4 else 62 if n == 3 else 50
        for k, i in enumerate(indexen):
            x = 50 if n == 1 else 50 - breedte / 2 + breedte * k / (n - 1)
            uitkomst[i] = (x, hoogte[soort])
    return uitkomst


def speler(x, y, naam, keeper=False):
    breedte = 14 + 9.5 * len(naam)
    kleur, rand = ("#EF7E22", "#C8641A") if keeper else ("#FFFFFF", "#D5DDD7")
    return (f'<rect x="{x - breedte / 2:.1f}" y="{y - 15:.1f}" width="{breedte:.1f}" height="30" rx="8" fill="{kleur}" stroke="{rand}"/>'
            f'<text x="{x:.1f}" y="{y + 6:.1f}" text-anchor="middle" font-size="17" font-weight="700" fill="#16202B">{naam}</text>')


def veld_svg(formatie, titel):
    """Een volledige SVG van een 6 tegen 6-veld met keeper en de formatie."""
    b, h = VELD_BREEDTE, VELD_LENGTE
    banen = "".join(f'<rect x="0" y="{i * h / 10:.1f}" width="{b}" height="{h / 10:.1f}" fill="{"#2F7A4B" if i % 2 else "#2B7045"}"/>' for i in range(10))
    lijn = 'fill="none" stroke="#E8F2EA" stroke-width="2.5"'
    keepersgebied = h * 7 / 42.5   # 7 meter van de achterlijn
    doel = b * 5 / 30              # doel van 5 meter breed
    lijnen = (f'<rect x="10" y="10" width="{b - 20}" height="{h - 20}" {lijn}/>'
              f'<line x1="10" y1="{h / 2}" x2="{b - 10}" y2="{h / 2}" {lijn}/>'
              f'<circle cx="{b / 2}" cy="{h / 2}" r="34" {lijn}/>'
              f'<line x1="10" y1="{10 + keepersgebied:.1f}" x2="{b - 10}" y2="{10 + keepersgebied:.1f}" {lijn} stroke-dasharray="6 7"/>'
              f'<line x1="10" y1="{h - 10 - keepersgebied:.1f}" x2="{b - 10}" y2="{h - 10 - keepersgebied:.1f}" {lijn} stroke-dasharray="6 7"/>'
              f'<rect x="{(b - doel) / 2:.1f}" y="2" width="{doel:.1f}" height="8" fill="#E8F2EA"/>'
              f'<rect x="{(b - doel) / 2:.1f}" y="{h - 10}" width="{doel:.1f}" height="8" fill="#E8F2EA"/>')
    spelers = speler(b / 2, h * 0.9, NAMEN[0], keeper=True)
    for (x, y), naam in zip(plekken(linies(formatie)), NAMEN[1:]):
        spelers += speler(b * x / 100, h * y / 100, naam)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {b} {h}" width="{b}" height="{h}" role="img" '
            f'font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif"><title>{titel}</title>'
            f'<clipPath id="r"><rect width="{b}" height="{h}" rx="18"/></clipPath><g clip-path="url(#r)">{banen}{lijnen}</g>{spelers}</svg>\n')
