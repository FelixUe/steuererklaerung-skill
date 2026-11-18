# Steuererklärung — Claude-Skill für die deutsche Einkommensteuer

Jedes Jahr dasselbe: Belege aus Mails, Drive und Schuhkartons zusammensuchen, die Hälfte vergessen
und am Ende raten, welche Variante günstiger war. Dieser Skill dreht das um.

Was unveränderlich ist — wer zum Haushalt gehört, wo gearbeitet wird, welche Rechnungen jedes Jahr
wiederkommen — steht **einmal** in `haushalt.yaml`. Pro Steuerjahr wird nur noch eingesammelt,
gerechnet und geprüft. Das Ergebnis ist ein **Dossier**: eine Datei, die abschnittsweise die Zahlen
enthält, die ein Steuerprogramm abfragt, dazu die Varianten­rechnungen mit Empfehlung und eine Liste
dessen, was noch fehlt.

Die Abgabe macht man selbst, im eigenen Programm (CHECK24 Steuer, WISO, Taxfix, ELSTER). Der Skill
übermittelt nichts, füllt kein Portal aus und ist keine Steuerberatung.

## Was er abdeckt

- **Werbungskosten** — Entfernungspauschale, Homeoffice-Tagespauschale, Arbeitszimmer, Arbeitsmittel,
  Fortbildung, Reisekosten, Berufsverband, mit Variantenvergleich und Prüfung gegen den
  Arbeitnehmer-Pauschbetrag
- **Kinder und Familie** — Betreuungskosten, Schulgeld, Ausbildungsfreibetrag, Höchstbeträge und
  Haushaltszugehörigkeit
- **Haushalt und Handwerker** — § 35a mit Lohnanteil, Zahlungsart und Ausschöpfung der Höchstbeträge
- **Sonderausgaben und Vorsorge** — Kirchensteuer, Spenden, Versicherungen, Riester/Rürup
- **Außergewöhnliche Belastungen** — Krankheitskosten gegen die stufenweise zumutbare Belastung

## Woher die Daten kommen

Aus Gmail und Google Drive, über die Connectors von Claude, nach fertigen Suchrezepten pro
Kategorie. Die Dezember-Lohnabrechnung ist der Einstieg, weil sie die Jahreswerte kumuliert.
Der Skill liest nur: keine Mails senden, nichts löschen, nichts verschieben.

Ohne Connectors funktioniert er auch — dann wandern die Belege per Hand in `belege.json`, und das
Rechenwerk und die Prüflisten greifen genauso.

## Installation

Als Plugin, in zwei Schritten — das Repo ist gleichzeitig ein Marketplace:

```bash
claude plugin marketplace add FelixUe/steuererklaerung-skill
```

```bash
claude plugin install steuererklaerung@felixue-skills
```

In einer laufenden Sitzung gehen `/plugin marketplace add FelixUe/steuererklaerung-skill` und
`/plugin install steuererklaerung@felixue-skills` genauso.

Oder, ohne Plugin-Mechanik, einfach den Skill-Ordner kopieren:

```bash
cp -r plugins/steuererklaerung/skills/steuererklaerung ~/.claude/skills/
```

Danach zieht der Skill von selbst, sobald es um Steuererklärung, Belege oder Werbungskosten geht.
Ausdrücklich aufrufen kann man ihn als `/steuererklaerung` (kopierter Ordner) bzw.
`/steuererklaerung:steuererklaerung` (als Plugin — Plugin-Skills tragen den Plugin-Namen als Präfix).

## Nutzung

```bash
python scripts/steuer.py init          # Arbeitsverzeichnis + haushalt.yaml anlegen
python scripts/steuer.py jahr 2026     # Steuerjahr anlegen, wiederkehrende Posten vormerken
python scripts/steuer.py rechnen 2026  # Varianten und Höchstbeträge rechnen
python scripts/steuer.py dossier 2026  # dossier.md erzeugen
```

Das Skript liegt in `plugins/steuererklaerung/skills/steuererklaerung/scripts/`; die Befehle oben
gelten relativ zum Skill-Ordner.

Im Alltag ruft man das nicht selbst auf — man sagt Claude, dass die Steuererklärung dran ist, und
beantwortet Fragen. Weitere Unterkommandos: `arbeitstage` (Büro- und Homeoffice-Tage aus dem
Wochenmuster und den Feiertagen des Bundeslands schätzen) und `regeln` (Pauschalen und Rechtsstand
eines Jahres zeigen).

Python 3.9+, keine Abhängigkeiten. PyYAML wird benutzt, wenn vorhanden; sonst greift ein
mitgelieferter YAML-Leser für die Struktur der Vorlage.

## Wo die Daten liegen

Standardmäßig unter `~/Documents/Steuer`, überschreibbar mit `STEUER_PFAD` oder `--pfad`:

```
~/Documents/Steuer/
├── haushalt.yaml          # Stammdaten, einmal angelegt
└── 2026/
    ├── belege.json        # Positionen des Jahres
    ├── belege/            # die PDFs
    ├── berechnung.json
    └── dossier.md
```

**Nichts davon gehört in ein Repo.** Das Arbeitsverzeichnis liegt außerhalb, und die `.gitignore`
dieses Repos schließt `haushalt.yaml`, `belege.json`, Jahresordner und PDFs zusätzlich hart aus.

## Rechtsstand

Pauschalen, Höchstbeträge und Fristen stehen versioniert in
`plugins/steuererklaerung/skills/steuererklaerung/assets/steuerrecht.json`, mit `stand`-Datum,
Quellenliste und einer `unsicher`-Liste je Jahr für Werte, die noch zu prüfen sind. Abgedeckt sind
2023 bis 2026.

Der Stand ist **2026-11-18** und stammt aus öffentlichen Steuerportalen, nicht aus amtlichen
Quellen. Der Skill ist angewiesen, das Datum zu prüfen und bei älterem Stand nachzurecherchieren,
statt veraltete Zahlen als Fakt zu verkaufen. Wer die Datei aktualisiert, trägt das neue `stand`
ein — Pull Requests dafür sind willkommen.

## Tests

Drei Testfälle mit Eingabedaten und geprüften Sollwerten: Variantenvergleich Fahrt gegen Homeoffice,
Formfehler bei Handwerkerrechnungen (Barzahlung, fehlender Lohnanteil), und die zumutbare Belastung
bei Krankheitskosten.

```bash
claude plugin eval plugins/steuererklaerung/skills/steuererklaerung --allow-tools Write,Edit,Bash --scaffold
```

Das sind echte, kostenpflichtige Modellläufe. Die Manifeste prüft man ohne Kosten mit:

```bash
claude plugin validate .
```

## Haftung

Kein Steuerberatungsangebot und keine Gewähr für die Richtigkeit der Beträge. Bei doppelter
Haushaltsführung, Vermietung, Selbständigkeit, Auslandsbezug, Erbschaft oder Trennung sollte ein
Steuerberater draufschauen — der Skill bereitet die Unterlagen dann so vor, dass dessen Zeit nicht
fürs Sortieren draufgeht.

## Lizenz

MIT, siehe [LICENSE](LICENSE).
