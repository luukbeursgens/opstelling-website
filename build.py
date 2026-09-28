#!/usr/bin/env python3
"""Bouwt de statische marketingsite voor Opstelling.

Eén bestand per pagina, geen JavaScript, alles vooraf klaargezet:
titels, beschrijvingen, canonieke adressen, gestructureerde gegevens,
sitemap en robots.txt. Aanpassen? Wijzig de teksten hieronder en draai
opnieuw: python3 build.py
"""
import os, pathlib, datetime

SITE = "https://www.jouwdomein.nl"          # eigen domein; pas dit aan als je een ander domein neemt
APP = "https://opstellingapp.netlify.app"
OUT = pathlib.Path(__file__).parent
TODAY = datetime.date.today().isoformat()

NAV = [("/", "Home"), ("/wisselschema-maken/", "Wisselschema maken"),
       ("/speeltijd-eerlijk-verdelen/", "Eerlijke speeltijd"), ("/knvb-wedstrijdvormen/", "KNVB-wedstrijdvormen"),
       ("/prijzen/", "Prijzen")]

PRIJS = "6,99"          # per team, per drie maanden
GRATIS = "3"            # wedstrijden gratis per team


def page(path, title, description, body, extra_ld=None, keywords_hint=""):
    url = SITE + path
    # Let op: geen backslash binnen een f-string, anders werkt dit niet op oudere Python-versies
    huidig = ' aria-current="page"'
    nav = "".join(
        '<a href="{}"{}>{}</a>'.format(href, huidig if href == path else '', label)
        for href, label in NAV)
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
    head = f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
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
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">Naar de inhoud</a>
<header class="site">
  <div class="bar">
    <a class="logo" href="/"><img src="/img/icon.png" alt="" width="34" height="34"> Opstelling</a>
    <nav aria-label="Hoofdmenu">{nav}</nav>
    <a class="btn small" href="{APP}">Probeer gratis</a>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site">
  <div class="bar">
    <p><strong>Opstelling</strong> · eerlijke speeltijd voor elk jeugdteam</p>
    <nav aria-label="Voettekst">{nav}<a href="/privacy/">Privacy</a></nav>
    <p class="small">Gemaakt door een jeugdtrainer, voor jeugdtrainers. Niet verbonden aan de KNVB.</p>
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
    sub = sub or f"De eerste {GRATIS} wedstrijden zijn gratis. Daarna {PRIJS} euro per drie maanden, per team. Geen installatie, geen wachtwoord."
    return f"""<section class="cta">
  <h2>{tekst}</h2>
  <p>{sub}</p>
  <p><a class="btn big" href="{APP}">Open Opstelling</a></p>
</section>"""


def faq_ld(pairs):
    return [{"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": v, "acceptedAnswer": {"@type": "Answer", "text": a}} for v, a in pairs]}]


def faq_html(pairs, titel="Veelgestelde vragen"):
    items = "".join(f"<details><summary>{v}</summary><p>{a}</p></details>" for v, a in pairs)
    return f'<section><h2>{titel}</h2>{items}</section>'


# ---------------------------------------------------------------- home
home_faq = [
    ("Wat kost Opstelling?", f"De eerste {GRATIS} wedstrijden van een team zijn gratis, zodat je het rustig kunt uitproberen. Daarna kost het {PRIJS} euro per drie maanden voor dat team. Medetrainers die je toevoegt betalen niets."),
    ("Moet ik iets installeren?", "Nee. Opstelling werkt in je browser en je kunt hem op je beginscherm zetten, zodat hij opent als een gewone app."),
    ("Werkt het ook voor 6 tegen 6 en 8 tegen 8?", "Ja. Je kiest het niveau van O7 tot en met O13, en de app volgt de KNVB-wedstrijdvormen: aantal spelers, wel of geen keeper, speelduur en wisselmomenten."),
    ("Kunnen meerdere trainers hetzelfde team beheren?", "Ja, en dat kost niets extra. Je voegt trainers toe met hun e-mailadres. Iedereen ziet dezelfde wedstrijden en kan de opstelling klaarzetten of de wedstrijd bijhouden."),
    ("Houdt de app rekening met de posities van spelers?", "Als je dat aanzet wel. Je geeft per speler aan waar hij goed uit de voeten kan, en de app stelt spelers zoveel mogelijk zo op, zonder de eerlijke speeltijd los te laten."),
]
page("/",
     "Opstelling: eerlijke speeltijd en opstellingen voor jeugdvoetbal",
     f"Maak in een minuut een opstelling, verdeel de speeltijd eerlijk over het seizoen en deel een verslag met de ouders. Eerste {GRATIS} wedstrijden gratis.",
     f"""
<section class="hero">
  <div>
    <h1>Eerlijke speeltijd voor elk kind, zonder gepuzzel</h1>
    <p class="lead">Opstelling maakt in een minuut een opstelling voor je jeugdteam, houdt bij wie hoeveel speelt en telt dat mee in de volgende wedstrijd. Tijdens de wedstrijd zie je precies wanneer je moet wisselen.</p>
    <p><a class="btn big" href="{APP}">Probeer gratis</a> <a class="btn ghost big" href="#hoe">Bekijk hoe het werkt</a></p>
    <p class="small">Eerste {GRATIS} wedstrijden gratis · daarna {PRIJS} euro per 3 maanden per team · werkt op elke telefoon</p>
  </div>
  <img src="/img/site-opstelling.png" width="390" height="780" alt="De opstelling per kwart in de app Opstelling" loading="eager" fetchpriority="high">
</section>

<section>
  <h2>Waarom trainers Opstelling gebruiken</h2>
  <div class="grid">
    <article><h3>Iedereen speelt evenveel</h3><p>De app verdeelt de speeltijd zo gelijk mogelijk en onthoudt wie vorige week minder speelde. Die krijgt de week erna voorrang, ook als er ineens meer kinderen zijn.</p></article>
    <article><h3>Je hoeft niet meer te rekenen</h3><p>Geen briefje met streepjes meer. Je vinkt aan wie er is, kiest de keepers en klaar. Ruilen kan altijd met twee tikken.</p></article>
    <article><h3>Rust langs de lijn</h3><p>Tijdens de wedstrijd loopt de klok mee en zie je wanneer er gewisseld moet worden en wie erin komt. Ook je medetrainers kunnen live meekijken.</p></article>
    <article><h3>Ouders zien wat hun kind deed</h3><p>Na afloop deel je met één tik een wedstrijdverslag met de uitslag, het verloop en de doelpuntenmakers in de groepsapp.</p></article>
  </div>
</section>

<section id="hoe">
  <h2>Zo werkt het</h2>
  <ol class="steps">
    <li><strong>Team aanmaken.</strong> Kies het niveau (O7 tot en met O13) en voeg je spelers toe. De KNVB-regels voor speelduur, aantal spelers en wisselmomenten staan er automatisch bij.</li>
    <li><strong>Wedstrijd klaarzetten.</strong> Vink aan wie er is, kies de keepers en hoe je wilt wisselen: automatisch, op vaste momenten, of helemaal zelf.</li>
    <li><strong>Spelen.</strong> Start de wedstrijd, noteer doelpunten en volg de wisselmomenten. Je medetrainers kijken live mee.</li>
    <li><strong>Delen en bijhouden.</strong> Sluit af, deel het verslag met de ouders en zie per speler de speeltijd en doelpunten over het hele seizoen.</li>
  </ol>
  <div class="shots">
    <figure><img src="/img/site-wedstrijd.png" width="390" height="780" alt="Het wedstrijdscherm met klok, stand en de opstelling" loading="lazy"><figcaption>Tijdens de wedstrijd</figcaption></figure>
    <figure><img src="/img/verslag.png" width="540" height="725" alt="Voorbeeld van een deelbaar wedstrijdverslag met uitslag en doelpuntenmakers" loading="lazy"><figcaption>Het verslag voor de ouders</figcaption></figure>
    <figure><img src="/img/site-seizoen.png" width="390" height="780" alt="Speeltijd per speler over het seizoen" loading="lazy"><figcaption>Speeltijd over het seizoen</figcaption></figure>
  </div>
</section>

<section>
  <h2>Meer lezen</h2>
  <ul class="links">
    <li><a href="/wisselschema-maken/">Een wisselschema maken voor je jeugdteam</a> — hoe je in vijf stappen een schema maakt dat langs de lijn ook echt werkt.</li>
    <li><a href="/speeltijd-eerlijk-verdelen/">Speeltijd eerlijk verdelen</a> — waarom het ertoe doet en hoe je het bijhoudt zonder rekenwerk.</li>
    <li><a href="/knvb-wedstrijdvormen/">KNVB-wedstrijdvormen per leeftijd</a> — speelduur, aantal spelers en wisselmomenten van O7 tot en met O13 in één tabel.</li>
  </ul>
</section>

<section id="prijs">
  <h2>Wat het kost</h2>
  <div class="prijs">
    <div class="kaart">
      <h3>Uitproberen</h3>
      <p class="bedrag">Gratis</p>
      <p class="small">De eerste {GRATIS} wedstrijden van je team</p>
      <ul><li>Alle functies, niets beperkt</li><li>Zoveel trainers als je wilt</li><li>Geen betaalgegevens nodig</li></ul>
    </div>
    <div class="kaart uitgelicht">
      <h3>Per team</h3>
      <p class="bedrag">{PRIJS} <span>euro per 3 maanden</span></p>
      <p class="small">Voor één team, het hele seizoen door op te zeggen</p>
      <ul><li>Onbeperkt wedstrijden plannen</li><li>Speeltijd over het hele seizoen</li><li>Medetrainers gratis</li><li>Wedstrijdverslagen delen</li></ul>
      <p><a class="btn" href="{APP}">Begin met je team</a></p>
    </div>
  </div>
  <p class="small">Meerdere teams? Je betaalt per team. Een trainer die alleen is toegevoegd aan het team van iemand anders, betaalt niets.</p>
</section>

{faq_html(home_faq)}
{cta()}
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
    ("Mag je bij de pupillen onbeperkt wisselen?", "Ja. Bij de pupillen mag je doorwisselen; de onderbrekingen tussen de kwarten en de rust zijn de natuurlijke momenten."),
    ("Wat als er iemand geblesseerd raakt of te laat komt?", "Dan klopt je schema niet meer. In Opstelling geef je de wijziging door en maakt de app de rest van de wedstrijd opnieuw, met de al gespeelde minuten erin verwerkt."),
    ("Kan een medetrainer hetzelfde schema zien?", "Ja. Iedere trainer van het team ziet dezelfde wedstrijd, kan de opstelling klaarzetten en tijdens de wedstrijd live meekijken."),
    ("Moet de keeper ook in het veld spelen?", "Als je met wisselende keepers speelt wel, en de app regelt dat: wie een helft keept, krijgt in de andere helft veldtijd."),
]
page("/wisselschema-maken/",
     "Wisselschema maken voor jeugdvoetbal: zo doe je het snel",
     f"Een wisselschema dat langs de lijn werkt, zonder rekenen: Opstelling maakt het per wedstrijd en houdt de speeltijd bij. Eerste {GRATIS} wedstrijden gratis.",
     f"""
<section class="prose">
  <h1>Een wisselschema maken voor je jeugdteam</h1>
  <p class="lead">Een wisselschema moet twee dingen doen: iedereen speelt ongeveer evenveel, en jij hoeft langs de lijn niet te rekenen. Dat tweede is precies waar het bij een schema op papier misgaat.</p>

  <h2>Waarom het op papier zelden standhoudt</h2>
  <ul>
    <li>Op vrijdagavond melden er twee kinderen af en klopt je indeling niet meer.</li>
    <li>Een blessure of een late aankomst gooit de rest van de wedstrijd om.</li>
    <li>Je weet aan het eind niet meer wie nu precies hoe lang speelde, dus de week erna begin je weer bij nul.</li>
    <li>Keepen telt mee als speeltijd, terwijl dat kind niet gevoetbald heeft.</li>
  </ul>

  <h2>Hoe Opstelling het doet</h2>
  <p>Je vinkt aan wie er is en kiest de keepers. De app maakt daarna het schema: wie speelt welk kwart, wie wisselt wanneer, en wie staat waar. Tijdens de wedstrijd loopt de klok mee en zie je het volgende wisselmoment met de namen erbij.</p>
  <p>Wijzigt er iets, dan past de app de rest van de wedstrijd aan met de al gespeelde minuten erin verwerkt. En de minuten van vandaag tellen automatisch mee bij de volgende wedstrijd, zodat wie nu minder speelde, dan voorrang krijgt.</p>

  <h2>Je houdt zelf de regie</h2>
  <p>Je kunt spelers altijd ruilen, zelf de wisselmomenten kiezen (bijvoorbeeld alleen in de rust), of de opstelling helemaal zelf neerzetten en de app alleen de tijd laten bijhouden.</p>
</section>

{{faq_html(ws_faq)}}
{{cta("Laat de app je wisselschema maken", f"Aanvinken wie er is, keepers kiezen en klaar. De eerste {GRATIS} wedstrijden zijn gratis.")}}

<section><h2>Verder lezen</h2><ul class="links">
  <li><a href="/speeltijd-eerlijk-verdelen/">Eerlijke speeltijd over het seizoen</a></li>
  <li><a href="/knvb-wedstrijdvormen/">Speelduur en wisselmomenten per leeftijdscategorie</a></li>
  <li><a href="/prijzen/">Wat Opstelling kost</a></li>
</ul></section>
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

{{faq_html(st_faq)}}
{{cta("Laat de speeltijd zichzelf bijhouden", f"Opstelling verdeelt de minuten en onthoudt wie achterliep. De eerste {GRATIS} wedstrijden zijn gratis.")}}

<section><h2>Verder lezen</h2><ul class="links">
  <li><a href="/wisselschema-maken/">Een wisselschema maken zonder rekenen</a></li>
  <li><a href="/knvb-wedstrijdvormen/">KNVB-wedstrijdvormen per leeftijd</a></li>
  <li><a href="/prijzen/">Wat Opstelling kost</a></li>
</ul></section>
""", extra_ld=faq_ld(st_faq))

# ------------------------------------------------ knvb wedstrijdvormen
rows = [
    ("O7", "4 tegen 4", "Nee", "3 × 15 minuten", "6 blokken van 7,5 minuut"),
    ("O8 en O9", "6 tegen 6", "Ja", "2 × 20 minuten", "4 kwarten van 10 minuten"),
    ("O10", "6 tegen 6", "Ja", "2 × 25 minuten", "4 kwarten van 12,5 minuut"),
    ("O11 en O12", "8 tegen 8", "Ja", "2 × 30 minuten", "4 kwarten van 15 minuten"),
    ("O13 (9 tegen 9)", "9 tegen 9", "Ja", "2 × 30 min (divisie 1 en 2: 2 × 35)", "4 kwarten"),
    ("O13 (11 tegen 11)", "11 tegen 11", "Ja", "2 × 30 min (divisie 1 en 2: 2 × 35)", "4 kwarten"),
]
tabel = "".join(f"<tr><th scope='row'>{a}</th><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>" for a, b, c, d, e in rows)
knvb_faq = [
    ("Hoe lang duurt een wedstrijd bij O8?", "Twee keer twintig minuten, gespeeld in vier kwarten van tien minuten."),
    ("Spelen pupillen met een keeper?", "Vanaf O8 wel. Bij O7 wordt 4 tegen 4 gespeeld zonder keeper."),
    ("Wanneer mag je wisselen bij de pupillen?", "Bij de pupillen mag je onbeperkt wisselen. In de praktijk doen trainers dat bij de onderbrekingen: tussen de kwarten en in de rust."),
]
page("/knvb-wedstrijdvormen/",
     "KNVB-wedstrijdvormen O7 t/m O13: speelduur, spelers en wisselen",
     "Overzicht van de KNVB-wedstrijdvormen per leeftijd: aantal spelers, wel of geen keeper, speelduur en handige wisselmomenten, van O7 tot en met O13.",
     f"""
<section class="prose">
  <h1>KNVB-wedstrijdvormen per leeftijd</h1>
  <p class="lead">Handig overzicht voor jeugdtrainers: hoeveel spelers, wel of geen keeper, hoe lang er gespeeld wordt en welke wisselmomenten daarbij passen. Bedoeld als spiekbriefje langs de lijn; de officiële regels staan op knvb.nl.</p>

  <div class="tablewrap"><table>
    <caption>Wedstrijdvormen en speelduur per leeftijdscategorie (seizoen 2026/'27)</caption>
    <thead><tr><th scope="col">Leeftijd</th><th scope="col">Vorm</th><th scope="col">Keeper</th><th scope="col">Speelduur</th><th scope="col">Handige wisselmomenten</th></tr></thead>
    <tbody>{tabel}</tbody>
  </table></div>

  <h2>Wat betekent dit voor je speeltijd?</h2>
  <p>Bij 6 tegen 6 met 2 × 20 minuten zijn er 240 speelminuten te verdelen (zes plekken maal veertig minuten). Met negen kinderen komt dat neer op ongeveer 27 minuten per kind, keepen meegerekend. Zijn er twaalf kinderen, dan blijft er twintig minuten per kind over, en wordt het belangrijker om over de weken heen bij te houden wie minder speelde.</p>

  <h2>Wisselen bij de pupillen</h2>
  <p>Bij de pupillen mag je onbeperkt wisselen. De onderbrekingen tussen de kwarten zijn de natuurlijke momenten. Wissel je alleen in de rust, dan speelt iedereen een hele of een halve wedstrijd, en zijn de verschillen groot.</p>
</section>

{faq_html(knvb_faq)}
{cta("Laat de app de regels toepassen", "Kies het niveau van je team en Opstelling gebruikt automatisch de juiste speelduur, spelers en wisselmomenten.")}

<section><h2>Verder lezen</h2><ul class="links">
  <li><a href="/wisselschema-maken/">Een wisselschema maken in vijf stappen</a></li>
  <li><a href="/speeltijd-eerlijk-verdelen/">Speeltijd eerlijk verdelen</a></li>
</ul></section>
""", extra_ld=faq_ld(knvb_faq))

# ------------------------------------------------------------- prijzen
pr_faq = [
    ("Betaal ik per trainer of per team?", f"Per team. Een team kost {PRIJS} euro per drie maanden. Alle trainers die je aan dat team toevoegt, gebruiken de app gratis."),
    ("Wat zit er in de gratis proef?", f"De eerste {GRATIS} wedstrijden van een team, met alle functies: opstellingen, het wedstrijdscherm, verslagen en de speeltijd over het seizoen."),
    ("Zit ik ergens aan vast?", "Nee. Je betaalt per drie maanden en zegt op wanneer je wilt, bijvoorbeeld in de winterstop of aan het eind van het seizoen."),
    ("Wat gebeurt er met mijn gegevens als ik stop?", "Je spelers, wedstrijden en verslagen blijven zichtbaar. Je kunt alleen geen nieuwe wedstrijden meer plannen tot je weer betaalt."),
    ("Heb ik meerdere teams? ", "Dan betaal je per team. Train je twee teams, dan zijn dat twee keer de kosten."),
]
page("/prijzen/",
     f"Prijzen: {PRIJS} euro per 3 maanden per team",
     f"Opstelling kost {PRIJS} euro per drie maanden per team, en de eerste {GRATIS} wedstrijden zijn gratis. Medetrainers gebruiken de app kosteloos.",
     f"""
<section class="prose">
  <h1>Wat Opstelling kost</h1>
  <p class="lead">Eén eenvoudig tarief per team, en geen verrassingen. Je begint gratis en betaalt pas als je team het echt gebruikt.</p>
</section>

<section id="prijs">
  <div class="prijs">
    <div class="kaart">
      <h3>Uitproberen</h3>
      <p class="bedrag">Gratis</p>
      <p class="small">De eerste {GRATIS} wedstrijden van je team</p>
      <ul><li>Alle functies, niets beperkt</li><li>Zoveel trainers als je wilt</li><li>Geen betaalgegevens nodig</li></ul>
    </div>
    <div class="kaart uitgelicht">
      <h3>Per team</h3>
      <p class="bedrag">{PRIJS} <span>euro per 3 maanden</span></p>
      <p class="small">Voor één team, wanneer je wilt op te zeggen</p>
      <ul><li>Onbeperkt wedstrijden plannen</li><li>Speeltijd over het hele seizoen</li><li>Medetrainers gratis</li><li>Wedstrijdverslagen delen</li></ul>
      <p><a class="btn" href="{APP}">Begin met je team</a></p>
    </div>
  </div>
</section>

<section class="prose">
  <h2>Waarom niet gratis?</h2>
  <p>Opstelling draait op een server die geld kost, en wordt onderhouden naast een gewone baan. Een klein bedrag per team houdt de app onafhankelijk: geen advertenties, geen sponsors en geen doorverkoop van gegevens van kinderen.</p>
  <h2>Voor de hele club?</h2>
  <p>Wil je met meerdere teams tegelijk aan de slag, of als club afspraken maken? Laat het weten, dan kijken we naar een clubtarief.</p>
</section>

{{faq_html(pr_faq)}}
{{cta("Begin met je eigen team", f"De eerste {GRATIS} wedstrijden zijn gratis, zonder betaalgegevens.")}}
""", extra_ld=faq_ld(pr_faq))

# ------------------------------------------------------------- privacy
page("/privacy/",
     "Privacy en gegevens · Opstelling",
     "Welke gegevens Opstelling opslaat, waarom, en hoe je ze laat verwijderen. Geen advertenties, geen doorverkoop, alleen wat nodig is voor de opstelling.",
     """
<section class="prose">
  <h1>Privacy en gegevens</h1>
  <p class="lead">Opstelling is gemaakt voor kinderteams, dus we slaan zo min mogelijk op.</p>
  <h2>Wat wordt opgeslagen</h2>
  <ul>
    <li><strong>Van trainers:</strong> e-mailadres en de naam die je zelf invult. Het e-mailadres is nodig om in te loggen en om je aan een team te koppelen.</li>
    <li><strong>Van spelers:</strong> alleen een voornaam, plus wat je zelf invult over posities, en per wedstrijd de speeltijd en doelpunten. Geen geboortedata, adressen of foto's.</li>
    <li><strong>Van wedstrijden:</strong> datum, tegenstander, opstelling, wissels en de uitslag.</li>
  </ul>
  <h2>Wie het kan zien</h2>
  <p>Alleen de trainers van hetzelfde team. Dat is niet alleen een afspraak: de database staat het technisch niet toe dat iemand de gegevens van een ander team opvraagt.</p>
  <h2>Verwijderen</h2>
  <p>Een speler of een heel team verwijder je zelf in de app; dan zijn de gegevens weg. Wil je je account laten verwijderen, stuur dan een bericht vanaf het e-mailadres waarmee je inlogt.</p>
  <h2>Geen advertenties, geen trackers</h2>
  <p>Er staan geen advertentie- of volgscripts in de app of op deze site, en gegevens worden niet gedeeld met anderen.</p>
  <h2>Tips voor trainers</h2>
  <p>Gebruik alleen voornamen, zoals de app voorstelt. Deel het wedstrijdverslag in de groepsapp van je eigen team, niet openbaar.</p>
</section>
""")

# ------------------------------------------------------ sitemap, robots
paths = ["/", "/prijzen/", "/wisselschema-maken/", "/speeltijd-eerlijk-verdelen/", "/knvb-wedstrijdvormen/", "/privacy/"]
def prioriteit(p):
    if p == "/":
        return "1.0"
    return "0.3" if p == "/privacy/" else "0.8"

urls = "".join(
    "<url><loc>{}{}</loc><lastmod>{}</lastmod><changefreq>monthly</changefreq>"
    "<priority>{}</priority></url>".format(SITE, p, TODAY, prioriteit(p)) for p in paths)
(OUT / "sitemap.xml").write_text(
    f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
    encoding="utf-8")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
print("Site gebouwd:", ", ".join(paths))
