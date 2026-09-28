# Website van Opstelling

Statische marketingsite: geen JavaScript, vijf pagina's, klaar voor Google.

## Pagina's en hun zoekvraag

| Pagina | Waarop hij moet scoren |
|---|---|
| `/` | opstelling app jeugdvoetbal, opstelling maken, speeltijd bijhouden |
| `/wisselschema-maken/` | wisselschema maken jeugdvoetbal, wisselschema pupillen |
| `/speeltijd-eerlijk-verdelen/` | speeltijd eerlijk verdelen, speelminuten jeugdvoetbal |
| `/knvb-wedstrijdvormen/` | KNVB wedstrijdvormen, speelduur O8, hoe lang duurt een wedstrijd O10 |
| `/privacy/` | (niet voor Google, wel voor vertrouwen bij clubs) |

## Aanpassen

Teksten staan in `build.py`. Wijzig ze en draai:

```bash
python3 build.py
```

Dat schrijft de HTML-bestanden, de sitemap en robots.txt opnieuw.

**Eigen domein?** Pas `SITE` bovenin `build.py` aan en draai opnieuw. Het adres van de app staat er als `APP` boven.

## Testen

```bash
npm install          # eenmalig, gebruikt @playwright/test
npx playwright test
```

De test controleert per pagina: unieke titel en beschrijving met de juiste lengte, canoniek adres, één h1, geldige gestructureerde gegevens, sociale kaart, alt-teksten, interne links, de knop naar de app, en of de pagina onder de 500 kB blijft.

## Online zetten

De site staat op Netlify en wordt automatisch gepubliceerd vanuit GitHub.

### Werkwijze

1. Pas de teksten aan in `build.py`.
2. Draai `python3 build.py` (dat schrijft de HTML, de sitemap en robots.txt).
3. Commit **zowel** `build.py` als de gebouwde bestanden, en push naar `main`.

GitHub Actions bouwt daarna opnieuw, controleert of jouw gebouwde bestanden kloppen, draait de SEO-controles en publiceert pas daarna naar Netlify. Faalt er iets, dan blijft de oude site staan.

Op een pull request draaien dezelfde controles, maar wordt er niet gepubliceerd.

### Eenmalig instellen

1. Zet deze map in een eigen GitHub-repository (bijvoorbeeld `opstelling-website`).
2. Maak in Netlify een site aan met **Deploy manually** (dus **niet** koppelen aan GitHub, anders publiceert Netlify zelf ook nog eens buiten de controles om).
3. Haal in Netlify twee waarden op:
   - **Site ID:** Site configuration > General > Site details (heet ook wel API ID).
   - **Token:** rechtsboven op je profiel > User settings > Applications > Personal access tokens > New access token.
4. Zet die in GitHub onder Settings > Secrets and variables > Actions als `NETLIFY_SITE_ID` en `NETLIFY_AUTH_TOKEN`.

Daarna het domein koppelen in Netlify en de site aanmelden in Google Search Console, met de sitemap: `/sitemap.xml`.
