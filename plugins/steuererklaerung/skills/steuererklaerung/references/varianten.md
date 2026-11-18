# Varianten und Wahlrechte

Das Steuerrecht lässt an mehreren Stellen eine Wahl. Die Wahl ist rechnerisch entscheidbar — und
genau dafür ist `scripts/steuer.py rechnen` da. Diese Datei erklärt, *warum* die Varianten so
gerechnet werden, damit sich das Ergebnis dem Nutzer erklären lässt.

## Fahrtkosten und Homeoffice

Das ist bei Angestellten mit Mischarbeit fast immer der größte Posten, und hier wird am häufigsten
Geld verschenkt.

### Die drei Instrumente

**Entfernungspauschale.** Je **Entfernungs**kilometer (einfache Strecke, nicht hin und zurück) und je
Arbeitstag, an dem man zur ersten Tätigkeitsstätte gefahren ist. Bis 2025 gestaffelt: 0,30 € für die
ersten 20 km, 0,38 € ab dem 21. Kilometer. Ab 2026 einheitlich 0,38 € ab dem ersten Kilometer.
Maßgeblich ist die kürzeste Straßenverbindung, unabhängig vom benutzten Verkehrsmittel.

**Tagespauschale (Homeoffice-Pauschale).** 6 € für jeden Tag, an dem die Tätigkeit *überwiegend* in
der Wohnung ausgeübt wurde, höchstens 210 Tage, also 1.260 € im Jahr. Kein eigenes Zimmer
erforderlich — der Küchentisch genügt.

**Arbeitszimmer.** Nur wenn das häusliche Arbeitszimmer der *qualitative Mittelpunkt* der gesamten
Tätigkeit ist. Dann Jahrespauschale 1.260 € oder, wenn höher, die tatsächlichen Kosten anteilig nach
Fläche. Bei Angestellten, die regelmäßig ins Büro fahren, liegt der Mittelpunkt praktisch nie zu
Hause; ein optimistischer Ansatz führt zur Nachfrage und Streichung.

### Was sich kombinieren lässt

**Entfernungspauschale und Tagespauschale schließen sich nicht aus**, sondern teilen das Jahr
tageweise auf: Bürotage zählen für die Entfernungspauschale, Homeoffice-Tage für die Tagespauschale.
Das ist der Normalfall und meist die beste Variante. Doppelt zählt kein Tag.

Eine **Ausnahme, die man kennen muss**: Steht dauerhaft kein anderer Arbeitsplatz zur Verfügung — der
Arbeitgeber hat also keinen Schreibtisch für diese Person —, darf die Tagespauschale auch für Tage
angesetzt werden, an denen man zusätzlich zur Tätigkeitsstätte gefahren ist. Wer unter diese Regel
fällt, lässt sonst bares Geld liegen. Das sollte der Arbeitgeber bescheinigen können.

**Tagespauschale und Arbeitszimmer-Jahrespauschale** dürfen nicht für denselben Zeitraum
nebeneinander angesetzt werden. Hier ist also zu wählen, nicht zu kombinieren.

### Die kürzere oder die schnellere Strecke

Angesetzt wird grundsätzlich die kürzeste Straßenverbindung. Eine **längere Strecke** ist zulässig,
wenn sie offensichtlich verkehrsgünstiger ist und regelmäßig benutzt wird — typischerweise Autobahn
statt Ortsdurchfahrten. Der Unterschied ist oft dreistellig, also immer beide Varianten rechnen. Die
Begründung sollte in `haushalt.yaml` stehen, denn sie wird im Zweifel verlangt.

### ÖPNV: Pauschale oder tatsächliche Kosten

Ohne eigenes Fahrzeug ist die Entfernungspauschale auf 4.500 € im Jahr begrenzt. Die **tatsächlichen
Kosten öffentlicher Verkehrsmittel** dürfen aber angesetzt werden, soweit sie den gesamten
Jahresbetrag der Entfernungspauschale übersteigen. Verglichen wird also **jahresbezogen**, nicht pro
Fahrt. Bei kurzen Entfernungen und einem Jahresabo gewinnt oft der tatsächliche Betrag.

### Was die Fahrtkosten kürzt

Ein steuerfreier Fahrtkostenzuschuss oder ein Jobticket nach § 3 Nr. 15 EStG und pauschal
besteuerte Arbeitgeberleistungen für diese Fahrten mindern die Entfernungspauschale. Der Betrag steht
in der Lohnsteuerbescheinigung, das Finanzamt kennt ihn also. Ebenso schließt eine steuerfreie
Sammelbeförderung (Großbuchstabe F) den Ansatz für diese Strecke aus.

### Der Pauschbetrag als Schwelle

Der Arbeitnehmer-Pauschbetrag von 1.230 € wird immer abgezogen. Werbungskosten wirken deshalb erst
**oberhalb** dieser Summe — darunter bringt jeder einzelne Beleg exakt nichts. Das ist die erste
Zahl, die man kennen will, bevor man Stunden mit dem Sammeln von Arbeitsmitteln verbringt.

Zwei wichtige Relativierungen dazu: Ab 2026 sind Gewerkschafts- und Berufsverbandsbeiträge
**zusätzlich** zum Pauschbetrag abziehbar, wirken also auch darunter. Und § 35a sowie Sonderausgaben
sind vom Pauschbetrag völlig unabhängig — wer unter 1.230 € bleibt, hat trotzdem Gründe abzugeben.

### Mobilitätsprämie

Liegt das zu versteuernde Einkommen unter dem Grundfreibetrag, wirkt die Entfernungspauschale nicht,
weil keine Steuer anfällt. Stattdessen gibt es für die Fernpendler-Kilometer die Mobilitätsprämie —
ab 2026 unbefristet. Das betrifft Teilzeit, Elternzeit, Ausbildung und Jahre mit Jobwechsel.

## Zusammen- oder Einzelveranlagung

Bei Ehepaaren und eingetragenen Partnerschaften ist die **Zusammenveranlagung** mit Splittingtarif
fast immer günstiger, und je unterschiedlicher die Einkommen, desto deutlicher. Rechnen lohnt sich
aber in diesen Fällen:

- Einer hat **Lohnersatzleistungen** mit Progressionsvorbehalt (Elterngeld, Krankengeld,
  Arbeitslosengeld). Bei Einzelveranlagung trifft die Progression nur dessen eigenes Einkommen.
- Einer hat eine **Abfindung** mit Fünftelregelung.
- Einer hat **Verluste** oder ausländische Einkünfte mit Progressionsvorbehalt.
- Einer hat hohe **außergewöhnliche Belastungen**: die zumutbare Belastung bemisst sich bei
  Einzelveranlagung nur nach seinem eigenen, niedrigeren Einkommen, sodass mehr durchschlägt.
- Beide haben **Kirchensteuer** in unterschiedlicher Höhe oder unterschiedliche Konfession.

Die Wahl trifft man jedes Jahr neu und kann sie bis zur Bestandskraft des Bescheids ändern. Wenn ein
solcher Fall vorliegt, nenne ihn dem Nutzer — die meisten Programme rechnen beide Varianten, wenn man
sie darum bittet.

## Kinder

Die **Günstigerprüfung** zwischen Kindergeld und Kinderfreibetrag macht das Finanzamt automatisch; es
gibt hier nichts zu wählen. Die Anlage Kind ist trotzdem abzugeben, denn an ihr hängen die
Kinderbetreuungskosten, das Schulgeld, der Ausbildungsfreibetrag und die Übertragung von
Freibeträgen.

Rechnen lohnt sich bei getrennt lebenden Eltern: die **Übertragung des BEA-Freibetrags** oder des
halben Kinderfreibetrags auf den Elternteil, bei dem das Kind lebt, ist beantragbar, wenn der andere
seiner Unterhaltspflicht nicht wesentlich nachkommt.

## Kapitalerträge

Die Anlage KAP ist freiwillig, außer in Sonderfällen. Sie lohnt sich, wenn

- der persönliche Steuersatz unter 25 % liegt (Günstigerprüfung beantragen),
- der Sparer-Pauschbetrag nicht ausgeschöpft wurde, weil kein Freistellungsauftrag vorlag,
- Verluste bei einer Bank mit Gewinnen bei einer anderen zu verrechnen sind (dafür braucht man eine
  Verlustbescheinigung, und die muss bis zum 15. Dezember des Jahres beantragt werden),
- Kirchensteuer auf Kapitalerträge nachzuerheben oder zu korrigieren ist.

## Bündelung über Jahre

Drei Schwellen machen es sinnvoll, Zahlungen bewusst in ein Jahr zu legen oder zu verteilen. Wenn das
Steuerjahr noch läuft, ist das der wertvollste Hinweis, den dieser Skill geben kann.

**Zumutbare Belastung bei Krankheitskosten.** Es wirkt nur, was über der Schwelle liegt. Zwei Jahre
mit je 1.500 € bringen oft nichts, ein Jahr mit 3.000 € dagegen schon. Planbare Behandlungen — Brille,
Zahnersatz, Physiotherapie — also in einem Jahr konzentrieren.

**§ 35a-Höchstbeträge.** Sie gelten pro Jahr. 10.000 € Handwerkerarbeitslohn in einem Jahr bringen
1.200 €; aufgeteilt auf zwei Jahre bringen 6.000 € plus 4.000 € zusammen 2.000 €. Bei größeren
Vorhaben lohnt es sich, über den Jahreswechsel hinweg in Teilrechnungen zu zahlen.

**Arbeitnehmer-Pauschbetrag.** Liegen die Werbungskosten knapp unter 1.230 €, lohnt es sich, eine
geplante Anschaffung vorzuziehen, damit die Summe die Schwelle überschreitet — oder sie zu
verschieben, wenn das nächste Jahr ohnehin darüber liegt.

Für 2027 ist geplant, den Handwerkerbonus auf 15 % und 900 € zu senken (Stand 2026-11-18 nicht
beschlossen). Falls das kommt, ist eine Zahlung noch in 2026 günstiger. Prüfe den aktuellen Stand,
bevor du darauf hinweist.
