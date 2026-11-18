# Dezemberabrechnung und Lohnsteuerbescheinigung auswerten

Die Dezember-Lohnabrechnung ist der beste erste Griff: sie zeigt die Jahreswerte kumuliert und ist
inhaltlich fast deckungsgleich mit der elektronischen Lohnsteuerbescheinigung, die der Arbeitgeber im
Februar ans Finanzamt meldet. Wer sie liest, hat die Hälfte der Erklärung schon beisammen — und
findet die Posten, die *andere* Positionen kürzen.

Die Bescheinigung selbst kommt meist erst im Februar; sie geht elektronisch ans Finanzamt und wird in
Steuerprogrammen oft automatisch vorbefüllt (vorausgefüllte Steuererklärung / Belegabruf). Trotzdem
lohnt der Blick auf das Papier: die Vorbefüllung ist nicht immer vollständig, und manches muss man
kennen, um es nicht zu übersehen.

## Hinweis zur Nummerierung

Die Nummerierung der Lohnsteuerbescheinigung ändert sich über die Jahre. Verlass dich auf die
**Beschriftung** der Zeile, nicht auf eine Nummer aus dem Gedächtnis. Stabil sind die vorderen
Nummern (1–6) und die Großbuchstaben. Bei allem anderen: lies das Label auf dem Dokument.

## Was man herausliest, und wozu

| Zeile / Feld | Wozu man den Wert braucht |
|---|---|
| **Nr. 3 — Bruttoarbeitslohn** | Grundlage für die zumutbare Belastung bei außergewöhnlichen Belastungen und für die Plausibilität der ganzen Erklärung. Ohne diesen Wert lässt sich nicht sagen, ob Krankheitskosten überhaupt wirken. |
| **Nr. 4 — einbehaltene Lohnsteuer** | Die Zahl, gegen die die Erstattung läuft. Mehr als das kann nicht zurückkommen (plus Soli und Kirchensteuer). |
| **Nr. 5 — Solidaritätszuschlag** | Teil der Erstattungsgrundlage. |
| **Nr. 6 — einbehaltene Kirchensteuer** | **Sonderausgabe.** Gezahlte Kirchensteuer minus im selben Jahr erstattete Kirchensteuer ist voll abziehbar und wird häufig vergessen. |
| **Zeitraum / Nr. 1** | Teilzeitbeschäftigung im Jahr? Dann sind Arbeitstage und Pauschalen zu kürzen. Mehrere Arbeitgeber heißt: mehrere Bescheinigungen, und ein Pflichtveranlagungsgrund. |
| **Steuerfreie Arbeitgeberleistungen für Fahrten Wohnung ↔ erste Tätigkeitsstätte (§ 3 Nr. 15)** | **Kürzt die Entfernungspauschale.** Jobticket, Deutschlandticket-Zuschuss, Fahrtkostenzuschuss. Steht ein Betrag hier, muss er in `belege.json` als `jobticket_zuschuss_eur` landen. |
| **Pauschal besteuerte Arbeitgeberleistungen für diese Fahrten (§ 40 Abs. 2)** | Kürzt die Entfernungspauschale ebenfalls. |
| **Steuerfreie Verpflegungszuschüsse bei Auswärtstätigkeit** | Kürzen die Verpflegungspauschalen, die man selbst ansetzt. |
| **Steuerfreie Arbeitgeberleistungen bei doppelter Haushaltsführung** | Kürzen den entsprechenden Werbungskostenabzug. |
| **Arbeitnehmeranteile Renten-, Kranken-, Pflege-, Arbeitslosenversicherung** | Vorsorgeaufwendungen. Werden in Steuerprogrammen meist übernommen; dennoch prüfen, ob sie vollständig drin sind. |
| **Nachgewiesene Beiträge zur privaten Kranken-/Pflegeversicherung** | Dito, bei privat Versicherten der größere Posten. |
| **Vermögenswirksame Leistungen / betriebliche Altersversorgung** | Eigenanteil kann relevant sein (Arbeitnehmer-Sparzulage, Riester-Zusatz). |
| **Zahl der Kinderfreibeträge** | Plausibilitätsprüfung gegen `haushalt.yaml`: stimmt die Zahl der Kinder und die Aufteilung? |
| **Lohnsteuerabzugsmerkmale / eingetragener Freibetrag** | Hat der Arbeitgeber schon einen Freibetrag berücksichtigt (Lohnsteuer-Ermäßigung)? Dann ist die Erstattung kleiner — und es besteht Pflicht zur Abgabe. |

## Die Großbuchstaben

Sie stehen in einer eigenen Zeile und sind leicht zu überlesen, verändern aber die Rechnung:

- **U** — Unterbrechung des Anspruchs auf Arbeitslohn (unbezahlter Urlaub, Krankengeld über die
  Lohnfortzahlung hinaus). Zahl dahinter = Anzahl der Unterbrechungen. Relevant für Arbeitstage und
  für den Progressionsvorbehalt bei Lohnersatzleistungen.
- **S** — sonstiger Bezug aus einem früheren Dienstverhältnis, nach Jahrestabelle besteuert. Deutet
  oft auf eine Abfindung oder Nachzahlung hin; die Fünftelregelung sollte geprüft werden.
- **M** — der Arbeitgeber hat Mahlzeiten gestellt. **Kürzt die Verpflegungspauschalen** bei
  Dienstreisen (20 % für Frühstück, je 40 % für Mittag und Abendessen vom Tagessatz).
- **F** — steuerfreie Sammelbeförderung durch den Arbeitgeber. Schließt die Entfernungspauschale für
  diese Strecke aus.
- **FR** — Grenzgängerregelung Frankreich.

## Lohnersatzleistungen

Elterngeld, Krankengeld, Kurzarbeitergeld, Arbeitslosengeld und Mutterschaftsgeld sind steuerfrei,
unterliegen aber dem **Progressionsvorbehalt**: sie erhöhen den Steuersatz auf das übrige Einkommen.
Ab 410 € im Jahr besteht deshalb **Pflicht zur Abgabe** einer Steuererklärung — und das Ergebnis kann
eine Nachzahlung sein. Diese Leistungen kommen nicht vom Arbeitgeber, sondern per separater
Bescheinigung von Krankenkasse, Agentur für Arbeit oder Elterngeldstelle. Sie gehören auf die
Beschaffungsliste, sobald im Jahr eine Elternzeit, längere Krankheit oder Kurzarbeit lag.

## Was nach dem Lesen in `belege.json` gehört

Lege die Werte unter `lohndaten` ab, pro Person:

```json
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
}
```

Beträge, die man nicht sicher lesen kann, lieber als `null` lassen und auf die Beschaffungsliste
setzen, als zu raten. Ein falscher Bruttolohn verfälscht die zumutbare Belastung und damit die
Empfehlung zu den Krankheitskosten.
