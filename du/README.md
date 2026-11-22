# Du-Fassung der deutschen Cal.diy-Texte

`de-du.json` enthält alle 1055 Texte aus `packages/i18n/locales/de/common.json` (Cal.diy-Stand 2eb48ecc), die Cal.diy mit Sie anspricht, in der Du-Form. Der Build-Workflow legt sie beim Schalter `du_fassung` über die Originaldatei, das Abbild bekommt den Zusatz `-du` im Tag.

Prüfen: `python3 du/pruefen.py <sie-quelle.json> du/de-du.json` (gleiche Platzhalter und Tags, keine Sie-Form, kein Gedankenstrich).

Neuer Cal.diy-Stand: Der Workflow bricht ab, wenn ein Schlüssel fehlt oder Platzhalter abweichen. Dann die Sie-Texte neu ziehen und nur die Abweichungen nachübersetzen.
