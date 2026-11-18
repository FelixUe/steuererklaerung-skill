#!/usr/bin/env python3
"""Rechenwerk für die Vorbereitung der deutschen Einkommensteuererklärung.

Unterkommandos:
    init                        Arbeitsverzeichnis und haushalt.yaml anlegen
    jahr <JAHR>                 Steuerjahr anlegen, belege.json aus Stammdaten vorbefüllen
    arbeitstage <JAHR>          Büro- und Homeoffice-Tage schätzen (Feiertage je Bundesland)
    regeln <JAHR>               Pauschalen und Höchstbeträge des Jahres samt Rechtsstand zeigen
    rechnen <JAHR>              Varianten und Höchstbeträge rechnen -> berechnung.json
    dossier <JAHR>              dossier.md aus der Berechnung erzeugen

Arbeitsverzeichnis: --pfad, sonst $STEUER_PFAD, sonst ~/Documents/Steuer
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"

# --------------------------------------------------------------------------- #
# Kategorien
# --------------------------------------------------------------------------- #

WERBUNGSKOSTEN = {
    "arbeitsmittel", "fortbildung", "berufsverband", "reisekosten",
    "doppelte_haushaltsfuehrung", "bewerbung", "kontofuehrung",
    "telefon_internet", "umzug_beruflich", "arbeitskleidung",
    "steuerberatung_werbungskosten",
}
P35A = {"haushaltsnahe_dienstleistung", "handwerkerleistung", "minijob_im_haushalt"}
SONDERAUSGABEN = {
    "kirchensteuer", "spende", "parteibeitrag", "versicherung_vorsorge",
    "riester_ruerup", "unterhalt_ex_partner", "eigene_berufsausbildung",
}
KINDER = {"kinderbetreuung", "schulgeld", "kind_ausbildung", "kind_versicherung"}
AUSSERGEWOEHNLICH = {
    "krankheitskosten", "behinderung", "pflegekosten", "bestattungskosten", "kur",
}
FAHRT = {"fahrt_arbeit", "homeoffice", "arbeitszimmer"}

ANLAGE = {
    "arbeitsmittel": ("Anlage N", "Arbeitsmittel"),
    "fortbildung": ("Anlage N", "Fortbildungskosten"),
    "berufsverband": ("Anlage N", "Beiträge zu Berufsverbänden"),
    "reisekosten": ("Anlage N", "Reisekosten bei Auswärtstätigkeit"),
    "doppelte_haushaltsfuehrung": ("Anlage N", "Doppelte Haushaltsführung"),
    "bewerbung": ("Anlage N", "Weitere Werbungskosten"),
    "kontofuehrung": ("Anlage N", "Weitere Werbungskosten"),
    "telefon_internet": ("Anlage N", "Weitere Werbungskosten"),
    "umzug_beruflich": ("Anlage N", "Umzugskosten"),
    "arbeitskleidung": ("Anlage N", "Arbeitsmittel"),
    "steuerberatung_werbungskosten": ("Anlage N", "Weitere Werbungskosten"),
    "fahrt_arbeit": ("Anlage N", "Wege zwischen Wohnung und erster Tätigkeitsstätte"),
    "homeoffice": ("Anlage N", "Häusliches Arbeitszimmer / Tagespauschale"),
    "arbeitszimmer": ("Anlage N", "Häusliches Arbeitszimmer"),
    "kirchensteuer": ("Anlage Sonderausgaben", "Kirchensteuer"),
    "spende": ("Anlage Sonderausgaben", "Zuwendungen"),
    "parteibeitrag": ("Anlage Sonderausgaben", "Zuwendungen an politische Parteien"),
    "versicherung_vorsorge": ("Anlage Vorsorgeaufwand", "Sonstige Vorsorgeaufwendungen"),
    "riester_ruerup": ("Anlage Vorsorgeaufwand / Anlage AV", "Altersvorsorgebeiträge"),
    "unterhalt_ex_partner": ("Anlage Sonderausgaben / Anlage U", "Unterhaltsleistungen"),
    "eigene_berufsausbildung": ("Anlage Sonderausgaben", "Berufsausbildungskosten"),
    "kinderbetreuung": ("Anlage Kind", "Kinderbetreuungskosten"),
    "schulgeld": ("Anlage Kind", "Schulgeld"),
    "kind_ausbildung": ("Anlage Kind", "Auswärtige Unterbringung"),
    "kind_versicherung": ("Anlage Kind", "Beiträge zur Kranken- und Pflegeversicherung"),
    "haushaltsnahe_dienstleistung": ("Anlage Haushaltsnahe Aufwendungen", "Haushaltsnahe Dienstleistungen"),
    "handwerkerleistung": ("Anlage Haushaltsnahe Aufwendungen", "Handwerkerleistungen"),
    "minijob_im_haushalt": ("Anlage Haushaltsnahe Aufwendungen", "Haushaltsnahes Beschäftigungsverhältnis"),
    "krankheitskosten": ("Anlage Außergewöhnliche Belastungen", "Krankheitskosten"),
    "behinderung": ("Anlage Außergewöhnliche Belastungen", "Behinderung"),
    "pflegekosten": ("Anlage Außergewöhnliche Belastungen", "Pflegekosten"),
    "bestattungskosten": ("Anlage Außergewöhnliche Belastungen", "Bestattungskosten"),
    "kur": ("Anlage Außergewöhnliche Belastungen", "Kur"),
    "kapitalertraege": ("Anlage KAP", "Kapitalerträge"),
    "vermietung": ("Anlage V", "Vermietung und Verpachtung"),
    "selbstaendig": ("Anlage S", "Selbständige Arbeit"),
    "lohnersatzleistung": ("Anlage N", "Lohnersatzleistungen (Progressionsvorbehalt)"),
    "rente": ("Anlage R", "Renten"),
}

# --------------------------------------------------------------------------- #
# Feiertage
# --------------------------------------------------------------------------- #

LAENDER = ["BW", "BY", "BE", "BB", "HB", "HH", "HE", "MV",
           "NI", "NW", "RP", "SL", "SN", "ST", "SH", "TH"]


def ostersonntag(jahr: int) -> dt.date:
    """Anonyme gregorianische Osterformel."""
    a = jahr % 19
    b = jahr // 100
    c = jahr % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    monat = (h + l - 7 * m + 114) // 31
    tag = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(jahr, monat, tag)


def feiertage(jahr: int, land: str) -> dict[dt.date, str]:
    """Gesetzliche Feiertage. Ohne Gemeinde-Sonderfälle; Mariä Himmelfahrt wird
    für Bayern vollständig gezählt, obwohl sie dort nur in überwiegend
    katholischen Gemeinden gilt. Das Ergebnis ist eine Schätzung."""
    land = (land or "").upper()
    o = ostersonntag(jahr)
    t: dict[dt.date, str] = {
        dt.date(jahr, 1, 1): "Neujahr",
        o - dt.timedelta(days=2): "Karfreitag",
        o + dt.timedelta(days=1): "Ostermontag",
        dt.date(jahr, 5, 1): "Tag der Arbeit",
        o + dt.timedelta(days=39): "Christi Himmelfahrt",
        o + dt.timedelta(days=50): "Pfingstmontag",
        dt.date(jahr, 10, 3): "Tag der Deutschen Einheit",
        dt.date(jahr, 12, 25): "1. Weihnachtstag",
        dt.date(jahr, 12, 26): "2. Weihnachtstag",
    }
    if land in {"BW", "BY", "ST"}:
        t[dt.date(jahr, 1, 6)] = "Heilige Drei Könige"
    if land in {"BE", "MV"}:
        t[dt.date(jahr, 3, 8)] = "Internationaler Frauentag"
    if land in {"BW", "BY", "HE", "NW", "RP", "SL"}:
        t[o + dt.timedelta(days=60)] = "Fronleichnam"
    if land in {"BY", "SL"}:
        t[dt.date(jahr, 8, 15)] = "Mariä Himmelfahrt"
    if land == "TH":
        t[dt.date(jahr, 9, 20)] = "Weltkindertag"
    if land in {"BB", "HB", "HH", "MV", "NI", "SH", "SN", "ST", "TH"}:
        t[dt.date(jahr, 10, 31)] = "Reformationstag"
    if land in {"BW", "BY", "NW", "RP", "SL"}:
        t[dt.date(jahr, 11, 1)] = "Allerheiligen"
    if land == "SN":
        d = dt.date(jahr, 11, 23)
        while d.weekday() != 2:                      # Mittwoch vor dem 23.11.
            d -= dt.timedelta(days=1)
        t[d] = "Buß- und Bettag"
    if land == "BE" and jahr == 2025:
        t[dt.date(jahr, 5, 8)] = "80. Jahrestag der Befreiung (einmalig)"
    return t


WOCHENTAGE = ["mo", "di", "mi", "do", "fr", "sa", "so"]


def tage_nach_muster(jahr: int, land: str, muster: dict) -> dict:
    """Zählt Büro- und Homeoffice-Tage anhand des Wochenmusters, ohne Feiertage."""
    fei = feiertage(jahr, land)
    zaehler = {"buero": 0, "homeoffice": 0, "frei": 0}
    feiertage_an_arbeitstagen = []
    tag = dt.date(jahr, 1, 1)
    ende = dt.date(jahr, 12, 31)
    while tag <= ende:
        key = WOCHENTAGE[tag.weekday()]
        art = (muster or {}).get(key, "buero" if tag.weekday() < 5 else "frei")
        if tag.weekday() >= 5:
            art = "frei"
        if art in ("buero", "homeoffice") and tag in fei:
            feiertage_an_arbeitstagen.append(f"{tag.isoformat()} {fei[tag]}")
            art = "frei"
        zaehler[art if art in zaehler else "frei"] += 1
        tag += dt.timedelta(days=1)
    return {
        "buero_roh": zaehler["buero"],
        "homeoffice_roh": zaehler["homeoffice"],
        "feiertage_an_arbeitstagen": feiertage_an_arbeitstagen,
    }


def arbeitstage_schaetzen(jahr, land, muster, urlaub=0, krank=0, sonstige=0) -> dict:
    roh = tage_nach_muster(jahr, land, muster)
    b, h = roh["buero_roh"], roh["homeoffice_roh"]
    gesamt_roh = b + h
    abwesend = (urlaub or 0) + (krank or 0) + (sonstige or 0)
    abwesend = min(abwesend, gesamt_roh)
    if gesamt_roh == 0:
        buero = homeoffice = 0
    else:
        ab_b = round(abwesend * b / gesamt_roh)
        buero = max(0, b - ab_b)
        homeoffice = max(0, h - (abwesend - ab_b))
    return {
        "arbeitstage_gesamt": buero + homeoffice,
        "buero_tage": buero,
        "homeoffice_tage": homeoffice,
        "bundesland": (land or "").upper(),
        "abwesenheit": {"urlaub": urlaub, "krank": krank, "sonstige": sonstige},
        "roh": roh,
        "grundlage": (
            f"Wochenmuster aus haushalt.yaml, Feiertage {(land or '').upper() or 'bundesweit'}, "
            f"abzüglich {abwesend} Abwesenheitstage"
        ),
        "bestaetigt": False,
    }


# --------------------------------------------------------------------------- #
# Laden und Speichern
# --------------------------------------------------------------------------- #

def basis(args) -> Path:
    if getattr(args, "pfad", None):
        return Path(args.pfad).expanduser()
    if os.environ.get("STEUER_PFAD"):
        return Path(os.environ["STEUER_PFAD"]).expanduser()
    return Path.home() / "Documents" / "Steuer"


def lade_haushalt(root: Path) -> dict:
    jsn = root / "haushalt.json"
    if jsn.exists():
        return json.loads(jsn.read_text(encoding="utf-8"))
    for name in ("haushalt.yaml", "haushalt.yml"):
        p = root / name
        if p.exists():
            text = p.read_text(encoding="utf-8")
            try:
                import yaml  # type: ignore
                return yaml.safe_load(text) or {}
            except ImportError:
                pass
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import minyaml
            try:
                return minyaml.load(text) or {}
            except minyaml.YamlFehler as e:
                sys.exit(
                    f"{p} konnte nicht gelesen werden: {e}\n"
                    "Der eingebaute YAML-Leser deckt nur die Struktur der Vorlage ab. "
                    "Entweder die Zeile an die Vorlage anpassen oder 'pip install pyyaml' "
                    "ausführen, dann wird der vollständige Parser benutzt."
                )
    sys.exit(f"Keine haushalt.yaml in {root}. Zuerst 'steuer.py init' ausführen.")


def lade_recht() -> dict:
    return json.loads((ASSETS / "steuerrecht.json").read_text(encoding="utf-8"))


def regeln_fuer(jahr: int) -> tuple[dict, dict, str]:
    recht = lade_recht()
    j = recht["jahre"].get(str(jahr))
    if not j:
        verfuegbar = ", ".join(sorted(recht["jahre"]))
        sys.exit(
            f"Für {jahr} liegen keine Werte in assets/steuerrecht.json.\n"
            f"Vorhanden: {verfuegbar}. Werte recherchieren und eintragen."
        )
    return j, recht["konstant"], recht["stand"]


def eur(x) -> str:
    """Deutsche Schreibweise: 1.234,56 €"""
    if x is None:
        return "–"
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


# --------------------------------------------------------------------------- #
# Rechenbausteine
# --------------------------------------------------------------------------- #

def entfernungspauschale_pro_tag(km: float, stufen: list) -> float:
    betrag, bisher = 0.0, 0.0
    for s in stufen:
        grenze = s.get("bis_km")
        if grenze is None:
            segment = max(0.0, km - bisher)
        else:
            segment = max(0.0, min(km, float(grenze)) - bisher)
            bisher = float(grenze)
        betrag += segment * s["eur_pro_km"]
    return round(betrag, 4)


def zumutbare_belastung(gde: float, kinder: int, veranlagung: str, konst: dict) -> dict:
    cfg = konst["zumutbare_belastung"]
    g1, g2 = cfg["grenzen_eur"]
    if kinder >= 3:
        key = "kinder_ab_3"
    elif kinder >= 1:
        key = "kinder_1_bis_2"
    elif veranlagung == "zusammen":
        key = "ohne_kinder_splitting"
    else:
        key = "ohne_kinder_grundtarif"
    s1, s2, s3 = cfg["saetze"][key]
    b1 = min(gde, g1)
    b2 = max(0.0, min(gde, g2) - g1)
    b3 = max(0.0, gde - g2)
    betrag = b1 * s1 + b2 * s2 + b3 * s3
    return {
        "betrag_eur": round(betrag, 2),
        "staffel": key,
        "saetze": [s1, s2, s3],
        "grundlage_gde_eur": round(gde, 2),
        "kinder": kinder,
        "berechnung": "stufenweise nach BFH VI R 75/14",
    }


def netto(b: dict) -> float:
    """Abziehbarer Betrag eines Belegs nach Erstattung und beruflichem Anteil."""
    betrag = float(b.get("betrag_brutto_eur") or 0)
    betrag -= float(b.get("erstattung_eur") or 0)
    anteil = b.get("beruflicher_anteil_prozent")
    if anteil:
        betrag *= float(anteil) / 100.0
    return round(max(0.0, betrag), 2)


def aktiv(b: dict) -> bool:
    return (b.get("status") or "bestaetigt") == "bestaetigt"


# --------------------------------------------------------------------------- #
# Varianten Fahrt / Homeoffice
# --------------------------------------------------------------------------- #

def fahrtvarianten(person: dict, tage: dict, jahr_regeln: dict,
                   lohn: dict, wohnen: list) -> dict:
    ag = (person.get("arbeitgeber") or [{}])[0]
    ets = ag.get("erste_taetigkeitsstaette") or {}
    km_kurz = ets.get("entfernung_km")
    km_lang = ets.get("entfernung_km_verkehrsguenstig")
    stufen = jahr_regeln["entfernungspauschale"]["stufen"]
    cap_ohne_kfz = jahr_regeln["entfernungspauschale"]["hoechstbetrag_ohne_eigenes_kfz_eur"]
    ho = jahr_regeln["homeoffice_tagespauschale"]
    jahrespauschale = jahr_regeln["arbeitszimmer_jahrespauschale_eur"]

    buero = int(tage.get("buero_tage") or 0)
    hotage = int(tage.get("homeoffice_tage") or 0)
    alle = buero + hotage
    zuschuss = float((lohn or {}).get("jobticket_zuschuss_eur") or 0)
    eigenes_kfz = (ag.get("verkehrsmittel") or "auto") == "auto"

    def fahrt(km, tage_n):
        if not km:
            return None
        rohbetrag = entfernungspauschale_pro_tag(float(km), stufen) * tage_n
        gedeckelt = rohbetrag if eigenes_kfz else min(rohbetrag, cap_ohne_kfz)
        return round(max(0.0, gedeckelt - zuschuss), 2)

    ho_betrag = lambda n: round(min(n, ho["max_tage"]) * ho["eur_pro_tag"], 2)

    varianten = []
    hinweise: list[str] = []

    def add(name, posten, bedingung="", erfuellt=True):
        """erfuellt: True = belegt, None = ungeprüft, False = trifft nicht zu (wird nicht
        empfohlen). Eine Variante mit falscher Voraussetzung darf nie oben stehen — sonst
        empfiehlt das Dossier eine unrichtige Angabe."""
        summe = round(sum(v for _, v in posten if v is not None), 2)
        varianten.append({
            "name": name,
            "posten": [{"bezeichnung": k, "betrag_eur": v} for k, v in posten if v is not None],
            "summe_eur": summe,
            "bedingung": bedingung,
            "bedingung_erfuellt": erfuellt,
        })

    ho_posten = (f"{min(hotage, ho['max_tage'])} Homeoffice-Tage × {ho['eur_pro_tag']} €",
                 ho_betrag(hotage))

    if km_kurz:
        add("Entfernungspauschale (kürzeste Strecke) + Homeoffice-Tagespauschale",
            [(f"{buero} Bürotage × {km_kurz} km", fahrt(km_kurz, buero)), ho_posten])

    if km_lang and km_kurz and float(km_lang) > float(km_kurz):
        begruendung = ets.get("verkehrsguenstig_begruendet")
        add("Entfernungspauschale (verkehrsgünstigere Strecke) + Homeoffice-Tagespauschale",
            [(f"{buero} Bürotage × {km_lang} km", fahrt(km_lang, buero)), ho_posten],
            bedingung=("Längere Strecke muss offensichtlich verkehrsgünstiger sein und regelmäßig "
                       "benutzt werden. Begründung: "
                       + (begruendung or "FEHLT — in haushalt.yaml nachtragen")),
            erfuellt=True if begruendung else None)

    best_km = km_lang if (km_lang and km_kurz and float(km_lang) > float(km_kurz)) else km_kurz

    az = person.get("arbeitszimmer") or {}
    if az.get("mittelpunkt"):
        add("Arbeitszimmer-Jahrespauschale + Entfernungspauschale für Bürotage",
            [("Arbeitszimmer-Jahrespauschale", float(jahrespauschale)),
             (f"{buero} Bürotage × {best_km} km", fahrt(best_km, buero))],
            bedingung="Arbeitszimmer ist der qualitative Mittelpunkt der Tätigkeit.",
            erfuellt=None)
        if az.get("qm") and az.get("wohnung_qm"):
            w = (wohnen or [{}])[0]
            jahreskosten = (float(w.get("miete_kalt_monatlich") or 0)
                            + float(w.get("nebenkosten_monatlich") or 0)) * 12
            anteil = float(az["qm"]) / float(az["wohnung_qm"])
            tats = round(jahreskosten * anteil, 2)
            if tats > jahrespauschale:
                add("Tatsächliche Arbeitszimmerkosten + Entfernungspauschale für Bürotage",
                    [(f"{az['qm']} von {az['wohnung_qm']} qm = {anteil*100:.1f} % der Wohnkosten", tats),
                     (f"{buero} Bürotage × {best_km} km", fahrt(best_km, buero))],
                    bedingung=("Mittelpunkt der Tätigkeit UND Einzelnachweis der Wohnkosten. "
                               "Angesetzt sind nur Kaltmiete und Nebenkosten, ohne Strom und Reinigung."),
                    erfuellt=None)

    # Sonderfall § 4 Abs. 5 Nr. 6c EStG. Nur anbieten, wenn in den Stammdaten bestätigt —
    # bei vielen Bürotagen trifft er fast nie zu, und eine falsche Angabe ist teurer als
    # der gewonnene Abzug.
    kein_platz = ag.get("kein_anderer_arbeitsplatz")
    if best_km and alle and kein_platz:
        add("Tagespauschale für alle Arbeitstage + Entfernungspauschale (kein anderer Arbeitsplatz)",
            [(f"{min(alle, ho['max_tage'])} Arbeitstage × {ho['eur_pro_tag']} €", ho_betrag(alle)),
             (f"{buero} Bürotage × {best_km} km", fahrt(best_km, buero))],
            bedingung=("§ 4 Abs. 5 Nr. 6c EStG: dauerhaft kein anderer Arbeitsplatz beim "
                       "Arbeitgeber. In haushalt.yaml bestätigt — Arbeitgeberbescheinigung "
                       "bereithalten."),
            erfuellt=True)
    elif best_km and alle and kein_platz is None and buero and hotage:
        extra = round(ho_betrag(alle) - ho_betrag(hotage), 2)
        if extra > 0:
            hinweise.append(
                f"Falls beim Arbeitgeber dauerhaft kein Arbeitsplatz zur Verfügung steht, darf die "
                f"Tagespauschale auch für Bürotage angesetzt werden — das wären zusätzlich "
                f"{eur(extra)}. Trifft das zu, 'kein_anderer_arbeitsplatz: true' beim Arbeitgeber "
                "in haushalt.yaml setzen und eine Bescheinigung besorgen.")

    # ÖPNV: Vergleich nur gegen den Fahrtkostenanteil, nicht gegen die Gesamtvariante.
    oepnv = ag.get("oepnv_kosten_jaehrlich")
    if oepnv and best_km and buero:
        entf_brutto = round(entfernungspauschale_pro_tag(float(best_km), stufen) * buero, 2)
        if float(oepnv) > entf_brutto:
            hinweise.append(
                f"Tatsächliche ÖPNV-Kosten ({eur(float(oepnv))}) liegen über der "
                f"Entfernungspauschale für die Wege ({eur(entf_brutto)}). Der übersteigende Betrag "
                f"ist zusätzlich abziehbar (§ 9 Abs. 2 EStG) — also rund "
                f"{eur(round(float(oepnv) - entf_brutto, 2))} mehr. Jahresticket und Belege "
                "bereithalten; ein steuerfreier Arbeitgeberzuschuss ist davon abzuziehen.")

    waehlbar = [v for v in varianten if v["bedingung_erfuellt"] is not False]
    empfehlung = max(waehlbar, key=lambda v: v["summe_eur"]) if waehlbar else None
    unbedingt = [v for v in varianten if not v["bedingung"]]
    sicher = max(unbedingt, key=lambda v: v["summe_eur"]) if unbedingt else None

    return {
        "entfernung_km": km_kurz,
        "entfernung_km_verkehrsguenstig": km_lang,
        "eur_pro_tag_kuerzeste": entfernungspauschale_pro_tag(float(km_kurz), stufen) if km_kurz else None,
        "arbeitgeberzuschuss_abgezogen_eur": zuschuss,
        "varianten": varianten,
        "empfehlung": empfehlung["name"] if empfehlung else None,
        "empfehlung_summe_eur": empfehlung["summe_eur"] if empfehlung else 0.0,
        "empfehlung_ungeprueft": bool(empfehlung and empfehlung["bedingung_erfuellt"] is None),
        "ohne_bedingung": sicher["name"] if sicher else None,
        "ohne_bedingung_summe_eur": sicher["summe_eur"] if sicher else 0.0,
        "hinweise": hinweise,
    }


# --------------------------------------------------------------------------- #
# rechnen
# --------------------------------------------------------------------------- #

def cmd_rechnen(args):
    root = basis(args)
    jahr = args.jahr
    jd = root / str(jahr)
    belege_pfad = jd / "belege.json"
    if not belege_pfad.exists():
        sys.exit(f"{belege_pfad} fehlt. Zuerst 'steuer.py jahr {jahr}' ausführen.")

    haushalt = lade_haushalt(root)
    daten = json.loads(belege_pfad.read_text(encoding="utf-8"))
    jr, konst, stand = regeln_fuer(jahr)

    veranlagung = daten.get("veranlagung") or (haushalt.get("haushalt") or {}).get("veranlagung") or "einzeln"
    personen = {p["id"]: p for p in (haushalt.get("personen") or [])}
    kinder = haushalt.get("kinder") or []
    belege = [b for b in (daten.get("belege") or [])]
    warnungen: list[str] = []
    jahr_laeuft = dt.date.today() <= dt.date(jahr, 12, 31)

    # --- Werbungskosten je Person -----------------------------------------
    werbungskosten = {}
    for pid, person in personen.items():
        tage = (daten.get("arbeitstage") or {}).get(pid) or {}
        if not tage:
            land = (haushalt.get("haushalt") or {}).get("bundesland")
            muster = ((person.get("arbeitgeber") or [{}])[0]).get("arbeitstage_muster")
            tage = arbeitstage_schaetzen(jahr, land, muster)
            warnungen.append(
                f"Arbeitstage für {pid} waren nicht in belege.json; geschätzt "
                f"({tage['buero_tage']} Bürotage, {tage['homeoffice_tage']} Homeoffice). "
                "Vom Nutzer bestätigen lassen.")
        elif not tage.get("bestaetigt"):
            warnungen.append(f"Arbeitstage für {pid} sind noch nicht bestätigt.")

        lohn = (daten.get("lohndaten") or {}).get(pid) or {}
        fahrt = fahrtvarianten(person, tage, jr, lohn, haushalt.get("wohnen") or [])
        for h in fahrt["hinweise"]:
            warnungen.append(f"{pid}: {h}")
        if fahrt.get("empfehlung_ungeprueft"):
            warnungen.append(
                f"{pid}: Die günstigste Fahrtvariante hängt an einer ungeprüften Bedingung "
                f"({fahrt['empfehlung']}). Vor dem Ansetzen klären, sonst "
                f"{eur(fahrt['ohne_bedingung_summe_eur'])} statt "
                f"{eur(fahrt['empfehlung_summe_eur'])}.")

        sonstige = []
        for b in belege:
            if b.get("person") != pid or b.get("kategorie") not in WERBUNGSKOSTEN:
                continue
            if not aktiv(b):
                continue
            sonstige.append({
                "bezeichnung": b.get("bezeichnung"),
                "kategorie": b.get("kategorie"),
                "betrag_eur": netto(b),
                "anlage": ANLAGE.get(b.get("kategorie"), ("?", "?")),
            })
        summe_sonstige = round(sum(s["betrag_eur"] for s in sonstige), 2)

        pauschbetrag = jr["arbeitnehmer_pauschbetrag_eur"]
        gewerkschaft_extra = 0.0
        if jr.get("gewerkschaftsbeitrag_zusaetzlich_zum_pauschbetrag"):
            gewerkschaft_extra = round(sum(
                s["betrag_eur"] for s in sonstige if s["kategorie"] == "berufsverband"), 2)

        kern = round(fahrt["empfehlung_summe_eur"] + summe_sonstige - gewerkschaft_extra, 2)
        werbungskosten[pid] = {
            "fahrt_und_homeoffice": fahrt,
            "sonstige_werbungskosten": sonstige,
            "sonstige_summe_eur": summe_sonstige,
            "summe_eur": round(fahrt["empfehlung_summe_eur"] + summe_sonstige, 2),
            "arbeitnehmer_pauschbetrag_eur": pauschbetrag,
            "zusaetzlich_zum_pauschbetrag_eur": gewerkschaft_extra,
            "ueber_pauschbetrag_eur": round(kern - pauschbetrag, 2),
            "wirkt": kern > pauschbetrag or gewerkschaft_extra > 0,
            "arbeitstage": tage,
        }
        if kern <= pauschbetrag:
            fehlt = round(pauschbetrag - kern, 2)
            warnungen.append(
                f"Werbungskosten {pid}: {eur(kern)} liegen unter dem Pauschbetrag "
                f"({eur(pauschbetrag)}). Es fehlen {eur(fehlt)}, damit überhaupt etwas wirkt.")

    # --- § 35a -------------------------------------------------------------
    p35a = {}
    for kat in ("haushaltsnahe_dienstleistung", "handwerkerleistung", "minijob_im_haushalt"):
        cfg_key = {"haushaltsnahe_dienstleistung": "haushaltsnahe_dienstleistungen",
                   "handwerkerleistung": "handwerkerleistungen",
                   "minijob_im_haushalt": "minijob_im_haushalt"}[kat]
        cfg = jr["paragraph_35a"][cfg_key]
        posten, bar, ohne_lohnanteil = [], [], []
        for b in belege:
            if b.get("kategorie") != kat or not aktiv(b):
                continue
            if (b.get("zahlungsart") or "").lower() == "bar":
                bar.append(b.get("bezeichnung"))
                continue
            if kat == "handwerkerleistung":
                if b.get("lohnanteil_eur") in (None, ""):
                    ohne_lohnanteil.append(b.get("bezeichnung"))
                    continue
                betrag = float(b["lohnanteil_eur"])
            else:
                betrag = float(b.get("lohnanteil_eur") or b.get("betrag_brutto_eur") or 0)
            posten.append({"bezeichnung": b.get("bezeichnung"),
                           "anbieter": b.get("anbieter"),
                           "datum_zahlung": b.get("datum_zahlung"),
                           "anrechenbar_eur": round(betrag, 2)})
        grundlage = round(sum(p["anrechenbar_eur"] for p in posten), 2)
        angerechnet = min(grundlage, cfg["bemessungsgrundlage_max_eur"])
        ermaessigung = round(min(angerechnet * cfg["satz"], cfg["hoechstbetrag_eur"]), 2)
        p35a[kat] = {
            "posten": posten,
            "grundlage_eur": grundlage,
            "satz": cfg["satz"],
            "hoechstbetrag_eur": cfg["hoechstbetrag_eur"],
            "bemessungsgrundlage_max_eur": cfg["bemessungsgrundlage_max_eur"],
            "steuerermaessigung_eur": ermaessigung,
            "ausschoepfung_prozent": round(100 * ermaessigung / cfg["hoechstbetrag_eur"], 1),
            "noch_moeglich_eur": round(max(0.0, cfg["bemessungsgrundlage_max_eur"] - grundlage), 2),
            "anlage": ANLAGE[kat],
        }
        for name in bar:
            warnungen.append(f"§ 35a: '{name}' wurde bar gezahlt — nicht abziehbar, ohne Ausnahme.")
        for name in ohne_lohnanteil:
            warnungen.append(
                f"§ 35a: bei '{name}' fehlt der ausgewiesene Lohnanteil. Korrigierte Rechnung "
                "beim Handwerker anfordern, sonst fällt der Posten weg.")
        # Der Hinweis auf freie Höchstbeträge hilft nur, solange das Jahr noch läuft —
        # danach lässt sich nichts mehr verschieben, und er wäre bloß Rauschen.
        if jahr_laeuft and p35a[kat]["noch_moeglich_eur"] > 0 and grundlage > 0:
            warnungen.append(
                f"§ 35a {kat}: Höchstbetrag noch nicht erreicht. Bis zum 31.12.{jahr} bezahlte "
                f"weitere Arbeitskosten würden noch mit {int(cfg['satz']*100)} % gefördert, "
                f"bis zu {eur(round(cfg['hoechstbetrag_eur'] - p35a[kat]['steuerermaessigung_eur'], 2))} "
                "zusätzliche Ermäßigung.")
        if grundlage > cfg["bemessungsgrundlage_max_eur"]:
            warnungen.append(
                f"§ 35a {kat}: Höchstbetrag überschritten um "
                f"{eur(round(grundlage - cfg['bemessungsgrundlage_max_eur'], 2))} Kosten. "
                "Wenn möglich, eine Teilzahlung ins andere Jahr verschieben.")
    p35a["steuerermaessigung_gesamt_eur"] = round(
        sum(v["steuerermaessigung_eur"] for k, v in p35a.items() if isinstance(v, dict)), 2)

    # --- Kinder ------------------------------------------------------------
    kb_cfg = jr["kinderbetreuung"]
    sg_cfg = jr["schulgeld"]
    kinder_ergebnis = []
    for kind in kinder:
        kid = kind.get("id")
        geb = kind.get("geburtsdatum")
        alter_ende = None
        if geb:
            gd = dt.date.fromisoformat(str(geb))
            alter_ende = jahr - gd.year - ((12, 31) < (gd.month, gd.day))
        kosten = 0.0
        herkunft = []
        for bet in (kind.get("betreuung") or []):
            brutto = float(bet.get("monatlich") or 0) * 12
            verpflegung = float(bet.get("verpflegungsanteil_monatlich") or 0) * 12
            zuschuss = float(bet.get("arbeitgeberzuschuss_monatlich") or 0) * 12
            anrechenbar = max(0.0, brutto - verpflegung - zuschuss)
            kosten += anrechenbar
            herkunft.append({
                "art": bet.get("art"), "einrichtung": bet.get("einrichtung"),
                "jahreskosten_eur": round(brutto, 2),
                "verpflegung_abgezogen_eur": round(verpflegung, 2),
                "arbeitgeberzuschuss_abgezogen_eur": round(zuschuss, 2),
                "anrechenbar_eur": round(anrechenbar, 2),
                "quelle": "haushalt.yaml",
            })
        for b in belege:
            if b.get("kategorie") == "kinderbetreuung" and b.get("person") == kid and aktiv(b):
                kosten += netto(b)
                herkunft.append({"art": "beleg", "einrichtung": b.get("bezeichnung"),
                                 "anrechenbar_eur": netto(b), "quelle": "belege.json"})
        abzug = round(min(kosten * kb_cfg["anteil"], kb_cfg["hoechstbetrag_eur"]), 2)
        kosten_fuer_vollen_abzug = round(kb_cfg["hoechstbetrag_eur"] / kb_cfg["anteil"], 2)

        schulgeld = float((kind.get("schule") or {}).get("schulgeld_jaehrlich") or 0)
        for b in belege:
            if b.get("kategorie") == "schulgeld" and b.get("person") == kid and aktiv(b):
                schulgeld += netto(b)
        sg_abzug = round(min(schulgeld * sg_cfg["anteil"], sg_cfg["hoechstbetrag_eur"]), 2)

        eintrag = {
            "id": kid, "name": kind.get("name"), "alter_jahresende": alter_ende,
            "haushaltszugehoerig": kind.get("haushaltszugehoerig"),
            "betreuung": {
                "positionen": herkunft,
                "kosten_eur": round(kosten, 2),
                "anteil": kb_cfg["anteil"],
                "hoechstbetrag_eur": kb_cfg["hoechstbetrag_eur"],
                "abzug_eur": abzug,
                "kosten_fuer_vollen_abzug_eur": kosten_fuer_vollen_abzug,
                "anlage": ANLAGE["kinderbetreuung"],
            },
            "schulgeld": {
                "kosten_eur": round(schulgeld, 2),
                "anteil": sg_cfg["anteil"],
                "hoechstbetrag_eur": sg_cfg["hoechstbetrag_eur"],
                "abzug_eur": sg_abzug,
                "anlage": ANLAGE["schulgeld"],
            } if schulgeld else None,
        }
        kinder_ergebnis.append(eintrag)

        if kosten > 0 and kind.get("haushaltszugehoerig") is False:
            warnungen.append(
                f"Kind {kid}: Betreuungskosten erfasst, aber nicht als haushaltszugehörig "
                "markiert — dann ist kein Abzug möglich. Prüfen.")
        if alter_ende is not None and alter_ende >= kb_cfg["alter_bis_jahre"] and kosten > 0:
            warnungen.append(
                f"Kind {kid} ist zum Jahresende {alter_ende} Jahre alt. Betreuungskosten sind nur "
                f"bis zum {kb_cfg['alter_bis_jahre']}. Geburtstag abziehbar — nur den Teil des "
                "Jahres ansetzen.")

    # --- Sonderausgaben ----------------------------------------------------
    sonderausgaben = {}
    for kat in sorted(SONDERAUSGABEN):
        posten = [{"bezeichnung": b.get("bezeichnung"), "betrag_eur": netto(b),
                   "person": b.get("person")}
                  for b in belege if b.get("kategorie") == kat and aktiv(b)]
        if kat == "kirchensteuer":
            for pid, lohn in (daten.get("lohndaten") or {}).items():
                ks = float(lohn.get("kirchensteuer_eur") or 0)
                if ks:
                    posten.append({"bezeichnung": f"einbehaltene Kirchensteuer {pid}",
                                   "betrag_eur": round(ks, 2), "person": pid})
        if not posten:
            continue
        sonderausgaben[kat] = {
            "posten": posten,
            "summe_eur": round(sum(p["betrag_eur"] for p in posten), 2),
            "anlage": ANLAGE.get(kat, ("?", "?")),
        }
    if "versicherung_vorsorge" in sonderausgaben or "riester_ruerup" in sonderausgaben:
        sonderausgaben["_hinweis_vorsorge"] = (
            "Die Höchstbeträge für Vorsorgeaufwendungen rechnet das Steuerprogramm aus den "
            "Beiträgen und der Lohnsteuerbescheinigung. Hier werden nur die Belege gesammelt.")
    if "spende" in sonderausgaben:
        sonderausgaben["spende"]["hoechstanteil_einkuenfte"] = jr["spenden_hoechstanteil_einkuenfte"]

    # --- Außergewöhnliche Belastungen -------------------------------------
    agb_posten = [{"bezeichnung": b.get("bezeichnung"), "kategorie": b.get("kategorie"),
                   "betrag_eur": netto(b), "person": b.get("person")}
                  for b in belege if b.get("kategorie") in AUSSERGEWOEHNLICH and aktiv(b)]
    agb_summe = round(sum(p["betrag_eur"] for p in agb_posten), 2)

    gde = (daten.get("einkuenfte") or {}).get("gesamtbetrag_der_einkuenfte_eur")
    gde_geschaetzt = False
    if not gde:
        brutto = sum(float(l.get("bruttoarbeitslohn_eur") or 0)
                     for l in (daten.get("lohndaten") or {}).values())
        abzug_wk = sum(max(w["summe_eur"], w["arbeitnehmer_pauschbetrag_eur"])
                       for w in werbungskosten.values()) if werbungskosten else 0
        gde = max(0.0, brutto - abzug_wk)
        gde_geschaetzt = True

    zb = zumutbare_belastung(float(gde), len(kinder), veranlagung, konst)
    zb["geschaetzt"] = gde_geschaetzt
    wirksam = round(max(0.0, agb_summe - zb["betrag_eur"]), 2)
    agb = {
        "posten": agb_posten,
        "summe_eur": agb_summe,
        "zumutbare_belastung": zb,
        "wirksam_eur": wirksam,
        "fehlt_bis_wirksamkeit_eur": round(max(0.0, zb["betrag_eur"] - agb_summe), 2),
        "anlage": ANLAGE["krankheitskosten"],
    }
    if agb_summe > 0 and wirksam == 0:
        warnungen.append(
            f"Außergewöhnliche Belastungen: {eur(agb_summe)} liegen unter der zumutbaren Belastung "
            f"({eur(zb['betrag_eur'])}). Es fehlen {eur(agb['fehlt_bis_wirksamkeit_eur'])}. "
            "Entweder weitere selbst getragene Kosten suchen oder planbare Behandlungen in einem "
            "Jahr bündeln.")

    # --- Offene Punkte und Abgleich mit wiederkehrenden Posten -------------
    offen = list(daten.get("offen") or [])
    erfasste = {(b.get("bezeichnung") or "").lower() for b in belege}
    for w in (haushalt.get("wiederkehrend") or []):
        bez = (w.get("bezeichnung") or "")
        if bez and bez.lower() not in erfasste:
            offen.append({
                "was": bez,
                "warum": f"steht als wiederkehrender Posten in haushalt.yaml ({w.get('kategorie')}), "
                         f"typisch {eur(float(w.get('typisch_eur') or 0))}, im Jahr {jahr} nicht erfasst",
                "naechster_schritt": (f"Gmail nach from:{w['mail_absender']} durchsuchen"
                                      if w.get("mail_absender") else
                                      f"bei {w.get('anbieter') or 'Anbieter'} nachfordern"),
            })
    for b in belege:
        if (b.get("status") or "") in ("fehlt", "unklar"):
            offen.append({
                "was": b.get("bezeichnung"),
                "warum": f"Status '{b.get('status')}' in belege.json",
                "naechster_schritt": b.get("notiz") or "Beleg beschaffen bzw. Betrag klären",
            })

    ergebnis = {
        "schema": 1,
        "jahr": jahr,
        "erzeugt": dt.datetime.now().isoformat(timespec="seconds"),
        "rechtsstand": stand,
        "rechtsstand_unsicher": jr.get("unsicher", []),
        "neu_in_diesem_jahr": jr.get("neu_in_diesem_jahr", []),
        "ausblick": jr.get("ausblick", []),
        "fristen": jr.get("fristen", {}),
        "veranlagung": veranlagung,
        "werbungskosten": werbungskosten,
        "paragraph_35a": p35a,
        "kinder": kinder_ergebnis,
        "sonderausgaben": sonderausgaben,
        "aussergewoehnliche_belastungen": agb,
        "offene_punkte": offen,
        "warnungen": warnungen,
    }
    ziel = jd / "berechnung.json"
    ziel.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"geschrieben: {ziel}")
    print(f"Rechtsstand der Werte: {stand}")
    for w in warnungen:
        print(f"  ! {w}")
    return 0


# --------------------------------------------------------------------------- #
# dossier
# --------------------------------------------------------------------------- #

def cmd_dossier(args):
    root = basis(args)
    jahr = args.jahr
    jd = root / str(jahr)
    p = jd / "berechnung.json"
    if not p.exists():
        sys.exit(f"{p} fehlt. Zuerst 'steuer.py rechnen {jahr}' ausführen.")
    r = json.loads(p.read_text(encoding="utf-8"))
    gs = args.grenzsteuersatz

    L: list[str] = []
    a = L.append
    a(f"# Steuererklärung {jahr} — Dossier")
    a("")
    a(f"Erzeugt am {r['erzeugt'][:10]} · Veranlagung: **{r['veranlagung']}** · "
      f"Rechtsstand der Pauschalen: **{r['rechtsstand']}**")
    a("")
    fr = r.get("fristen") or {}
    if fr:
        a(f"Fristen: ohne Berater **{fr.get('ohne_berater','?')}**, "
          f"mit Berater {fr.get('mit_berater','?')}, "
          f"freiwillige Abgabe bis {fr.get('freiwillig_bis','?')}.")
        a("")
    if r.get("neu_in_diesem_jahr"):
        a(f"**Neu in {jahr}:**")
        for n in r["neu_in_diesem_jahr"]:
            a(f"- {n}")
        a("")

    # Zusammenfassung
    a("## 1. Auf einen Blick")
    a("")
    a("| Bereich | Betrag | Wirkung |")
    a("|---|---:|---|")
    for pid, w in (r.get("werbungskosten") or {}).items():
        ueber = w["ueber_pauschbetrag_eur"]
        wirkung = (f"{eur(ueber)} über dem Pauschbetrag" if ueber > 0
                   else f"wirkungslos, {eur(abs(ueber))} unter dem Pauschbetrag")
        a(f"| Werbungskosten {pid} | {eur(w['summe_eur'])} | {wirkung} |")
    p35 = r.get("paragraph_35a") or {}
    if p35.get("steuerermaessigung_gesamt_eur"):
        a(f"| Haushaltsnahe Aufwendungen (§ 35a) | "
          f"{eur(p35['steuerermaessigung_gesamt_eur'])} | direkter Steuerabzug, voll wirksam |")
    for k in (r.get("kinder") or []):
        if k["betreuung"]["abzug_eur"]:
            a(f"| Kinderbetreuung {k['name'] or k['id']} | "
              f"{eur(k['betreuung']['abzug_eur'])} | Sonderausgabe |")
        if k.get("schulgeld"):
            a(f"| Schulgeld {k['name'] or k['id']} | "
              f"{eur(k['schulgeld']['abzug_eur'])} | Sonderausgabe |")
    for kat, v in (r.get("sonderausgaben") or {}).items():
        if isinstance(v, dict) and v.get("summe_eur"):
            a(f"| {kat.replace('_', ' ').title()} | {eur(v['summe_eur'])} | Sonderausgabe |")
    agb = r.get("aussergewoehnliche_belastungen") or {}
    if agb.get("summe_eur"):
        a(f"| Außergewöhnliche Belastungen | {eur(agb['summe_eur'])} | "
          f"davon wirksam {eur(agb['wirksam_eur'])} |")
    a("")
    if gs:
        a(f"Grober Anhaltspunkt bei einem Grenzsteuersatz von {gs*100:.0f} %: ein Euro Abzug bringt "
          f"etwa {eur(gs)} zurück. § 35a wirkt dagegen in voller Höhe. Die tatsächliche Erstattung "
          "rechnet das Steuerprogramm.")
    else:
        a("Wie viel ein Abzugsbetrag zurückbringt, hängt vom Grenzsteuersatz ab (meist 25–45 %). "
          "§ 35a mindert dagegen direkt die Steuer, wirkt also in voller Höhe. Die genaue Erstattung "
          "rechnet das Steuerprogramm.")
    a("")

    # Werbungskosten
    a("## 2. Werbungskosten — Anlage N")
    for pid, w in (r.get("werbungskosten") or {}).items():
        f = w["fahrt_und_homeoffice"]
        t = w["arbeitstage"]
        a("")
        a(f"### {pid}")
        a("")
        a(f"Grundlage: **{t.get('buero_tage','?')} Bürotage**, "
          f"**{t.get('homeoffice_tage','?')} Homeoffice-Tage** "
          f"({t.get('grundlage','')}) — "
          f"{'bestätigt' if t.get('bestaetigt') else '**noch nicht bestätigt**'}.")
        a("")
        a("**Varianten Wege und Homeoffice**")
        a("")
        a("| Variante | Summe | Bedingung | geprüft |")
        a("|---|---:|---|---|")
        for v in f["varianten"]:
            marke = " ✅" if v["name"] == f["empfehlung"] else ""
            geprueft = {True: "ja", False: "trifft nicht zu", None: "**offen**"}[
                v["bedingung_erfuellt"]] if v["bedingung"] else "—"
            a(f"| {v['name']}{marke} | {eur(v['summe_eur'])} | {v['bedingung'] or '—'} | {geprueft} |")
        a("")
        for v in f["varianten"]:
            if v["name"] == f["empfehlung"]:
                a("Zusammensetzung der günstigsten Variante:")
                for po in v["posten"]:
                    a(f"- {po['bezeichnung']}: {eur(po['betrag_eur'])}")
                a("")
        if f.get("empfehlung_ungeprueft") and f["ohne_bedingung"]:
            diff = f["empfehlung_summe_eur"] - f["ohne_bedingung_summe_eur"]
            a(f"> Die günstigste Variante hängt an einer noch **nicht geprüften** Bedingung. "
              f"Trifft sie nicht zu, bleiben {eur(f['ohne_bedingung_summe_eur'])} — es geht also "
              f"um {eur(diff)}. Vor dem Ansetzen klären.")
            a("")
        if f.get("arbeitgeberzuschuss_abgezogen_eur"):
            a(f"> Vom Fahrtkostenbetrag wurden {eur(f['arbeitgeberzuschuss_abgezogen_eur'])} "
              "steuerfreier Arbeitgeberzuschuss abgezogen (§ 3 Nr. 15 EStG).")
            a("")
        for h in (f.get("hinweise") or []):
            a(f"> {h}")
            a("")
        if w["sonstige_werbungskosten"]:
            a("**Weitere Werbungskosten**")
            a("")
            a("| Position | Betrag | Abschnitt |")
            a("|---|---:|---|")
            for s in w["sonstige_werbungskosten"]:
                a(f"| {s['bezeichnung']} | {eur(s['betrag_eur'])} | {s['anlage'][1]} |")
            a(f"| **Summe** | **{eur(w['sonstige_summe_eur'])}** | |")
            a("")
        a(f"Summe Werbungskosten: **{eur(w['summe_eur'])}** gegen Arbeitnehmer-Pauschbetrag "
          f"{eur(w['arbeitnehmer_pauschbetrag_eur'])}.")
        if w["zusaetzlich_zum_pauschbetrag_eur"]:
            a(f"Davon {eur(w['zusaetzlich_zum_pauschbetrag_eur'])} Berufsverbandsbeiträge, die in "
              "diesem Jahr zusätzlich zum Pauschbetrag abziehbar sind.")
        a("")

    # § 35a
    if p35:
        a("## 3. Haushaltsnahe Aufwendungen — Anlage Haushaltsnahe Aufwendungen")
        a("")
        a("Diese Beträge mindern **direkt die Steuer**, unabhängig von allen Pauschbeträgen.")
        a("")
        a("| Art | Kosten | Satz | Ermäßigung | Höchstbetrag | ausgeschöpft |")
        a("|---|---:|---:|---:|---:|---:|")
        for kat in ("haushaltsnahe_dienstleistung", "handwerkerleistung", "minijob_im_haushalt"):
            v = p35.get(kat)
            if not isinstance(v, dict) or not v["grundlage_eur"]:
                continue
            a(f"| {kat.replace('_', ' ')} | {eur(v['grundlage_eur'])} | "
              f"{int(v['satz']*100)} % | {eur(v['steuerermaessigung_eur'])} | "
              f"{eur(v['hoechstbetrag_eur'])} | {v['ausschoepfung_prozent']:.0f} % |")
        a(f"| **Summe Steuerermäßigung** | | | **{eur(p35['steuerermaessigung_gesamt_eur'])}** | | |")
        a("")
        for kat in ("haushaltsnahe_dienstleistung", "handwerkerleistung", "minijob_im_haushalt"):
            v = p35.get(kat)
            if not isinstance(v, dict) or not v["posten"]:
                continue
            a(f"**{kat.replace('_', ' ')}**")
            a("")
            a("| Leistung | Anbieter | gezahlt am | anrechenbar |")
            a("|---|---|---|---:|")
            for po in v["posten"]:
                a(f"| {po['bezeichnung']} | {po.get('anbieter') or '—'} | "
                  f"{po.get('datum_zahlung') or '—'} | {eur(po['anrechenbar_eur'])} |")
            a("")

    # Kinder
    if r.get("kinder"):
        a("## 4. Kinder — je Kind eine Anlage Kind")
        for k in r["kinder"]:
            b = k["betreuung"]
            a("")
            a(f"### {k['name'] or k['id']} (am Jahresende {k['alter_jahresende']} Jahre)")
            a("")
            if b["positionen"]:
                a("| Position | anrechenbar | Quelle |")
                a("|---|---:|---|")
                for po in b["positionen"]:
                    a(f"| {po.get('einrichtung') or po.get('art')} | "
                      f"{eur(po['anrechenbar_eur'])} | {po.get('quelle')} |")
                a("")
            a(f"Betreuungskosten {eur(b['kosten_eur'])} × {int(b['anteil']*100)} % = "
              f"**{eur(b['abzug_eur'])}** (Höchstbetrag {eur(b['hoechstbetrag_eur'])}).")
            if b["kosten_eur"] < b["kosten_fuer_vollen_abzug_eur"]:
                luft = b["kosten_fuer_vollen_abzug_eur"] - b["kosten_eur"]
                a(f"Der Höchstbetrag wäre bei {eur(b['kosten_fuer_vollen_abzug_eur'])} Kosten "
                  f"erreicht — es sind noch {eur(luft)} Luft. Fehlt noch Ferienbetreuung, "
                  "Hort oder ein Babysitter mit Rechnung?")
            a("")
            if k.get("schulgeld"):
                s = k["schulgeld"]
                a(f"Schulgeld {eur(s['kosten_eur'])} × {int(s['anteil']*100)} % = "
                  f"**{eur(s['abzug_eur'])}** (Höchstbetrag {eur(s['hoechstbetrag_eur'])}), "
                  "Verpflegung und Betreuung herausgerechnet.")
                a("")

    # Sonderausgaben
    so = {k: v for k, v in (r.get("sonderausgaben") or {}).items() if isinstance(v, dict)}
    if so:
        a("## 5. Sonderausgaben")
        a("")
        a("| Position | Betrag | Anlage / Abschnitt |")
        a("|---|---:|---|")
        for kat, v in so.items():
            for po in v["posten"]:
                a(f"| {po['bezeichnung']} | {eur(po['betrag_eur'])} | "
                  f"{v['anlage'][0]} — {v['anlage'][1]} |")
        a("")
        if r["sonderausgaben"].get("_hinweis_vorsorge"):
            a(f"> {r['sonderausgaben']['_hinweis_vorsorge']}")
            a("")

    # AgB
    if agb.get("summe_eur"):
        zb = agb["zumutbare_belastung"]
        a("## 6. Außergewöhnliche Belastungen")
        a("")
        a("| Position | Betrag |")
        a("|---|---:|")
        for po in agb["posten"]:
            a(f"| {po['bezeichnung']} ({po['kategorie']}) | {eur(po['betrag_eur'])} |")
        a(f"| **Summe** | **{eur(agb['summe_eur'])}** |")
        a("")
        a(f"Zumutbare Belastung: **{eur(zb['betrag_eur'])}** "
          f"(Staffel *{zb['staffel']}*, Sätze {zb['saetze']}, stufenweise aus einem "
          f"Gesamtbetrag der Einkünfte von {eur(zb['grundlage_gde_eur'])}"
          f"{' — **geschätzt** aus dem Bruttolohn' if zb.get('geschaetzt') else ''}).")
        a("")
        if agb["wirksam_eur"]:
            a(f"Wirksam sind damit **{eur(agb['wirksam_eur'])}**.")
        else:
            a(f"Damit wirkt noch **nichts**: es fehlen {eur(agb['fehlt_bis_wirksamkeit_eur'])}.")
        a("")

    # Offene Punkte
    if r.get("offene_punkte"):
        a("## 7. Offene Punkte")
        a("")
        a("| Was fehlt | Warum | Nächster Schritt |")
        a("|---|---|---|")
        for o in r["offene_punkte"]:
            a(f"| {o.get('was')} | {o.get('warum')} | {o.get('naechster_schritt')} |")
        a("")

    if r.get("warnungen"):
        a("## 8. Hinweise aus der Berechnung")
        a("")
        for w in r["warnungen"]:
            a(f"- {w}")
        a("")

    a("## Annahmen und Grenzen")
    a("")
    a(f"- Pauschalen und Höchstbeträge mit Rechtsstand **{r['rechtsstand']}**.")
    if r.get("rechtsstand_unsicher"):
        a(f"- Noch zu prüfen: {', '.join(r['rechtsstand_unsicher'])}.")
    a("- Arbeitstage sind aus dem Wochenmuster geschätzt, nicht aus einem Kalender gezählt. "
      "Das Finanzamt darf einen Nachweis verlangen.")
    a("- Die Höchstbeträge für Vorsorgeaufwendungen und die tatsächliche Steuer rechnet das "
      "Steuerprogramm; dieses Dossier liefert die Eingabewerte.")
    a("- Keine Steuerberatung. Bei doppelter Haushaltsführung, Vermietung, Selbständigkeit, "
      "Auslandsbezug oder Trennung sollte ein Steuerberater draufschauen.")
    if r.get("ausblick"):
        a("")
        a("**Ausblick**")
        for x in r["ausblick"]:
            a(f"- {x}")

    ziel = jd / "dossier.md"
    ziel.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"geschrieben: {ziel}")
    return 0


# --------------------------------------------------------------------------- #
# init / jahr / arbeitstage / regeln
# --------------------------------------------------------------------------- #

def cmd_init(args):
    root = basis(args)
    root.mkdir(parents=True, exist_ok=True)
    ziel = root / "haushalt.yaml"
    if ziel.exists():
        print(f"{ziel} existiert bereits — nichts überschrieben.")
    else:
        shutil.copyfile(ASSETS / "haushalt.example.yaml", ziel)
        print(f"angelegt: {ziel}")
        print("Jetzt mit den echten Daten füllen. Die Beispielwerte sind Platzhalter.")
    print(f"Arbeitsverzeichnis: {root}")
    return 0


def cmd_jahr(args):
    root = basis(args)
    jahr = args.jahr
    jd = root / str(jahr)
    (jd / "belege").mkdir(parents=True, exist_ok=True)
    ziel = jd / "belege.json"
    if ziel.exists():
        print(f"{ziel} existiert bereits — nichts überschrieben.")
        return 0

    haushalt = lade_haushalt(root)
    hh = haushalt.get("haushalt") or {}
    land = hh.get("bundesland")

    arbeitstage = {}
    for p in (haushalt.get("personen") or []):
        muster = ((p.get("arbeitgeber") or [{}])[0]).get("arbeitstage_muster")
        arbeitstage[p["id"]] = arbeitstage_schaetzen(
            jahr, land, muster, args.urlaub, args.krank, args.sonstige)

    offen = []
    for w in (haushalt.get("wiederkehrend") or []):
        offen.append({
            "was": w.get("bezeichnung"),
            "warum": f"wiederkehrender Posten ({w.get('kategorie')}), typisch "
                     f"{w.get('typisch_eur')} €",
            "naechster_schritt": (f"Gmail nach from:{w['mail_absender']} durchsuchen"
                                  if w.get("mail_absender") else
                                  f"bei {w.get('anbieter') or 'Anbieter'} anfordern"),
        })

    daten = {
        "schema": 1,
        "jahr": jahr,
        "stand": dt.date.today().isoformat(),
        "veranlagung": hh.get("veranlagung"),
        "lohndaten": {p["id"]: {} for p in (haushalt.get("personen") or [])},
        "arbeitstage": arbeitstage,
        "einkuenfte": {
            "gesamtbetrag_der_einkuenfte_eur": None,
            "hinweis": "für die zumutbare Belastung; wenn leer, wird aus dem Bruttolohn geschätzt",
        },
        "belege": [],
        "offen": offen,
    }
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"angelegt: {ziel}")
    print(f"Belegordner: {jd / 'belege'}")
    print(f"{len(offen)} wiederkehrende Posten als offen vorgemerkt.")
    for pid, t in arbeitstage.items():
        print(f"  {pid}: {t['buero_tage']} Bürotage, {t['homeoffice_tage']} Homeoffice "
              f"(geschätzt, bitte bestätigen)")
    if not (args.urlaub or args.krank or args.sonstige):
        print("Hinweis: Urlaub und Krankheitstage sind noch NICHT abgezogen, die Tageszahlen sind "
              "daher zu hoch. Mit --urlaub/--krank/--sonstige neu rechnen "
              f"('steuer.py arbeitstage {jahr} --urlaub 30 --krank 5') und die Werte in "
              "belege.json eintragen.")
    return 0


def cmd_arbeitstage(args):
    root = basis(args)
    jahr = args.jahr
    land = args.bundesland
    muster = None
    if args.muster:
        werte = [x.strip() for x in args.muster.split(",")]
        muster = dict(zip(["mo", "di", "mi", "do", "fr"], werte))
    elif (root / "haushalt.yaml").exists() or (root / "haushalt.json").exists():
        haushalt = lade_haushalt(root)
        land = land or (haushalt.get("haushalt") or {}).get("bundesland")
        personen = haushalt.get("personen") or []
        person = next((p for p in personen if p["id"] == args.person), personen[0] if personen else {})
        muster = ((person.get("arbeitgeber") or [{}])[0]).get("arbeitstage_muster")

    erg = arbeitstage_schaetzen(jahr, land, muster, args.urlaub, args.krank, args.sonstige)
    print(json.dumps(erg, ensure_ascii=False, indent=2))
    print()
    print(f"Arbeitstage gesamt: {erg['arbeitstage_gesamt']}  "
          f"(Büro {erg['buero_tage']}, Homeoffice {erg['homeoffice_tage']})")
    print("Schätzung aus dem Wochenmuster. Vom Nutzer bestätigen lassen und in belege.json "
          "unter 'arbeitstage' mit \"bestaetigt\": true eintragen.")
    return 0


def cmd_regeln(args):
    jr, konst, stand = regeln_fuer(args.jahr)
    print(f"Rechtsstand der Datei: {stand}")
    if jr.get("unsicher"):
        print(f"UNGEPRÜFT für {args.jahr}: {', '.join(jr['unsicher'])}")
    print()
    print(json.dumps({"jahr": args.jahr, "werte": jr, "konstant": konst},
                     ensure_ascii=False, indent=2))
    heute = dt.date.today()
    if dt.date(args.jahr, 12, 31) >= heute:
        print()
        print(f"Das Steuerjahr {args.jahr} läuft noch. Jetzt sind die Punkte aus "
              "references/pruefliste.md, Abschnitt D, noch beeinflussbar — "
              "nach dem 31.12. nicht mehr.")
    return 0


# --------------------------------------------------------------------------- #

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Rechenwerk zur Vorbereitung der deutschen Einkommensteuererklärung")
    ap.add_argument("--pfad", help="Arbeitsverzeichnis (sonst $STEUER_PFAD oder ~/Documents/Steuer)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Arbeitsverzeichnis und haushalt.yaml anlegen")

    p = sub.add_parser("jahr", help="Steuerjahr anlegen")
    p.add_argument("jahr", type=int)
    p.add_argument("--urlaub", type=int, default=0)
    p.add_argument("--krank", type=int, default=0)
    p.add_argument("--sonstige", type=int, default=0, help="Fortbildung, Dienstreisen, Elternzeit")

    p = sub.add_parser("arbeitstage", help="Büro- und Homeoffice-Tage schätzen")
    p.add_argument("jahr", type=int)
    p.add_argument("--person", default=None)
    p.add_argument("--bundesland", default=None, help=f"eines von {', '.join(LAENDER)}")
    p.add_argument("--urlaub", type=int, default=0)
    p.add_argument("--krank", type=int, default=0)
    p.add_argument("--sonstige", type=int, default=0, help="Fortbildung, Dienstreisen, Elternzeit")
    p.add_argument("--muster", default=None,
                   help="Mo-Fr als Liste, z. B. buero,buero,homeoffice,buero,homeoffice")

    p = sub.add_parser("regeln", help="Pauschalen und Höchstbeträge des Jahres zeigen")
    p.add_argument("jahr", type=int)

    p = sub.add_parser("rechnen", help="Varianten und Höchstbeträge rechnen")
    p.add_argument("jahr", type=int)

    p = sub.add_parser("dossier", help="dossier.md erzeugen")
    p.add_argument("jahr", type=int)
    p.add_argument("--grenzsteuersatz", type=float, default=None,
                   help="z. B. 0.36, nur für eine grobe Wirkungsangabe")

    args = ap.parse_args(argv)
    return {
        "init": cmd_init, "jahr": cmd_jahr, "arbeitstage": cmd_arbeitstage,
        "regeln": cmd_regeln, "rechnen": cmd_rechnen, "dossier": cmd_dossier,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
