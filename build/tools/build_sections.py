"""Writes the sections below the Hero (02–09 + footer) into index.html and
de/index.html, from one content table, so both languages stay in step.
Facts come from the AIK Studio business plan (Nov 2026); nothing invented:
no testimonials, no client numbers. Prices are the owner's own ranges."""
import json, re, html, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/build"

T = {
"en": dict(
  base="./", lang="en",
  nav=[("#work", "Work"), ("#services", "Services"), ("#process", "Approach"), ("#why", "About"), ("#contact", "Contact")],
  talk="Let’s talk",
  marquee=["Redesign", "Built for enquiries", "Speed", "SEO", "Care", "Turnkey"],
  offer=dict(idx="02", label="The problem", right="Why redesign",
    title="Your business is <em>better</em> than your website.",
    pains=[("Slow", "Visitors leave before the first screen has even loaded."),
           ("Weak on the phone", "Most of your customers see a squeezed desktop site."),
           ("No clear next step", "People look, don’t know where to click, and go to a competitor."),
           ("Weaker than you are", "Online, a strong business looks small. That costs trust before the first call.")],
    stat="53", stat_txt="of mobile visits are abandoned when a page takes longer than 3 seconds to load.", stat_src="Source: Google",
    answer="We rebuild it — <em>turnkey,</em> and built to bring enquiries.",
    answer_lead="A modern website that hooks in the first three seconds, guides visitors through the page and leads them to an enquiry. You don’t have to think about the technology: we take all of it on.",
    cta="Talk about your project"),
  work=dict(idx="01", label="Selected work", right="Recent projects",
    title="Work that <em>speaks</em> for itself.",
    cases=[("MA’LOA", ["Restaurants · Eschborn", "Concept"], "Homepage and franchise page for a Hawaiian poké bowl chain. Self-initiated concept, not the live maloa.com.", "media/work/maloa-hero.webp", "https://maolaheropage.netlify.app/"),
           ("BLF Service", ["Trees & land · Seddiner See", "Website"], "Website for a tree, land and forestry service: services all year round, enquiries and jobs.", "media/work/blf-service.webp", "https://lucky-parfait-f6d633.netlify.app/"),
           ("Architekturcontor", ["Architecture · Potsdam", "Concept"], "Redesign concept for an architecture office focused on schools: project catalogue and a four-step enquiry.", "media/work/architekturcontor.webp", "https://nimble-hummingbird-a98d10.netlify.app/"),
           ("Gute Räume", ["Interior design · Potsdam", "Concept"], "Concept for a studio for spatial concepts and circular interior design.", "media/work/raum-studio.webp", "https://helpful-otter-6da26b.netlify.app/"),
           ("Handy-Chirurg", ["Phone repair · Potsdam", "Website"], "Website for a phone repair shop in Potsdam: design and build.", "", "")],
    view="View"),
  system=dict(idx="03", label="How it brings clients", right="The system",
    title="A website is a <em>system,</em> not a picture.",
    steps=[("3 s", "Hook", "In the first three seconds the visitor understands who you are and why it matters to them."),
           ("1 path", "Guide", "The page leads step by step: what you offer, proof, price, the next step. No dead ends."),
           ("1 click", "Enquiry", "Call, WhatsApp or form — one clear action on every screen, especially on the phone.")],
    foot="And you see it working: analytics show how many enquiries the website brings.", cta="See the process"),
  process=dict(idx="04", label="Process", right="Your time: 1–3 × 30 min",
    title="You give us <em>one to three</em> 30-minute calls.",
    lead="Everything else is on us: structure, copy, design, technology, legal pages. Clear plan, timeline and price from the very beginning.",
    steps=[("Call", "We understand the business", "Your goals, your customers, what the old site gets wrong.", "30 min"),
           ("Concept", "You see the direction", "Structure and the first screens, as a real page in the browser.", "30 min"),
           ("Build", "We do the work", "Design, copy, development, speed, SEO basics, Impressum and Datenschutz.", "none"),
           ("Launch", "Live, and handed over", "All access is yours. We stay on for care if you want.", "30 min")],
    you="Your time"),
  services=dict(idx="05", label="Services &amp; prices", right="Clear from day one",
    title="Prices you know <em>before</em> we start.",
    packs=[("Landing page", "900 – 1 400 €", "one page, one goal", ["One page built for one offer", "Fast on every phone", "Contact form or WhatsApp", "Basic SEO"], False),
           ("Website", "2 400 – 4 600 €", "redesign or new", ["Full redesign, built for enquiries", "Structure, copy, design, build", "Speed and technical SEO", "Impressum & Datenschutz", "First month of care free"], True),
           ("Premium", "from 6 900 €", "signature site", ["Everything in Website", "Signature hero: film, 3D or animation", "Up to 12 pages, two languages", "Admin panel and 3 months of care included", "Priority timeline"], False)],
    badge="Most chosen", pick="Choose", pick_hot="Start with this",
    extras=["Care from 150 €/month", "Admin panel +600 €", "Speed optimisation", "SEO", "3D visualisation", "Market analysis", "Larger projects on request"],
    calc_title="Estimate your project", type_lbl="Type", types={"landing": "Landing page", "site": "Website", "big": "Large project"},
    pages_lbl="Pages", cms="Admin panel (edit it yourself)", cms_note="+600 €", care_lbl="Care after launch", care={"none": "None", "basic": "150 €/mo", "full": "300 €/mo"},
    out_lbl="Your estimate", note="A guide, not an offer. The exact price comes after a 30-minute call — fixed before we start.", go="Send this estimate",
    t=dict(from_="from", month="per month for care", noCare="No care plan", pages="pages", cms="admin panel", care="care", mo="month", prefill="My estimate")),
  why=dict(idx="06", label="Why AIK", right="Founder-led",
    title="Agency level. <em>Direct</em> line to the founder.",
    name="Nikolay Riabov", role="Founder, AIK Studio", quote="You talk to the person who builds your website. No managers in between.",
    th=["", "Price", "Upside", "Downside"],
    rows=[("Website builder", "7–36 €/mo", "Cheap", "You do it all yourself; looks like a template"),
          ("Freelancer", "800–3 000 €", "Cheaper than an agency", "Quality varies; often just a picture"),
          ("Agency", "2 000–8 000 €", "Team and process", "Expensive, slow, through a manager"),
          ("AIK Studio", "2 400–4 600 €", "Turnkey, built for enquiries, direct", "One founder — so all access is handed to you")],
    reasons=[("Fast", "A clear plan and short loops instead of months of back and forth."),
             ("Clear", "Price, timeline and steps fixed before we start."),
             ("Reliable", "Contract, 50 % prepayment, all access handed over."),
             ("Quality", "Hand-built, measured on real phones, no templates.")]),
  faq=dict(idx="07", label="Questions", right="Before you ask",
    title="Good <em>questions.</em>",
    items=[("How much of my time does it take?", "One to three calls of 30 minutes. We prepare everything else and show you results, not homework."),
           ("What does it cost?", "A landing page is 900–1 400 €, a website 2 400–4 600 €, larger projects more. You get a fixed price after the first call."),
           ("Who owns the website?", "You do. Domain, hosting, code and all access are handed over at launch."),
           ("How does payment work?", "We sign a short contract. 50 % before we start, 50 % at launch."),
           ("What about Impressum, Datenschutz and DSGVO?", "Legal pages and a privacy-friendly setup are part of the build. For legal advice we recommend your Steuerberater or lawyer."),
           ("What happens after launch?", "Care by subscription (150–300 € per month) or by the hour — or you run it yourself."),
           ("Do you work in German and English?", "Yes. Websites in German, English or both.")]),
  contact=dict(idx="08", label="Contact", right="Potsdam · Berlin",
    title="Let’s talk about <em>your</em> project.",
    lead="Tell us what your business does and what the website should achieve. We reply within one working day.",
    dl=[("Based", "Potsdam · Berlin · all of Germany"), ("Founder", "Nikolay Riabov"), ("Response", "Within one working day")],
    f=dict(name="Name", email="E-mail", site="Current website", need="What do you need?", needs=["Redesign", "New website", "Landing page", "Care / support", "Not sure yet"],
           msg="Message", send="Send enquiry", fine="We only use your details to answer your enquiry.",
           ok="Preview: this form is not connected yet. On the live site it goes straight to AIK Studio.")),
  foot=dict(nav=[("#work", "Work"), ("#services", "Services"), ("#process", "Process"), ("#contact", "Contact")],
            legal=[("impressum.html", "Impressum"), ("datenschutz.html", "Datenschutz")], copy="© 2026 AIK Studio"),
),
"de": dict(
  base="../", lang="de",
  nav=[("#work", "Arbeiten"), ("#services", "Leistungen"), ("#process", "Ablauf"), ("#why", "Über uns"), ("#contact", "Kontakt")],
  talk="Projekt anfragen",
  marquee=["Redesign", "Gebaut für Anfragen", "Tempo", "SEO", "Betreuung", "Schlüsselfertig"],
  offer=dict(idx="02", label="Das Problem", right="Warum Redesign",
    title="Ihr Unternehmen ist <em>besser</em> als Ihre Website.",
    pains=[("Langsam", "Besucher gehen, bevor der erste Bildschirm geladen ist."),
           ("Schwach auf dem Handy", "Die meisten Kunden sehen eine gequetschte Desktop-Seite."),
           ("Kein klarer nächster Schritt", "Man schaut, weiß nicht, wo man klicken soll, und geht zur Konkurrenz."),
           ("Schwächer, als Sie sind", "Online wirkt ein starkes Unternehmen klein. Das kostet Vertrauen vor dem ersten Anruf.")],
    stat="53", stat_txt="der mobilen Besuche werden abgebrochen, wenn eine Seite länger als 3 Sekunden lädt.", stat_src="Quelle: Google",
    answer="Wir bauen sie neu — <em>schlüsselfertig</em> und auf Anfragen ausgelegt.",
    answer_lead="Eine moderne Website, die in den ersten drei Sekunden überzeugt, Besucher durch die Seite führt und zur Anfrage bringt. Um die Technik müssen Sie sich nicht kümmern: Das übernehmen wir komplett.",
    cta="Projekt besprechen"),
  work=dict(idx="01", label="Ausgewählte Arbeiten", right="Aktuelle Projekte",
    title="Arbeiten, die <em>für sich</em> sprechen.",
    cases=[("MA’LOA", ["Gastronomie · Eschborn", "Konzept"], "Startseite und Franchise-Seite für eine Hawaiian-Poké-Bowl-Kette. Eigeninitiatives Konzept, nicht die Live-Seite maloa.com.", "media/work/maloa-hero.webp", "https://maolaheropage.netlify.app/"),
           ("BLF Service", ["Baum & Land · Seddiner See", "Website"], "Website für einen Baum-, Land- und Forstservice: Leistungen das ganze Jahr, Anfragen und Jobs.", "media/work/blf-service.webp", "https://lucky-parfait-f6d633.netlify.app/"),
           ("Architekturcontor", ["Architektur · Potsdam", "Konzept"], "Redesign-Konzept für ein Architekturbüro mit Schwerpunkt Schulbau: Werkverzeichnis und Anfrage in vier Schritten.", "media/work/architekturcontor.webp", "https://nimble-hummingbird-a98d10.netlify.app/"),
           ("Gute Räume", ["Interior Design · Potsdam", "Konzept"], "Konzept für ein Studio für Raumkonzepte und zirkuläres Interior Design.", "media/work/raum-studio.webp", "https://helpful-otter-6da26b.netlify.app/"),
           ("Handy-Chirurg", ["Handyreparatur · Potsdam", "Website"], "Website für eine Handywerkstatt in Potsdam: Design und Umsetzung.", "", "")],
    view="Ansehen"),
  system=dict(idx="03", label="Wie sie Kunden bringt", right="Das System",
    title="Eine Website ist ein <em>System,</em> kein Bild.",
    steps=[("3 s", "Überzeugen", "In den ersten drei Sekunden versteht der Besucher, wer Sie sind und warum das für ihn zählt."),
           ("1 Weg", "Führen", "Die Seite führt Schritt für Schritt: Angebot, Beweise, Preis, nächster Schritt. Keine Sackgassen."),
           ("1 Klick", "Anfrage", "Anruf, WhatsApp oder Formular — eine klare Aktion auf jedem Bildschirm, gerade auf dem Handy.")],
    foot="Und Sie sehen, dass es funktioniert: Die Analyse zeigt, wie viele Anfragen die Website bringt.", cta="Zum Ablauf"),
  process=dict(idx="04", label="Ablauf", right="Ihre Zeit: 1–3 × 30 Min.",
    title="Sie investieren <em>ein bis drei</em> Gespräche à 30 Minuten.",
    lead="Alles andere übernehmen wir: Struktur, Texte, Design, Technik, rechtliche Seiten. Klarer Plan, Zeitrahmen und Preis von Anfang an.",
    steps=[("Gespräch", "Wir verstehen Ihr Geschäft", "Ihre Ziele, Ihre Kunden, was die alte Seite falsch macht.", "30 Min."),
           ("Konzept", "Sie sehen die Richtung", "Struktur und erste Bildschirme, als echte Seite im Browser.", "30 Min."),
           ("Umsetzung", "Wir machen die Arbeit", "Design, Texte, Entwicklung, Tempo, SEO-Basis, Impressum und Datenschutz.", "keine"),
           ("Launch", "Live und übergeben", "Alle Zugänge gehören Ihnen. Auf Wunsch betreuen wir weiter.", "30 Min.")],
    you="Ihre Zeit"),
  services=dict(idx="05", label="Leistungen &amp; Preise", right="Klar ab Tag eins",
    title="Preise, die Sie <em>vorher</em> kennen.",
    packs=[("Landingpage", "900 – 1.400 €", "eine Seite, ein Ziel", ["Eine Seite für ein Angebot", "Schnell auf jedem Handy", "Kontaktformular oder WhatsApp", "SEO-Grundlagen"], False),
           ("Website", "2.400 – 4.600 €", "Redesign oder neu", ["Komplettes Redesign für Anfragen", "Struktur, Texte, Design, Umsetzung", "Tempo und technisches SEO", "Impressum & Datenschutz", "Erster Monat Betreuung gratis"], True),
           ("Premium", "ab 6.900 €", "Signature-Website", ["Alles aus „Website“", "Signature-Hero: Film, 3D oder Animation", "Bis zu 12 Seiten, zweisprachig", "Admin-Panel und 3 Monate Betreuung inklusive", "Priorisierter Zeitplan"], False)],
    badge="Am häufigsten gewählt", pick="Auswählen", pick_hot="Damit starten",
    extras=["Betreuung ab 150 €/Monat", "Admin-Panel +600 €", "Tempo-Optimierung", "SEO", "3D-Visualisierung", "Marktanalyse", "Größere Projekte auf Anfrage"],
    calc_title="Projekt schätzen", type_lbl="Art", types={"landing": "Landingpage", "site": "Website", "big": "Großes Projekt"},
    pages_lbl="Seiten", cms="Admin-Panel (selbst pflegen)", cms_note="+600 €", care_lbl="Betreuung nach dem Launch", care={"none": "Keine", "basic": "150 €/Mon.", "full": "300 €/Mon."},
    out_lbl="Ihre Schätzung", note="Eine Orientierung, kein Angebot. Den genauen Preis erhalten Sie nach einem 30-Minuten-Gespräch — fest, bevor wir beginnen.", go="Schätzung senden",
    t=dict(from_="ab", month="pro Monat Betreuung", noCare="Ohne Betreuung", pages="Seiten", cms="Admin-Panel", care="Betreuung", mo="Monat", prefill="Meine Schätzung")),
  why=dict(idx="06", label="Warum AIK", right="Gründergeführt",
    title="Agentur-Niveau. <em>Direkter</em> Draht zum Gründer.",
    name="Nikolay Riabov", role="Gründer, AIK Studio", quote="Sie sprechen mit dem Menschen, der Ihre Website baut. Keine Manager dazwischen.",
    th=["", "Preis", "Vorteil", "Nachteil"],
    rows=[("Baukasten", "7–36 €/Mon.", "Günstig", "Alles selbst machen; wirkt wie eine Vorlage"),
          ("Freelancer", "800–3.000 €", "Günstiger als Agentur", "Qualität schwankt; oft nur ein Bild"),
          ("Agentur", "2.000–8.000 €", "Team und Prozess", "Teuer, langsam, über einen Manager"),
          ("AIK Studio", "2.400–4.600 €", "Schlüsselfertig, für Anfragen, direkt", "Ein Gründer — deshalb bekommen Sie alle Zugänge")],
    reasons=[("Schnell", "Klarer Plan und kurze Schleifen statt monatelangem Hin und Her."),
             ("Klar", "Preis, Zeitrahmen und Schritte stehen vor dem Start fest."),
             ("Verlässlich", "Vertrag, 50 % Anzahlung, alle Zugänge werden übergeben."),
             ("Qualität", "Von Hand gebaut, auf echten Handys gemessen, keine Vorlagen.")]),
  faq=dict(idx="07", label="Fragen", right="Bevor Sie fragen",
    title="Gute <em>Fragen.</em>",
    items=[("Wie viel Zeit kostet mich das?", "Ein bis drei Gespräche à 30 Minuten. Alles andere bereiten wir vor und zeigen Ihnen Ergebnisse statt Hausaufgaben."),
           ("Was kostet das?", "Eine Landingpage 900–1.400 €, eine Website 2.400–4.600 €, größere Projekte mehr. Nach dem ersten Gespräch erhalten Sie einen Festpreis."),
           ("Wem gehört die Website?", "Ihnen. Domain, Hosting, Code und alle Zugänge werden beim Launch übergeben."),
           ("Wie läuft die Bezahlung?", "Wir schließen einen kurzen Vertrag. 50 % vor dem Start, 50 % zum Launch."),
           ("Und Impressum, Datenschutz, DSGVO?", "Rechtliche Seiten und ein datenschutzfreundliches Setup gehören zur Umsetzung. Für Rechtsberatung empfehlen wir Ihren Steuerberater oder Anwalt."),
           ("Was passiert nach dem Launch?", "Betreuung im Abo (150–300 € pro Monat) oder nach Aufwand — oder Sie pflegen die Seite selbst."),
           ("Arbeiten Sie auf Deutsch und Englisch?", "Ja. Websites auf Deutsch, Englisch oder in beiden Sprachen.")]),
  contact=dict(idx="08", label="Kontakt", right="Potsdam · Berlin",
    title="Sprechen wir über <em>Ihr</em> Projekt.",
    lead="Erzählen Sie, was Ihr Unternehmen macht und was die Website erreichen soll. Wir antworten innerhalb eines Werktags.",
    dl=[("Standort", "Potsdam · Berlin · ganz Deutschland"), ("Gründer", "Nikolay Riabov"), ("Antwort", "Innerhalb eines Werktags")],
    f=dict(name="Name", email="E-Mail", site="Aktuelle Website", need="Was brauchen Sie?", needs=["Redesign", "Neue Website", "Landingpage", "Betreuung", "Noch unklar"],
           msg="Nachricht", send="Anfrage senden", fine="Wir nutzen Ihre Angaben nur, um Ihre Anfrage zu beantworten.",
           ok="Vorschau: Dieses Formular ist noch nicht verbunden. Auf der Live-Seite geht es direkt an AIK Studio.")),
  foot=dict(nav=[("#work", "Arbeiten"), ("#services", "Leistungen"), ("#process", "Ablauf"), ("#contact", "Kontakt")],
            legal=[("impressum.html", "Impressum"), ("datenschutz.html", "Datenschutz")], copy="© 2026 AIK Studio"),
),
}


def idx(no, label, right):
    return f'<p class="idx" data-fade><b>{no}</b><i></i>{label}<span class="r">{right}</span></p>'


def build(c):
    b = c["base"]
    o, w, s, p, sv, wy, fq, ct, ft = (c[k] for k in ["offer", "work", "system", "process", "services", "why", "faq", "contact", "foot"])
    mq = "".join(f"<span>{x}</span>" for x in c["marquee"] * 2)
    pains = "".join(f'<li data-fade style="--d:{i*90}"><span class="n">0{i+1}</span><div><h3>{h}</h3><p>{t}</p></div></li>' for i, (h, t) in enumerate(o["pains"]))
    cases = ""
    for i, (nm, meta, note, img, url) in enumerate(w["cases"]):
        data_img = f' data-img="{b}{img}"' if img else ""
        cur = f' data-cursor="{w["view"]}"' if url else ""
        href = f'href="{url}" target="_blank" rel="noopener"' if url else 'href="#contact"'
        im = f'<div class="case__img"><img src="{b}{img}" alt="" loading="lazy" decoding="async"></div>' if img else ""
        cases += (f'<li class="case"{data_img} data-fade style="--d:{i*80}"><a {href}{cur}>'
                  f'<span class="n">0{i+1}</span><span class="name">{nm}</span>'
                  f'<span class="meta"><span>{meta[0]}</span><span class="tag">{meta[1]}</span></span>'
                  f'<p class="note">{note}</p></a>{im}</li>')
    reel_imgs = json.dumps([f"{b}media/work/{x}.webp" for x in ["maloa-hero", "architekturcontor", "blf-service", "raum-studio", "maloa-franchise"]])
    reel = f"<div class=\"reel\" data-images='{reel_imgs}' data-aspect=\"0.64\" data-tile=\"84\" data-curve=\"62\" data-speed=\"4.5\"></div>"
    climb = "".join(f'<li data-fade style="--d:{i*120}"><span class="big">{a}</span><h3>{h}</h3><p>{t}</p></li>' for i, (a, h, t) in enumerate(s["steps"]))
    steps = "".join(f'<li class="step"><div class="top"><span>0{i+1}</span><span>{a}</span></div><span class="num">0{i+1}</span>'
                    f'<h3>{h}</h3><p>{t}</p><p class="you">{p["you"]}: <b>{tm}</b></p></li>' for i, (a, h, t, tm) in enumerate(p["steps"]))
    packs = ""
    for nm, price, sub, lst, hot in sv["packs"]:
        badge = f'<span class="badge">{sv["badge"]}</span>' if hot else ""
        packs += (f'<article class="pack{" hot" if hot else ""}" data-fade>{badge}<p class="k">{sub}</p><h3>{nm}</h3>'
                  f'<p class="price">{price}</p><ul>{"".join(f"<li>{x}</li>" for x in lst)}</ul>'
                  f'<a class="pack__go" href="#contact">{sv["pick_hot"] if hot else sv["pick"]} <span aria-hidden="true">→</span></a></article>')
    extras = "".join(f"<span>{x}</span>" for x in sv["extras"])
    t = dict(sv["t"]); t["from"] = t.pop("from_"); t["types"] = sv["types"]
    calc = f'''<div class="calc" data-fade data-t='{html.escape(json.dumps(t, ensure_ascii=False), quote=True)}'>
        <div class="calc__in">
          <h3>{sv["calc_title"]}</h3>
          <div class="field"><p class="lbl">{sv["type_lbl"]}</p><div class="seg">{"".join(f'<button type="button" data-type="{k}" aria-pressed="{str(k=="site").lower()}">{v}</button>' for k, v in sv["types"].items())}</div></div>
          <div class="field f-pages"><label class="lbl" for="c-pages"><span>{sv["pages_lbl"]}</span><span class="pages-out">6</span></label><input class="range" id="c-pages" type="range" min="3" max="12" value="6"></div>
          <div class="toggles"><label class="tog"><span>{sv["cms"]}<small>{sv["cms_note"]}</small></span><input id="c-cms" type="checkbox"></label></div>
          <div class="field"><p class="lbl">{sv["care_lbl"]}</p><div class="seg">{"".join(f'<button type="button" data-care="{k}" aria-pressed="{str(k=="none").lower()}">{v}</button>' for k, v in sv["care"].items())}</div></div>
        </div>
        <div class="calc__out" aria-live="polite">
          <p class="idx">{sv["out_lbl"]}</p>
          <p class="calc__price">—</p>
          <p class="calc__monthly"></p>
          <a class="cta cta--solid to-form" href="#contact">{sv["go"]} <span class="arr" aria-hidden="true">→</span></a>
          <p class="calc__note">{sv["note"]}</p>
        </div>
      </div>'''
    rows = "".join(f'<tr class="{"us" if i == 3 else ""}"><td>{a}</td><td>{bb}</td><td>{cc}</td><td>{d}</td></tr>' for i, (a, bb, cc, d) in enumerate(wy["rows"]))
    reasons = "".join(f"<li><b>{h}</b><span>{x}</span></li>" for h, x in wy["reasons"])
    faqs = "".join(f'<details data-fade><summary>{q}<span class="pm" aria-hidden="true"></span></summary><p class="a">{a}</p></details>' for q, a in fq["items"])
    dl = "".join(f"<dt>{a}</dt><dd>{x}</dd>" for a, x in ct["dl"])
    f = ct["f"]
    needs = "".join(f"<option>{x}</option>" for x in f["needs"])
    fnav = "".join(f'<a href="{h}">{x}</a>' for h, x in ft["nav"])
    flegal = "".join(f'<a href="{b}{h}">{x}</a>' for h, x in ft["legal"])

    return f'''
  <section class="v2 work2" id="work" aria-labelledby="work-title">
    <div class="v2__bg" style="background-image:url({b}media/bg/bg-spires.webp)" aria-hidden="true"></div>
    <div class="marquee" aria-hidden="true"><div class="marquee__track">{mq}</div></div>
    <div class="container">
      {idx(w["idx"], w["label"], w["right"])}
      <h2 class="serif" id="work-title" data-split>{w["title"]}</h2>
    </div>
    {reel}
    <div class="container">
      <ol class="cases">{cases}</ol>
    </div>
  </section>

  <section class="v2 offer" id="offer" aria-labelledby="offer-title">
    <div class="v2__bg" style="background-image:url({b}media/bg/bg-peaks.webp)" aria-hidden="true"></div>
    <div class="container">
      {idx(o["idx"], o["label"], o["right"])}
      <h2 class="serif" id="offer-title" data-split>{o["title"]}</h2>
      <div class="offer__grid">
        <ol class="pains">{pains}</ol>
        <div class="stat" data-fade><p class="stat__num"><span data-count="{o["stat"]}">{o["stat"]}</span><sup>%</sup></p><p class="stat__txt">{o["stat_txt"]}</p><p class="stat__src">{o["stat_src"]}</p></div>
      </div>
      <div class="answer">
        <p class="serif" data-split>{o["answer"]}</p>
        <div data-fade><p class="lead">{o["answer_lead"]}</p><a class="cta" href="#contact">{o["cta"]} <span class="arr" aria-hidden="true">→</span></a></div>
      </div>
    </div>
  </section>

  <section class="v2 system" id="system" aria-labelledby="system-title">
    <div class="container">
      {idx(s["idx"], s["label"], s["right"])}
      <h2 class="serif" id="system-title" data-split>{s["title"]}</h2>
      <ol class="climb">{climb}</ol>
      <div class="system__foot" data-fade><p>{s["foot"]}</p><a class="cta" href="#process">{s["cta"]} <span class="arr" aria-hidden="true">↓</span></a></div>
    </div>
  </section>

  <section class="v2 process" id="process" aria-labelledby="process-title">
    <div class="v2__bg" style="background-image:url({b}media/bg/bg-walls.webp)" aria-hidden="true"></div>
    <div class="process__pin"><div class="process__sticky"><div class="container">
      {idx(p["idx"], p["label"], p["right"])}
      <div class="process__intro"><h2 class="serif" id="process-title" data-split>{p["title"]}</h2><p class="lead" data-fade>{p["lead"]}</p></div>
      <ol class="steps">{steps}</ol>
    </div></div></div>
  </section>

  <section class="v2 services" id="services" aria-labelledby="services-title">
    <div class="container">
      {idx(sv["idx"], sv["label"], sv["right"])}
      <h2 class="serif" id="services-title" data-split>{sv["title"]}</h2>
      <div class="packs">{packs}</div>
      <div class="extras" data-fade>{extras}</div>
      {calc}
    </div>
  </section>

  <section class="v2 why" id="why" aria-labelledby="why-title">
    <div class="container">
      {idx(wy["idx"], wy["label"], wy["right"])}
      <h2 class="serif" id="why-title" data-split>{wy["title"]}</h2>
      <div class="why__grid">
        <figure class="founder" data-fade>
          <img class="mono" src="{b}media/logo/aik-lockup.png" alt="" width="197" height="90" loading="lazy">
          <p class="nm">{wy["name"]}</p><p class="rl">{wy["role"]}</p><q>{wy["quote"]}</q>
        </figure>
        <div data-fade>
          <table class="compare"><thead><tr>{"".join(f"<th>{x}</th>" for x in wy["th"])}</tr></thead><tbody>{rows}</tbody></table>
          <ul class="reasons">{reasons}</ul>
        </div>
      </div>
    </div>
  </section>

  <section class="v2 faq" id="faq" aria-labelledby="faq-title">
    <div class="container">
      {idx(fq["idx"], fq["label"], fq["right"])}
      <h2 class="serif" id="faq-title" data-split>{fq["title"]}</h2>
      <div class="faq__list">{faqs}</div>
    </div>
  </section>

  <section class="v2 contact2" id="contact" aria-labelledby="contact-title" data-contact-email="">
    <div class="v2__bg" style="background-image:url({b}media/bg/bg-dusk.webp)" aria-hidden="true"></div>
    <div class="container">
      {idx(ct["idx"], ct["label"], ct["right"])}
      <h2 id="contact-title" data-split>{ct["title"]}</h2>
      <div class="contact__grid">
        <div class="contact__side" data-fade><p>{ct["lead"]}</p><dl>{dl}</dl></div>
        <form class="form" name="enquiry" method="POST" data-netlify="true" netlify-honeypot="bot" data-fade>
          <input type="hidden" name="form-name" value="enquiry"><p hidden><label>Bot <input name="bot"></label></p>
          <div><label for="f-name">{f["name"]}</label><input id="f-name" name="name" autocomplete="name" required></div>
          <div><label for="f-email">{f["email"]}</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
          <div><label for="f-site">{f["site"]}</label><input id="f-site" name="website" type="url" inputmode="url" placeholder="https://"></div>
          <div><label for="f-need">{f["need"]}</label><select id="f-need" name="need">{needs}</select></div>
          <div class="full"><label for="f-msg">{f["msg"]}</label><textarea id="f-msg" name="message"></textarea></div>
          <div class="full actions"><button class="cta cta--solid" type="submit">{f["send"]} <span class="arr" aria-hidden="true">→</span></button><p class="fine">{f["fine"]}</p></div>
          <p class="form__ok" role="status">{f["ok"]}</p>
        </form>
      </div>
    </div>
  </section>

  <footer class="foot">
    <div class="container">
      <p class="foot__mega" aria-hidden="true">AIK Studio</p>
      <div class="foot__row"><nav aria-label="Footer">{fnav}</nav><nav aria-label="Legal">{flegal}</nav><span>Potsdam · Berlin</span><span>{ft["copy"]}</span></div>
    </div>
  </footer>
'''


for lang, path in [("en", "index.html"), ("de", "de/index.html")]:
    c = T[lang]
    fp = f"{ROOT}/{path}"
    s = open(fp).read()
    a = s.index('</section>', re.search(r'<section class="(?:hero[234]|hx)"', s).start()) + len('</section>')
    e = s.index('</main>')
    s = s[:a] + "\n" + build(c) + s[e:]
    # header nav
    nav = "".join(f'<li><a href="{h}">{x}</a></li>' for h, x in c["nav"])
    s = re.sub(r'<ul class="nav__list">.*?</ul>', f'<ul class="nav__list">{nav}</ul>', s, count=1, flags=re.S)
    s = re.sub(r'(<a class="btn btn--line btn--sm" href="#contact">)[^<]*(</a>)', rf'\g<1>{c["talk"]}\g<2>', s, count=1)
    b = c["base"]
    for old in ["work.css", "sections.css"]:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/{old}">\n', "")
    if "css/v2.css" not in s:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/hero.css">', f'<link rel="stylesheet" href="{b}css/hero.css">\n<link rel="stylesheet" href="{b}css/v2.css">')
    s = s.replace(f'<script src="{b}js/work.js" defer></script>', f'<script src="{b}js/v2.js" defer></script>')
    for js in ["curve-reel.js"]:
        if f"js/{js}" not in s:
            s = s.replace(f'<script src="{b}js/v2.js" defer></script>', f'<script src="{b}js/v2.js" defer></script>\n<script src="{b}js/{js}" defer></script>')
    if False:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/v2.css">', f'<link rel="stylesheet" href="{b}css/v2.css">\n<link rel="stylesheet" href="{b}css/liquid-nav.css">')
    for js in ["curve-reel.js"]:
        if f"js/{js}" not in s:
            s = s.replace(f'<script src="{b}js/v2.js" defer></script>', f'<script src="{b}js/v2.js" defer></script>\n<script src="{b}js/{js}" defer></script>')
    if False:
        s = s.replace(f'<link rel="stylesheet" href="{b}css/v2.css">', f'<link rel="stylesheet" href="{b}css/v2.css">\n<link rel="stylesheet" href="{b}css/liquid-nav.css">')
    open(fp, "w").write(s)
    print(path, "ok", s.count("<section"), "sections")
