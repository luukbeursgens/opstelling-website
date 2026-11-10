#!/usr/bin/env python3
"""Bouwt de statische marketingsite voor Opstelling.

Eén bestand per pagina, geen JavaScript, alles vooraf klaargezet:
titels, beschrijvingen, canonieke adressen, gestructureerde gegevens,
sitemap en robots.txt. Aanpassen? Wijzig de teksten hieronder en draai
opnieuw: python3 build.py
"""
import os, pathlib

SITE = "https://opstellingapp.nl"          # eigen domein; pas dit aan als je een ander domein neemt
APP = "https://app.opstellingapp.nl"
AANMELDEN = APP + "/?account=nieuw"   # opent in de app meteen "Maak je account aan"
CONTACT_MAIL = "info@opstellingapp.nl"
OUT = pathlib.Path(__file__).parent

TIPS = "/tips-en-tops-per-speler/"
AGENDA = "/voetbal-nl-kalender-koppelen/"
# Menu bovenaan (op kleine schermen verborgen) en de voettekst, die alle pagina's noemt
NAV = [("/wisselschema-maken/", "Wisselschema maken"), ("/speeltijd-eerlijk-verdelen/", "Eerlijke speeltijd"),
       (TIPS, "Tips en tops"), (AGENDA, "Wedstrijdagenda"),
       ("/prijzen/", "Prijzen"), ("/contact/", "Contact")]
VOET = [("/", "Home"), ("/wisselschema-maken/", "Wisselschema maken"), ("/speeltijd-eerlijk-verdelen/", "Eerlijke speeltijd"),
        (TIPS, "Tips en tops"), (AGENDA, "Wedstrijdagenda"), ("/knvb-wedstrijdvormen/", "KNVB-wedstrijdvormen"),
        ("/prijzen/", "Prijzen"), ("/contact/", "Contact")]

# Alle openbare pagina's met titel en beschrijving; daarmee worden de sitemap en llms.txt gemaakt
PAGINA_INFO = []

PUBLIEK = True         # False zolang de site nog niet openbaar mag zijn: geen zoekmachines
PRIJS = "29,99"         # per team, per seizoen, één keer vooraf betalen
PRIJS_LD = "29.99"
SEIZOEN = "2026/'27"   # huidig KNVB-seizoen, staat in de titels van de leeftijdspagina's
SEIZOEN_TOT = "31 juli"   # een seizoen loopt tot en met deze datum      # dezelfde prijs met een punt, voor de gegevens voor zoekmachines
GRATIS = 1              # aantal gratis wedstrijden per team
# Zinnen over de gratis wedstrijd(en), in enkelvoud of meervoud, zodat ze kloppen als GRATIS verandert
GRATIS_KORT = "Eerste wedstrijd gratis" if GRATIS == 1 else f"Eerste {GRATIS} wedstrijden gratis"
GRATIS_ZIN = "De eerste wedstrijd is gratis" if GRATIS == 1 else f"De eerste {GRATIS} wedstrijden zijn gratis"
GRATIS_WAT = "de eerste wedstrijd" if GRATIS == 1 else f"de eerste {GRATIS} wedstrijden"
GRATIS_IS = "is" if GRATIS == 1 else "zijn"
GRATIS_WOORD = "wedstrijd" if GRATIS == 1 else "wedstrijden"
BETAALD_VANAF = {1: "tweede", 2: "derde", 3: "vierde", 4: "vijfde"}.get(GRATIS, "volgende")

# Cloudflare Web Analytics: plak hier de token uit het Cloudflare-dashboard
# (Web Analytics > je site > "Manage site" > JS snippet, de waarde achter "token").
# Leeg laten = geen analytics. Cloudflare telt bezoeken zonder cookies.
CF_TOKEN = "622bc38b1c73451abece02918dc7e2ea"

# IndexNow: hiermee meldt de publicatiestap gewijzigde pagina's meteen aan Bing (en
# daarmee ook aan ChatGPT-zoeken), zie indexnow.py. De sleutel is openbaar bedoeld:
# hij staat als <sleutel>.txt op de site, zodat Bing ziet dat de melding van ons komt.
INDEXNOW_SLEUTEL = "5f27039d2d4b77adb817cc285153f710"


# Versienummer van de stijl: verandert style.css, dan verandert het adres, en
# halen browsers meteen de nieuwe versie op in plaats van een oude uit hun geheugen.
import hashlib
CSS_VERSIE = hashlib.sha256((OUT / "style.css").read_bytes()).hexdigest()[:10]
# Zelfde voor de deelkaart: afbeeldingen worden een jaar bewaard, dus een nieuwe kaart krijgt een nieuw adres
OG_VERSIE = hashlib.sha256((OUT / "img" / "og.png").read_bytes()).hexdigest()[:10]


def kruimelpad(naam):
    """Zichtbaar kruimelpad bovenaan een pagina: Home › naam."""
    return f'<nav class="kruimel" aria-label="Kruimelpad"><a href="/">Home</a> <span aria-hidden="true">›</span> <span aria-current="page">{naam}</span></nav>'


def page(path, title, description, body, extra_ld=None, keywords_hint="", index=True, kruimel=None):
    url = SITE + path
    # Let op: geen backslash binnen een f-string, anders werkt dit niet op oudere Python-versies
    huidig = ' aria-current="page"'
    kopmenu = "".join(
        '<a href="{}"{}>{}</a>'.format(href, huidig if href == path else '', label)
        for href, label in NAV)
    voetmenu = "".join('<a href="{}">{}</a>'.format(href, label) for href, label in VOET)
    if index:
        PAGINA_INFO.append((path, title, description))
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "Opstelling",
             "inLanguage": "nl-NL", "publisher": {"@id": SITE + "/#org"}},
            {"@type": "Organization", "@id": SITE + "/#org", "name": "Opstelling", "url": SITE + "/",
             "logo": SITE + "/img/icon.png"},
            {"@type": "WebPage", "@id": url + "#page", "url": url, "name": title, "description": description,
             "isPartOf": {"@id": SITE + "/#website"}, "inLanguage": "nl-NL"},
        ],
    }
    if kruimel:
        ld["@graph"].append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": kruimel, "item": url}]})
    if extra_ld:
        ld["@graph"].extend(extra_ld)
    import json
    analytics = ""
    if CF_TOKEN:
        beacon = json.dumps({"token": CF_TOKEN})
        analytics = f"""<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{beacon}'></script>
"""
    robots = "index, follow, max-image-preview:large" if (PUBLIEK and index) else "noindex, nofollow"
    head = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta property="og:type" content="website">
<meta property="og:locale" content="nl_NL">
<meta property="og:site_name" content="Opstelling">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/og.png?v={OG_VERSIE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Opstelling: eerlijke speeltijd voor elk kind in je jeugdteam. {GRATIS_KORT}.">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2F7A4B">
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="preload" href="/fonts/bricolage-grotesque.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css?v={CSS_VERSIE}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{analytics}</head>
<body>
<a class="skip" href="#main">Naar de inhoud</a>
<header class="site">
  <div class="wrap">
    <a class="logo" href="/"><img src="/img/icon.png" alt="" width="34" height="34">Opstelling</a>
    <nav aria-label="Hoofdmenu">{kopmenu}</nav>
    <a class="btn btn-main btn-sm" href="{AANMELDEN}">Probeer gratis</a>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site">
  <div class="wrap">
    <div>
      <a class="logo" href="/"><img src="/img/icon.png" alt="" width="34" height="34">Opstelling</a>
      <p>Eerlijke speeltijd voor elk jeugdteam. Gemaakt door jeugdtrainers, voor jeugdtrainers. Niet verbonden aan de KNVB.</p>
    </div>
    <nav aria-label="Voettekst">{voetmenu}</nav>
  </div>
</footer>
</body>
</html>
"""
    target = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(head, encoding="utf-8")
    return path


def cta(tekst="Probeer het met je eigen team", sub=None):
    sub = sub or f"{GRATIS_ZIN}. Daarna {PRIJS} euro per team voor het hele seizoen, één keer vooraf. Geen installatie, geen wachtwoord."
    return f"""<section class="final">
  <div class="box">
    <h2>{tekst}</h2>
    <p>{sub}</p>
    <a class="btn btn-light" href="{AANMELDEN}">Maak gratis een account</a>
  </div>
</section>"""


def faq_ld(pairs):
    return [{"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": v, "acceptedAnswer": {"@type": "Answer", "text": a}} for v, a in pairs]}]


def faq_html(pairs, titel="Veelgestelde vragen", open_eerste=False):
    items = "".join(
        "<details{}><summary>{}</summary><p>{}</p></details>".format(" open" if (open_eerste and i == 0) else "", v, a)
        for i, (v, a) in enumerate(pairs))
    return f'<section class="vragen" id="vragen"><h2>{titel}</h2><div class="faq">{items}</div></section>'


def lees_verder(items, titel="Verder lezen"):
    """items: lijst van (adres, soort, titel, uitleg)."""
    kaarten = "".join(
        f'<a class="read" href="{href}"><span class="k">{soort}</span><h3>{kop}</h3><p>{uitleg}</p><span class="go">Lees verder →</span></a>'
        for href, soort, kop, uitleg in items)
    return f'<section class="lezen"><h2>{titel}</h2><div class="reads">{kaarten}</div></section>'


GIDSEN = {
    "/wisselschema-maken/": ("Handleiding", "Een wisselschema maken", "Voorbeeldschema's voor 6 tegen 6 en 8 tegen 8, en de regels voor wisselen."),
    "/speeltijd-eerlijk-verdelen/": ("Achtergrond", "Speeltijd eerlijk verdelen", "Waarom het ertoe doet en hoe je het bijhoudt zonder rekenwerk."),
    "/knvb-wedstrijdvormen/": ("Overzicht", "KNVB-wedstrijdvormen", "Speelduur, aantal spelers en wisselmomenten van O7 tot en met O12 in één tabel."),
    TIPS: ("Functie", "Tips en tops per speler", "Zie waar elk kind aan werkt, wat al gelukt is en waar het team op moet trainen."),
    AGENDA: ("Handleiding", "Voetbal.nl-agenda koppelen","Alle wedstrijden van het seizoen in één keer klaar, plus het plaatje voor de ouders."),
    "/prijzen/": ("Prijzen", "Wat Opstelling kost", f"{GRATIS_KORT}, daarna {PRIJS} euro per team per seizoen, één keer vooraf."),
}


def gidsen(*adressen, titel="Verder lezen"):
    return lees_verder([(a,) + GIDSEN[a] for a in adressen], titel)


def prijskaarten():
    return f"""<div class="price-grid">
      <div class="incl">
        <h3>Altijd inbegrepen</h3>
        <ul>
          <li>Alle functies, niets afgeschermd</li>
          <li>Zoveel medetrainers als je wilt</li>
          <li>KNVB-wedstrijdvormen O7 t/m O12</li>
          <li>Voetbal.nl-agenda koppelen</li>
          <li>Tips en tops per speler</li>
          <li>Live meekijken tijdens de wedstrijd</li>
          <li>Verslagen delen met ouders</li>
        </ul>
      </div>
      <div class="plan">
        <h3>Uitproberen</h3>
        <p class="amount">Gratis</p>
        <p>{GRATIS_WAT.capitalize()} van je team. Geen betaalgegevens nodig.</p>
        <a class="btn btn-ghost" href="{AANMELDEN}">Maak een team aan</a>
      </div>
      <div class="plan featured">
        <div class="top"><h3>Per team</h3><span class="tag">Eén keer per seizoen</span></div>
        <p class="amount">€ {PRIJS}<span>per seizoen</span></p>
        <p>Onbeperkt wedstrijden plannen en de speeltijd bijhouden, tot en met {SEIZOEN_TOT}. Je betaalt één keer per seizoen.</p>
        <a class="btn btn-main" href="{AANMELDEN}">Begin met je team</a>
      </div>
    </div>
    <p class="note">Meerdere teams? Je betaalt per team. Een trainer die alleen is toegevoegd aan het team van een ander, betaalt niets.</p>"""


def telefoon(bestand, alt, laden="lazy"):
    extra = ' fetchpriority="high"' if laden == "eager" else ""
    return f'<div class="phone"><img src="/img/{bestand}" width="780" height="1560" alt="{alt}" loading="{laden}"{extra}></div>'


def plaatje(laden="lazy"):
    """Het plaatje dat trainers met de ouders delen (aanwezigheid, verzameltijd, wassen en fruit)."""
    return (f'<div class="plaatje"><img src="/img/site-ouders-plaatje.webp" width="810" height="1158" '
            f'alt="Plaatje voor de ouders: verzameltijd 09:30, aftrap 10:15, sportpark, wie er meegaat, wie de shirts wast en wie fruit meeneemt" loading="{laden}"></div>')


ICOON = {
    "balk": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 18h16M6 18V9M12 18V6M18 18v-7"/></svg>',
    "vink": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4 4 10-10"/></svg>',
    "klok": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2M10 2h4"/></svg>',
    "delen": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12v7a1 1 0 001 1h14a1 1 0 001-1v-7M16 6l-4-4-4 4M12 2v13"/></svg>',
}


def app_ld():
    """De app zelf, met functies en prijs, voor zoekmachines (op home en prijzen)."""
    return {
         "@type": "SoftwareApplication", "name": "Opstelling",
         "applicationCategory": "SportsApplication", "operatingSystem": "Web, iOS, Android",
         "url": APP, "inLanguage": "nl-NL",
         "description": "App voor jeugdtrainers: opstellingen maken, speeltijd eerlijk verdelen, wedstrijden uit de Voetbal.nl-agenda inlezen, tips en tops per speler bijhouden en wedstrijdverslagen delen.",
         "featureList": [
             "Eerlijke opstelling en wisselschema per wedstrijd",
             "Speeltijd eerlijk verdelen over het hele seizoen",
             "KNVB-wedstrijdvormen O7 tot en met O12",
             "Wedstrijdscherm met klok, stand en wisselmomenten",
             "Wedstrijden inlezen uit de Voetbal.nl-teamkalender",
             "Plaatje voor ouders met verzameltijd, locatie, wassen en fruit",
             "Tips en tops per speler en voor het team",
             "Wedstrijdverslag delen met ouders",
             "Meerdere trainers per team, live meekijken",
         ],
         "offers": [
             {"@type": "Offer", "name": "Uitproberen", "price": "0", "priceCurrency": "EUR",
              "description": f"{GRATIS_WAT.capitalize()} met je eerste team gratis, zonder betaalgegevens."},
             {"@type": "Offer", "name": "Per team per seizoen", "price": PRIJS_LD, "priceCurrency": "EUR",
              "url": SITE + "/prijzen/",
              "description": f"{PRIJS} euro per team voor een seizoen, tot en met {SEIZOEN_TOT}, één keer betaald. Medetrainers gratis."},
         ],
     }


# ---------------------------------------------------------------- home
home_faq = [
    ("Wat kost Opstelling?", f"{GRATIS_ZIN}, zodat je het eerst kunt uitproberen. Daarna betaal je {PRIJS} euro per team, één keer voor het hele seizoen (tot en met {SEIZOEN_TOT}). Medetrainers die je toevoegt betalen niets."),
    ("Moet ik iets installeren?", "Nee. Opstelling werkt in je browser en je kunt hem op je beginscherm zetten, zodat hij opent als een gewone app."),
    ("Moet ik alle wedstrijden zelf invoeren?", "Nee. Koppel de teamkalender uit de Voetbal.nl-app en alle wedstrijden van het seizoen komen er vanzelf in, met aftrap, tegenstander en locatie. Zelf een wedstrijd toevoegen kan ook altijd."),
    ("Kan ik ook bijhouden waar een speler aan moet werken?", "Ja. Bij elke speler leg je tips en tops vast. Je ziet wat al gelukt is en waar het team als geheel op kan trainen. Alleen trainers van het team zien dit."),
    ("Werkt het ook voor 6 tegen 6 en 8 tegen 8?", "Ja. Je kiest het niveau van O7 tot en met O12, en de app volgt de KNVB-wedstrijdvormen: aantal spelers, wel of geen keeper, speelduur en wisselmomenten."),
    ("Kunnen meerdere trainers hetzelfde team beheren?", "Ja, en dat kost niets extra. Je voegt trainers toe met hun e-mailadres. Iedereen ziet dezelfde wedstrijden en kan de opstelling klaarzetten of de wedstrijd bijhouden."),
    ("Houdt de app rekening met de posities van spelers?", "Als je dat aanzet wel. Je geeft per speler aan waar hij goed uit de voeten kan, en de app stelt spelers zoveel mogelijk zo op, zonder de eerlijke speeltijd los te laten."),
]
stappen = [
    ("Klaarzetten", "De wedstrijd staat al klaar uit je Voetbal.nl-agenda. Vink aan wie er is, kies de keepers en hoe je wilt wisselen: automatisch, op vaste momenten of helemaal zelf. Met een druk op de knop heb je een eerlijke opstelling.", "site-opstelling.webp", "De opstelling per kwart met de wisselspelers", "De opstelling per kwart"),
    ("Spelen", "Start de klok, noteer doelpunten en volg de wisselmomenten. Medetrainers kijken live mee en kunnen overnemen.", "site-wedstrijd.webp", "Het wedstrijdscherm met klok, stand en het volgende wisselmoment", "Tijdens de wedstrijd"),
    ("Delen", "Sluit af en deel het verslag met de ouders, met de uitslag, het verloop en wie er scoorde.", "verslag.webp", "Deelbaar wedstrijdverslag met uitslag en doelpuntenmakers", "Het verslag voor de ouders"),
    ("Bijhouden en verbeteren", "Zie per speler de speeltijd en doelpunten over het hele seizoen, en leg tips en tops vast. De volgende opstelling houdt rekening met de speeltijd.", "site-seizoen.webp", "Het seizoen in cijfers met topscorers en speeltijd", "Automatisch seizoensoverzicht"),
]
tab_knoppen = "".join(f'<input type="radio" name="stap" id="t{i}"{" checked" if i == 1 else ""}>' for i in range(1, 5))
tab_labels = "".join(
    f'<label for="t{i}"><span class="n">{i}</span><b>{kop}</b><small>{tekst}</small></label>'
    for i, (kop, tekst, _, _, _) in enumerate(stappen, 1))
tab_schermen = "".join(
    (f'<figure class="s{i}"><div class="kaartbeeld"><img src="/img/{img}" width="810" height="1088" alt="{alt}" loading="lazy"></div><figcaption>{onder}</figcaption></figure>'
     if img == "verslag.webp" else
     f'<figure class="s{i}">{telefoon(img, alt)}<figcaption>{onder}</figcaption></figure>')
    for i, (_, _, img, alt, onder) in enumerate(stappen, 1))

page("/",
     "Opstelling: eerlijke speeltijd en opstellingen voor jeugdvoetbal",
     f"Maak in een minuut een opstelling, verdeel de speeltijd eerlijk over het seizoen en deel een verslag met de ouders. {GRATIS_KORT}.",
     f"""
<section class="hero band">
  <div class="pitch" aria-hidden="true"></div>
  <div class="wrap">
    <div>
      <span class="eyebrow"><b></b>Voor jeugdteams van O7 tot en met O12</span>
      <h1>Eerlijke speeltijd voor <em>elk kind</em>, zonder gepuzzel</h1>
      <p class="lead">Maak in een minuut een opstelling voor je jeugdteam, houd bij wie hoeveel speelt en tel dat mee in de volgende wedstrijd.</p>
      <div class="actions">
        <a class="btn btn-main" href="{AANMELDEN}">Probeer gratis</a>
        <a class="btn btn-ghost" href="#hoe">Bekijk hoe het werkt</a>
      </div>
      <ul class="checks">
        <li>{GRATIS_KORT}, zonder betaalgegevens</li>
        <li>Alle wedstrijden van het seizoen in één keer uit Voetbal.nl</li>
        <li>Werkt op elke telefoon, niets te installeren</li>
      </ul>
    </div>
    <div class="hero-beeld">
      {telefoon("site-opstelling.webp", "De opstelling per kwart in de app Opstelling", "eager")}
      <div class="float" aria-hidden="true"><strong>4 × 10'</strong><span>Iedereen speelt<br>evenveel kwarten</span></div>
    </div>
  </div>
</section>

<section class="facts band" aria-label="In het kort">
  <div class="wrap">
    <div class="fact"><strong>1 minuut</strong><span>voor een opstelling</span></div>
    <div class="fact"><strong>O7–O12</strong><span>KNVB-regels ingebouwd</span></div>
    <div class="fact"><strong>{GRATIS} gratis</strong><span>{GRATIS_WOORD} om te proberen</span></div>
    <div class="fact"><strong>€ {PRIJS}</strong><span>per team per seizoen</span></div>
  </div>
</section>

<section class="block band">
  <div class="wrap">
    <div class="head">
      <h2>Geen briefje met streepjes meer</h2>
      <p>Geen gepuzzel, focus langs de lijn op coaching.</p>
    </div>
    <div class="benefits">
      <article class="benefit"><span class="ic" aria-hidden="true">{ICOON["balk"]}</span><h3>Iedereen speelt evenveel</h3><p>De speeltijd wordt zo gelijk mogelijk verdeeld. Wie vorige week minder speelde, krijgt de week erna voorrang, ook als er ineens meer kinderen zijn.</p></article>
      <article class="benefit"><span class="ic" aria-hidden="true">{ICOON["vink"]}</span><h3>Je hoeft niet te rekenen</h3><p>Vink aan wie er is, kies de keepers en klaar. Ruilen kan altijd met twee tikken.</p></article>
      <article class="benefit"><span class="ic" aria-hidden="true">{ICOON["klok"]}</span><h3>Rust langs de lijn</h3><p>De klok loopt mee en je ziet wanneer er gewisseld moet worden en wie erin komt. Medetrainers kijken live mee.</p></article>
      <article class="benefit"><span class="ic" aria-hidden="true">{ICOON["delen"]}</span><h3>Ouders zien het ook</h3><p>Na afloop deel je met één tik een verslag met uitslag en doelpuntenmakers in de groepsapp.</p></article>
    </div>
  </div>
</section>

<section class="block how band" id="hoe">
  <div class="wrap">
    <div class="head">
      <h2>Van aanwezigheid tot eindstand</h2>
      <p>Maak één keer je team en kies het niveau; de KNVB-regels voor speelduur, aantal spelers en wisselmomenten staan er dan automatisch bij. Daarna doorloop je elke wedstrijd in vier stappen.</p>
    </div>
    <div class="tabs">
      {tab_knoppen}
      <div class="tablist">{tab_labels}</div>
      <div class="screens">{tab_schermen}</div>
    </div>
  </div>
</section>

<section class="block band" id="verslag">
  <div class="wrap split">
    <div>
      <span class="eyebrow"><b></b>Na de wedstrijd</span>
      <h2>Ouders krijgen een kort wedstrijdverslag</h2>
      <p>Met één tik maak je een deelbaar verslag: de eindstand, het verloop per helft en wie er scoorde. Klaar om in de groepsapp te zetten, zonder dat je iets hoeft te typen.</p>
    </div>
    <div class="report"><img src="/img/verslag.webp" width="810" height="1088" alt="Wedstrijdverslag VV De Vaart JO8-1 tegen SV Westerkwartier, eindstand 2–1" loading="lazy"></div>
  </div>
</section>

<section class="block band" id="seizoen">
  <div class="wrap">
    <div class="head">
      <h2>Het hele seizoen in één app</h2>
      <p>Niet alleen de zaterdag zelf. Opstelling zet je wedstrijden klaar en helpt je zien waar elk kind aan werkt.</p>
    </div>

    <div class="feat">
      <div class="feat-tekst">
        <span class="eyebrow"><b></b>Wedstrijdagenda</span>
        <h3>Alle wedstrijden klaar, en ouders weten waar ze aan toe zijn</h3>
        <p>Koppel de teamkalender uit de Voetbal.nl-app en alle wedstrijden van het seizoen staan erin: datum, aftrap, tegenstander, thuis of uit en de locatie. Daarna maak je elke week eenvoudig een plaatje voor de ouders met wie er meegaat, hoe laat iedereen er moet zijn, wie de shirts wast en wie fruit meeneemt.</p>
        <ul class="vinkjes">
          <li>Eén keer koppelen, het hele seizoen klaar</li>
          <li>Verzameltijd rekent de app uit, voor thuis en uit</li>
          <li>Wassen en fruit: de app onthoudt wie het de vorige keer deed</li>
        </ul>
        <a class="meer" href="{AGENDA}">Zo werkt de wedstrijdagenda <span aria-hidden="true">→</span></a>
      </div>
      <div class="feat-beeld oranje metplaatje">
        {telefoon("site-agenda-wedstrijden.webp", "De komende wedstrijden uit de Voetbal.nl-agenda in de app, met thuis of uit, aftrap en sportpark")}
        {plaatje()}
      </div>
    </div>

    <div class="feat om">
      <div class="feat-tekst">
        <span class="eyebrow"><b></b>Tips en tops</span>
        <h3>Zie waar elk kind aan werkt</h3>
        <p>Leg per speler vast wat goed gaat en waar hij of zij aan kan werken. Een tip die gelukt is, wordt met één tik een top. Zo zie je over het seizoen de vooruitgang, en waar het hele team op moet trainen.</p>
        <ul class="vinkjes">
          <li>Kies uit vaardigheden aan de bal en zonder bal, of typ een eigen tip</li>
          <li>Waar trainen we op? De tips die het vaakst terugkomen</li>
          <li>Alleen zichtbaar voor trainers, niet in het verslag voor ouders</li>
        </ul>
        <a class="meer" href="{TIPS}">Meer over tips en tops per speler <span aria-hidden="true">→</span></a>
      </div>
      <div class="feat-beeld">
        {telefoon("site-speler-tips-tops.webp", "Tips en tops bij een speler: tops, tips en wat al gelukt is")}
      </div>
    </div>
  </div>
</section>

<section class="block pricing band" id="prijs">
  <div class="wrap">
    <div class="head">
      <h2>Probeer gratis!</h2>
      <p>Probeer het eerst uit met je eigen team. Pas als je doorgaat, betaal je een klein bedrag per team.</p>
    </div>
    {prijskaarten()}
  </div>
</section>

{gidsen("/wisselschema-maken/", "/speeltijd-eerlijk-verdelen/", "/knvb-wedstrijdvormen/", titel="Handig voor elke jeugdtrainer")}
<section class="prose"><p class="leeftijden">Spelregels en speeltijd per leeftijd: <a href="/jo6/">JO6</a> · <a href="/jo7/">JO7</a> · <a href="/jo8/">JO8</a> · <a href="/jo9/">JO9</a> · <a href="/jo10/">JO10</a> · <a href="/jo11/">JO11</a> · <a href="/jo12/">JO12</a></p></section>

{faq_html(home_faq, open_eerste=True)}
{cta("Probeer het zaterdag met je eigen team", f"{GRATIS_ZIN}. Geen installatie, geen wachtwoord.")}
""",
     extra_ld=[app_ld()] + faq_ld(home_faq))

# ------------------------------------------------- wisselschema maken
# Voorbeeldschema's: per speler wat hij of zij elk kwart doet (K = keeper, V = veld, W = wissel)
WS_LABEL = {"K": "Keeper", "V": "Veld", "W": "Wissel"}


def getal(x):
    """37.5 -> '37,5' en 30.0 -> '30', zoals je het in een Nederlandse tekst schrijft."""
    return f"{x:g}".replace(".", ",")


def afgerond(x):
    """Gewoon afronden: 22,5 wordt 23 (Pythons round() zou 22 geven)."""
    return int(x + 0.5)


def controleer_schema(schema, plekken):
    """Bouwt niet als een voorbeeldschema niet klopt: elk blok precies genoeg spelers, hooguit één keeper."""
    for blok in range(len(schema[0][1])):
        op_veld = [k for _, kwarten in schema for k in [kwarten[blok]] if k != "W"]
        assert len(op_veld) == plekken, f"blok {blok + 1}: {len(op_veld)} spelers in plaats van {plekken}"
        assert op_veld.count("K") <= 1, f"blok {blok + 1}: meer dan één keeper"


def wisselschema_tabel(onderschrift, kwart_minuten, schema, blok="Kwart"):
    """Tabel met per speler wat hij of zij elk blok doet, en de totale speeltijd."""
    rijen = "".join(
        f"<tr><th scope='row'>{naam}</th>"
        + "".join(f"<td class='ws-{k.lower()}'>{WS_LABEL[k]}</td>" for k in kwarten)
        + f"<td>{getal(sum(kwart_minuten for k in kwarten if k != 'W'))} min</td></tr>"
        for naam, kwarten in schema)
    # Op de telefoon valt het woord "Kwart" weg, zodat de tabel in beeld past
    kop = "".join(f'<th scope="col"><span class="ws-lang">{blok} </span>{i}</th>' for i in range(1, len(schema[0][1]) + 1))
    breed = " ws-breed" if len(schema[0][1]) > 4 else ""   # meer dan vier blokken: nog compacter op de telefoon
    return f"""<div class="tablewrap"><table class="ws{breed}">
    <caption>{onderschrift}</caption>
    <thead><tr><th scope="col">Speler</th>{kop}<th scope="col">Totaal</th></tr></thead>
    <tbody>{rijen}</tbody>
  </table></div>"""


WS_6_MET_8 = [("Daan", "KKWV"), ("Milan", "VWKK"), ("Luca", "VWVV"), ("Noud", "VVWV"),
              ("Finn", "VVVW"), ("Jesse", "VVVW"), ("Sven", "WVVV"), ("Bram", "WVVV")]
WS_6_MET_9 = [("Daan", "KKWV"), ("Milan", "VWKK"), ("Luca", "VWVV"), ("Noud", "VWVV"),
              ("Finn", "VVWV"), ("Jesse", "VVWV"), ("Sven", "WVVW"), ("Bram", "WVVW"), ("Stijn", "WVVW")]
WS_8_MET_10 = [("Daan", "KKVV"), ("Milan", "VVKK"), ("Luca", "WVVV"), ("Noud", "WVVV"), ("Finn", "VWVV"),
               ("Jesse", "VWVV"), ("Sven", "VVWV"), ("Bram", "VVWV"), ("Stijn", "VVVW"), ("Ruben", "VVVW")]
WS_8_MET_11 = [("Daan", "KKWV"), ("Milan", "WVKK"), ("Luca", "WVVW"), ("Noud", "WVVV"), ("Finn", "VWVV"),
               ("Jesse", "VWVV"), ("Sven", "VWVV"), ("Bram", "VVWV"), ("Stijn", "VVWV"), ("Ruben", "VVVW"), ("Thijs", "VVVW")]
# 4 tegen 4 zonder keeper: zes blokjes van 7,5 minuut, steeds een ander tweetal aan de kant
WS_4_MET_6 = [("Daan", "VVWVVW"), ("Milan", "VVWVVW"), ("Luca", "VWVVWV"), ("Noud", "VWVVWV"),
              ("Finn", "WVVWVV"), ("Jesse", "WVVWVV")]
for _schema, _plekken in [(WS_6_MET_8, 6), (WS_6_MET_9, 6), (WS_8_MET_10, 8), (WS_8_MET_11, 8), (WS_4_MET_6, 4)]:
    controleer_schema(_schema, _plekken)

ws_faq = [
    ("Hoe maak je een wisselschema voor voetbal?", "Deel de wedstrijd op in vaste blokken, bij de pupillen meestal de vier kwarten tussen de time-outs en de rust. Tel de plekken per blok, verdeel ze zo gelijk mogelijk over de kinderen die er zijn, en zet de keepers apart. Wie deze keer minder speelt, begint de volgende wedstrijd in het veld."),
    ("Wat zijn de regels voor wisselen bij jeugdvoetbal?", "Bij de pupillen (O8 tot en met O12) mag je onbeperkt wisselen, en een gewisselde speler mag weer terug. Je wisselt bij een onderbreking, en de time-outs en de rust zijn de handigste momenten. De officiële regels staan op knvb.nl."),
    ("Mag je bij de pupillen onbeperkt wisselen?", "Ja. Bij de pupillen mag je doorwisselen; de time-outs en de rust zijn de natuurlijke momenten."),
    ("Welke app gebruik je voor een wisselschema?", "Er zijn meerdere apps voor jeugdtrainers. Opstelling maakt het wisselschema per wedstrijd op basis van wie er is, houdt de speeltijd over het hele seizoen bij en geeft tijdens de wedstrijd een seintje bij elk wisselmoment."),
    ("Wat als er iemand geblesseerd raakt of te laat komt?", "Dan klopt je schema niet meer. In Opstelling geef je de wijziging door en maakt de app de rest van de wedstrijd opnieuw, met de al gespeelde minuten erin verwerkt."),
    ("Kan een medetrainer hetzelfde schema zien?", "Ja. Iedere trainer van het team ziet dezelfde wedstrijd, kan de opstelling klaarzetten en tijdens de wedstrijd live meekijken."),
    ("Kan de keeper ook in het veld spelen?", "Als je met wisselende keepers speelt wel, en de app regelt dat: wie een helft keept, krijgt in de andere helft veldtijd."),
]
page("/wisselschema-maken/",
     "Wisselschema voetbal: voorbeelden voor 6 tegen 6 en 8 tegen 8",
     "Wisselschema voetbal maken voor je jeugdteam: voorbeelden voor 6 tegen 6 en 8 tegen 8, de wisselregels bij de pupillen en tips voor eerlijke speeltijd.",
     f"""
<section class="prose">
  <h1>Wisselschema voetbal maken voor je jeugdteam</h1>
  <p class="lead">Een goed wisselschema voor voetbal zorgt ervoor dat elk kind ongeveer evenveel speeltijd krijgt en dat jij daar niet voor hoeft te rekenen langs de lijn. Hieronder staan voorbeelden voor 6 tegen 6 en 8 tegen 8 die je zo kunt overnemen, en de regels voor wisselen bij de pupillen.</p>

  <h2>Hoe maak je een wisselschema?</h2>
  <ol>
    <li><strong>Kies je wisselmomenten.</strong> Bij de pupillen heeft elke helft halverwege een time-out. Met de rust erbij heb je vier kwarten, en drie vaste momenten om te wisselen.</li>
    <li><strong>Tel de plekken.</strong> Bij 6 tegen 6 zijn er per kwart zes plekken, keeper meegerekend. Over vier kwarten zijn dat er 24.</li>
    <li><strong>Verdeel ze over wie er is.</strong> Met acht kinderen speelt iedereen drie kwarten. Met negen kinderen lukt dat niet precies: zes kinderen spelen drie kwarten, drie kinderen twee.</li>
    <li><strong>Zet de keepers apart.</strong> Laat een keeper in de andere helft in het veld spelen, zodat keepen niet ten koste gaat van voetballen.</li>
    <li><strong>Onthoud wie er minder speelde.</strong> Die kinderen beginnen de volgende wedstrijd in het veld. Zo wordt het over het seizoen eerlijk, ook als het in één wedstrijd niet precies rondkomt.</li>
  </ol>

  <h2>Wisselschema voetbal 6 tegen 6 (O8, O9 en O10)</h2>
  <p>Bij O8 en O9 speel je 2 × 20 minuten, dus vier kwarten van tien minuten. Met acht spelers zitten er elk kwart twee kinderen aan de kant, en speelt iedereen precies 30 minuten. Daan keept de eerste helft, Milan de tweede.</p>
  {wisselschema_tabel("Wisselschema 6 tegen 6 met 8 spelers, 2 × 20 minuten (O8 en O9)", 10, WS_6_MET_8)}
  <p>Wisselmomenten: na 10 minuten Sven en Bram erin voor Milan en Luca. In de rust Milan (keeper) en Luca erin voor Daan en Noud. Na 30 minuten Daan en Noud erin voor Finn en Jesse.</p>

  <h3>6 tegen 6 met 9 spelers</h3>
  <p>Met negen spelers zitten er elk kwart drie kinderen aan de kant. Dan komt het niet precies rond: zes kinderen spelen 30 minuten, drie kinderen 20. Sven, Bram en Stijn beginnen de volgende wedstrijd daarom in het veld. Wil je het binnen de wedstrijd gelijker, wissel dan ook halverwege een kwart.</p>
  {wisselschema_tabel("Wisselschema 6 tegen 6 met 9 spelers, 2 × 20 minuten (O8 en O9)", 10, WS_6_MET_9)}
  <p>Bij O10 speel je 2 × 25 minuten. Het schema blijft hetzelfde, alleen duurt elk kwart 12,5 minuut. Alle regels voor 6 tegen 6 op een rij staan op de pagina over <a href="/jo9/">JO9</a>.</p>

  <h2>Wisselschema voetbal 8 tegen 8 (O11 en O12)</h2>
  <p>Bij O11 en O12 speel je 2 × 30 minuten, dus vier kwarten van een kwartier. Met tien spelers zitten er elk kwart twee kinderen aan de kant. De twee keepers spelen de hele wedstrijd: een helft op doel en een helft in het veld. De andere acht spelen elk 45 minuten.</p>
  {wisselschema_tabel("Wisselschema 8 tegen 8 met 10 spelers, 2 × 30 minuten (O11 en O12)", 15, WS_8_MET_10)}

  <h2>Regels voor wisselen bij de pupillen</h2>
  <ul>
    <li><strong>Onbeperkt wisselen:</strong> je mag zo vaak wisselen als je wilt, en een gewisselde speler mag weer terug.</li>
    <li><strong>Vaste momenten:</strong> de time-out halverwege elke helft en de rust zijn de handigste momenten, want dan ligt het spel toch stil.</li>
    <li><strong>Speelduur per leeftijd:</strong> hoe lang een kwart duurt, hangt af van de leeftijd. Zie het overzicht van de <a href="/knvb-wedstrijdvormen/">KNVB-wedstrijdvormen</a>.</li>
  </ul>

  <h2>Wat maakt een wisselschema op papier lastig</h2>
  <ul>
    <li>Op vrijdagavond melden er twee kinderen af en klopt je indeling niet meer.</li>
    <li>Een blessure of een late aankomst gooit de rest van de wedstrijd om.</li>
    <li>Je weet aan het eind niet meer wie nu precies hoe lang speelde, dus de week erna begin je weer bij nul.</li>
    <li>Je rouleert keepers, dus het is lastig om bij te houden hoeveel speeltijd in het veld iedereen heeft.</li>
  </ul>

  <h2>Hoe de Opstelling app het doet</h2>
  <p>Je vinkt aan wie er is en kiest de keepers. De app maakt daarna het schema: wie speelt welk kwart, wie wisselt wanneer, en wie staat waar. Tijdens de wedstrijd loopt de klok mee en zie je het volgende wisselmoment met de namen erbij.</p>
  <div class="duo">
    <figure>{telefoon("site-opstelling.webp", "Wisselschema voetbal 6 tegen 6 in de Opstelling app: kwart 1 met Daan op doel, Luca en Jesse als wissel, en halverwege Finn erin voor Stijn")}<figcaption>Het wisselschema per kwart</figcaption></figure>
    <figure>{telefoon("site-wedstrijd.webp", "Wisselmoment tijdens de wedstrijd in de Opstelling app: Sven erin voor Jesse, met de klok en de stand erboven")}<figcaption>Een seintje bij elk wisselmoment</figcaption></figure>
  </div>
  <p>Wijzigt er iets, dan past de app de rest van de wedstrijd aan met de al gespeelde minuten erin verwerkt. En de minuten van vandaag tellen automatisch mee bij de volgende wedstrijd, zodat wie nu minder speelde, dan voorrang krijgt.</p>

  <h2>Je houdt zelf de regie</h2>
  <p>Je kunt spelers altijd ruilen, zelf de wisselmomenten kiezen (bijvoorbeeld alleen in de rust), of de opstelling helemaal zelf neerzetten en de app alleen de tijd laten bijhouden.</p>
  <p>Heb je de teamkalender uit de Voetbal.nl-app, dan staan alle wedstrijden al klaar en begin je meteen bij het aanvinken. Zo <a href="{AGENDA}">koppel je je Voetbal.nl-kalender</a>.</p>
</section>

{faq_html(ws_faq)}
{cta("Laat de app je wisselschema maken", f"Aanvinken wie er is, keepers kiezen en klaar. {GRATIS_ZIN}.")}

{gidsen("/speeltijd-eerlijk-verdelen/", AGENDA, "/knvb-wedstrijdvormen/")}
""", extra_ld=faq_ld(ws_faq))

# --------------------------------------------- speeltijd eerlijk verdelen
st_faq = [
    ("Wat is eerlijke speeltijd?", "Dat elk kind over het seizoen ongeveer evenveel speelt, ongeacht niveau. Binnen één wedstrijd lukt dat zelden precies; over meerdere wedstrijden wel."),
    ("Houdt Opstelling rekening met eerdere wedstrijden?", "Ja. De app onthoudt per speler de gespeelde minuten en geeft wie achterliep de volgende wedstrijd voorrang."),
    ("Telt keepen mee als speeltijd?", "Keepen telt mee in de totale tijd, maar de app zorgt ervoor dat een kind dat een halve wedstrijd keept in de andere helft in het veld staat."),
    ("Kan ik aan ouders laten zien hoeveel hun kind speelde?", "Ja. Per speler zie je de gespeelde minuten, het aandeel over het seizoen en de doelpunten."),
]
page("/speeltijd-eerlijk-verdelen/",
     "Eerlijke speeltijd in een jeugdteam, zonder bijhouden",
     f"Elk kind ongeveer evenveel speeltijd, ook als er elke week anderen zijn? Opstelling rekent en onthoudt het voor je. {GRATIS_KORT}.",
     f"""
<section class="prose">
  <h1>Eerlijke speeltijd in een jeugdteam</h1>
  <p class="lead">Kinderen worden beter van spelen, niet van kijken. Toch sluipt er zo een scheve verdeling in: de ene week zijn er dertien kinderen, de volgende week acht, en wie vorige keer lang op de bank zat, staat er deze week zomaar weer naast.</p>

  <h2>Waarom het lastig is om bij te houden</h2>
  <p>Binnen één wedstrijd komt het bijna nooit precies rond: met negen kinderen en zes plekken speelt de een nu eenmaal langer dan de ander. Eerlijk worden doet het pas over meerdere wedstrijden, en dan moet je wel weten wie er de vorige keren tekortkwam. Precies dat onthouden lukt langs de lijn niet.</p>

  <h2>Wat Opstelling voor je doet</h2>
  <ul>
    <li><strong>Verdeelt de minuten</strong> zo gelijk mogelijk over de kinderen die er zijn.</li>
    <li><strong>Onthoudt het seizoen:</strong> wie vorige keer minder speelde, krijgt nu voorrang.</li>
    <li><strong>Houdt rekening met keepen,</strong> zodat een keeper in de andere helft gewoon voetbalt.</li>
    <li><strong>Rekent mee tijdens de wedstrijd,</strong> ook bij blessures, late aankomst of uitloop.</li>
    <li><strong>Maakt het zichtbaar</strong> per speler, zodat je het kunt laten zien als een ouder ernaar vraagt.</li>
  </ul>

  <h2>Eerlijk verdelen en toch coachen</h2>
  <p>Eerlijke speeltijd betekent niet dat alles vastligt. Bij de pupillen wegen spelen en plezier het zwaarst; hoe ouder de kinderen, hoe meer ruimte er is voor keuzes op basis van inzet en training. Je kunt in de app altijd zelf ingrijpen, en de app rekent gewoon verder.</p>
  <p>Speeltijd is één kant. Wil je ook zien hoe elk kind zich ontwikkelt, dan leg je per speler <a href="{TIPS}">tips en tops</a> vast: wat gaat goed en waar werkt hij of zij aan.</p>
</section>

{faq_html(st_faq)}
{cta("Laat de speeltijd zichzelf bijhouden", f"Opstelling verdeelt de minuten en onthoudt wie achterliep. {GRATIS_ZIN}.")}

{gidsen("/wisselschema-maken/", TIPS, "/prijzen/")}
""", extra_ld=faq_ld(st_faq))

# ------------------------------------------------ knvb wedstrijdvormen
rows = [
    ("O7", "4 tegen 4", "Nee", "3 × 15 minuten", "Tussen de blokjes van 7,5 minuut (6 blokjes)"),
    ("O8 en O9", "6 tegen 6", "Ja", "2 × 20 minuten", "Time-out na 10 minuten per helft (4 kwarten)"),
    ("O10", "6 tegen 6", "Ja", "2 × 25 minuten", "Time-out na 12,5 minuut per helft (4 kwarten)"),
    ("O11 en O12", "8 tegen 8", "Ja", "2 × 30 minuten", "Time-out na 15 minuten per helft (4 kwarten)"),
]
tabel = "".join(f"<tr><th scope='row'>{a}</th><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in rows)
knvb_faq = [
    ("Hoe lang duurt een wedstrijd bij O8?", "Twee helften van twintig minuten, met in elke helft na tien minuten een korte time-out. Zo speel je in feite vier kwarten van tien minuten."),
    ("Spelen pupillen met een keeper?", "Vanaf O8 wel. Bij O7 wordt 4 tegen 4 gespeeld zonder keeper."),
    ("Wanneer mag je wisselen bij de pupillen?", "Bij de pupillen mag je onbeperkt wisselen. In de praktijk doen trainers dat bij de time-outs en in de rust."),
]
page("/knvb-wedstrijdvormen/",
     "KNVB-wedstrijdvormen O7 t/m O12: speelduur, spelers en wisselen",
     "Overzicht van de KNVB-wedstrijdvormen per leeftijd: aantal spelers, wel of geen keeper, speelduur en handige wisselmomenten, van O7 tot en met O12.",
     f"""
<section class="prose">
  <h1>KNVB-wedstrijdvormen per leeftijd</h1>
  <p class="lead">Handig overzicht voor jeugdtrainers: hoeveel spelers, wel of geen keeper, hoe lang er gespeeld wordt en welke wisselmomenten daarbij passen. Bedoeld als spiekbriefje langs de lijn; de officiële regels staan op knvb.nl.</p>

  <div class="tablewrap"><table>
    <caption>Wedstrijdvormen en speelduur per leeftijdscategorie (seizoen 2026/'27)</caption>
    <thead><tr><th scope="col">Leeftijd</th><th scope="col">Vorm</th><th scope="col">Keeper</th><th scope="col">Speelduur</th><th scope="col">Handige wisselmomenten</th></tr></thead>
    <tbody>{tabel}</tbody>
  </table></div>
  <p>Elke helft heeft halverwege een korte time-out. In de praktijk speel je dus vier kwarten, met de time-outs en de rust als wisselmomenten.</p>
  <p>Alles over één leeftijd, met spelregels, speeltijd, opstelling en wisselschema: <a href="/jo6/">JO6</a>, <a href="/jo7/">JO7</a>, <a href="/jo8/">JO8</a>, <a href="/jo9/">JO9</a>, <a href="/jo10/">JO10</a>, <a href="/jo11/">JO11</a> en <a href="/jo12/">JO12</a>.</p>

  <h2>Wat betekent dit voor je speeltijd?</h2>
  <p>Bij 6 tegen 6 met 2 × 20 minuten zijn er 240 speelminuten te verdelen (zes plekken maal veertig minuten). Met negen kinderen komt dat neer op ongeveer 27 minuten per kind, keepen meegerekend. Zijn er twaalf kinderen, dan blijft er twintig minuten per kind over, en wordt het belangrijker om over de weken heen bij te houden wie minder speelde.</p>

  <h2>Wisselen bij de pupillen</h2>
  <p>Bij de pupillen mag je onbeperkt wisselen. De time-outs en de rust zijn de natuurlijke momenten. Wissel je alleen in de rust, dan speelt iedereen een hele of een halve wedstrijd, en zijn de verschillen groot.</p>
</section>

{faq_html(knvb_faq)}
{cta("Laat de app de regels toepassen", "Kies het niveau van je team en Opstelling gebruikt automatisch de juiste speelduur, spelers en wisselmomenten.")}

{gidsen("/wisselschema-maken/", "/speeltijd-eerlijk-verdelen/", "/prijzen/")}
""", extra_ld=faq_ld(knvb_faq))

# ------------------------------------------------ pagina's per leeftijd
# Eén pagina per leeftijd (O9 = JO9), omdat trainers en ouders per leeftijd zoeken:
# "spelregels jo9", "speeltijd jo9", "jo9 hoeveel spelers". Bron: de KNVB-infographics
# 4 tegen 4, 6 tegen 6 en 8 tegen 8 voor seizoen 2026/'27 en de KNVB-pagina over O6.
# Sinds 2026/'27 heet JO9 officieel O9; er wordt nog vooral op "jo9" gezocht.

def speeltijd_per_kind(plekken, minuten, aantallen, blok="kwart"):
    """Tabel: hoeveel minuten elk kind ongeveer speelt bij een bepaald aantal spelers."""
    rijen = "".join(f"<tr><th scope='row'>{n} spelers</th><td>{n - plekken}</td><td>ongeveer {afgerond(plekken * minuten / n)} minuten</td></tr>"
                    for n in aantallen)
    return f"""<div class="tablewrap"><table>
    <caption>Speeltijd per kind bij {plekken} tegen {plekken} en {minuten} minuten speeltijd ({plekken * minuten} speelminuten)</caption>
    <thead><tr><th scope="col">Aantal spelers</th><th scope="col">Wissels per {blok}</th><th scope="col">Speeltijd per kind</th></tr></thead>
    <tbody>{rijen}</tbody>
  </table></div>"""


def in_het_kort(rijen, onderschrift):
    regels = "".join(f"<tr><th scope='row'>{a}</th><td>{b}</td></tr>" for a, b in rijen)
    return f"""<div class="tablewrap"><table>
    <caption>{onderschrift}</caption>
    <tbody>{regels}</tbody>
  </table></div>"""


def regellijst(regels):
    return "<ul>" + "".join(f"<li><strong>{kop}:</strong> {tekst}</li>" for kop, tekst in regels) + "</ul>"


# De spelregels per wedstrijdvorm, samengevat uit de KNVB-infographics
VORM = {
    4: {
        "veld_zin": "30 bij 20 meter, met doeltjes van 3 bij 1 meter en zonder keeper. Er wordt gespeeld met een bal maat 3.",
        "naam": "4 tegen 4", "veld": "30 × 20 meter", "doel": "3 × 1 meter, zonder keeper", "bal": "Maat 3",
        "keeper": "Nee", "leiding": "Geen scheidsrechter of spelbegeleider: de begeleiders van beide teams zorgen samen voor een goed verloop",
        "dispensatie": "Maximaal 1 speler per wedstrijd", "strafschop": "Niet tijdens de wedstrijd; na afloop vanaf 7 meter, in onderling overleg",
        "standen": "Geen standen en uitslagen gepubliceerd",
        "regels": [
            ("Aftrap", "in het midden van het veld, met een dribbel of een pass. Beide teams starten op eigen helft."),
            ("Na een doelpunt", "dribbelt een speler van het team dat het tegendoelpunt kreeg de bal in naast het eigen doel. De tegenpartij begint op eigen helft."),
            ("Uitbal", "je dribbelt de bal in. Inpassen of inschieten mag niet. Na het indribbelen mag die speler wel meteen scoren."),
            ("Achterbal", "een speler dribbelt de bal in naast het doel."),
            ("Hoekschop", "vanaf de hoek indribbelen, inpassen of inschieten. Je mag er direct uit scoren."),
            ("Vrije bal", "alleen bij hoge uitzondering. Je mag dribbelen, passen of schieten vanaf de plek van de overtreding."),
            ("Afstand", "bij een hervatting staat de tegenstander op minimaal 5 meter, behalve na een doelpunt."),
            ("Superspeler", "staat een team 3 doelpunten achter, dan mag het met 5 spelers spelen. Is het verschil weer 2 doelpunten, dan vervalt de superspeler."),
            ("Strafschoppen", "niet tijdens de wedstrijd. Na afloop mag het wel, in overleg. De KNVB stelt voor dat ieder kind er een neemt en daarna probeert er een te stoppen."),
            ("Voor en na de wedstrijd", "begroeten spelers en begeleiders elkaar met een boks."),
        ],
    },
    6: {
        "veld_zin": "Een bijna kwart veld van 42,5 bij 30 meter, met pupillendoelen van 5 bij 2 meter. Er wordt gespeeld met een bal maat 4 (290 gram).",
        "naam": "6 tegen 6", "veld": "42,5 × 30 meter (bijna een kwart veld)", "doel": "Pupillendoel, 5 × 2 meter", "bal": "Maat 4 (290 gram)",
        "keeper": "Ja", "leiding": "Spelbegeleider langs het veld", "dispensatie": "Maximaal 1 speler per wedstrijd",
        "strafschop": "Vanaf 7 meter", "standen": "Geen standen en uitslagen gepubliceerd", "rust": 10,
        "regels": [
            ("Aftrap", "in het midden van het veld, beide teams starten op eigen helft. Uit een aftrap kun je niet direct scoren. Na een doelpunt neemt het team dat het tegendoelpunt kreeg de aftrap."),
            ("Uitbal", "je dribbelt de bal in. Inpassen of inschieten mag niet. Na het indribbelen mag die speler wel meteen scoren."),
            ("Achterbal", "de keeper of een veldspeler dribbelt, past of schiet de bal in vanaf de grond, binnen het keepersgebied."),
            ("Hoekschop", "vanaf de hoek indribbelen, inpassen of inschieten. Je mag er direct uit scoren."),
            ("Vrije bal", "altijd direct. Je mag dribbelen, passen of schieten. De tegenstander staat bij elke hervatting op minimaal 5 meter."),
            ("Keepersgebied", "tot 7 meter van de achterlijn, gemarkeerd met twee pionnen. Tot daar mag de keeper de bal in de handen hebben."),
            ("Terugspeelbal", "speelt een teamgenoot de bal met de voet terug, dan mag de keeper hem niet oppakken."),
            ("Strafschop", "alleen als een duidelijke scoringskans in het keepersgebied wordt ontnomen. Na de wedstrijd nemen de teams strafschoppen tegen elkaar."),
            ("Voor en na de wedstrijd", "begroeten spelers en begeleiders elkaar met een boks."),
        ],
    },
    8: {
        "veld_zin": "Bijna een half veld van 64 bij 42,5 meter, met pupillendoelen van 5 bij 2 meter. Er wordt gespeeld met een bal maat 5 (320 gram).",
        "naam": "8 tegen 8", "veld": "64 × 42,5 meter (bijna een half veld)", "doel": "Pupillendoel, 5 × 2 meter", "bal": "Maat 5 (320 gram)",
        "keeper": "Ja", "leiding": "Pupillenscheidsrechter van minimaal 12 jaar, in het veld", "dispensatie": "Maximaal 2 spelers per wedstrijd",
        "strafschop": "Vanaf 9 meter", "standen": "Ja, de KNVB publiceert uitslagen en standen", "rust": 15,
        "regels": [
            ("Aftrap", "in het midden van het veld, beide teams starten op eigen helft. Anders dan bij 6 tegen 6 mag je uit de aftrap direct scoren. Na een doelpunt neemt het team dat het tegendoelpunt kreeg de aftrap."),
            ("Uitbal", "je dribbelt de bal in. Inpassen of inschieten mag niet. Na het indribbelen mag die speler wel meteen scoren."),
            ("Achterbal", "de keeper of een veldspeler dribbelt, past of schiet de bal in vanaf de grond, binnen het keepersgebied."),
            ("Hoekschop", "vanaf de hoek indribbelen, inpassen of inschieten. Je mag er direct uit scoren."),
            ("Vrije bal", "altijd direct. Je mag dribbelen, passen of schieten. De tegenstander staat bij elke hervatting op minimaal 5 meter."),
            ("Keepersgebied", "tot de hoogte van de zijkant van het strafschopgebied (de 16 meter), gemarkeerd met twee pionnen. Tot daar mag de keeper de bal in de handen hebben."),
            ("Terugspeelbal", "speelt een teamgenoot de bal met de voet terug, dan mag de keeper hem niet oppakken. Gebeurt het weer, dan volgt een indirecte vrije trap op 9 meter."),
            ("Strafschop", "vanaf 9 meter, alleen als een duidelijke scoringskans in het keepersgebied wordt ontnomen. Na de wedstrijd nemen de teams strafschoppen tegen elkaar."),
            ("Voor en na de wedstrijd", "begroeten spelers en de pupillenscheidsrechter elkaar met een boks."),
        ],
    },
}

OPSTELLINGEN = {
    4: [("1-2-1", "één speler achter, twee op de zijkanten en één voorin. Een ruit, met veel driehoekjes om naar elkaar te passen."),
        ("2-2", "twee achter en twee voor. Eenvoudig, maar met minder verbinding tussen achter en voor.")],
    6: [("1-2-1-2", "een keeper, twee verdedigers, één middenvelder en twee aanvallers. Een ruit, met veel driehoekjes om naar elkaar te passen."),
        ("1-2-2-1", "een keeper, twee verdedigers, twee middenvelders en één spits. Meer spelers in het midden, minder voorin.")],
    8: [("1-3-3-1", "een keeper, drie verdedigers, drie middenvelders en één spits. Evenwichtig, met de ruimte goed verdeeld over het veld."),
        ("1-2-3-2", "een keeper, twee verdedigers, drie middenvelders en twee aanvallers. Aanvallender, met minder spelers achterin.")],
}

PRESTATIEF = """<h2>Prestatief spelen of gelijke speeltijd?</h2>
  <p>Vanaf O11 houdt de KNVB standen bij, en sommige clubs hebben dan een selectieteam dat prestatiever speelt. Dan wil je niet altijd iedereen evenveel laten spelen, en dat hoeft ook niet. Belangrijk is wel dat je weet wie hoeveel speelt, zodat niemand ongemerkt wekenlang aan de kant staat.</p>
  <p>In Opstelling kies je per wedstrijd hoe je wisselt: de app verdeelt de speeltijd eerlijk, je kiest zelf vaste wisselmomenten, of je zet de opstelling helemaal zelf neer. De app houdt de minuten in alle gevallen bij.</p>"""

AANTALLEN = {4: [5, 6, 7, 8], 6: [7, 8, 9, 10, 11, 12], 8: [9, 10, 11, 12, 13, 14]}

# Per leeftijd: geboortejaar in 2026/'27, wedstrijdvorm, minuten per helft, en een eigen inleiding en voorbeeld
LEEFTIJDEN = [
    {"o": 7, "geboren": 2020, "vorm": 4, "titel": f"Spelregels JO7 {SEIZOEN}: 4 tegen 4, speeltijd en wisselschema",
     "beschrijving": "Alles over JO7 (O7): spelregels van 4 tegen 4 zonder keeper, hoe lang de wedstrijdjes duren, het veld, de superspeler en een eerlijk wisselschema.",
     "inleiding": "Bij JO7, sinds dit seizoen officieel O7 (Onder 7), maken kinderen kennis met echte wedstrijdjes. Ze spelen 4 tegen 4 zonder keeper op een klein veld, zodat iedereen veel aan de bal komt en veel scoort.",
     "schema": (WS_4_MET_6, 7.5, "Wisselschema JO7, 4 tegen 4 met 6 spelers, 6 blokjes van 7,5 minuut", "Met zes kinderen staan er elk blokje twee aan de kant, steeds een ander tweetal. Zo speelt iedereen 30 van de 45 minuten."),
     "extra": "<h2>Na JO7</h2>\n  <p>Vanaf O8 speel je 6 tegen 6 op een groter veld, en voor het eerst met een keeper. Zie <a href=\"/jo8/\">JO8</a>.</p>"},
    {"o": 8, "geboren": 2019, "vorm": 6, "helft": 20, "titel": f"Spelregels JO8 {SEIZOEN}: speeltijd, veld en wisselschema",
     "beschrijving": "Alles over JO8 (O8): de overstap naar 6 tegen 6 met keeper, spelregels, hoe lang een wedstrijd duurt, het veld, een opstelling en een eerlijk wisselschema.",
     "inleiding": "Bij JO8, sinds dit seizoen officieel O8 (Onder 8), gaan kinderen van 4 tegen 4 naar 6 tegen 6. Voor het eerst staat er een keeper in het doel en is het veld een stuk groter.",
     "schema": (WS_6_MET_9, None, "Wisselschema JO8, 6 tegen 6 met 9 spelers, 2 × 20 minuten", "Met negen kinderen staan er elk kwart drie aan de kant. Dan komt het niet precies rond: zes kinderen spelen 30 minuten, drie kinderen 20. Sven, Bram en Stijn beginnen de volgende wedstrijd daarom in het veld."),
     "extra": "<h2>Voor het eerst een keeper</h2>\n  <p>Bij JO8 wil bijna elk kind wel eens op doel staan, of juist helemaal niet. Laat de keepers rouleren, bijvoorbeeld één keeper per helft. Zo leert iedereen het een keer, en voetbalt een keeper in de andere helft gewoon mee in het veld.</p>"},
    {"o": 9, "geboren": 2018, "vorm": 6, "helft": 20, "titel": f"Spelregels JO9 {SEIZOEN}: speeltijd, veld en wisselschema",
     "beschrijving": "Alles over JO9 (O9): spelregels, hoe lang een wedstrijd duurt, hoeveel spelers, het veld, een opstelling voor 6 tegen 6 en een eerlijk wisselschema.",
     "inleiding": "Bij JO9, sinds dit seizoen officieel O9 (Onder 9), spelen kinderen 6 tegen 6 op een kwart veld. Op deze pagina staat alles wat je als trainer of ouder wilt weten: de spelregels, hoe lang een wedstrijd duurt, een opstelling en een wisselschema waarmee iedereen eerlijk speelt.",
     "schema": (WS_6_MET_8, None, "Wisselschema JO9, 6 tegen 6 met 8 spelers, 2 × 20 minuten", "Met acht kinderen staan er elk kwart twee aan de kant, en speelt iedereen precies 30 minuten. Daan keept de eerste helft, Milan de tweede."),
     "extra": ""},
    {"o": 10, "geboren": 2017, "vorm": 6, "helft": 25, "titel": f"Spelregels JO10 {SEIZOEN}: speeltijd, veld en wisselschema",
     "beschrijving": "Alles over JO10 (O10): spelregels van 6 tegen 6, hoe lang een wedstrijd duurt (2 × 25 minuten), het veld, een opstelling en een eerlijk wisselschema.",
     "inleiding": "Bij JO10, sinds dit seizoen officieel O10 (Onder 10), spelen kinderen hun laatste jaar 6 tegen 6. De regels zijn hetzelfde als bij JO8 en JO9, maar de helften duren vijf minuten langer.",
     "schema": (WS_6_MET_8, None, "Wisselschema JO10, 6 tegen 6 met 8 spelers, 2 × 25 minuten", "Met acht kinderen staan er elk kwart twee aan de kant, en speelt iedereen precies 37,5 minuut. Daan keept de eerste helft, Milan de tweede."),
     "extra": "<h2>Na JO10</h2>\n  <p>Vanaf O11 speel je 8 tegen 8 op bijna een half veld, met een pupillenscheidsrechter en standen. Laat kinderen in het laatste jaar 6 tegen 6 daarom al eens op verschillende plekken spelen. Zie <a href=\"/jo11/\">JO11</a>.</p>"},
    {"o": 11, "geboren": 2016, "vorm": 8, "helft": 30, "titel": f"Spelregels JO11 {SEIZOEN}: 8 tegen 8, speeltijd en spelers",
     "beschrijving": "Alles over JO11 (O11 en MO11): spelregels van 8 tegen 8, hoe lang een wedstrijd duurt, het veld, standen, een opstelling en een wisselschema.",
     "inleiding": "Bij JO11, sinds dit seizoen officieel O11 (Onder 11), gaan kinderen van 6 tegen 6 naar 8 tegen 8 op bijna een half veld. Er fluit een pupillenscheidsrechter, en voor het eerst publiceert de KNVB uitslagen en standen. Meidenteams heten MO11 en spelen met dezelfde regels.",
     "schema": (WS_8_MET_10, None, "Wisselschema JO11, 8 tegen 8 met 10 spelers, 2 × 30 minuten", "Met tien spelers staan er elk kwart twee aan de kant. De twee keepers spelen de hele wedstrijd: een helft op doel en een helft in het veld. De andere acht spelen elk 45 minuten."),
     "extra": PRESTATIEF},
    {"o": 12, "geboren": 2015, "vorm": 8, "helft": 30, "titel": f"Spelregels JO12 {SEIZOEN}: 8 tegen 8, speeltijd en opstelling",
     "beschrijving": "Alles over JO12 (O12): spelregels van 8 tegen 8, hoe lang een wedstrijd duurt, het veld, standen, een opstelling en een wisselschema met 11 spelers.",
     "inleiding": "Bij JO12, sinds dit seizoen officieel O12 (Onder 12), spelen kinderen hun tweede en laatste jaar 8 tegen 8. Daarna gaan ze naar een groter veld en meer spelers.",
     "schema": (WS_8_MET_11, None, "Wisselschema JO12, 8 tegen 8 met 11 spelers, 2 × 30 minuten", "Met elf spelers staan er elk kwart drie aan de kant. Tien spelers spelen 45 minuten. Luca speelt deze keer een kwart minder en begint de volgende wedstrijd in het veld."),
     "extra": PRESTATIEF},
]


def leeftijd_faq(l, v):
    jo = f"JO{l['o']}"
    if l["vorm"] == 4:
        duur = "Elk team speelt per keer drie wedstrijdjes van 15 minuten, elk in twee blokjes van 7,5 minuut."
        wie = "Niemand: er is geen scheidsrechter of spelbegeleider. De begeleiders van beide teams zorgen samen dat het spel goed verloopt."
        spelers = "Met 4 tegen 4, zonder keeper. Staat een team 3 doelpunten achter, dan mag het met een vijfde speler spelen, de superspeler."
    else:
        h = l["helft"]
        duur = (f"Twee helften van {h} minuten. Halverwege elke helft is er een time-out van maximaal twee minuten, en de rust duurt maximaal {v['rust']} minuten. "
                f"Met alles erbij ben je hooguit zo'n {afgerond((2 * h + 4 + v['rust']) / 5) * 5} minuten bezig.")
        wie = ("Een spelbegeleider. Die staat langs het veld, laat de kinderen zoveel mogelijk zelf spelen en grijpt alleen in als de spelregels duidelijk niet goed gaan."
               if v["naam"] == "6 tegen 6" else
               "Een pupillenscheidsrechter van minimaal 12 jaar. Die beweegt tussen de spelers, fluit als het nodig is en legt de spelregels uit.")
        spelers = f"Met {v['naam']}, de keeper meegerekend. Je mag onbeperkt wisselen."
    standen = ("De KNVB publiceert bij O7 tot en met O10 geen standen en uitslagen. De uitslag wordt wel doorgegeven, zodat teams op het juiste niveau worden ingedeeld."
               if v["naam"] != "8 tegen 8" else "Ja. Vanaf O11 publiceert de KNVB de uitslagen en standen.")
    return [
        (f"Hoe lang duurt een wedstrijd bij {jo}?", duur),
        (f"Met hoeveel spelers speelt {jo}?", spelers),
        (f"Hoe groot is het veld bij {jo}?", v["veld_zin"]),
        (f"Is er buitenspel bij {jo}?", f"Nee. De buitenspelregel geldt niet bij {v['naam']}."),
        (f"Wie fluit er bij {jo}?", wie),
        ("Worden de uitslagen en standen bijgehouden?", standen),
        (f"Welk geboortejaar speelt in {jo}?", f"In seizoen 2026/'27 spelen kinderen die in {l['geboren']} geboren zijn in O{l['o']}."),
        (f"Wat is het verschil tussen {jo} en O{l['o']}?", f"Er is geen verschil. Sinds seizoen 2026/'27 heet {jo} bij de KNVB officieel O{l['o']} (Onder {l['o']}). Veel clubs en ouders zeggen nog {jo}."),
    ]


def kort_antwoord(l, v):
    """Eén alinea met de kern, bovenaan de pagina: Google neemt zulke zinnen graag over in zijn antwoord."""
    jo, veld = f"JO{l['o']}", v["veld"].split(" (")[0]
    if l["vorm"] == 4:
        kern = (f"{jo} speelt 4 tegen 4 zonder keeper: drie wedstrijdjes van 15 minuten op een veld van {veld}, "
                "met doeltjes van 3 × 1 meter. Er is geen scheidsrechter, geen buitenspel en geen stand.")
    else:
        leiding = ("Een spelbegeleider staat langs het veld" if l["vorm"] == 6 else "Een pupillenscheidsrechter leidt de wedstrijd")
        standen = ("de KNVB publiceert geen standen" if l["vorm"] == 6 else "de KNVB publiceert uitslagen en standen")
        kern = (f"{jo} speelt {v['naam']} met keeper, 2 × {l['helft']} minuten met een time-out halverwege elke helft, "
                f"op een veld van {veld} met een bal {v['bal'][0].lower()}{v['bal'][1:]}. {leiding}, er is geen buitenspel en {standen}.")
    return f'<p class="kort-antwoord"><strong>In het kort:</strong> {kern}</p>'


def leeftijd_navigatie(o):
    """Links naar alle leeftijden, zodat Google (en de bezoeker) ze allemaal vindt."""
    links = " · ".join(f'<a href="/jo{n}/">JO{n}</a>' if n != o else f"<strong>JO{n}</strong>" for n in range(6, 13))
    return f'<p class="leeftijden">Per leeftijd: {links}</p>'


for l in LEEFTIJDEN:
    v = VORM[l["vorm"]]
    jo, plekken = f"JO{l['o']}", l["vorm"]
    schema, blok_minuten, onderschrift, uitleg = l["schema"]
    if plekken == 4:
        speeltijd = "3 wedstrijdjes van 15 minuten, elk in 2 blokjes van 7,5 minuut"
        totaal, blok = 45, "blokje"
        tijd_rijen = [("Speeltijd", speeltijd)]
        wissel_tekst = "Elk wedstrijdje bestaat uit twee blokjes van 7,5 minuut. Tussen de blokjes door is een handig moment om te wisselen."
    else:
        h = l["helft"]
        blok_minuten = h / 2
        totaal, blok = 2 * h, "kwart"
        tijd_rijen = [("Speeltijd", f"2 × {h} minuten, met een time-out halverwege elke helft"),
                      ("Time-out en rust", f"Time-out maximaal 2 minuten, rust maximaal {v['rust']} minuten"),
                      ("Wisselen", "Onbeperkt, een gewisselde speler mag terug")]
        wissel_tekst = f"De time-outs en de rust verdelen de wedstrijd in vier kwarten van {getal(blok_minuten)} minuten. Dat zijn de handigste wisselmomenten."
    kort = [("Leeftijd", f"Onder {l['o']}: in seizoen 2026/'27 geboren in {l['geboren']}"),
            ("Spelvorm", v["naam"] + (", met keeper" if v["keeper"] == "Ja" else ", zonder keeper")),
            ("Veld", v["veld"]), ("Doelen", v["doel"]), ("Bal", v["bal"])] + tijd_rijen + [
            ("Leiding", v["leiding"]), ("Buitenspel", "Nee"), ("Strafschop", v["strafschop"]),
            ("Dispensatie", v["dispensatie"]), ("Standen", v["standen"])]
    faq = leeftijd_faq(l, v)
    opstellingen = "".join(f"<li><strong>{naam}:</strong> {uitleg_o}</li>" for naam, uitleg_o in OPSTELLINGEN[plekken])
    keeper_zin = "" if plekken == 4 else ", de keeper meegerekend"
    page(f"/jo{l['o']}/", l["titel"], l["beschrijving"], f"""
<section class="prose">
  {kruimelpad(jo)}
  <h1>{jo}: spelregels, speeltijd en opstelling</h1>
  <p class="lead">{l['inleiding']}</p>
  {kort_antwoord(l, v)}

  <h2>{jo} in het kort</h2>
  {in_het_kort(kort, f"{jo} (O{l['o']}) in het kort, seizoen 2026/'27")}

  <h2>Spelregels bij {jo}</h2>
  {regellijst(v['regels'])}
  <p>Dit is een samenvatting. De volledige regels staan in de infographic {v['naam']} op knvb.nl. Het overzicht van alle leeftijden vind je bij de <a href="/knvb-wedstrijdvormen/">KNVB-wedstrijdvormen</a>.</p>

  <h2>Hoeveel speeltijd krijgt elk kind?</h2>
  <p>Bij {v['naam']} en {totaal} minuten speeltijd zijn er {plekken * totaal} speelminuten te verdelen{keeper_zin}. Hoeveel elk kind speelt, hangt af van het aantal kinderen dat er is:</p>
  {speeltijd_per_kind(plekken, totaal, AANTALLEN[plekken], blok)}
  <p>Lukt het in één wedstrijd niet precies, laat wie deze keer minder speelde dan de volgende keer beginnen. Meer daarover lees je bij <a href="/speeltijd-eerlijk-verdelen/">speeltijd eerlijk verdelen</a>.</p>

  <h2>Wisselschema voor {jo}</h2>
  <p>{wissel_tekst} {uitleg}</p>
  {wisselschema_tabel(onderschrift, blok_minuten, schema, "Blok" if plekken == 4 else "Kwart")}
  <p>Meer voorbeelden staan bij <a href="/wisselschema-maken/">wisselschema maken</a>.</p>

  <h2>Opstelling bij {jo}</h2>
  <p>Twee opstellingen die goed werken bij {v['naam']}:</p>
  <ul>{opstellingen}</ul>
  <p>Laat kinderen bij de pupillen vooral veel aan de bal komen en verschillende plekken leren kennen. In de app kies je de opstelling die bij je team past.{' Alle vijf opstellingen met een tekening staan bij <a href="/opstelling-6-tegen-6/">opstelling 6 tegen 6</a>.' if plekken == 6 else ''}</p>
  {l['extra']}

  <h2>Wat doen trainers en ouders?</h2>
  <p>De KNVB vraagt de trainer om positief te coachen vanaf de zijlijn. Ouders moedigen positief aan, achter de omheining of langs de zijlijn. Houd rond het veld 2 meter vrij, ook voor de wisselspelers.</p>
  {leeftijd_navigatie(l['o'])}
</section>

{faq_html(faq)}
{cta(f"Laat de app je {jo}-wedstrijd regelen", f"Opstelling kent de regels van {jo}, maakt de opstelling en het wisselschema, en houdt de speeltijd bij over het hele seizoen. {GRATIS_ZIN}.")}

{gidsen("/wisselschema-maken/", "/speeltijd-eerlijk-verdelen/", "/knvb-wedstrijdvormen/")}
""", extra_ld=faq_ld(faq), kruimel=jo)

# JO6 heeft geen competitie en de app begint bij O7; daarom een eigen, kortere pagina
o6_faq = [
    ("Speelt JO6 competitie?", "Nee. De KNVB organiseert geen competitie voor O6. De wedstrijdjes zijn bij voorkeur toernooitjes, op de eigen club of met clubs uit de buurt."),
    ("Met hoeveel spelers speelt JO6?", "De KNVB adviseert 2 tegen 2. Zo komen de kinderen veel aan de bal en scoren ze veel. 4 tegen 4 kan ook."),
    ("Welk geboortejaar speelt in JO6?", "In seizoen 2026/'27 spelen kinderen die in 2021 geboren zijn in O6. Ze zijn 4 of 5 jaar."),
    ("Wat is het verschil tussen JO6 en O6?", "Er is geen verschil. Sinds seizoen 2026/'27 heet JO6 bij de KNVB officieel O6 (Onder 6)."),
]
page("/jo6/",
     f"JO6 voetbal {SEIZOEN}: 2 tegen 2, toernooitjes en spelregels",
     "Alles over JO6 (O6), de jongste voetballers van 4 en 5 jaar: waarom de KNVB 2 tegen 2 adviseert, hoe de toernooitjes werken en wat er daarna komt bij JO7.",
     f"""
<section class="prose">
  {kruimelpad("JO6")}
  <h1>JO6: de eerste wedstrijdjes</h1>
  <p class="lead">Bij JO6, sinds dit seizoen officieel O6 (Onder 6), maken kinderen van 4 en 5 jaar voor het eerst kennis met voetbal. Jongens en meiden spelen vaak samen. Plezier staat voorop, en voetbal leren ze spelenderwijs.</p>
  <p class="kort-antwoord"><strong>In het kort:</strong> JO6 speelt geen competitie. De KNVB adviseert 2 tegen 2 in toernooitjes, op de eigen club of met clubs uit de buurt. 4 tegen 4 mag ook, met dezelfde regels als bij JO7.</p>

  <h2>2 tegen 2</h2>
  <p>De KNVB adviseert om bij O6 2 tegen 2 te spelen. Zo komt elk kind veel aan de bal, scoort het veel en blijft het betrokken bij het spel. 4 tegen 4 mag ook. De spelregels van 2 tegen 2 zijn dezelfde als die van 4 tegen 4 bij <a href="/jo7/">JO7</a>.</p>

  <h2>Toernooitjes in plaats van competitie</h2>
  <p>De KNVB organiseert geen competitie voor O6. De wedstrijdjes worden bij voorkeur als toernooitje gespeeld, op de eigen club of samen met clubs uit de buurt. Het liefst wisselen de kinderen bij elke wedstrijd van team, zodat er steeds andere teams ontstaan.</p>

  <h2>Na JO6</h2>
  <p>Bij O7 spelen kinderen 4 tegen 4 zonder keeper, met wekelijkse wedstrijdjes in toernooivorm. Daar begint ook Opstelling: de app maakt dan de opstelling en verdeelt de speeltijd eerlijk.</p>
  {leeftijd_navigatie(6)}
</section>

{faq_html(o6_faq)}
{cta("Volgend seizoen naar JO7?", f"Opstelling werkt vanaf O7: de app maakt de opstelling en verdeelt de speeltijd eerlijk. {GRATIS_ZIN}.")}

{gidsen("/knvb-wedstrijdvormen/", "/speeltijd-eerlijk-verdelen/", "/wisselschema-maken/")}
""", extra_ld=faq_ld(o6_faq), kruimel="JO6")

# ------------------------------------------------ opstelling 6 tegen 6
# Zoekvraag "opstelling 6 tegen 6": bovenaan staan nu vooral PDF'jes en losse oefeningen.
# De formaties zijn dezelfde als die je in de app kunt kiezen (FORMATIONS[6] in js/rules.js).
import veldtekening

FORMATIES_6 = [
    {"app": "2-1-2", "naam": "1-2-1-2", "bijnaam": "de ruit",
     "wat": "Twee verdedigers, één middenvelder en twee aanvallers. De spelers staan als een ruit rond de middenvelder, zodat er overal driehoekjes zijn om de bal rond te spelen.",
     "sterk": "Evenwichtig: twee spelers achter, twee voor, en de middenvelder verbindt ze. Iedereen heeft een medespeler dichtbij om naar te passen.",
     "let_op": "De middenvelder heeft het druk, met verdedigen én aanvallen. Wissel die plek vaak, zodat het niet steeds hetzelfde kind is.",
     "past": "Een goede standaard voor elk team. Met deze opstelling begint ook de app."},
    {"app": "2-2-1", "naam": "1-2-2-1", "bijnaam": "met één spits",
     "wat": "Twee verdedigers, twee middenvelders en één spits.",
     "sterk": "Veel spelers in het midden, dus de tegenstander komt er minder makkelijk door. De twee middenvelders kunnen de zijkanten opzoeken.",
     "let_op": "De spits staat vaak alleen. De middenvelders moeten meekomen om kansen te maken.",
     "past": "Tegen een sterkere tegenstander, of als je team nog moeite heeft met verdedigen."},
    {"app": "1-2-2", "naam": "1-1-2-2", "bijnaam": "aanvallend",
     "wat": "Eén verdediger, twee middenvelders en twee aanvallers.",
     "sterk": "Veel spelers voorin, dus veel kansen om te scoren.",
     "let_op": "Achterin staan alleen de verdediger en de keeper. Bij balverlies moeten de middenvelders snel terug.",
     "past": "Tegen een zwakkere tegenstander, of als je juist het aanvallen wilt oefenen."},
    {"app": "1-3-1", "naam": "1-1-3-1", "bijnaam": "met een vol middenveld",
     "wat": "Eén verdediger, drie middenvelders en één spits.",
     "sterk": "Er staat iemand links, rechts en in het midden van het veld. Zo leren kinderen de hele breedte van het veld te gebruiken.",
     "let_op": "De middenvelders aan de zijkant moeten veel lopen, want ze helpen zowel voor als achter.",
     "past": "Teams die al wat samenspelen en de breedte willen leren gebruiken."},
    {"app": "3-1-1", "naam": "1-3-1-1", "bijnaam": "verdedigend",
     "wat": "Drie verdedigers, één middenvelder en één spits.",
     "sterk": "Stevig achterin, met een verdediger links, rechts en in het midden.",
     "let_op": "Met weinig spelers voorin is scoren lastig. Laat de verdedigers ook eens meegaan naar voren.",
     "past": "Tegen een veel sterkere tegenstander, als het even tegenzit."},
]


def formatie_blok(f, nummer):
    """Tekening plus uitleg van één formatie. De tekening wordt een losse afbeelding, zodat Google Afbeeldingen hem vindt."""
    bestand = f"opstelling-6-tegen-6-{f['naam']}.svg"
    svg = veldtekening.veld_svg(f["app"], f"Opstelling 6 tegen 6 in {f['naam']}, {f['bijnaam']}")
    (OUT / "img" / bestand).write_text(svg, encoding="utf-8")
    versie = hashlib.sha256(svg.encode()).hexdigest()[:10]
    return f"""<div class="formatie" id="f{nummer}">
    <figure><img src="/img/{bestand}?v={versie}" width="300" height="425" loading="lazy"
      alt="Opstelling 6 tegen 6 in {f['naam']} ({f['bijnaam']}): {f['wat'][0].lower()}{f['wat'][1:-1]}, met de keeper in het doel"></figure>
    <div>
      <h3>{nummer}. {f['naam']}, {f['bijnaam']}</h3>
      <p>{f['wat']}</p>
      <ul>
        <li><strong>Sterk:</strong> {f['sterk']}</li>
        <li><strong>Let op:</strong> {f['let_op']}</li>
        <li><strong>Past bij:</strong> {f['past']}</li>
      </ul>
    </div>
  </div>"""


op6_faq = [
    ("Wat is de beste opstelling bij 6 tegen 6?", "Een goede standaard is 1-2-1-2, de ruit: een keeper, twee verdedigers, één middenvelder en twee aanvallers. Die is evenwichtig en geeft elk kind een medespeler dichtbij. Tegen een sterkere tegenstander kun je kiezen voor 1-2-2-1, met één spits."),
    ("Wat betekenen de cijfers, zoals 1-2-1-2?", "Je telt van achter naar voren: eerst de keeper, dan de verdedigers, de middenvelders en de aanvallers. 1-2-1-2 is dus een keeper, twee verdedigers, één middenvelder en twee aanvallers. Samen zijn dat de zes spelers op het veld."),
    ("Moet je bij JO8 al een vaste opstelling hebben?", "Dat hoeft niet. Bij de jongste kinderen is het genoeg dat ze weten of ze voor of achter staan. Een vaste opstelling helpt vooral om het veld goed te verdelen, zodat niet iedereen achter de bal aan rent."),
    ("Moet een kind steeds op dezelfde plek spelen?", "Liever niet. Kinderen worden betere voetballers als ze verschillende plekken leren kennen. Laat ze per wedstrijd of per kwart van plek wisselen, en laat iedereen eens keepen."),
    ("Kan ik de opstelling in de app kiezen?", "Ja. In Opstelling kies je bij 6 tegen 6 uit deze vijf opstellingen. De app zet de kinderen op hun plek en maakt er een wisselschema bij, met eerlijke speeltijd voor iedereen."),
]
afbeeldingen_6 = "\n  ".join(formatie_blok(f, i + 1) for i, f in enumerate(FORMATIES_6))
page("/opstelling-6-tegen-6/",
     "Opstelling 6 tegen 6: 5 formaties met posities en tips",
     "Opstelling 6 tegen 6 voor JO8, JO9 en JO10: vijf formaties met een tekening, wat elke positie doet, de voor- en nadelen, en tips voor het kiezen.",
     f"""
<section class="prose">
  {kruimelpad("Opstelling 6 tegen 6")}
  <h1>Opstelling 6 tegen 6</h1>
  <p class="lead">Bij JO8, JO9 en JO10 speel je 6 tegen 6: een keeper en vijf veldspelers. Hier vind je vijf opstellingen met een tekening, wat elke positie doet, en wanneer je welke kiest.</p>
  <p class="kort-antwoord"><strong>In het kort:</strong> een goede standaard bij 6 tegen 6 is 1-2-1-2, de ruit: een keeper, twee verdedigers, één middenvelder en twee aanvallers. Tegen een sterkere tegenstander kies je 1-2-2-1, met één spits en meer spelers in het midden.</p>

  <h2>Zo lees je een opstelling</h2>
  <p>Je telt van achter naar voren. Het eerste cijfer is de keeper, daarna komen de verdedigers, de middenvelders en de aanvallers. 1-2-1-2 betekent dus: een keeper, twee verdedigers, één middenvelder en twee aanvallers. Bij 6 tegen 6 tellen de cijfers samen altijd op tot zes.</p>

  <h2>Vijf opstellingen voor 6 tegen 6</h2>
  {afbeeldingen_6}

  <h2>Wat doet elke positie?</h2>
  <ul>
    <li><strong>Keeper:</strong> houdt de bal uit het doel en begint de aanval. Bij 6 tegen 6 mag de keeper de bal in de handen hebben tot 7 meter van de achterlijn, de stippellijn in de tekeningen.</li>
    <li><strong>Verdedigers:</strong> houden de aanvallers van de tegenstander tegen en spelen de bal naar voren. Bij balbezit mogen ze best mee naar voren.</li>
    <li><strong>Middenvelders:</strong> verbinden de verdediging met de aanval. Ze helpen achterin en zoeken voorin de aanvallers op.</li>
    <li><strong>Aanvallers:</strong> proberen te scoren en zetten de tegenstander onder druk als die de bal heeft.</li>
  </ul>

  <h2>Tips voor het kiezen</h2>
  <ul>
    <li><strong>Begin eenvoudig.</strong> Speel eerst een tijd met 1-2-1-2, zodat de kinderen hun plek leren kennen. Wissel pas van opstelling als het team dat aankan.</li>
    <li><strong>Laat kinderen van plek wisselen.</strong> Wie altijd verdedigt, leert niet aanvallen. Wissel bijvoorbeeld per kwart van positie.</li>
    <li><strong>Laat de keepers rouleren.</strong> Bijvoorbeeld één keeper per helft. Een keeper speelt in de andere helft gewoon in het veld.</li>
    <li><strong>Denk ook aan de wissels.</strong> Een opstelling en een wisselschema horen bij elkaar. Voorbeelden staan bij <a href="/wisselschema-maken/">wisselschema maken</a>.</li>
  </ul>
  <div class="duo">
    <figure>{telefoon("site-opstelling.webp", "Opstelling 6 tegen 6 in 1-2-1-2 in de Opstelling app: keeper Daan, twee verdedigers, een middenvelder en twee aanvallers, met de wissels eronder")}<figcaption>De opstelling per kwart in de app</figcaption></figure>
  </div>
  <p>Alles over de regels van 6 tegen 6 per leeftijd: <a href="/jo8/">JO8</a>, <a href="/jo9/">JO9</a> en <a href="/jo10/">JO10</a>.</p>
</section>

{faq_html(op6_faq)}
{cta("Laat de app de opstelling maken", f"Kies de opstelling, vink aan wie er is, en Opstelling zet iedereen op zijn plek met een eerlijk wisselschema erbij. {GRATIS_ZIN}.")}

{gidsen("/wisselschema-maken/", "/speeltijd-eerlijk-verdelen/", "/knvb-wedstrijdvormen/")}
""", extra_ld=faq_ld(op6_faq), kruimel="Opstelling 6 tegen 6")

# ------------------------------------------------ tips en tops per speler
VAARDIGHEDEN_BAL = ["Passen over de grond", "Passen door de lucht", "Schieten op doel", "Aannemen in stilstand",
                    "Aannemen in beweging", "Dribbelen", "Drijven", "Passeren", "Positie kiezen"]
VAARDIGHEDEN_ZONDER = ["Druk zetten lopend", "Druk zetten rennend", "Mandekken", "Sliding maken", "Duelleren",
                       "Blokken", "Knijpen", "Rugdekking geven", "Positie kiezen"]
tt_faq = [
    ("Zien ouders de tips en tops?", "Nee. Alleen trainers van het team zien ze. Ze staan niet in het wedstrijdverslag dat je met ouders deelt."),
    ("Kan ik een eigen tip toevoegen?", "Ja. Naast de vaste lijst met vaardigheden kun je altijd een eigen aantekening typen, zoals meer praten in het veld."),
    ("Kunnen medetrainers ook tips en tops geven?", "Ja. Iedere trainer van het team kan ze toevoegen en ziet dezelfde lijst."),
    ("Hoe zie ik of een speler vooruitgaat?", "Een tip die gelukt is, zet je met één tik om naar een top; hij blijft zichtbaar onder Gelukt. In het teamoverzicht kies je tussen de laatste zes weken en het hele seizoen."),
    ("Wat kost het?", f"Tips en tops zitten gewoon in Opstelling. {GRATIS_ZIN}, daarna kost het {PRIJS} euro per team per seizoen."),
]
lijst = lambda items: "".join(f"<li>{v}</li>" for v in items)
page(TIPS,
     "Tips en tops per speler: voortgang volgen in je jeugdteam",
     "Leg per speler tips en tops vast, zie wat al gelukt is en waar je team op moet trainen. Een eenvoudig spelersvolgsysteem zonder cijfers.",
     f"""
<section class="prose">
  {kruimelpad("Tips en tops")}
  <h1>Tips en tops per speler</h1>
  <p class="lead">Wat gaat goed, waar kan een kind nog aan werken en wat is inmiddels gelukt? Met Opstelling houd je dat per speler bij, in een paar tikken na de wedstrijd of de training. Zo zie je over het seizoen echt vooruitgang.</p>

  <div class="duo">
    <figure>{telefoon("site-speler-tips-tops.webp", "Tips en tops bij een speler: tops, tips en wat al gelukt is", "eager")}<figcaption>Tips en tops bij een speler</figcaption></figure>
    <figure>{telefoon("site-team-tips-tops.webp", "Het teamoverzicht Waar trainen we op? met de vaardigheden die het vaakst een tip krijgen")}<figcaption>Waar trainen we op?</figcaption></figure>
  </div>

  <h2>Een spelersvolgsysteem zonder cijfers</h2>
  <p>Een rapportcijfer zegt een kind van negen weinig. Een concrete tip wel: neem de bal aan in beweging, of geef rugdekking. En een top laat zien wat er al goed gaat. Daarom werkt Opstelling niet met scores, maar met tips en tops die je aan een vaardigheid koppelt. Dat is snel ingevuld en je ziet meteen of een tip na een paar weken een top is geworden.</p>

  <h2>Zo werkt het</h2>
  <ul>
    <li><strong>Kies een vaardigheid</strong> uit de lijst (aan de bal of zonder bal), of typ een eigen aantekening.</li>
    <li><strong>Geef je dezelfde tip nog eens,</strong> dan telt hij op. Zo zie je wat vaker terugkomt.</li>
    <li><strong>Is een tip gelukt?</strong> Met één tik wordt hij een top, en hij blijft zichtbaar onder Gelukt.</li>
    <li><strong>Oudere aantekeningen worden lichter</strong> na zes weken, zodat je ziet wat nu speelt.</li>
    <li><strong>Tips voor het hele team</strong> leg je vast na een wedstrijd, in het scherm na afloop.</li>
  </ul>

  <h2>Waar moet het team op trainen?</h2>
  <p>Bovenaan de spelerslijst staat <em>Waar trainen we op?</em>: de tips die het vaakst terugkomen, bij spelers en na wedstrijden, over de laatste zes weken. In het teamoverzicht zie je per vaardigheid hoeveel spelers er een tip of top voor hebben, en wie nog geen aantekening heeft. Zo vergeet je niemand, en weet je wat je de volgende training oefent.</p>

  <h2>De vaardigheden in de app</h2>
  <div class="kolommen">
    <div><h3>Aan de bal</h3><ul>{lijst(VAARDIGHEDEN_BAL)}</ul></div>
    <div><h3>Zonder bal</h3><ul>{lijst(VAARDIGHEDEN_ZONDER)}</ul></div>
  </div>
  <p>Past iets niet in de lijst, zoals meer praten met je medespelers, dan typ je het als eigen tip.</p>

  <h2>Alleen zichtbaar voor trainers</h2>
  <p>Tips en tops zijn alleen zichtbaar voor de trainers van het team. Ze staan niet in het wedstrijdverslag dat je met ouders deelt. Wil je het met een kind of ouder bespreken, dan heb je alles bij de hand.</p>
</section>

{faq_html(tt_faq)}
{cta("Zie waar je team aan werkt", f"Tips en tops zitten gewoon in Opstelling. {GRATIS_ZIN}.")}

{gidsen("/speeltijd-eerlijk-verdelen/", AGENDA, "/knvb-wedstrijdvormen/")}
""", extra_ld=faq_ld(tt_faq), kruimel="Tips en tops")

# ------------------------------------------------ voetbal.nl-kalender koppelen
ag_faq = [
    ("Hoe zet ik de wedstrijden van Voetbal.nl in mijn agenda?", "Koop in de Voetbal.nl-app de teamkalender. Je krijgt een mail met een link. Die voeg je als agenda-abonnement toe in de agenda van je telefoon, of je plakt hem in Opstelling. Daarna komen alle wedstrijden en wijzigingen vanzelf in je agenda."),
    ("Wat kost de Voetbal.nl-teamkalender?", "Voetbal.nl vraagt € 1,99 voor de teamkalender. Koppelen in Opstelling kost niets extra."),
    ("Werkt het ook zonder de teamkalender?", "Ja. Dan voeg je de wedstrijden zelf toe en kies je thuis of uit. Alles werkt verder hetzelfde."),
    ("Wat gebeurt er als de bond een wedstrijd verplaatst?", "De app haalt de wijziging op en past datum, aftrap of locatie aan. Wat je al had klaargezet, zoals aanwezigen en opstelling, blijft staan."),
    ("Kan ik bijhouden wie de shirts wast en wie fruit meeneemt?", "Ja. Bij het plaatje voor de ouders kies je wie er deze week wast en wie fruit meeneemt. De app laat zien wie het de vorige keer deed, zodat je makkelijk rouleert."),
    ("Hoe bepaalt de app de verzameltijd?", "Je stelt één keer in hoeveel eerder iedereen er moet zijn, apart voor thuis en uit. De app rekent het daarna per wedstrijd uit vanaf de aftrap."),
    ("Kunnen medetrainers de agenda ook zien?", "Ja. De wedstrijden horen bij het team, dus iedere trainer ziet dezelfde agenda. Eén keer koppelen is genoeg."),
]
page(AGENDA,
     "Voetbal.nl agenda koppelen: hele seizoen in één keer klaar",
     "Zo koppel je de Voetbal.nl-agenda, ook wel de Voetbal.nl-kalender, in 3 stappen. Alle wedstrijden van je team staan meteen klaar, in Opstelling of je telefoon.",
     f"""
<section class="prose">
  {kruimelpad("Wedstrijdagenda")}
  <h1>Je Voetbal.nl-agenda koppelen</h1>
  <p class="lead">Zet alle wedstrijden van het seizoen in één keer in je agenda, met aftrap, tegenstander, thuis of uit en de locatie. Dat kan in de agenda van je telefoon en in Opstelling. In Opstelling maak je daarna elke week eenvoudig een plaatje voor de ouders: wie er meegaat, hoe laat ze er moeten zijn, wie de shirts wast en wie fruit meeneemt.</p>

  <h2>In drie stappen gekoppeld</h2>
  <ol class="stappen">
    <li><b>Koop de teamkalender in de Voetbal.nl-app</b><span>Zet je team eerst bij je favorieten, want de kalender neemt alleen favoriete teams mee. Ga dan naar je team, en naar Programma › Kalender. De teamkalender kost € 1,99 bij Voetbal.nl. Je krijgt een mail met een link.</span></li>
    <li><b>Kopieer de link uit de mail</b><span>Het is een adres dat met webcal:// of https:// begint.</span></li>
    <li><b>Plak hem in Opstelling bij Agenda koppelen</b><span>Op het tabblad Wedstrijd of Team. Alle wedstrijden van het seizoen staan er meteen in.</span></li>
  </ol>

  <div class="duo">
    <figure>{telefoon("site-agenda-wedstrijden.webp", "De komende wedstrijden uit de Voetbal.nl-agenda in de app, met thuis of uit, aftrap en sportpark")}<figcaption>De wedstrijden uit de agenda</figcaption></figure>
  </div>

  <h2>Wat er dan klaarstaat</h2>
  <p>Per wedstrijd de datum en aftrap, de tegenstander, of je thuis of uit speelt en waar. Je opent de wedstrijd, vinkt aan wie er is en maakt de opstelling. Zelf een wedstrijd toevoegen, zoals een oefenwedstrijd of toernooi, kan altijd.</p>

  <h2>Verplaatst of afgelast?</h2>
  <ul>
    <li><strong>De app werkt de agenda vanzelf bij</strong> als je het tabblad Wedstrijd opent, of met Nu bijwerken.</li>
    <li><strong>Aanwezigen en opstelling blijven staan,</strong> ook als de aftrap of het veld verandert.</li>
    <li><strong>Verdwijnt een wedstrijd uit de agenda,</strong> dan krijgt hij een label en kies je zelf: afgelasten of verwijderen.</li>
    <li><strong>Had je hem al zelf aangemaakt?</strong> Dan vraagt de app of het dezelfde wedstrijd is en voegt ze samen.</li>
  </ul>

  <h2>Voetbal.nl-wedstrijden in de agenda van je telefoon</h2>
  <p>Met dezelfde link uit de mail zet je de wedstrijden ook in je eigen agenda. Je voegt hem toe als agenda-abonnement, zodat wijzigingen vanzelf meekomen.</p>
  <ul>
    <li><strong>iPhone:</strong> open Instellingen › Agenda › Accounts › Voeg account toe › Andere › Voeg agenda-abonnement toe, en plak de link.</li>
    <li><strong>Google Agenda (Android):</strong> open Google Agenda op een computer, klik bij Andere agenda's op het plusje, kies Via URL en plak de link. Daarna staat hij ook op je telefoon.</li>
    <li><strong>Outlook:</strong> kies Agenda toevoegen › Abonneren via internet en plak de link.</li>
  </ul>
  <p>De menunamen verschillen soms per versie. Een agenda-abonnement wordt niet direct bijgewerkt: het kan een paar uur duren voordat een verplaatste wedstrijd in je agenda staat.</p>

  <p class="opm">Opstelling is niet verbonden aan Voetbal.nl of de KNVB. De teamkalender koop je in de Voetbal.nl-app; de prijs bepaalt Voetbal.nl.</p>
</section>

<section class="block band ouderblok" id="ouders">
  <div class="wrap split">
    <div>
      <span class="eyebrow"><b></b>Delen met ouders</span>
      <h2>Verzameltijd, wassen en fruit in één plaatje</h2>
      <p>Geen appje meer typen met namen, tijden en een adres. Onder <em>Wie is er?</em> maak je eenvoudig een plaatje voor de groepsapp, met alles wat ouders voor zaterdag moeten weten.</p>
      <div class="ouderpunten">
        <div><h3>Wie gaat er mee</h3><p>Wie er is en wie is afgemeld, rechtstreeks uit je aanwezigheid.</p></div>
        <div><h3>Hoe laat verzamelen</h3><p>De app rekent het uit de aftrap, met een eigen tijd voor thuis en uit.</p></div>
        <div><h3>Waar er gespeeld wordt</h3><p>Het sportpark en adres komen mee uit de Voetbal.nl-agenda.</p></div>
        <div><h3>Wie wast en wie neemt fruit mee</h3><p>Kies met een tik. De app laat zien wie het de vorige keer deed, zodat het eerlijk rondgaat.</p></div>
      </div>
    </div>
    <div class="report">{plaatje()}</div>
  </div>
</section>

{faq_html(ag_faq)}
{cta("Zet je seizoen in één keer klaar", f"Koppel je Voetbal.nl-kalender, deel de verzameltijd met de ouders en maak zaterdag de eerste opstelling. {GRATIS_ZIN}.")}

{gidsen("/wisselschema-maken/", TIPS, "/prijzen/")}
""", extra_ld=faq_ld(ag_faq), kruimel="Wedstrijdagenda")

# ------------------------------------------------------------- prijzen
pr_faq = [
    ("Betaal ik per trainer of per team?", f"Per team. Een team kost {PRIJS} euro per seizoen, één keer vooraf betaald. Alle trainers die je aan dat team toevoegt, gebruiken de app gratis."),
    ("Wanneer betaal ik?", f"Bij de opstelling voor je {BETAALD_VANAF} wedstrijd vraagt de app je om een seizoen te regelen: één keer {PRIJS} euro per team, tot en met {SEIZOEN_TOT}. Kies je voor verder, dan krijg je de betaallink per mail en kun je die wedstrijd nog gewoon spelen."),
    ("Hoe lang loopt een seizoen?", f"Tot en met {SEIZOEN_TOT}. Je betaalt één keer en kunt daarna tot het eind van het seizoen onbeperkt verder, met alle trainers van het team."),
    ("Wat zit er in de gratis proef?", f"{GRATIS_WAT.capitalize()} met je eerste team, met alle functies: opstellingen, het wedstrijdscherm, verslagen en de speeltijd over het seizoen."),
    ("Zit ik ergens aan vast?", "Nee. Je betaalt één keer vooraf voor het hele seizoen. Daarna komen er geen maandelijkse of tussentijdse kosten bij."),
    ("Wat gebeurt er met mijn gegevens als ik stop?", "Je spelers, wedstrijden en verslagen blijven zichtbaar. Je kunt alleen geen nieuwe wedstrijden meer plannen tot je weer betaalt."),
    ("Kan ik meerdere teams aanmaken?", f"Ja, maar alleen je eerste eigen team krijgt een gratis wedstrijd. Voor elk volgend team regel je meteen een seizoen (€ {PRIJS} per team). Je kunt het team wel al inrichten. Wil je meteen spelen, dan vraag je een betaallink aan en kun je al één wedstrijd spelen terwijl de betaling loopt."),
]
page("/prijzen/",
     f"Prijzen: {PRIJS} euro per team per seizoen, eerst gratis",
     f"Opstelling kost {PRIJS} euro per team per seizoen, één keer vooraf betaald. {GRATIS_ZIN}. Medetrainers gebruiken de app kosteloos.",
     f"""
<section class="prose">
  <h1>Wat Opstelling kost</h1>
  <p class="lead">Eén bedrag per team per seizoen, en geen verrassingen. Je begint gratis en betaalt pas als je team het echt gebruikt: dan één keer {PRIJS} euro voor het hele seizoen.</p>
</section>

<section class="prijzen">
  {prijskaarten()}
</section>

<section class="prose">
  <h2>Waarom niet gratis?</h2>
  <p>Opstelling draait op een server die geld kost. Een klein bedrag per team houdt de app onafhankelijk: geen advertenties, geen sponsors en geen doorverkoop van gegevens van kinderen.</p>
  <h2>Voor de hele club?</h2>
  <p>Wil je met meerdere teams tegelijk aan de slag, of als club afspraken maken? <a href="/contact/">Laat het weten</a>, dan kijken we naar een clubtarief.</p>
</section>

{faq_html(pr_faq)}
{cta("Begin met je eigen team", f"{GRATIS_ZIN}, zonder betaalgegevens.")}
""", extra_ld=[app_ld()] + faq_ld(pr_faq))

# ------------------------------------------------------------- contact
# Het formulier wordt verwerkt door Netlify Forms (werkt zonder JavaScript).
# Berichten gaan naar CONTACT_MAIL; dat stel je eenmalig in bij Netlify, zie README.
page("/contact/",
     "Contact: vraag, idee of hulp bij Opstelling",
     f"Een vraag over Opstelling, een idee of loopt er iets niet goed? Stuur een bericht via het formulier of mail naar {CONTACT_MAIL}. Je krijgt antwoord per mail.",
     f"""
<section class="prose">
  <h1>Contact met Opstelling</h1>
  <p class="lead">Een vraag, een idee of loopt er iets niet goed? Laat het weten. Je krijgt antwoord op het e-mailadres dat je invult.</p>
</section>

<section class="contact">
  <form class="formulier" name="contact" method="POST" action="/bedankt/" data-netlify="true" netlify-honeypot="bedrijf">
    <input type="hidden" name="form-name" value="contact">
    <p class="verstopt" aria-hidden="true"><label>Niet invullen <input name="bedrijf" tabindex="-1" autocomplete="off"></label></p>
    <div class="rij">
      <label class="veld" for="c-naam">Je naam<input id="c-naam" type="text" name="naam" required maxlength="80" autocomplete="name"></label>
      <label class="veld" for="c-mail">E-mailadres<input id="c-mail" type="email" name="email" required maxlength="120" autocomplete="email" inputmode="email"></label>
    </div>
    <div class="rij">
      <label class="veld" for="c-team"><span>Club en team <small>(mag leeg)</small></span><input id="c-team" type="text" name="team" maxlength="80" placeholder="Bijvoorbeeld VV De Vaart JO9-2"></label>
      <label class="veld" for="c-over">Waarover<select id="c-over" name="onderwerp">
        <option>Een vraag</option><option>Een idee</option><option>Er werkt iets niet</option><option>Meerdere teams of een clubtarief</option><option>Iets anders</option>
      </select></label>
    </div>
    <label class="veld" for="c-bericht">Je bericht<textarea id="c-bericht" name="bericht" required rows="6" maxlength="4000"></textarea></label>
    <button class="btn btn-main" type="submit">Verstuur bericht</button>
    <p class="klein">We gebruiken je naam en e-mailadres alleen om je bericht te beantwoorden.</p>
  </form>
  <aside class="liever">
    <h2>Liever mailen?</h2>
    <p>Dat kan ook: <a href="mailto:{CONTACT_MAIL}">{CONTACT_MAIL}</a></p>
    <p>Heb je een vraag over hoe iets werkt? Kijk ook even bij de <a href="/#vragen">veelgestelde vragen</a>.</p>
  </aside>
</section>
""")

page("/bedankt/",
     "Bedankt voor je bericht · Opstelling",
     "Je bericht is verstuurd. Je krijgt zo snel mogelijk antwoord op het e-mailadres dat je hebt ingevuld. Ondertussen kun je gewoon verder met Opstelling.",
     f"""
<section class="prose">
  <h1>Bedankt voor je bericht</h1>
  <p class="lead">Je bericht is verstuurd. Je krijgt zo snel mogelijk antwoord op het e-mailadres dat je hebt ingevuld.</p>
  <div class="actions"><a class="btn btn-main" href="{AANMELDEN}">Maak gratis een account</a><a class="btn btn-ghost" href="/">Terug naar de homepagina</a></div>
</section>
""", index=False)

# ------------------------------------------------------ sitemap, robots
paths = [p for p, _, _ in PAGINA_INFO]
def prioriteit(p):
    if p == "/":
        return "1.0"
    return "0.3" if p == "/contact/" else "0.8"

# Geen datum in de sitemap: die zou bij elke bouwdag verschillen, waardoor de
# controle in de pipeline denkt dat de bestanden niet bijgewerkt zijn.
urls = "".join(
    "<url><loc>{}{}</loc><changefreq>monthly</changefreq>"
    "<priority>{}</priority></url>".format(SITE, p, prioriteit(p)) for p in paths)
(OUT / "sitemap.xml").write_text(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
    encoding="utf-8")
(OUT / f"{INDEXNOW_SLEUTEL}.txt").write_text(INDEXNOW_SLEUTEL, encoding="utf-8")
if PUBLIEK:
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: {}/sitemap.xml\n".format(SITE), encoding="utf-8")
else:
    # nog niet openbaar: alle zoekmachines weren
    (OUT / "robots.txt").write_text("# Site is nog in aanbouw\nUser-agent: *\nDisallow: /\n", encoding="utf-8")

# ------------------------------------------------------------- llms.txt
# Een korte samenvatting in platte tekst voor AI-assistenten (ChatGPT, Claude,
# Perplexity en dergelijke), volgens het voorstel op llmstxt.org. Wordt uit
# dezelfde titels en beschrijvingen gemaakt als de pagina's, dus loopt nooit achter.
llms = f"""# Opstelling

> Opstelling is een Nederlandse webapp voor trainers van jeugdvoetbalteams (O7 tot en met O12). De app maakt opstellingen en wisselschema's, verdeelt de speeltijd eerlijk over het hele seizoen, leest wedstrijden in uit de Voetbal.nl-teamkalender, houdt tips en tops per speler bij en maakt deelbare verslagen voor ouders.

Kernfeiten:

- Voor wie: jeugdtrainers in Nederland, teams van O7 tot en met O12, volgens de KNVB-wedstrijdvormen (4 tegen 4, 6 tegen 6, 8 tegen 8).
- Prijs: {GRATIS_WAT} {GRATIS_IS} gratis (voor het eerste team van een nieuwe trainer), daarna {PRIJS} euro per team per seizoen, één keer betaald. Een seizoen loopt tot en met {SEIZOEN_TOT}. Bij de opstelling voor de {BETAALD_VANAF} wedstrijd krijgt de trainer een betaallink per mail en kan die wedstrijd nog spelen. Medetrainers betalen niets.
- Werkt in de browser op elke telefoon; niets te installeren. App: {APP}
- Eerlijke speeltijd: de app verdeelt de minuten binnen een wedstrijd en geeft wie eerder minder speelde voorrang bij de volgende wedstrijd.
- Wedstrijdagenda: koppel de teamkalender uit de Voetbal.nl-app (kost 1,99 euro bij Voetbal.nl) en alle wedstrijden staan klaar, met aftrap, tegenstander, thuis of uit en locatie. Wijzigingen worden automatisch bijgewerkt.
- Delen met ouders: een plaatje met wie er meegaat, verzameltijd, locatie, wie de shirts wast en wie fruit meeneemt.
- Tips en tops: per speler vastleggen wat goed gaat en waar hij of zij aan werkt, gekoppeld aan vaardigheden aan de bal en zonder bal; alleen zichtbaar voor trainers.
- Opstelling is niet verbonden aan de KNVB of Voetbal.nl.

## Pagina's

""" + "".join(f"- [{t}]({SITE}{p}): {d}\n" for p, t, d in PAGINA_INFO) + f"""
## Contact

- E-mail: {CONTACT_MAIL}
"""
(OUT / "llms.txt").write_text(llms, encoding="utf-8")

print("Site gebouwd:", ", ".join(paths))
print("Zoekmachines:", "toegestaan" if PUBLIEK else "geweerd (PUBLIEK staat op False in build.py)")
