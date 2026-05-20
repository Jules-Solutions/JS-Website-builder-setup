---
type: page
slug: /
language: de
title: "Start"
seo_title: "Payload-Fixture — Start"
seo_description: "Synthetische Fixture zur Validierung des Payload-CMS-Adapters."
sections: [hero, features-grid, cta]
---

## Hero section

[Synthetischer Inhalt. Payload Block: hero. Überschrift + Untertitel + CTA.]

Willkommen auf der Payload-Fixture-Seite. Filler-Inhalt, geseedet per `payload.create({collection: 'pages', locale: 'de'})` an Phase 18 — gleicher `_id` wie die EN-Version (Approach 2: Layout geteilt, Text per Locale).

## Features Grid section

[Payload Block: featuresGrid. 3 Einträge.]

(Einträge in components.yaml definiert. Titel + Beschreibung je Eintrag lokalisiert.)

## CTA section

[Payload Block: cta. Referenziert {strings.cta.subscribe} aus messages/de.json — Option A Strings-Layer.]

(Sektion verwendet Strings-Referenz; Agent löst zur Renderzeit via next-intl auf.)
