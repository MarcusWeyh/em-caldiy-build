# Prueft eine Du-Fassung gegen ihre Sie-Quelle.
# Aufruf: python3 pruefen.py <quelle.json> <du.json>
# Gleiche Schluessel, gleiche Platzhalter ({{x}}, $t(...)), gleiche HTML-Tags, kein Sie mehr,
# kein Gedankenstrich (U+2012 bis U+2015, U+2212). Exit 0 nur ohne Befund.
import json, re, sys

quelle = json.load(open(sys.argv[1]))
du = json.load(open(sys.argv[2]))
befunde = []

sie = re.compile(r'\b(Sie|Ihr|Ihre|Ihren|Ihrem|Ihrer|Ihres|Ihnen)\b')
platz = re.compile(r'\{\{[^}]*\}\}|\$t\([^)]*\)|<[^>]+>|%\w|\{\d+\}')
strich = re.compile('[‒–—―−]')

fehlend = set(quelle) - set(du)
zuviel = set(du) - set(quelle)
if fehlend: befunde.append(f'fehlende Schluessel: {sorted(fehlend)[:10]} ({len(fehlend)})')
if zuviel: befunde.append(f'fremde Schluessel: {sorted(zuviel)[:10]} ({len(zuviel)})')

for k, q in quelle.items():
    if k not in du: continue
    v = du[k]
    if not isinstance(v, str) or not v.strip():
        befunde.append(f'{k}: leer oder kein Text'); continue
    if sorted(platz.findall(q)) != sorted(platz.findall(v)):
        befunde.append(f'{k}: Platzhalter oder Tags abweichend')
    if sie.search(v):
        befunde.append(f'{k}: noch Sie-Form: {v[:80]}')
    if strich.search(v):
        befunde.append(f'{k}: Gedankenstrich')
    if re.search(r'\bDu\b|\bDein', v) and not re.match(r'^(Du|Dein)', v) and not re.search(r'[.!?:\]]\s+(Du|Dein)', v):
        befunde.append(f'{k}: Du gross mitten im Satz: {v[:80]}')

for b in befunde: print(b)
print(f'{len(du)} Eintraege, {len(befunde)} Befunde')
sys.exit(1 if befunde else 0)
