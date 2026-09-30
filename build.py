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
PRIJS = "6,99"          # per team, per kwartaal (per kwartaal opzegbaar)
GRATIS = "3"            # wedstrijden gratis per team

# Cloudflare Web Analytics: plak hier de token uit het Cloudflare-dashboard
# (Web Analytics > je site > "Manage site" > JS snippet, de waarde achter "token").
# Leeg laten = geen analytics. Cloudflare telt bezoeken zonder cookies.
CF_TOKEN = "622bc38b1c73451abece02918dc7e2ea"


# Versienummer van de stijl: verandert style.css, dan verandert het adres, en
# halen browsers meteen de nieuwe versie op in plaats van een oude uit hun geheugen.
import hashlib
CSS_VERSIE = hashlib.sha256((OUT / "style.css").read_bytes()).hexdigest()[:10]


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
<meta property="og:image" content="{SITE}/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
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
    sub = sub or f"De eerste {GRATIS} wedstrijden zijn gratis. Daarna {PRIJS} euro per kwartaal per team, per kwartaal opzegbaar. Geen installatie, geen wachtwoord."
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
    "/wisselschema-maken/": ("Handleiding", "Een wisselschema maken", "In vijf stappen een schema dat langs de lijn ook echt werkt."),
    "/speeltijd-eerlijk-verdelen/": ("Achtergrond", "Speeltijd eerlijk verdelen", "Waarom het ertoe doet en hoe je het bijhoudt zonder rekenwerk."),
    "/knvb-wedstrijdvormen/": ("Overzicht", "KNVB-wedstrijdvormen", "Speelduur, aantal spelers en wisselmomenten van O7 tot en met O12 in één tabel."),
    TIPS: ("Functie", "Tips en tops per speler", "Zie waar elk kind aan werkt, wat al gelukt is en waar het team op moet trainen."),
    AGENDA: ("Handleiding", "Voetbal.nl-kalender koppelen", "Alle wedstrijden van het seizoen in één keer klaar, plus het plaatje voor de ouders."),
    "/prijzen/": ("Prijzen", "Wat Opstelling kost", f"De eerste {GRATIS} wedstrijden gratis, daarna {PRIJS} euro per kwartaal per team, per kwartaal opzegbaar."),
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
        <p>De eerste {GRATIS} wedstrijden van je team. Geen betaalgegevens nodig.</p>
        <a class="btn btn-ghost" href="{AANMELDEN}">Maak een team aan</a>
      </div>
      <div class="plan featured">
        <div class="top"><h3>Per team</h3><span class="tag">Per kwartaal opzegbaar</span></div>
        <p class="amount">€ {PRIJS}<span>per kwartaal</span></p>
        <p>Onbeperkt wedstrijden plannen en speeltijd over het hele seizoen. Per kwartaal opzegbaar.</p>
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


# ---------------------------------------------------------------- home
home_faq = [
    ("Wat kost Opstelling?", f"De eerste {GRATIS} wedstrijden van een team zijn gratis, zodat je het rustig kunt uitproberen. Daarna kost het {PRIJS} euro per kwartaal voor dat team, per kwartaal opzegbaar. Medetrainers die je toevoegt betalen niets."),
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
     f"Maak in een minuut een opstelling, verdeel de speeltijd eerlijk over het seizoen en deel een verslag met de ouders. Eerste {GRATIS} wedstrijden gratis.",
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
        <li>Eerste {GRATIS} wedstrijden gratis, zonder betaalgegevens</li>
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
    <div class="fact"><strong>{GRATIS} gratis</strong><span>wedstrijden per team</span></div>
    <div class="fact"><strong>€ {PRIJS}</strong><span>per kwartaal, opzegbaar</span></div>
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
        <p>Koppel de teamkalender uit de Voetbal.nl-app en alle wedstrijden van het seizoen staan erin: datum, aftrap, tegenstander, thuis of uit en de locatie. Daarna deel je elke week met één tik een plaatje met wie er meegaat, hoe laat iedereen er moet zijn, wie de shirts wast en wie fruit meeneemt.</p>
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
      <p>Probeer het rustig uit met je eigen team. Pas als je doorgaat, betaal je een klein bedrag per team.</p>
    </div>
    {prijskaarten()}
  </div>
</section>

{gidsen("/wisselschema-maken/", "/speeltijd-eerlijk-verdelen/", "/knvb-wedstrijdvormen/", titel="Handig voor elke jeugdtrainer")}

{faq_html(home_faq, open_eerste=True)}
{cta("Probeer het zaterdag met je eigen team", f"De eerste {GRATIS} wedstrijden zijn gratis. Geen installatie, geen wachtwoord.")}
""",
     extra_ld=[{
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
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
     }] + faq_ld(home_faq))

# ------------------------------------------------- wisselschema maken
ws_faq = [
    ("Mag je bij de pupillen onbeperkt wisselen?", "Ja. Bij de pupillen mag je doorwisselen; de time-outs en de rust zijn de natuurlijke momenten."),
    ("Wat als er iemand geblesseerd raakt of te laat komt?", "Dan klopt je schema niet meer. In Opstelling geef je de wijziging door en maakt de app de rest van de wedstrijd opnieuw, met de al gespeelde minuten erin verwerkt."),
    ("Kan een medetrainer hetzelfde schema zien?", "Ja. Iedere trainer van het team ziet dezelfde wedstrijd, kan de opstelling klaarzetten en tijdens de wedstrijd live meekijken."),
    ("Kan de keeper ook in het veld spelen?", "Als je met wisselende keepers speelt wel, en de app regelt dat: wie een helft keept, krijgt in de andere helft veldtijd."),
]
page("/wisselschema-maken/",
     "Wisselschema maken voor jeugdvoetbal: zo doe je het snel",
     f"Een wisselschema dat langs de lijn werkt, zonder rekenen: Opstelling maakt het per wedstrijd en houdt de speeltijd bij. Eerste {GRATIS} wedstrijden gratis.",
     f"""
<section class="prose">
  <h1>Een wisselschema maken voor je jeugdteam</h1>
  <p class="lead">Een goed wisselschema zorgt ervoor dat elk kind ongeveer evenveel speeltijd krijgt en dat jij daar niet voor hoeft te rekenen langs de lijn. In de praktijk blijkt dat op papier toch een heel gedoe.</p>

  <h2>Wat maakt een papiertje lastig</h2>
  <ul>
    <li>Op vrijdagavond melden er twee kinderen af en klopt je indeling niet meer.</li>
    <li>Een blessure of een late aankomst gooit de rest van de wedstrijd om.</li>
    <li>Je weet aan het eind niet meer wie nu precies hoe lang speelde, dus de week erna begin je weer bij nul.</li>
    <li>Je rouleert keepers, dus het is lastig om bij te houden hoeveel speeltijd in het veld iedereen heeft.</li>
  </ul>

  <h2>Hoe de Opstelling app het doet</h2>
  <p>Je vinkt aan wie er is en kiest de keepers. De app maakt daarna het schema: wie speelt welk kwart, wie wisselt wanneer, en wie staat waar. Tijdens de wedstrijd loopt de klok mee en zie je het volgende wisselmoment met de namen erbij.</p>
  <p>Wijzigt er iets, dan past de app de rest van de wedstrijd aan met de al gespeelde minuten erin verwerkt. En de minuten van vandaag tellen automatisch mee bij de volgende wedstrijd, zodat wie nu minder speelde, dan voorrang krijgt.</p>

  <h2>Je houdt zelf de regie</h2>
  <p>Je kunt spelers altijd ruilen, zelf de wisselmomenten kiezen (bijvoorbeeld alleen in de rust), of de opstelling helemaal zelf neerzetten en de app alleen de tijd laten bijhouden.</p>
  <p>Heb je de teamkalender uit de Voetbal.nl-app, dan staan alle wedstrijden al klaar en begin je meteen bij het aanvinken. Zo <a href="{AGENDA}">koppel je je Voetbal.nl-kalender</a>.</p>
</section>

{faq_html(ws_faq)}
{cta("Laat de app je wisselschema maken", f"Aanvinken wie er is, keepers kiezen en klaar. De eerste {GRATIS} wedstrijden zijn gratis.")}

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
     f"Elk kind ongeveer evenveel speeltijd, ook als er elke week anderen zijn? Opstelling rekent en onthoudt het voor je. Eerste {GRATIS} wedstrijden gratis.",
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
{cta("Laat de speeltijd zichzelf bijhouden", f"Opstelling verdeelt de minuten en onthoudt wie achterliep. De eerste {GRATIS} wedstrijden zijn gratis.")}

{gidsen("/wisselschema-maken/", TIPS, "/prijzen/")}
""", extra_ld=faq_ld(st_faq))

# ------------------------------------------------ knvb wedstrijdvormen
rows = [
    ("O7", "4 tegen 4", "Nee", "3 × 15 minuten", "Time-out na 7,5 minuut per wedstrijdje (6 blokken)"),
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

  <h2>Wat betekent dit voor je speeltijd?</h2>
  <p>Bij 6 tegen 6 met 2 × 20 minuten zijn er 240 speelminuten te verdelen (zes plekken maal veertig minuten). Met negen kinderen komt dat neer op ongeveer 27 minuten per kind, keepen meegerekend. Zijn er twaalf kinderen, dan blijft er twintig minuten per kind over, en wordt het belangrijker om over de weken heen bij te houden wie minder speelde.</p>

  <h2>Wisselen bij de pupillen</h2>
  <p>Bij de pupillen mag je onbeperkt wisselen. De time-outs en de rust zijn de natuurlijke momenten. Wissel je alleen in de rust, dan speelt iedereen een hele of een halve wedstrijd, en zijn de verschillen groot.</p>
</section>

{faq_html(knvb_faq)}
{cta("Laat de app de regels toepassen", "Kies het niveau van je team en Opstelling gebruikt automatisch de juiste speelduur, spelers en wisselmomenten.")}

{gidsen("/wisselschema-maken/", "/speeltijd-eerlijk-verdelen/", "/prijzen/")}
""", extra_ld=faq_ld(knvb_faq))

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
    ("Wat kost het?", f"Tips en tops zitten gewoon in Opstelling. De eerste {GRATIS} wedstrijden van een team zijn gratis, daarna kost het {PRIJS} euro per kwartaal per team."),
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
{cta("Zie waar je team aan werkt", f"Tips en tops zitten gewoon in Opstelling. De eerste {GRATIS} wedstrijden zijn gratis.")}

{gidsen("/speeltijd-eerlijk-verdelen/", AGENDA, "/knvb-wedstrijdvormen/")}
""", extra_ld=faq_ld(tt_faq), kruimel="Tips en tops")

# ------------------------------------------------ voetbal.nl-kalender koppelen
ag_faq = [
    ("Wat kost de Voetbal.nl-teamkalender?", "Voetbal.nl vraagt € 1,99 voor de teamkalender. Koppelen in Opstelling kost niets extra."),
    ("Werkt het ook zonder de teamkalender?", "Ja. Dan voeg je de wedstrijden zelf toe en kies je thuis of uit. Alles werkt verder hetzelfde."),
    ("Wat gebeurt er als de bond een wedstrijd verplaatst?", "De app haalt de wijziging op en past datum, aftrap of locatie aan. Wat je al had klaargezet, zoals aanwezigen en opstelling, blijft staan."),
    ("Kan ik bijhouden wie de shirts wast en wie fruit meeneemt?", "Ja. Bij het plaatje voor de ouders kies je wie er deze week wast en wie fruit meeneemt. De app laat zien wie het de vorige keer deed, zodat je makkelijk rouleert."),
    ("Hoe bepaalt de app de verzameltijd?", "Je stelt één keer in hoeveel eerder iedereen er moet zijn, apart voor thuis en uit. De app rekent het daarna per wedstrijd uit vanaf de aftrap."),
    ("Kunnen medetrainers de agenda ook zien?", "Ja. De wedstrijden horen bij het team, dus iedere trainer ziet dezelfde agenda. Eén keer koppelen is genoeg."),
]
page(AGENDA,
     "Voetbal.nl-kalender koppelen: hele seizoen in één keer klaar",
     "Alle wedstrijden uit de Voetbal.nl-app in één keer klaar, en met één tik laat je ouders weten hoe laat ze er zijn, wie wast en wie fruit meeneemt.",
     f"""
<section class="prose">
  {kruimelpad("Wedstrijdagenda")}
  <h1>Je Voetbal.nl-kalender koppelen</h1>
  <p class="lead">Zet alle wedstrijden van het seizoen in één keer klaar in Opstelling, met aftrap, tegenstander, thuis of uit en de locatie. En laat ouders elke week met één tik weten wie er meegaat, hoe laat ze er moeten zijn, wie de shirts wast en wie fruit meeneemt.</p>

  <h2>In drie stappen gekoppeld</h2>
  <ol class="stappen">
    <li><b>Koop de teamkalender in de Voetbal.nl-app</b><span>Ga naar je team, dan Programma › Kalender. De teamkalender kost € 1,99 bij Voetbal.nl. Je krijgt een mail met een link.</span></li>
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

  <p class="opm">Opstelling is niet verbonden aan Voetbal.nl of de KNVB. De teamkalender koop je in de Voetbal.nl-app; de prijs bepaalt Voetbal.nl.</p>
</section>

<section class="block band ouderblok" id="ouders">
  <div class="wrap split">
    <div>
      <span class="eyebrow"><b></b>Delen met ouders</span>
      <h2>Verzameltijd, wassen en fruit in één plaatje</h2>
      <p>Geen appje meer typen met namen, tijden en een adres. Onder <em>Wie is er?</em> maak je met één tik een plaatje voor de groepsapp, met alles wat ouders voor zaterdag moeten weten.</p>
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
{cta("Zet je seizoen in één keer klaar", f"Koppel je Voetbal.nl-kalender, deel de verzameltijd met de ouders en maak zaterdag de eerste opstelling. De eerste {GRATIS} wedstrijden zijn gratis.")}

{gidsen("/wisselschema-maken/", TIPS, "/prijzen/")}
""", extra_ld=faq_ld(ag_faq), kruimel="Wedstrijdagenda")

# ------------------------------------------------------------- prijzen
pr_faq = [
    ("Betaal ik per trainer of per team?", f"Per team. Een team kost {PRIJS} euro per kwartaal en is per kwartaal opzegbaar. Alle trainers die je aan dat team toevoegt, gebruiken de app gratis."),
    ("Wat zit er in de gratis proef?", f"De eerste {GRATIS} wedstrijden van een team, met alle functies: opstellingen, het wedstrijdscherm, verslagen en de speeltijd over het seizoen."),
    ("Zit ik ergens aan vast?", "Nee. Je betaalt per kwartaal en het abonnement is per kwartaal opzegbaar, bijvoorbeeld tegen de winterstop of het eind van het seizoen."),
    ("Wat gebeurt er met mijn gegevens als ik stop?", "Je spelers, wedstrijden en verslagen blijven zichtbaar. Je kunt alleen geen nieuwe wedstrijden meer plannen tot je weer betaalt."),
    ("Heb ik meerdere teams? ", "Dan betaal je per team. Train je twee teams, dan zijn dat twee keer de kosten."),
]
page("/prijzen/",
     f"Prijzen: {PRIJS} euro per kwartaal per team, opzegbaar",
     f"Opstelling kost {PRIJS} euro per kwartaal per team en is per kwartaal opzegbaar. De eerste {GRATIS} wedstrijden zijn gratis. Medetrainers gebruiken de app kosteloos.",
     f"""
<section class="prose">
  <h1>Wat Opstelling kost</h1>
  <p class="lead">Eén eenvoudig tarief per team, en geen verrassingen. Je begint gratis en betaalt pas als je team het echt gebruikt.</p>
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
{cta("Begin met je eigen team", f"De eerste {GRATIS} wedstrijden zijn gratis, zonder betaalgegevens.")}
""", extra_ld=faq_ld(pr_faq))

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
- Prijs: de eerste {GRATIS} wedstrijden per team zijn gratis, daarna {PRIJS} euro per kwartaal per team, per kwartaal opzegbaar. Medetrainers betalen niets.
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
