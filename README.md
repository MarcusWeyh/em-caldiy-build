# em-caldiy-build

Baut das Container-Image von [Cal.diy](https://github.com/calcom/cal.diy) für die Terminbuchung von Effizienzmaster (`termin.effizienzmaster.de`) und legt es öffentlich in der GitHub Container Registry ab: `ghcr.io/marcusweyh/em-caldiy`.

Das Repo enthält keinen Cal.diy-Quelltext. Der Workflow klont den gepinnten Commit beim Bauen.

## Warum selbst bauen

Für Cal.diy gibt es kein öffentliches Image (Stand 09.11.2026: Docker Hub `calcom/cal.diy` ohne Tags, `ghcr.io/calcom/cal.diy` nicht vorhanden). Das letzte öffentliche Image `calcom/cal.com:v6.2.0` ist noch Cal.com unter AGPL, nicht Cal.diy unter MIT.

## Gepinnter Stand

| | |
|---|---|
| Upstream | `github.com/calcom/cal.diy`, Zweig `main` |
| Commit | `2eb48eccd8aca8a0c0ffabf28cf92e298b33ecee` |
| Datum | 03.11.2026 (neuester Stand von `main` am 09.11.2026) |
| Image-Tag | `ghcr.io/marcusweyh/em-caldiy:2eb48ecc` |

Cal.diy hat seit dem Wechsel von Cal.com keine Release-Tags. Gepinnt wird deshalb auf den vollen Commit, nie auf `main`. Der Pin steht als `CALDIY_SHA` in `.github/workflows/build.yml`.

## Was ins Image gebacken wird

Nur öffentliche Werte, die ohnehin im Browser der Besucher landen:

- `NEXT_PUBLIC_WEBAPP_URL=https://termin.effizienzmaster.de`
- `NEXT_PUBLIC_DISABLE_SIGNUP=true` (Registrierung gesperrt, nur das Konto aus dem Einrichtungsassistenten)
- `NEXT_PUBLIC_LICENSE_CONSENT=agree`, `CALCOM_TELEMETRY_DISABLED=1`
- `NEXT_PUBLIC_APP_NAME=Effizienzmaster Termine`, `NEXT_PUBLIC_COMPANY_NAME=Effizienzmaster`
- Adressen von Datenschutzerklärung und Impressum auf `effizienzmaster.de`

Keine Geheimnisse. `NEXTAUTH_SECRET` und `CALENDSO_ENCRYPTION_KEY` bleiben beim Build auf den Platzhaltern des Upstream-Dockerfiles; die echten Werte setzt Coolify zur Laufzeit. Der Workflow nutzt nur das automatische `GITHUB_TOKEN`, und nur im letzten Schritt für den Push.

Zwei Änderungen am Upstream-Stand:

1. **Google Fonts in den Mails** (Eingang `google_fonts_entfernen`, Standard ja): Die Einbindung von `fonts.googleapis.com` in `packages/emails/src/components/EmailHead.tsx` wird entfernt, damit das Mailprogramm der Empfänger keine Verbindung zu Google aufbaut. Der Workflow prüft das in der Datei und im gebauten Image. Mit `false` gebaut, heißt der Tag `<kurz>-mit-google-fonts`. Die Entscheidung liegt bei Marcus.
2. **Lizenzhinweis:** Die MIT-Lizenz von Cal.diy wird als `/calcom/apps/web/LICENSE.cal.diy` ins Image gelegt, weil das Upstream-Dockerfile die Lizenzdatei nicht mitkopiert.

## Prüfungen im Lauf

- Ausgecheckter Stand ist genau der gepinnte Commit, Lizenz ist MIT.
- Rauchtest gegen `pgvector/pgvector:pg18` (dasselbe Image wie die gemeinsame PostgreSQL am Server): Start bis `/auth/login`, danach `POST /api/auth/signup` muss mit 403 und „Signup is disabled“ abgewiesen werden, ohne dass die Sperre zur Laufzeit gesetzt ist.
- Lizenzhinweis und Google-Fonts-Entfernung am gebauten Image.

## Neu bauen

1. Neuesten Stand lesen: `git ls-remote https://github.com/calcom/cal.diy refs/heads/main`.
2. `CALDIY_SHA` in `.github/workflows/build.yml` ändern, Datum im Kommentar und in dieser Datei nachziehen, committen.
3. Actions, „Cal.diy-Image bauen“, Run workflow.
4. Die Zusammenfassung des Laufs nennt die Referenz mit Digest (`ghcr.io/marcusweyh/em-caldiy:<kurz>@sha256:…`). Nur diese Referenz mit Digest kommt in Coolify, nie der Tag allein.
5. Vor dem Wechsel in Coolify eine frische Sicherung der Datenbank `em_calcom`, weil Cal.diy beim Start Migrationen ausführt.

Der Workflow startet nur von Hand (`workflow_dispatch`). Er deployt nichts.

## Lizenz

Cal.diy steht unter der MIT-Lizenz, Copyright (c) 2020-present Cal.com, Inc. Einzelheiten in `NOTICE`. Für die eigenen Dateien dieses Repos ist keine Lizenz vergeben.
