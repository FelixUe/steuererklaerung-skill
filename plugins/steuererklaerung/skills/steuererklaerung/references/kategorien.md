# Belegschema, Kategorien und Zuordnung

## Inhalt

1. Schema von `belege.json`
2. Kategorienkatalog mit Zuordnung zu ELSTER-Anlagen
3. Regeln, die je Kategorie zu beachten sind
4. Hinweis zu Zeilennummern

---

## 1. Schema von `belege.json`

Eine Datei pro Steuerjahr, unter `<arbeitsverzeichnis>/<jahr>/belege.json`.

```json
{
  "schema": 1,
  "jahr": 2025,
  "stand": "2026-11-18",
  "veranlagung": "zusammen",

  "lohndaten": {
    "felix": {
      "arbeitgeber": "Muster GmbH",
      "zeitraum": "2025-01-01 bis 2025-12-31",
      "bruttoarbeitslohn_eur": 68400.00,
      "lohnsteuer_eur": 13120.00,
      "soli_eur": 0.00,
      "kirchensteuer_eur": 1180.80,
      "jobticket_zuschuss_eur": 0.00,
      "verpflegungszuschuss_eur": 0.00,
      "grossbuchstaben": ["M"],
      "kinderfreibetraege": 2.0,
      "quelle": "Drive: Finanzen/Lohnabrechnungen/Lohnabrechnung_2025_12.pdf"
    }
  },

  "arbeitstage": {
    "felix": {
      "arbeitstage_gesamt": 215,
      "buero_tage": 129,
      "homeoffice_tage": 86,
      "grundlage": "Muster 3 Bürotage / 2 Homeoffice aus haushalt.yaml, minus 30 Urlaub und 5 Krankheitstage",
      "bestaetigt": false
    }
  },

  "einkuenfte": {
    "gesamtbetrag_der_einkuenfte_eur": null,
    "hinweis": "für die zumutbare Belastung; wenn unbekannt, wird aus dem Bruttolohn geschätzt"
  },

  "belege": [
    {
      "id": "2025-035",
      "person": "felix",
      "kategorie": "handwerkerleistung",
      "bezeichnung": "Heizungswartung",
      "anbieter": "Sanitär Schmidt GmbH",
      "datum_rechnung": "2025-04-12",
      "datum_zahlung": "2025-04-20",
      "betrag_brutto_eur": 480.00,
      "lohnanteil_eur": 180.00,
      "beruflicher_anteil_prozent": null,
      "erstattung_eur": 0.00,
      "zahlungsart": "ueberweisung",
      "quelle": { "typ": "gmail", "ref": "Rechnung 2025-0412 Sanitär Schmidt", "datum": "2025-04-12" },
      "datei": "belege/2025-04-12_heizungswartung.pdf",
      "status": "bestaetigt",
      "notiz": ""
    }
  ],

  "offen": [
    {
      "was": "Zuwendungsbestätigung Hilfswerk e.V. 2025",
      "warum": "Dauerspende 240 € steht auf dem Konto, Bescheinigung fehlt",
      "naechster_schritt": "kommt üblicherweise im Januar; Postfach Ende Januar erneut durchsuchen"
    }
  ]
}
```

### Feldbedeutungen

| Feld | Bedeutung |
|---|---|
| `person` | `id` aus `haushalt.yaml`, oder `haushalt` für Posten, die niemandem einzeln zuzuordnen sind (§ 35a, Nebenkosten) |
| `datum_zahlung` | **wichtiger als `datum_rechnung`** — bestimmt bei § 35a und Sonderausgaben das Steuerjahr |
| `betrag_brutto_eur` | der gezahlte Gesamtbetrag |
| `lohnanteil_eur` | nur bei § 35a: der Arbeits-, Fahrt- und Maschinenkostenanteil inkl. darauf entfallender USt. Material zählt nicht. `null`, wenn die Rechnung ihn nicht ausweist — dann ist der Posten noch nicht verwendbar |
| `beruflicher_anteil_prozent` | bei gemischt genutzten Arbeitsmitteln (Laptop 70 % beruflich) |
| `erstattung_eur` | von Kasse, Arbeitgeber oder Versicherung Erstattetes; mindert den Abzug |
| `zahlungsart` | `ueberweisung`, `karte`, `lastschrift`, `bar`. **Bar schließt § 35a aus** |
| `status` | `bestaetigt` (Beleg liegt vor), `unklar` (Betrag oder Zuordnung offen), `fehlt` (Beleg fehlt noch) |

---

## 2. Kategorienkatalog

Die Spalte "Anlage" nennt die ELSTER-Anlage und den Abschnitt. Steuerprogramme fragen die Posten in
ähnlicher Reihenfolge ab, auch wenn sie andere Worte benutzen.

### Werbungskosten — Anlage N

| Kategorie | Abschnitt in Anlage N | Kernregel |
|---|---|---|
| `fahrt_arbeit` | Wege zwischen Wohnung und erster Tätigkeitsstätte | Entfernungspauschale je Entfernungskilometer und Arbeitstag; Zuschüsse des Arbeitgebers kürzen |
| `homeoffice` | Häusliches Arbeitszimmer / Tagespauschale | 6 €/Tag, max. 210 Tage; nur für Tage ohne Weg zur Tätigkeitsstätte |
| `arbeitszimmer` | Häusliches Arbeitszimmer | Jahrespauschale oder tatsächliche Kosten, nur bei Tätigkeitsmittelpunkt |
| `arbeitsmittel` | Arbeitsmittel | bis zur Sofortabzugsgrenze voll, darüber Abschreibung; Computer und Software 1 Jahr |
| `fortbildung` | Fortbildungskosten | Kurs, Fahrt, Unterkunft, Verpflegungspauschale, Material |
| `berufsverband` | Beiträge zu Berufsverbänden | Gewerkschaft, Kammer, Berufsverband |
| `reisekosten` | Reisekosten bei Auswärtstätigkeit | Fahrtkosten 0,30 €/km tatsächlich gefahren, Verpflegungspauschalen, Übernachtung; Mahlzeiten des Arbeitgebers kürzen |
| `doppelte_haushaltsfuehrung` | Doppelte Haushaltsführung | Unterkunft max. 1.000 €/Monat, eine Familienheimfahrt pro Woche |
| `bewerbung` | Weitere Werbungskosten | Fahrten, Porto, Beglaubigungen, Fotos |
| `kontofuehrung` | Weitere Werbungskosten | pauschal 16 €/Jahr ohne Nachweis |
| `telefon_internet` | Weitere Werbungskosten | pauschal 20 %, max. 20 €/Monat |
| `umzug_beruflich` | Umzugskosten | nur bei beruflichem Anlass; Pauschale plus nachgewiesene Kosten |
| `arbeitskleidung` | Arbeitsmittel | nur typische Berufskleidung, keine Alltagskleidung; Reinigung anteilig |
| `steuerberatung_werbungskosten` | Weitere Werbungskosten | nur der Anteil, der auf die Einkünfteermittlung entfällt |

### Sonderausgaben — Anlage Sonderausgaben und Anlage Vorsorgeaufwand

| Kategorie | Anlage | Kernregel |
|---|---|---|
| `kirchensteuer` | Sonderausgaben | gezahlte minus erstattete Kirchensteuer, voll abziehbar; nicht die Kirchensteuer auf Kapitalerträge |
| `spende` | Sonderausgaben | bis 20 % des Gesamtbetrags der Einkünfte; bis 300 € je Spende genügt der Zahlungsnachweis |
| `parteibeitrag` | Sonderausgaben | 50 % direkt von der Steuer, max. 825 €; darüber als Sonderausgabe |
| `versicherung_vorsorge` | Vorsorgeaufwand | Basisversorgung und sonstige Vorsorge getrennt; Höchstbeträge rechnet das Programm |
| `riester_ruerup` | Vorsorgeaufwand / Anlage AV | Zulagen nicht vergessen |
| `unterhalt_ex_partner` | Sonderausgaben / Anlage U | nur mit Zustimmung des Empfängers |
| `eigene_berufsausbildung` | Sonderausgaben | Erstausbildung bis 6.000 €; Zweitausbildung dagegen Werbungskosten |

### Kinder — Anlage Kind, je Kind eine Anlage

| Kategorie | Abschnitt | Kernregel |
|---|---|---|
| `kinderbetreuung` | Kinderbetreuungskosten | ab 2025 80 % der Kosten, max. 4.800 € je Kind; bis 2024 zwei Drittel, max. 4.000 €. Kind muss zum Haushalt gehören, Alter bis unter 14. **Verpflegung zählt nicht.** Überweisung erforderlich |
| `schulgeld` | Schulgeld | 30 %, max. 5.000 € je Kind; nur anerkannte Ersatz- oder Ergänzungsschulen, ohne Verpflegung und Betreuung |
| `kind_ausbildung` | Auswärtige Unterbringung | Freibetrag 924 € bei auswärtiger Unterbringung eines volljährigen Kindes in Ausbildung |
| `kind_versicherung` | Beiträge | Kranken- und Pflegeversicherung des Kindes, wenn die Eltern sie tragen |
| `entlastungsbetrag_alleinerziehende` | Entlastungsbetrag | nur bei echtem Alleinstehen mit Kind im Haushalt |

### Haushaltsnahe Aufwendungen — Anlage Haushaltsnahe Aufwendungen (§ 35a EStG)

Hier wird nicht das Einkommen gemindert, sondern **direkt die Steuer**. Deshalb wirken diese Posten
auch dann, wenn Werbungskosten unter dem Pauschbetrag bleiben — und sie sind oft der größte Hebel.

| Kategorie | Satz / Höchstbetrag | Kernregel |
|---|---|---|
| `haushaltsnahe_dienstleistung` | 20 %, max. 4.000 € | Reinigung, Garten, Winterdienst, Schornsteinfeger, Pflege, Tierbetreuung im Haushalt; auch der ausgewiesene Anteil der Nebenkosten- oder Hausgeldabrechnung |
| `handwerkerleistung` | 20 %, max. 1.200 € | nur Arbeits-, Fahrt- und Maschinenkosten, kein Material; Renovierung und Erhaltung, **nicht Neubau** |
| `minijob_im_haushalt` | 20 %, max. 510 € | haushaltsnahes Beschäftigungsverhältnis auf Minijob-Basis, über die Minijob-Zentrale angemeldet |

Zwei Voraussetzungen gelten ohne Ausnahme: **Rechnung** und **Zahlung per Überweisung**. Bargeld
schließt den Abzug aus, auch bei vorliegender Rechnung.

Die Höchstbeträge gelten pro Haushalt und Jahr, nicht pro Person. Handwerkerleistungen und
haushaltsnahe Dienstleistungen haben getrennte Höchstbeträge und dürfen beide voll ausgeschöpft
werden.

### Außergewöhnliche Belastungen — Anlage Außergewöhnliche Belastungen

| Kategorie | Kernregel |
|---|---|
| `krankheitskosten` | nur selbst getragene Kosten; wirken erst oberhalb der zumutbaren Belastung. Rezeptgebühren, Zuzahlungen, Zahnersatz, Brille, Physiotherapie, Fahrten zum Arzt |
| `behinderung` | Pauschbetrag nach Grad der Behinderung, oder tatsächliche Kosten |
| `pflegekosten` | Pflegedienst, Pflegeheim; Pflege-Pauschbetrag für unentgeltliche Pflege von Angehörigen |
| `bestattungskosten` | soweit sie den Nachlass übersteigen |
| `kur` | nur mit vorheriger ärztlicher Verordnung |

Weil hier eine Selbstbehaltsschwelle gilt, lohnt es sich, planbare Kosten in **einem** Jahr zu
bündeln. Zwei Jahre mit je 1.500 € bringen oft nichts, ein Jahr mit 3.000 € dagegen schon.

### Weitere Anlagen

| Kategorie | Anlage |
|---|---|
| `kapitalertraege` | Anlage KAP; lohnt bei Günstigerprüfung, nicht ausgeschöpftem Sparer-Pauschbetrag oder Verlustverrechnung über Banken hinweg |
| `vermietung` | Anlage V |
| `selbstaendig` | Anlage S mit EÜR |
| `lohnersatzleistung` | Anlage N, Abschnitt Lohnersatzleistungen; steuerfrei, aber Progressionsvorbehalt — ab 410 € besteht Abgabepflicht |
| `rente` | Anlage R |

---

## 3. Hinweis zu Zeilennummern

Die **Zeilennummern** der ELSTER-Formulare ändern sich von Jahr zu Jahr; eine Nummer aus dem
Gedächtnis ist häufiger falsch als richtig. Nenne deshalb Anlage und Abschnittsbezeichnung — danach
findet man das Feld in jedem Programm und in jedem Jahr. Wenn der Nutzer eine exakte Zeile braucht,
schau sie im Formular des betreffenden Jahres nach, statt sie zu schätzen.
