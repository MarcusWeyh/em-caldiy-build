"""Cal.diy ohne Verweise auf cal.com (P-2026-11-28-AD).

Aufruf im Build-Workflow, im ausgecheckten Cal.diy-Quelltext (Wurzel = Ordner mit apps/ und packages/):
    python3 em-eigen/ohne-calcom/ohne-calcom.py .
Jede Ersetzung bricht ab, wenn die Stelle nicht genau so oft gefunden wird wie erwartet (Upstream geändert),
statt halb zu patchen. Keine Zugangsdaten, keine fremden Adressen: Ziele sind effizienzmaster.de und LinkedIn.
"""
import re, sys
from pathlib import Path

wurzel = Path(sys.argv[1])
SEITE = "https://effizienzmaster.de"
WISSEN = f"{SEITE}/wissen/"
TERMIN = "https://termin.effizienzmaster.de/marcus/erstgespraech"
LINKEDIN = "https://www.linkedin.com/in/marcus-weyh-effizienzmaster/"
MAIL = "info@effizienzmaster.de"


def lesen(rel):
    p = wurzel / rel
    if not p.is_file():
        sys.exit(f"{rel} fehlt. Upstream geändert, Patch prüfen.")
    return p, p.read_text(encoding="utf-8")


def ersetzen(text, alt, neu, erwartet, rel):
    n = text.count(alt)
    if n != erwartet:
        sys.exit(f"{rel}: erwartet {erwartet} mal {alt[:60]!r}, gefunden {n}. Upstream geändert, Patch prüfen.")
    return text.replace(alt, neu)


def block_entfernen(text, start, ende, rel):
    i = text.find(start)
    if i < 0 or text.count(start) != 1:
        sys.exit(f"{rel}: Anfang {start[:60]!r} nicht eindeutig. Upstream geändert, Patch prüfen.")
    j = text.find(ende, i)
    if j < 0:
        sys.exit(f"{rel}: Ende {ende[:60]!r} nicht gefunden. Upstream geändert, Patch prüfen.")
    return text[:i] + text[j + len(ende):]


# 1. 404-Seite: eigene Einträge statt Dokumentation und Blog
rel = "apps/web/app/notFoundClient.tsx"
p, t = lesen(rel)
t = ersetzen(t, 'import { DOCS_URL, IS_CALCOM, WEBSITE_URL } from "@calcom/lib/constants";',
             'import { IS_CALCOM, WEBSITE_URL } from "@calcom/lib/constants";', 1, rel)
m = re.search(r"  const links = \[\n.*?\n  \];\n", t, re.S)
if not m or t.count("  const links = [") != 1:
    sys.exit(f"{rel}: links-Liste nicht eindeutig. Upstream geändert, Patch prüfen.")
eintraege = [
    ("Termin buchen", "Buche dein Erstgespräch mit Marcus.", "calendar", TERMIN),
    ("Startseite", "Zurück zu effizienzmaster.de.", "globe", SEITE + "/"),
    ("Wissen", "Artikel und Anleitungen von Effizienzmaster.", "book-open", WISSEN),
    ("LinkedIn", "Folge Marcus auf LinkedIn.", "external-link", LINKEDIN),
]
neu = "  const links = [\n" + "".join(
    f'    {{\n      title: "{a}",\n      description: "{b}",\n      icon: "{c}" as const,\n      href: "{d}",\n    }},\n'
    for a, b, c, d in eintraege) + "  ];\n"
t = t[:m.start()] + neu + t[m.end():]
t = ersetzen(t, '<Link href={WEBSITE_URL} className="font-medium text-base text-emphasis hover:text-subtle">',
             f'<Link href="{SEITE}/" className="font-medium text-base text-emphasis hover:text-subtle">', 1, rel)
p.write_text(t, encoding="utf-8")

# 2. Metadaten: twitter:site und twitter:creator "@calcom" entfernen
rel = "apps/web/app/layout.tsx"
p, t = lesen(rel)
t = ersetzen(t, '    site: "@calcom",\n    creator: "@calcom",\n', "", 1, rel)
p.write_text(t, encoding="utf-8")
for rel in ("apps/web/lib/config/next-seo.config.ts", "packages/lib/next-seo.config.ts"):
    p, t = lesen(rel)
    t = ersetzen(t, '      handle: "@calcom",\n      site: "@calcom",\n', "", 1, rel)
    p.write_text(t, encoding="utf-8")

# 3. Feste Adressen in den Konstanten
rel = "packages/lib/constants.ts"
p, t = lesen(rel)
t = ersetzen(t, 'export const ROADMAP = "https://cal.com/roadmap";', f'export const ROADMAP = "{WISSEN}";', 1, rel)
t = ersetzen(t, 'export const DESKTOP_APP_LINK = "https://cal.com/download";', f'export const DESKTOP_APP_LINK = "{SEITE}/";', 1, rel)
t = ersetzen(t, 'export const POWERED_BY_URL = "https://go.cal.com/booking";', f'export const POWERED_BY_URL = "{SEITE}/";', 1, rel)
t = ersetzen(t, 'export const DOCS_URL = "https://cal.com/docs";', f'export const DOCS_URL = "{WISSEN}";', 1, rel)
t = ersetzen(t, 'export const DEVELOPER_DOCS = "https://developer.cal.com";', f'export const DEVELOPER_DOCS = "{WISSEN}";', 1, rel)
t = ersetzen(t, 'process.env.NEXT_PUBLIC_SUPPORT_MAIL_ADDRESS || "help@cal.com"', f'process.env.NEXT_PUBLIC_SUPPORT_MAIL_ADDRESS || "{MAIL}"', 1, rel)
p.write_text(t, encoding="utf-8")

# 4. Bestätigungsseite nach der Buchung: Anmelde-Kasten (cal.com/signup) und Google-Blog-Hinweis raus
rel = "apps/web/modules/bookings/views/bookings-single-view.tsx"
p, t = lesen(rel)
t = block_entfernen(t, "                    {session === null && !(userIsOwner || props.hideBranding) && (\n",
                    "                        </div>\n                      </>\n                    )}\n", rel)
t = block_entfernen(t, "              {isGmail && !isFeedbackMode && (\n", "                />\n              )}\n", rel)
if "cal.com" in t.replace("@calcom/", ""):
    sys.exit(f"{rel}: enthält noch cal.com")
p.write_text(t, encoding="utf-8")

# 5. Fehlerseite: Support-Adresse
rel = "apps/web/components/error/error-page.tsx"
p, t = lesen(rel)
t = ersetzen(t, 'href="mailto:support@cal.com"', f'href="mailto:{MAIL}"', 1, rel)
p.write_text(t, encoding="utf-8")

# 6. Seitenleiste im Dashboard: Firmenname und Version ohne Links nach go.cal.com
rel = "packages/ui/components/credits/Credits.tsx"
p, t = lesen(rel)
t = ersetzen(t, '<Link href="https://go.cal.com/credits" target="_blank" className="hover:underline">\n        {COMPANY_NAME}\n      </Link>',
             "<span>{COMPANY_NAME}</span>", 1, rel)
t = ersetzen(t, '<Link href="https://go.cal.com/releases" target="_blank" className="hover:underline">\n            {CalComVersion}\n          </Link>',
             "<span>{CalComVersion}</span>", 1, rel)
p.write_text(t, encoding="utf-8")
print("ohne-calcom: 6 Dateigruppen angepasst")
