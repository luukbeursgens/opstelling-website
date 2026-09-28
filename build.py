#!/usr/bin/env python3
"""Bouwt de statische marketingsite voor Opstelling.

Eén bestand per pagina, geen JavaScript, alles vooraf klaargezet:
titels, beschrijvingen, canonieke adressen, gestructureerde gegevens,
sitemap en robots.txt. Aanpassen? Wijzig de teksten hieronder en draai
opnieuw: python3 build.py
"""
import os, pathlib

SITE = "https://opstellingapp.nl"          # eigen domein; pas dit aan als je een ander domein neemt
APP = "https://opstellingapp.netlify.app"
AANMELDEN = APP + "/?account=nieuw"   # opent in de app meteen "Maak je account aan"
CONTACT_MAIL = "info@opstellingapp.nl"
OUT = pathlib.Path(__file__).parent

NAV = [("/", "Home"), ("/wisselschema-maken/", "Wisselschema maken"),
       ("/speeltijd-eerlijk-verdelen/", "Eerlijke speeltijd"), ("/knvb-wedstrijdvormen/", "KNVB-wedstrijdvormen"),
       ("/prijzen/", "Prijzen"), ("/contact/", "Contact")]

PUBLIEK = False         # False zolang de site nog niet openbaar mag zijn: geen zoekmachines
PRIJS = "6,99"          # per team, per kwartaal (per kwartaal opzegbaar)
GRATIS = "3"            # wedstrijden gratis per team

# Cloudflare Web Analytics: plak hier de token uit het Cloudflare-dashboard
# (Web Analytics > je site > "Manage site" > JS snippet, de waarde achter "token").
# Leeg laten = geen analytics. Cloudflare telt bezoeken zonder cookies.
CF_TOKEN = ""


# Versienummer van de stijl: verandert style.css, dan verandert het adres, en
# halen browsers meteen de nieuwe versie op in plaats van een oude uit hun geheugen.
import hashlib
CSS_VERSIE = hashlib.sha256((OUT / "style.css").read_bytes()).hexdigest()[:10]


def page(path, title, description, body, extra_ld=None, keywords_hint="", index=True):
    url = SITE + path
    # Let op: geen backslash binnen een f-string, anders werkt dit niet op oudere Python-versies
    huidig = ' aria-current="page"'
    kopmenu = "".join(
        '<a href="{}"{}>{}</a>'.format(href, huidig if href == path else '', label)
        for href, label in NAV if href != "/")
    voetmenu = "".join('<a href="{}">{}</a>'.format(href, label) for href, label in NAV)
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
    ("Werkt het ook voor 6 tegen 6 en 8 tegen 8?", "Ja. Je kiest het niveau van O7 tot en met O12, en de app volgt de KNVB-wedstrijdvormen: aantal spelers, wel of geen keeper, speelduur en wisselmomenten."),
    ("Kunnen meerdere trainers hetzelfde team beheren?", "Ja, en dat kost niets extra. Je voegt trainers toe met hun e-mailadres. Iedereen ziet dezelfde wedstrijden en kan de opstelling klaarzetten of de wedstrijd bijhouden."),
    ("Houdt de app rekening met de posities van spelers?", "Als je dat aanzet wel. Je geeft per speler aan waar hij goed uit de voeten kan, en de app stelt spelers zoveel mogelijk zo op, zonder de eerlijke speeltijd los te laten."),
]
stappen = [
    ("Klaarzetten", "Vink aan wie er is, kies de keepers en hoe je wilt wisselen: automatisch, op vaste momenten of helemaal zelf. Met een druk op de knop heb je een eerlijke opstelling.", "site-opstelling.webp", "De opstelling per kwart met de wisselspelers", "De opstelling per kwart"),
    ("Spelen", "Start de klok, noteer doelpunten en volg de wisselmomenten. Medetrainers kijken live mee en kunnen overnemen.", "site-wedstrijd.webp", "Het wedstrijdscherm met klok, stand en het volgende wisselmoment", "Tijdens de wedstrijd"),
    ("Delen", "Sluit af en deel het verslag met de ouders, met de uitslag, het verloop en wie er scoorde.", "verslag.webp", "Deelbaar wedstrijdverslag met uitslag en doelpuntenmakers", "Het verslag voor de ouders"),
    ("Bijhouden", "Zie per speler de speeltijd en doelpunten over het hele seizoen. De volgende opstelling houdt daar rekening mee.", "site-seizoen.webp", "Het seizoen in cijfers met topscorers en speeltijd", "Automatisch seizoensoverzicht"),
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
        <li>Werkt op elke telefoon, niets te installeren</li>
        <li>Medetrainers kunnen gratis toegevoegd worden</li>
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
         "description": "App voor jeugdtrainers: opstellingen maken, speeltijd eerlijk verdelen en wedstrijdverslagen delen.",
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
</section>

{faq_html(ws_faq)}
{cta("Laat de app je wisselschema maken", f"Aanvinken wie er is, keepers kiezen en klaar. De eerste {GRATIS} wedstrijden zijn gratis.")}

{gidsen("/speeltijd-eerlijk-verdelen/", "/knvb-wedstrijdvormen/", "/prijzen/")}
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
</section>

{faq_html(st_faq)}
{cta("Laat de speeltijd zichzelf bijhouden", f"Opstelling verdeelt de minuten en onthoudt wie achterliep. De eerste {GRATIS} wedstrijden zijn gratis.")}

{gidsen("/wisselschema-maken/", "/knvb-wedstrijdvormen/", "/prijzen/")}
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
paths = ["/", "/prijzen/", "/wisselschema-maken/", "/speeltijd-eerlijk-verdelen/", "/knvb-wedstrijdvormen/", "/contact/"]
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
print("Site gebouwd:", ", ".join(paths))
print("Zoekmachines:", "toegestaan" if PUBLIEK else "geweerd (PUBLIEK staat op False in build.py)")
