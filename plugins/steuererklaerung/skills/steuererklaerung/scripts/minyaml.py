#!/usr/bin/env python3
"""Minimaler YAML-Leser für `haushalt.yaml`, als Fallback ohne PyYAML.

Beherrscht genau die Teilmenge, die die Vorlage benutzt: verschachtelte
Abbildungen, Listen von Abbildungen und Skalaren, einfache Flow-Listen,
gefaltete Blockskalare (`>`, `>-`, `|`, `|-`), Kommentare, `null`, Wahrheitswerte,
Zahlen und zitierte Zeichenketten.

Alles andere löst absichtlich einen Fehler mit Zeilennummer aus, statt still
etwas Falsches zu liefern — eine falsch gelesene Stammdatendatei wäre schlimmer
als eine klare Fehlermeldung. Wer mehr YAML braucht, installiert PyYAML; dann
wird dieser Leser nicht verwendet.
"""

from __future__ import annotations


class YamlFehler(ValueError):
    pass


def _ohne_kommentar(s: str) -> str:
    """Entfernt einen Kommentar, achtet dabei auf Anführungszeichen."""
    quote = None
    for i, ch in enumerate(s):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or s[i - 1] in " \t"):
            return s[:i]
    return s


def _skalar(roh: str, zeile: int):
    s = roh.strip()
    if not s:
        return None
    if s[0] in "\"'" and len(s) > 1 and s[-1] == s[0]:
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_skalar(t, zeile) for t in _trenne_flow(inner)]
    if s.startswith("{") and s.endswith("}"):
        raise YamlFehler(f"Zeile {zeile}: Flow-Abbildungen {{...}} werden nicht unterstützt")
    low = s.lower()
    if low in ("null", "~", ""):
        return None
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _trenne_flow(inner: str) -> list[str]:
    teile, puffer, quote = [], "", None
    for ch in inner:
        if quote:
            puffer += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            puffer += ch
        elif ch == ",":
            teile.append(puffer)
            puffer = ""
        else:
            puffer += ch
    if puffer.strip():
        teile.append(puffer)
    return teile


def _zeilen(text: str):
    """(indent, inhalt, nummer) für jede inhaltstragende Zeile."""
    out = []
    for nr, raw in enumerate(text.splitlines(), start=1):
        if raw.strip().startswith("#"):
            continue
        ohne = _ohne_kommentar(raw)
        if not ohne.strip():
            continue
        if "\t" in ohne[: len(ohne) - len(ohne.lstrip())]:
            raise YamlFehler(f"Zeile {nr}: Tabulator in der Einrückung; YAML verlangt Leerzeichen")
        indent = len(ohne) - len(ohne.lstrip(" "))
        out.append((indent, ohne.strip(), nr, raw))
    return out


def _block_skalar(roh_zeilen, i, basis_indent, stil):
    """Sammelt die eingerückten Zeilen eines Blockskalars aus dem Rohtext."""
    teile = []
    while i < len(roh_zeilen):
        raw = roh_zeilen[i]
        if not raw.strip():
            teile.append("")
            i += 1
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent <= basis_indent:
            break
        teile.append(raw.strip())
        i += 1
    if stil.startswith(">"):
        text = " ".join(t for t in teile if t)
    else:
        text = "\n".join(teile)
    if stil.endswith("-"):
        text = text.rstrip("\n")
    return text, i


def _parse(zeilen, pos, indent, roh_zeilen):
    if pos >= len(zeilen):
        return None, pos
    if zeilen[pos][1].startswith("- "):
        return _parse_liste(zeilen, pos, indent, roh_zeilen)
    return _parse_map(zeilen, pos, indent, roh_zeilen)


def _parse_map(zeilen, pos, indent, roh_zeilen):
    ergebnis = {}
    while pos < len(zeilen):
        ind, inhalt, nr, _ = zeilen[pos]
        if ind < indent:
            break
        if ind > indent:
            raise YamlFehler(f"Zeile {nr}: unerwartete Einrückung")
        if inhalt.startswith("- "):
            break
        if ":" not in inhalt:
            raise YamlFehler(f"Zeile {nr}: ':' fehlt in '{inhalt}'")
        key, _, rest = inhalt.partition(":")
        key = key.strip().strip("\"'")
        rest = rest.strip()
        pos += 1
        if rest in (">", ">-", "|", "|-", ">+", "|+"):
            text, _ = _block_skalar(roh_zeilen, nr, ind, rest)
            ergebnis[key] = text
            while pos < len(zeilen) and zeilen[pos][0] > ind:
                pos += 1
        elif rest:
            ergebnis[key] = _skalar(rest, nr)
        elif pos < len(zeilen) and zeilen[pos][0] > ind:
            ergebnis[key], pos = _parse(zeilen, pos, zeilen[pos][0], roh_zeilen)
        elif (pos < len(zeilen) and zeilen[pos][0] == ind
              and zeilen[pos][1].startswith("- ")):
            ergebnis[key], pos = _parse_liste(zeilen, pos, ind, roh_zeilen)
        else:
            ergebnis[key] = None
    return ergebnis, pos


def _parse_liste(zeilen, pos, indent, roh_zeilen):
    ergebnis = []
    while pos < len(zeilen):
        ind, inhalt, nr, _ = zeilen[pos]
        if ind < indent or not inhalt.startswith("- "):
            break
        if ind > indent:
            raise YamlFehler(f"Zeile {nr}: unerwartete Einrückung in einer Liste")
        rest = inhalt[2:].strip()
        pos += 1
        kind_indent = ind + 2
        if ":" in rest and not (rest[0] in "\"'" and rest.count(":") == 0):
            # Erster Schlüssel einer Abbildung steht in derselben Zeile.
            kunst = [(kind_indent, rest, nr, "")]
            while pos < len(zeilen) and zeilen[pos][0] >= kind_indent:
                kunst.append(zeilen[pos])
                pos += 1
            wert, _ = _parse_map(kunst, 0, kind_indent, roh_zeilen)
            ergebnis.append(wert)
        else:
            ergebnis.append(_skalar(rest, nr))
            while pos < len(zeilen) and zeilen[pos][0] > ind:
                pos += 1
    return ergebnis, pos


def load(text: str):
    """Liest die YAML-Teilmenge und gibt verschachtelte dicts/listen zurück."""
    roh = text.splitlines()
    zeilen = _zeilen(text)
    if not zeilen:
        return {}
    wert, pos = _parse(zeilen, 0, zeilen[0][0], roh)
    if pos < len(zeilen):
        raise YamlFehler(f"Zeile {zeilen[pos][2]}: konnte nicht gelesen werden")
    return wert


def load_path(pfad) -> dict:
    from pathlib import Path
    return load(Path(pfad).read_text(encoding="utf-8"))


if __name__ == "__main__":
    import json
    import sys
    print(json.dumps(load_path(sys.argv[1]), ensure_ascii=False, indent=2))
