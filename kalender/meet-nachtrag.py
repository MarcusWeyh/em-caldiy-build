"""Google-Kalender: Der Nachtrag des Meet-Links darf die Termin-ID nicht kosten.

Cal.diy legt einen Google-Termin mit events.insert an und schreibt danach mit events.patch
den Meet-Link in Beschreibung und Ort. Scheitert dieser zweite Aufruf (gemessen am
23.11.2026: 403 rateLimitExceeded), wirft createEvent, und Cal.diy speichert die Buchung
ohne Google-Termin-ID. Verschieben und Absagen finden den Termin danach nicht mehr
("bookingRefUid is empty"), er bleibt stehen.

Der Patch ersetzt beide Nachträge (createEvent und updateEvent) durch eine Methode, die
bis zu dreimal mit Pause (1, 2, 4 Sekunden) wiederholt und danach nur protokolliert.
Der Termin selbst steht dann schon, Google trägt den Meet-Link ohnehin in conferenceData.

Aufruf: python3 meet-nachtrag.py packages/app-store/googlecalendar/lib/CalendarService.ts
Bricht ab, wenn Upstream die Stellen geändert hat, statt halb zu patchen.
"""
import sys

pfad = sys.argv[1]
text = open(pfad, encoding="utf-8").read()

alt = (
    "        await calendar.events.patch({\n"
    "          // Update the same event but this time we know the hangout link\n"
)
neu = (
    "        await this.meetLinkNachtragen(calendar, {\n"
    "          // Update the same event but this time we know the hangout link\n"
)
anzahl = text.count(alt)
if anzahl != 2:
    sys.exit(f"Erwartet 2 Meet-Link-Nachträge, gefunden {anzahl}. Upstream geändert, Patch prüfen.")
text = text.replace(alt, neu)

anker = "  async createEvent(\n"
if text.count(anker) != 1:
    sys.exit("createEvent nicht eindeutig gefunden. Upstream geändert, Patch prüfen.")

methode = '''  // EM-Patch (em-caldiy-build, kalender/meet-nachtrag.py): Scheitert der Nachtrag des
  // Meet-Links, bleibt der Termin trotzdem mit seiner ID verknüpft.
  private async meetLinkNachtragen(
    calendar: calendar_v3.Calendar,
    params: calendar_v3.Params$Resource$Events$Patch
  ): Promise<void> {
    const pausen = [1000, 2000, 4000];
    for (let versuch = 0; ; versuch++) {
      try {
        await calendar.events.patch(params);
        return;
      } catch (error) {
        if (isGaxiosResponse(error)) {
          delete error.config.body;
        }
        if (versuch < pausen.length) {
          this.log.warn(
            "EM-Patch: Meet-Link-Nachtrag fehlgeschlagen, neuer Versuch",
            safeStringify({ versuch: versuch + 1, eventId: params.eventId })
          );
          await new Promise((fertig) => setTimeout(fertig, pausen[versuch]));
          continue;
        }
        this.log.error(
          "EM-Patch: Meet-Link-Nachtrag endgültig fehlgeschlagen, Termin bleibt verknüpft",
          safeStringify({ error, eventId: params.eventId })
        );
        return;
      }
    }
  }

'''
text = text.replace(anker, methode + anker)
open(pfad, "w", encoding="utf-8").write(text)
print("Meet-Link-Nachtrag gepatcht: 2 Stellen, Methode meetLinkNachtragen eingefügt")
