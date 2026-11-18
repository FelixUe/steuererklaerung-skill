# Stammdaten: `haushalt.yaml` anlegen und pflegen

Diese Datei ist der Grund, warum die Steuererklärung ab dem zweiten Jahr schnell geht. Alles, was
sich nicht jährlich ändert, steht hier. Vorlage: `assets/haushalt.example.yaml`.

## Wie das Gespräch laufen sollte

Nicht als Formular abfragen. Erschließe erst, frage dann — und frage in Blöcken, damit der Nutzer
nicht dreißig Einzelfragen beantworten muss.

1. **Erschließen.** Schau zuerst in Gmail und Drive: Arbeitgeber, Kita, Hausverwaltung, Versicherungen,
   Spendenempfänger stehen in den Mails der letzten zwei Jahre. Wenn ein Steuerbescheid oder eine
   alte Erklärung in Drive liegt, ist das die beste Quelle überhaupt — daraus lassen sich Finanzamt,
   Veranlagungsart, Kinder und die Posten des Vorjahres direkt übernehmen.
2. **Zusammengefasst vorlegen.** "Ich habe Folgendes gefunden: … Stimmt das, und was fehlt?"
3. **Gezielt nachfragen**, und zwar nur nach dem, was wirklich zählt (siehe unten).
4. **Schreiben, dann zeigen.** Datei anlegen, Inhalt zusammenfassen, bestätigen lassen.

## Die Felder, bei denen Genauigkeit Geld wert ist

**`entfernung_km`** — einfache Entfernung Wohnung ↔ erste Tätigkeitsstätte, **kürzeste
Straßenverbindung**, nicht Hin- und Rückweg, nicht die gefahrene Route. Auf ganze Kilometer
abgerundet, wenn das Finanzamt streng rechnet. Ein Kilometer zu viel sind bei 220 Tagen rund 84 € —
ein Kilometer zu wenig genauso.

**`entfernung_km_verkehrsguenstig`** — eine längere Strecke darf angesetzt werden, wenn sie
*offensichtlich verkehrsgünstiger* ist und regelmäßig benutzt wird. Das ist eine der am häufigsten
verschenkten Positionen. Nimm die Begründung gleich mit auf (`verkehrsguenstig_begruendet`), denn
danach wird im Zweifel gefragt. "Autobahn statt Ortsdurchfahrten, regelmäßig 15 Minuten schneller"
reicht; "ist schöner" nicht.

**`arbeitstage_muster`** — Büro oder Homeoffice pro Wochentag. Grundlage der Tageschätzung. Wenn das
Muster über das Jahr gewechselt hat (neuer Job, neue Regelung), notiere beide Zeiträume im Feld
`hinweis` und rechne das Jahr geteilt.

**`jobticket_arbeitgeber`** und **`oepnv_kosten_jaehrlich`** — ein steuerfreier Fahrtkostenzuschuss
oder ein Jobticket nach § 3 Nr. 15 EStG **kürzt die Entfernungspauschale**. Das wird oft übersehen
und fällt bei einer Prüfung auf, weil der Betrag in der Lohnsteuerbescheinigung steht. Bei ÖPNV
dürfen umgekehrt die tatsächlichen Kosten angesetzt werden, wenn sie über der Pauschale liegen.

**`kein_anderer_arbeitsplatz`** — `true` nur, wenn der Arbeitgeber dauerhaft keinen Schreibtisch für
diese Person bereitstellt. Dann darf die Tagespauschale auch für Tage angesetzt werden, an denen man
zusätzlich zur Tätigkeitsstätte gefahren ist — bei 200 Arbeitstagen ein vierstelliger Unterschied.
Solange das Feld `null` ist, rechnet das Skript diese Variante **nicht** mit, nennt sie aber als
Hinweis. Setze es nur auf `true`, wenn der Arbeitgeber das bescheinigen kann; eine falsche Angabe
kostet mehr, als sie bringt.

**`arbeitszimmer.mittelpunkt`** — nur `true`, wenn der *qualitative* Mittelpunkt der gesamten
Tätigkeit dort liegt. Bei Angestellten, die auch ins Büro fahren, ist das praktisch nie der Fall.
Ein falsches `true` führt zu einer Nachfrage und am Ende zur Streichung. Wenn unklar: `false`
setzen und die Tagespauschale nehmen.

**`kinder[].haushaltszugehoerig`** — harte Voraussetzung für den Abzug von Kinderbetreuungskosten.
Ohne Haushaltszugehörigkeit kein Abzug, egal wer zahlt.

**`betreuung[].verpflegungsanteil_monatlich`** — Essensgeld ist **nicht** abziehbar und muss aus dem
Kita-Beitrag herausgerechnet werden. Die meisten Bescheide weisen es getrennt aus; wenn nicht, ist das
eine Frage an die Einrichtung.

**`betreuung[].arbeitgeberzuschuss_monatlich`** — steuerfreie Kinderbetreuungszuschüsse des
Arbeitgebers mindern die abziehbaren Kosten.

## `wiederkehrend`: die eigentliche Arbeitsersparnis

Jede Rechnung, die jährlich wiederkommt, bekommt hier einen Eintrag mit Kategorie, Anbieter,
Absender-Mailadresse und typischem Betrag. In Phase 2 wird gegen diese Liste abgeglichen: Was hier
steht und im Steuerjahr nicht aufgetaucht ist, landet als offener Punkt im Dossier.

Das ist der Unterschied zwischen "ich habe gesammelt, was mir eingefallen ist" und "ich weiß, was
fehlt". Pflege die Liste jedes Jahr nach: taucht ein neuer Posten auf, gehört er hier hinein, auch
wenn er dieses Jahr schon erfasst ist.

Nützlich sind auch Posten, die man leicht vergisst, weil keine Rechnung kommt:

- Telefon- und Internetanteil (pauschal 20 %, max. 20 €/Monat)
- Kontoführungsgebühren (pauschal 16 €/Jahr)
- Gewerkschafts- oder Berufsverbandsbeitrag (ab 2026 zusätzlich zum Arbeitnehmer-Pauschbetrag)
- der § 35a-Anteil aus der Nebenkostenabrechnung (bei Mietern wie bei Eigentümern)
- Arbeitsmittel unter der Sofortabzugsgrenze, die über das Jahr verstreut gekauft wurden

## `erfahrungen`: was das Finanzamt gesagt hat

Jede Streichung, jede Nachfrage, jede anerkannte Begründung gehört hier hinein, mit Jahr. Das
verhindert, dass derselbe Punkt zweimal strittig wird, und es erklärt dem Skill im nächsten Jahr,
warum eine Position bewusst nicht angesetzt wird.

## Was nicht hineingehört

Keine Passwörter, keine Zugangsdaten zu ELSTER oder Steuerprogrammen, keine IBAN, keine
Kreditkartennummern. Steuer-Identifikationsnummern sind in Ordnung, wenn der Nutzer sie dort haben
will — die Datei bleibt lokal und steht in `.gitignore`. Frage einmal nach, bevor du eine Steuer-ID
hineinschreibst.

## Jährliche Pflege

Zu Beginn jedes Steuerjahres einmal durchgehen und `stand` aktualisieren. Die Fragen, die sich
lohnen:

- Hat sich die Wohnadresse, der Arbeitgeber oder die Tätigkeitsstätte geändert?
- Hat sich das Homeoffice-Muster geändert?
- Neues Kind, Kind aus der Betreuung herausgewachsen, Kind in die Schule gewechselt?
- Heirat, Trennung, Konfessionswechsel? Das ändert die Veranlagung und die Kirchensteuer.
- Neue wiederkehrende Rechnung, die in die Liste gehört?
- Steht im letzten Bescheid etwas, das in `erfahrungen` gehört?
