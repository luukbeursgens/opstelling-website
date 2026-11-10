"""Rekent voorbeeldwisselschema's uit voor de website: per kwart wie keept, speelt of wisselt.

Eerlijk binnen één wedstrijd: iedereen zit zo vaak mogelijk even vaak op de bank. Komt
het niet precies uit, dan zitten de keepers het minst (wie een helft keept, krijgt de extra
veldtijd, net als in de app). Een keeper zit nooit op de bank in de helft dat hij keept, en
waar het kan zit niemand twee kwarten achter elkaar aan de kant. Over het hele seizoen
eerlijk verdelen doet alleen de app.
"""
from itertools import combinations

# Voorbeeldnamen, bewust gemengd: jongens en meiden, en niet alleen Nederlandse namen
NAMEN = ["Daan", "Milan", "Yusuf", "Luca", "Finn", "Mohammed", "Sven", "Noor", "Ilias", "Amir", "Lina", "Adam", "Sara", "Jens"]


def bankbeurten(spelers, plekken, kwarten):
    """Hoe vaak elke speler op de bank zit; de extra beurten gaan naar de veldspelers achteraan de lijst."""
    totaal = kwarten * (spelers - plekken)
    basis, extra = divmod(totaal, spelers)
    beurten = [basis] * spelers
    for i in range(spelers - 1, 1, -1):   # de keepers (plek 0 en 1) krijgen geen extra beurt
        if extra == 0:
            break
        beurten[i] += 1
        extra -= 1
    assert extra == 0, "te veel bankbeurten om eerlijk te verdelen"
    return beurten


def schema(spelers, plekken, kwarten=4):
    """Lijst van (naam, rollen), bijvoorbeeld ('Daan', 'KKWV'): K = keeper, V = veld, W = wissel.

    De eerste speler keept de eerste helft, de tweede speler de tweede helft.
    """
    namen = NAMEN[:spelers]
    keeper_per_kwart = [0 if k < kwarten // 2 else 1 for k in range(kwarten)]
    nodig = bankbeurten(spelers, plekken, kwarten)
    per_kwart = spelers - plekken

    def zoek(kwart, over, banken, achter_elkaar_toegestaan):
        if kwart == kwarten:
            return banken
        kandidaten = [i for i in range(spelers) if over[i] > 0 and i != keeper_per_kwart[kwart]]
        # wie nog het meest op de bank moet, eerst; daarna wie het vorige kwart speelde
        kandidaten.sort(key=lambda i: (-over[i], i in (banken[-1] if banken else ()), -i))
        for bank in combinations(kandidaten, per_kwart):
            if not achter_elkaar_toegestaan and banken and set(bank) & set(banken[-1]):
                continue
            rest = list(over)
            for i in bank:
                rest[i] -= 1
            # haalbaar: genoeg kwarten over voor wat iedereen nog moet zitten
            nog = kwarten - kwart - 1
            if any(r > nog for r in rest) or sum(rest) != nog * per_kwart:
                continue
            uitkomst = zoek(kwart + 1, rest, banken + [set(bank)], achter_elkaar_toegestaan)
            if uitkomst:
                return uitkomst
        return None

    banken = zoek(0, nodig, [], False) or zoek(0, nodig, [], True)
    assert banken, f"geen schema gevonden voor {spelers} spelers"
    return [(naam, "".join("K" if keeper_per_kwart[k] == i else "W" if i in banken[k] else "V" for k in range(kwarten)))
            for i, naam in enumerate(namen)]


def wisselmomenten(uitkomst):
    """Per overgang tussen kwarten: (wie erin, wie eruit, wie gaat op doel)."""
    momenten = []
    for k in range(1, len(uitkomst[0][1])):
        erin = [n for n, r in uitkomst if r[k - 1] == "W" and r[k] != "W"]
        eruit = [n for n, r in uitkomst if r[k - 1] != "W" and r[k] == "W"]
        nieuwe_keeper = [n for n, r in uitkomst if r[k] == "K" and r[k - 1] != "K"]
        momenten.append((erin, eruit, nieuwe_keeper[0] if nieuwe_keeper else None))
    return momenten
