# Website van Opstelling

Statische marketingsite: geen eigen JavaScript, zeven pagina's, klaar voor Google en AI-assistenten. Alleen de bezoekersteller van Cloudflare wordt geladen (als die aan staat).

## Pagina's en hun zoekvraag

| Pagina | Waarop hij moet scoren |
|---|---|
| `/` | opstelling app jeugdvoetbal, opstelling maken, speeltijd bijhouden |
| `/wisselschema-maken/` | wisselschema maken jeugdvoetbal, wisselschema pupillen |
| `/speeltijd-eerlijk-verdelen/` | speeltijd eerlijk verdelen, speelminuten jeugdvoetbal |
| `/knvb-wedstrijdvormen/` | KNVB wedstrijdvormen, speelduur O8, hoe lang duurt een wedstrijd O10 |
| `/tips-en-tops-per-speler/` | tips en tops voetbal, spelersvolgsysteem jeugdvoetbal, voortgang spelers bijhouden |
| `/voetbal-nl-kalender-koppelen/` | voetbal.nl kalender, voetbal.nl agenda koppelen, verzameltijd, wasschema voetbal |
| `/contact/` | (contactformulier; berichten naar info@opstellingapp.nl) |

Het menu bovenaan en de voettekst staan als `NAV` en `VOET` bovenin `build.py`. De sitemap en `llms.txt` worden gemaakt uit de pagina's zelf, dus een nieuwe pagina komt daar vanzelf in.

## Voor AI-assistenten

`llms.txt` is een korte samenvatting van de site in platte tekst (kernfeiten, prijs en alle pagina's), bedoeld voor ChatGPT, Claude, Perplexity en dergelijke. De functiepagina's hebben daarnaast een kruimelpad en veelgestelde vragen in de gestructureerde gegevens, en de homepagina een lijst met functies van de app.

## Aanpassen

Teksten staan in `build.py`. Wijzig ze en draai:

```bash
python3 build.py
```

Dat schrijft de HTML-bestanden, de sitemap en robots.txt opnieuw.

**Eigen domein?** Pas `SITE` bovenin `build.py` aan en draai opnieuw. Het adres van de app staat er als `APP` boven.

## Bezoekers tellen (Cloudflare Web Analytics)

1. Log in op dash.cloudflare.com en ga naar **Web Analytics** > **Add a site**.
2. Vul het adres van de site in en kies de optie met het JavaScript-fragment (niet via Cloudflare DNS).
3. Kopieer uit dat fragment de waarde achter `"token"`.
4. Plak die bovenin `build.py` bij `CF_TOKEN = "..."` en draai `python3 build.py`.

Daarna staat de teller op elke pagina. Leeg laten = geen teller.
Cloudflare telt zonder cookies, dus er is geen cookiemelding nodig.

## Contactformulier (Netlify Forms)

Het formulier op `/contact/` wordt verwerkt door Netlify, zonder JavaScript. Eenmalig instellen in Netlify:

1. **Forms** > **Enable form detection** aanzetten, en daarna één keer opnieuw publiceren.
2. **Forms** > **Form notifications** > **Add notification** > **Email notification**: formulier `contact`, adres `info@opstellingapp.nl`.

Na versturen komt de bezoeker op `/bedankt/` (die pagina staat niet in Google). Spam wordt tegengehouden met een verborgen veld.
Netlify verwerkt gratis 100 berichten per maand.

## Knoppen naar de app

Alle knoppen gaan naar `AANMELDEN` (de app met `?account=nieuw`). De app laat daar "Maak je account aan" zien in plaats van "Inloggen".

## Uiterlijk

- Kleuren en opmaak staan in `style.css`.
- Lettertypes staan in `fonts/` (Bricolage Grotesque en Figtree, open licentie OFL). Ze komen van de eigen site, niet van Google.
- Schermafbeeldingen van de app staan als `.webp` in `img/`, gemaakt op drie keer schermresolutie.

## Testen

```bash
npm install          # eenmalig, gebruikt @playwright/test
npx playwright test
```

De test controleert per pagina: unieke titel en beschrijving met de juiste lengte, canoniek adres, één h1, geldige gestructureerde gegevens, sociale kaart, alt-teksten, interne links, de knop naar de app, of de pagina onder de 500 kB blijft, dat er op telefoon, tablet en laptop niets buiten beeld valt, en dat llms.txt alle pagina's noemt.

## Online zetten

De site staat op Netlify en wordt automatisch gepubliceerd vanuit GitHub.

### Werkwijze

1. Pas de teksten aan in `build.py`.
2. Draai `python3 build.py` (dat schrijft de HTML, de sitemap en robots.txt).
3. Commit **zowel** `build.py` als de gebouwde bestanden, en push naar `main`.

GitHub Actions bouwt daarna opnieuw, controleert of jouw gebouwde bestanden kloppen, draait de SEO-controles en publiceert pas daarna naar Netlify. Faalt er iets, dan blijft de oude site staan.

Op een pull request draaien dezelfde controles, maar wordt er niet gepubliceerd.

De site gaat altijd naar het echte adres. Zolang `PUBLIEK = False` in `build.py` staat, weren robots.txt en elke pagina zoekmachines: wie het adres kent kan kijken, maar Google neemt de site niet op. Zet `PUBLIEK = True` zodra de site gevonden mag worden.

Opnieuw publiceren zonder wijziging: GitHub > Actions > Controleren en publiceren > Run workflow.

### Eenmalig instellen

1. Zet deze map in een eigen GitHub-repository (bijvoorbeeld `opstelling-website`).
2. Maak in Netlify een site aan met **Deploy manually** (dus **niet** koppelen aan GitHub, anders publiceert Netlify zelf ook nog eens buiten de controles om).
3. Haal in Netlify twee waarden op:
   - **Site ID:** Site configuration > General > Site details (heet ook wel API ID).
   - **Token:** rechtsboven op je profiel > User settings > Applications > Personal access tokens > New access token.
4. Zet die in GitHub onder Settings > Secrets and variables > Actions als `NETLIFY_SITE_ID` en `NETLIFY_AUTH_TOKEN`.

Daarna het domein koppelen in Netlify en de site aanmelden in Google Search Console, met de sitemap: `/sitemap.xml`.
