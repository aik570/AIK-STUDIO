"""AIK Studio: writes index.html (EN) and de/index.html (DE) in full from one content table.

    python3 tools/build_site.py .

Structure (approved, do not reorder): Hero → Work → Problem → System → Process →
Services & prices + calculator → Why AIK → Questions → Contact → footer.
Plus: the six-step enquiry (dialog), the floating "Start a project" button.

Facts only: prices are the owner's own ranges, concepts are labelled as concepts,
no invented clients, numbers or testimonials. The owner's e-mail is NOT on the page
(not approved); enquiries go through Netlify Forms (the notification address is set in
the Netlify dashboard) or WhatsApp."""
import html, json, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
PLATE = json.loads((ROOT / 'media/hero4/plate.json').read_text())
LOADER = (ROOT / 'tools/partials/loader.html').read_text()

WA = '4915221595565'
WA_SHOW = '+49 1522 1595565'
SOCIAL = [('WhatsApp', f'https://wa.me/{WA}'), ('Telegram', 'https://t.me/Koliayounow'),
          ('Instagram', 'https://www.instagram.com/kolia_sb/'), ('LinkedIn', 'https://www.linkedin.com/in/nikolay-riabov-202920422')]

# AIK, drawn from the logo outline (media/loader: the mark's own vector trace), cleaned to straight edges.
AIK_VIEWBOX = '262 274 1348 534'
AIK_PATHS = [
    'M611 413 L872 800 L775 800 L705 690 L562 690 L591 651 L676 651 L611 548 L401 800 L277 800 Z',   # A
    'M918 283 L1001 342 L1001 800 L918 800 Z',                                                          # I
    'M1095 411 L1176 411 L1176 800 L1095 800 Z',                                                        # K stem
    'M1176 584 L1425 369 L1500 418 L1316 573 L1595 800 L1474 800 L1196 588 L1176 603 Z',               # K arms
]

ARROW = '<span class="btn__arrow" aria-hidden="true">→</span>'
OUT = '<span class="btn__arrow" aria-hidden="true">↗</span>'
CHECK = '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5 6.5 12 13 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PLUS = '<svg class="ico" viewBox="0 0 16 16" aria-hidden="true"><path d="M8 2v12M2 8h12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
CLOSE = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 3l10 10M13 3 3 13" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
PHONE = '<svg class="ico" viewBox="0 0 20 20" aria-hidden="true"><path d="M6.6 2.5 8.4 6c.2.4.1.9-.2 1.2L6.9 8.4a9.6 9.6 0 0 0 4.7 4.7l1.2-1.3c.3-.3.8-.4 1.2-.2l3.5 1.8c.4.2.6.7.5 1.1l-.5 2.1c-.1.5-.6.9-1.1.9A14.7 14.7 0 0 1 1.5 2.6c0-.5.4-1 .9-1.1l2.1-.5c.5-.1.9.1 1.1.5Z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>'
BUBBLE = '<svg class="ico" viewBox="0 0 20 20" aria-hidden="true"><path d="M10 2.5c4.4 0 7.5 2.9 7.5 6.6s-3.1 6.6-7.5 6.6c-.9 0-1.7-.1-2.5-.3L3.5 17l1-3.3A6.3 6.3 0 0 1 2.5 9.1C2.5 5.4 5.6 2.5 10 2.5Z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>'

T = {
'en': dict(
  lang='en', b='./', other='./de/', loading='Loading AIK Studio',
  title='AIK Studio | Premium websites for businesses in Berlin and Potsdam',
  desc='AIK Studio plans, writes, designs and builds websites for businesses in Berlin, Potsdam and across Germany. Redesign, new websites and SEO. Prices from 900 €.',
  skip='Skip to content', menu='Menu', close='Close',
  nav=[('#work', 'Work'), ('#services', 'Services'), ('#process', 'Approach'), ('#why', 'About'), ('#contact', 'Contact')],
  talk='Let’s talk', start='Start a project', pause='Pause motion', play='Resume motion',
  hero=dict(kicker=['Digital experiences', 'built with intention'], h=['Your business deserves', 'a better website.'],
    lead='We turn your business into a digital experience that builds trust, communicates value and moves people to act.',
    cta1='Discuss your project', cta2='Explore our work', skip='Skip intro',
    stages=['Strategy', 'UX design', 'Development', 'Growth'],
    alt='Three snowy peaks above a sea of clouds at sunset'),
  lbl=dict(work='Work', problem='The problem', system='The system', process='Your path', services='Services &amp; prices', why='Why AIK', faq='Questions', contact='Contact'),
  ghost=dict(work='WORK', system='SYSTEM', process='PATH', services='PRICES', why='AIK', faq='QUESTIONS', contact='CONTACT'),
  work=dict(title='Selected work', note='Concepts are labelled as concepts. Live sites open in a new tab.', live='View live', concept='Concept', site='Website', drag='Drag or scroll',
    cases=[('MA’LOA', 'Restaurants · Eschborn', 'concept', 'Homepage and franchise page for a Hawaiian poké bowl chain. Self-initiated concept, not the live maloa.com.', 'maloa-hero', 'https://maolaheropage.netlify.app/'),
           ('BLF Service', 'Trees & land · Seddiner See', 'site', 'Website for a tree, land and forestry service: services all year round, enquiries and jobs.', 'blf-service', 'https://lucky-parfait-f6d633.netlify.app/'),
           ('Architekturcontor', 'Architecture · Potsdam', 'concept', 'Redesign concept for an architecture office focused on schools: project catalogue and a four-step enquiry.', 'architekturcontor', 'https://nimble-hummingbird-a98d10.netlify.app/'),
           ('Gute Räume', 'Interior design · Potsdam', 'concept', 'Concept for a studio for spatial concepts and circular interior design.', 'raum-studio', 'https://helpful-otter-6da26b.netlify.app/'),
           ('Handy-Chirurg', 'Phone repair · Potsdam', 'site', 'Website for a phone repair shop in Potsdam: design and build.', '', 'https://handychirurg.de')]),
  problem=dict(title='Most websites lose customers quietly.',
    pains=[('Slow', 'Visitors leave before the first screen has loaded.'),
           ('Weak on the phone', 'Most of your customers see a squeezed desktop site.'),
           ('No clear next step', 'People look around, don’t know where to click and call a competitor.'),
           ('Smaller than you are', 'Online, a strong business looks small. That costs trust before the first call.')],
    stat='53', stat_txt='of mobile visits are abandoned when a page takes longer than three seconds to load.', stat_src='Source: Google',
    answer='We rebuild it turnkey: a website that makes its point in three seconds, guides people through the page and ends in an enquiry. The technology is our job, not yours.',
    cta='Talk about your project'),
  system=dict(title='A website is a system, not a picture.',
    steps=[('3 s', 'Hook', 'In the first three seconds the visitor understands who you are and why it matters to them.'),
           ('1 path', 'Guide', 'The page leads step by step: offer, proof, price, next step. No dead ends.'),
           ('1 click', 'Enquiry', 'Call, WhatsApp or form. One clear action on every screen, especially on the phone.')],
    foot='And you can see it working: analytics show how many enquiries the website brings.'),
  process=dict(title='One to three calls. We do the rest.',
    lead='Structure, copy, design, development and legal pages are on us. Plan, timeline and price are clear from the start.',
    you='Your time',
    steps=[('Call', 'We understand the business', 'Your goals, your customers and what the old site gets wrong.', '30 min'),
           ('Concept', 'You see the direction', 'Structure and the first screens, as a real page in your browser.', '30 min'),
           ('Build', 'We do the work', 'Design, copy, development, speed, SEO basics, legal pages set up.', 'none'),
           ('Launch', 'Live and handed over', 'All access is yours. We stay on for care if you want.', '30 min')]),
  services=dict(title='Prices you know before we start.', lead='Three packages, one price range each. The exact price is fixed after the first call.',
    packs=[('landing', 'Landing page', '900 – 1 400 €', 'One page, one goal', ['One page built for one offer', 'Fast on every phone', 'Contact form or WhatsApp', 'Basic SEO'], False),
           ('site', 'Website', '2 400 – 4 600 €', 'Redesign or new', ['Full redesign, built for enquiries', 'Structure, copy, design, build', 'Speed and technical SEO', 'Legal pages set up', 'First month of care free'], True),
           ('premium', 'Premium', 'from 6 900 €', 'Signature site', ['Everything in Website', 'Signature hero: film, 3D or animation', 'Up to 12 pages, two languages', 'Admin panel and 3 months of care', 'Priority timeline'], False)],
    badge='Recommended', pick='Choose', extras_lbl='Add on any time', extras=['Care from 150 €/month', 'Admin panel +600 €', 'Speed optimisation', 'SEO', '3D visualisation', 'Market analysis'],
    calc=dict(title='Estimate your project', type='Type', types=[('landing', 'Landing page'), ('site', 'Website'), ('big', 'Large project')],
      pages='Pages', cms='Admin panel (edit it yourself)', cms_note='+600 €', care='Care after launch', cares=[('0', 'None'), ('150', '150 €/mo'), ('300', '300 €/mo')],
      out='Your estimate', note='A guide, not an offer. The exact price comes after a 30-minute call and is fixed before we start.', go='Send this estimate',
      t=dict(pages='pages', noCare='No care plan', care='+ {n} € per month for care'))),
  why=dict(title='Agency quality. One person you talk to.',
    name='Nikolay Riabov', role='Founder, AIK Studio · Potsdam / Berlin',
    quote='You talk to the person who builds your website. No managers in between.',
    th=['', 'Price', 'Upside', 'Downside'],
    rows=[('Website builder', '7–36 €/mo', 'Cheap', 'You do it all yourself; looks like a template'),
          ('Freelancer', '800–3 000 €', 'Cheaper than an agency', 'Quality depends on the person'),
          ('Agency', '2 000–8 000 €', 'Team and process', 'Higher price, longer loops, a manager in between'),
          ('AIK Studio', '2 400–4 600 €', 'Turnkey, built for enquiries, direct', 'One founder, so every access is handed to you')],
    reasons=[('Fast', 'A clear plan and short loops instead of months of back and forth.'),
             ('Clear', 'Price, timeline and steps fixed before we start.'),
             ('Reliable', 'Contract, 50 % prepayment, all access handed over.'),
             ('Hand-built', 'Designed and coded for you, checked on real phones. No templates.')]),
  faq=dict(title='Questions, answered.',
    items=[('How much of my time does it take?', 'One to three calls of 30 minutes. We prepare everything else and show you results, not homework.'),
           ('What does it cost?', 'A landing page is 900–1 400 €, a website 2 400–4 600 €, larger projects more. You get a fixed price after the first call.'),
           ('Who owns the website?', 'You do. Domain, hosting, code and all access are handed over at launch.'),
           ('How does payment work?', 'We sign a short contract. 50 % before we start, 50 % at launch.'),
           ('What about Impressum, Datenschutz and DSGVO?', 'We set up the legal pages and build the site privacy-friendly: no tracking, no third-party fonts or scripts. The legal texts themselves come from a recognised legal-text generator or your lawyer; we don’t give legal advice.'),
           ('What happens after launch?', 'Care by subscription (150–300 € per month) or by the hour, or you run it yourself.'),
           ('Do you work in German and English?', 'Yes. Websites in German, English or both.'),
           ('How do I start?', 'Press “Start a project”, answer six short questions, and we get back to you within one working day. Or write on WhatsApp.')]),
  contact=dict(title='Let’s talk about your project.', lead='Tell us what your business does and what the website should achieve. We reply within one working day.',
    start='Start a project', start_sub='Six short questions, about two minutes.', wa='Write on WhatsApp', fine='Free and non-binding.', badge='Start a project · Start a project · '),
  foot=dict(studio='Studio', services='Services', contact='Contact',
    svc=['Website redesign', 'New website', 'Landing page', 'SEO and speed', 'Care'],
    who='AIK Studio · Nikolay Riabov · Potsdam / Berlin', legal=[('impressum.html', 'Impressum'), ('datenschutz.html', 'Datenschutz')], copy='© 2026 AIK Studio', top='Back to top'),
  form=dict(label='Start a project', of='of', back='Back', next='Next', send='Send request', sending='Sending…', fine='Free and non-binding.',
    s=[dict(t='What can we help you with?', h='Choose any', name='need', multi=True,
            o=['Website redesign', 'New website', 'Landing page', 'SEO and speed', 'Care and updates', 'Something else']),
       dict(t='What is your goal?', h='Choose any', name='goal', multi=True,
            o=['More enquiries', 'Look more professional', 'Stand out from competitors', 'Launch something new', 'Not sure yet']),
       dict(t='When would you like to start?', h='Pick one', name='start', multi=False,
            o=['As soon as possible', 'In the next two weeks', 'Next month', 'Just looking around']),
       dict(t='What is your budget?', h='Drag the slider to your amount.', name='budget'),
       dict(t='How would you like to continue?', name='way', o=[('call', 'Book a call', '15 minutes, by phone or WhatsApp'), ('request', 'Send a request', 'We reply within one working day')]),
       dict(t='How can we reach you?', h='That’s it.', name='contact')],
    fits=[(1400, 'fits a landing page'), (2300, 'between a landing page and a website'), (4600, 'fits a website'), (6800, 'a large website'), (99999, 'fits Premium')],
    f=dict(name='Name', name_ph='First and last name', phone='Phone / WhatsApp', phone_opt='(optional)', phone_ph='+49 151 23456789',
           email='E-mail', email_ph='you@company.de', privacy='We only use your details to answer your enquiry.', privacy_link='Privacy policy',
           need_phone='Please add a phone number so we can call you.', need_email='Please add an e-mail address.', need_name='Please add your name.'),
    ok_t='Thank you.', ok='Your request is with us. We get back to you within one working day.', ok_wa='Prefer WhatsApp? Write now',
    err='That didn’t go through. Send the same request on WhatsApp instead:', err_wa='Send on WhatsApp',
    wa_intro='Hello Nikolay, I would like to start a project.', wa_labels=dict(need='Need', goal='Goal', start='Start', budget='Budget', way='Next step', name='Name', phone='Phone', email='E-mail')),
),
'de': dict(
  lang='de', b='../', other='../', loading='AIK Studio wird geladen',
  title='AIK Studio | Premium-Websites für Unternehmen in Berlin und Potsdam',
  desc='AIK Studio plant, textet, gestaltet und baut Websites für Unternehmen in Berlin, Potsdam und ganz Deutschland. Redesign, neue Websites und SEO. Preise ab 900 €.',
  skip='Zum Inhalt', menu='Menü', close='Schließen',
  nav=[('#work', 'Arbeiten'), ('#services', 'Leistungen'), ('#process', 'Ablauf'), ('#why', 'Über uns'), ('#contact', 'Kontakt')],
  talk='Projekt anfragen', start='Projekt starten', pause='Bewegung anhalten', play='Bewegung fortsetzen',
  hero=dict(kicker=['Digitale Erlebnisse,', 'mit Absicht gebaut'], h=['Ihr Unternehmen verdient', 'eine bessere Website.'],
    lead='Wir machen Ihr Unternehmen zu einem digitalen Auftritt, der Vertrauen schafft, Wert vermittelt und Menschen zum Handeln bringt.',
    cta1='Projekt besprechen', cta2='Arbeiten ansehen', skip='Intro überspringen',
    stages=['Strategie', 'UX-Design', 'Entwicklung', 'Wachstum'],
    alt='Drei verschneite Gipfel über einem Wolkenmeer bei Sonnenuntergang'),
  lbl=dict(work='Arbeiten', problem='Das Problem', system='Das System', process='Ihr Weg', services='Leistungen &amp; Preise', why='Warum AIK', faq='Fragen', contact='Kontakt'),
  ghost=dict(work='ARBEITEN', system='SYSTEM', process='WEG', services='PREISE', why='AIK', faq='FRAGEN', contact='KONTAKT'),
  work=dict(title='Ausgewählte Arbeiten', note='Konzepte sind als Konzepte gekennzeichnet. Live-Seiten öffnen in einem neuen Tab.', live='Live ansehen', concept='Konzept', site='Website', drag='Ziehen oder scrollen',
    cases=[('MA’LOA', 'Gastronomie · Eschborn', 'concept', 'Startseite und Franchise-Seite für eine Hawaiian-Poké-Bowl-Kette. Eigeninitiatives Konzept, nicht die Live-Seite maloa.com.', 'maloa-hero', 'https://maolaheropage.netlify.app/'),
           ('BLF Service', 'Baum & Land · Seddiner See', 'site', 'Website für einen Baum-, Land- und Forstservice: Leistungen das ganze Jahr, Anfragen und Jobs.', 'blf-service', 'https://lucky-parfait-f6d633.netlify.app/'),
           ('Architekturcontor', 'Architektur · Potsdam', 'concept', 'Redesign-Konzept für ein Architekturbüro mit Schwerpunkt Schulbau: Werkverzeichnis und Anfrage in vier Schritten.', 'architekturcontor', 'https://nimble-hummingbird-a98d10.netlify.app/'),
           ('Gute Räume', 'Interior Design · Potsdam', 'concept', 'Konzept für ein Studio für Raumkonzepte und zirkuläres Interior Design.', 'raum-studio', 'https://helpful-otter-6da26b.netlify.app/'),
           ('Handy-Chirurg', 'Handyreparatur · Potsdam', 'site', 'Website für eine Handywerkstatt in Potsdam: Design und Umsetzung.', '', 'https://handychirurg.de')]),
  problem=dict(title='Die meisten Websites verlieren Kunden. Leise.',
    pains=[('Langsam', 'Besucher gehen, bevor der erste Bildschirm geladen ist.'),
           ('Schwach auf dem Handy', 'Die meisten Kunden sehen eine gequetschte Desktop-Seite.'),
           ('Kein klarer nächster Schritt', 'Man schaut, weiß nicht, wo man klicken soll, und ruft die Konkurrenz an.'),
           ('Kleiner, als Sie sind', 'Online wirkt ein starkes Unternehmen klein. Das kostet Vertrauen vor dem ersten Anruf.')],
    stat='53', stat_txt='der mobilen Besuche werden abgebrochen, wenn eine Seite länger als drei Sekunden lädt.', stat_src='Quelle: Google',
    answer='Wir bauen sie schlüsselfertig neu: eine Website, die in drei Sekunden überzeugt, Besucher durch die Seite führt und mit einer Anfrage endet. Die Technik ist unsere Aufgabe, nicht Ihre.',
    cta='Projekt besprechen'),
  system=dict(title='Eine Website ist ein System, kein Bild.',
    steps=[('3 s', 'Überzeugen', 'In den ersten drei Sekunden versteht der Besucher, wer Sie sind und warum das für ihn zählt.'),
           ('1 Weg', 'Führen', 'Die Seite führt Schritt für Schritt: Angebot, Beweise, Preis, nächster Schritt. Keine Sackgassen.'),
           ('1 Klick', 'Anfrage', 'Anruf, WhatsApp oder Formular. Eine klare Aktion auf jedem Bildschirm, gerade auf dem Handy.')],
    foot='Und Sie sehen, dass es funktioniert: Die Analyse zeigt, wie viele Anfragen die Website bringt.'),
  process=dict(title='Ein bis drei Gespräche. Den Rest machen wir.',
    lead='Struktur, Texte, Design, Entwicklung und rechtliche Seiten übernehmen wir. Plan, Zeitrahmen und Preis stehen von Anfang an fest.',
    you='Ihre Zeit',
    steps=[('Gespräch', 'Wir verstehen Ihr Geschäft', 'Ihre Ziele, Ihre Kunden und was die alte Seite falsch macht.', '30 Min.'),
           ('Konzept', 'Sie sehen die Richtung', 'Struktur und erste Bildschirme, als echte Seite in Ihrem Browser.', '30 Min.'),
           ('Umsetzung', 'Wir machen die Arbeit', 'Design, Texte, Entwicklung, Tempo, SEO-Basis, Rechtsseiten eingebunden.', 'keine'),
           ('Launch', 'Live und übergeben', 'Alle Zugänge gehören Ihnen. Auf Wunsch betreuen wir weiter.', '30 Min.')]),
  services=dict(title='Preise, die Sie vorher kennen.', lead='Drei Pakete, je eine Preisspanne. Den genauen Preis legen wir nach dem ersten Gespräch fest.',
    packs=[('landing', 'Landingpage', '900 – 1.400 €', 'Eine Seite, ein Ziel', ['Eine Seite für ein Angebot', 'Schnell auf jedem Handy', 'Kontaktformular oder WhatsApp', 'SEO-Grundlagen'], False),
           ('site', 'Website', '2.400 – 4.600 €', 'Redesign oder neu', ['Komplettes Redesign für Anfragen', 'Struktur, Texte, Design, Umsetzung', 'Tempo und technisches SEO', 'Rechtsseiten eingebunden', 'Erster Monat Betreuung gratis'], True),
           ('premium', 'Premium', 'ab 6.900 €', 'Signature-Website', ['Alles aus „Website“', 'Signature-Hero: Film, 3D oder Animation', 'Bis zu 12 Seiten, zweisprachig', 'Admin-Panel und 3 Monate Betreuung', 'Priorisierter Zeitplan'], False)],
    badge='Empfehlung', pick='Auswählen', extras_lbl='Jederzeit dazu', extras=['Betreuung ab 150 €/Monat', 'Admin-Panel +600 €', 'Tempo-Optimierung', 'SEO', '3D-Visualisierung', 'Marktanalyse'],
    calc=dict(title='Projekt schätzen', type='Art', types=[('landing', 'Landingpage'), ('site', 'Website'), ('big', 'Großes Projekt')],
      pages='Seiten', cms='Admin-Panel (selbst pflegen)', cms_note='+600 €', care='Betreuung nach dem Launch', cares=[('0', 'Keine'), ('150', '150 €/Mon.'), ('300', '300 €/Mon.')],
      out='Ihre Schätzung', note='Eine Orientierung, kein Angebot. Den genauen Preis erhalten Sie nach einem 30-Minuten-Gespräch, fest vor dem Start.', go='Schätzung senden',
      t=dict(pages='Seiten', noCare='Ohne Betreuung', care='+ {n} € pro Monat Betreuung'))),
  why=dict(title='Agentur-Qualität. Ein Ansprechpartner.',
    name='Nikolay Riabov', role='Gründer, AIK Studio · Potsdam / Berlin',
    quote='Sie sprechen mit dem Menschen, der Ihre Website baut. Keine Manager dazwischen.',
    th=['', 'Preis', 'Vorteil', 'Nachteil'],
    rows=[('Baukasten', '7–36 €/Mon.', 'Günstig', 'Alles selbst machen; wirkt wie eine Vorlage'),
          ('Freelancer', '800–3.000 €', 'Günstiger als Agentur', 'Qualität hängt von der Person ab'),
          ('Agentur', '2.000–8.000 €', 'Team und Prozess', 'Höherer Preis, längere Schleifen, ein Manager dazwischen'),
          ('AIK Studio', '2.400–4.600 €', 'Schlüsselfertig, für Anfragen, direkt', 'Ein Gründer, deshalb bekommen Sie alle Zugänge')],
    reasons=[('Schnell', 'Klarer Plan und kurze Schleifen statt monatelangem Hin und Her.'),
             ('Klar', 'Preis, Zeitrahmen und Schritte stehen vor dem Start fest.'),
             ('Verlässlich', 'Vertrag, 50 % Anzahlung, alle Zugänge werden übergeben.'),
             ('Von Hand gebaut', 'Für Sie gestaltet und programmiert, auf echten Handys geprüft. Keine Vorlagen.')]),
  faq=dict(title='Fragen, beantwortet.',
    items=[('Wie viel Zeit kostet mich das?', 'Ein bis drei Gespräche à 30 Minuten. Alles andere bereiten wir vor und zeigen Ihnen Ergebnisse statt Hausaufgaben.'),
           ('Was kostet das?', 'Eine Landingpage 900–1.400 €, eine Website 2.400–4.600 €, größere Projekte mehr. Nach dem ersten Gespräch erhalten Sie einen Festpreis.'),
           ('Wem gehört die Website?', 'Ihnen. Domain, Hosting, Code und alle Zugänge werden beim Launch übergeben.'),
           ('Wie läuft die Bezahlung?', 'Wir schließen einen kurzen Vertrag. 50 % vor dem Start, 50 % zum Launch.'),
           ('Und Impressum, Datenschutz, DSGVO?', 'Wir binden die Rechtsseiten ein und bauen die Website datenschutzfreundlich: ohne Tracking, ohne fremde Schriften oder Skripte. Die Rechtstexte selbst kommen aus einem anerkannten Rechtstext-Generator oder von Ihrem Anwalt; Rechtsberatung leisten wir nicht.'),
           ('Was passiert nach dem Launch?', 'Betreuung im Abo (150–300 € pro Monat) oder nach Aufwand, oder Sie pflegen die Seite selbst.'),
           ('Arbeiten Sie auf Deutsch und Englisch?', 'Ja. Websites auf Deutsch, Englisch oder in beiden Sprachen.'),
           ('Wie fange ich an?', 'Klicken Sie auf „Projekt starten“, beantworten Sie sechs kurze Fragen, und wir melden uns innerhalb eines Werktags. Oder schreiben Sie per WhatsApp.')]),
  contact=dict(title='Sprechen wir über Ihr Projekt.', lead='Erzählen Sie, was Ihr Unternehmen macht und was die Website erreichen soll. Wir antworten innerhalb eines Werktags.',
    start='Projekt starten', start_sub='Sechs kurze Fragen, etwa zwei Minuten.', wa='Per WhatsApp schreiben', fine='Kostenlos und unverbindlich.', badge='Projekt starten · Projekt starten · '),
  foot=dict(studio='Studio', services='Leistungen', contact='Kontakt',
    svc=['Website-Redesign', 'Neue Website', 'Landingpage', 'SEO und Tempo', 'Betreuung'],
    who='AIK Studio · Nikolay Riabov · Potsdam / Berlin', legal=[('impressum.html', 'Impressum'), ('datenschutz.html', 'Datenschutz')], copy='© 2026 AIK Studio', top='Nach oben'),
  form=dict(label='Projekt starten', of='von', back='Zurück', next='Weiter', send='Anfrage senden', sending='Wird gesendet…', fine='Kostenlos und unverbindlich.',
    s=[dict(t='Wobei dürfen wir helfen?', h='Mehrere möglich', name='need', multi=True,
            o=['Website-Redesign', 'Neue Website', 'Landingpage', 'SEO und Tempo', 'Betreuung und Pflege', 'Etwas anderes']),
       dict(t='Was ist Ihr Ziel?', h='Mehrere möglich', name='goal', multi=True,
            o=['Mehr Anfragen', 'Professioneller auftreten', 'Mich von anderen abheben', 'Etwas Neues starten', 'Weiß ich noch nicht genau']),
       dict(t='Wann möchten Sie starten?', h='Eins auswählen', name='start', multi=False,
            o=['So schnell wie möglich', 'In den nächsten zwei Wochen', 'Im nächsten Monat', 'Ich schaue mich erst um']),
       dict(t='Mit welchem Budget planen Sie?', h='Ziehen Sie den Regler auf Ihren Betrag.', name='budget'),
       dict(t='Wie möchten Sie weitermachen?', name='way', o=[('call', 'Gespräch vereinbaren', '15 Minuten, Anruf oder WhatsApp'), ('request', 'Anfrage senden', 'Wir antworten innerhalb eines Werktags')]),
       dict(t='Wie erreichen wir Sie?', h='Das ist schon alles.', name='contact')],
    fits=[(1400, 'passt zu einer Landingpage'), (2300, 'zwischen Landingpage und Website'), (4600, 'passt zu einer Website'), (6800, 'eine große Website'), (99999, 'passt zu Premium')],
    f=dict(name='Name', name_ph='Vor- und Nachname', phone='Telefon / WhatsApp', phone_opt='(freiwillig)', phone_ph='0151 23456789',
           email='E-Mail', email_ph='sie@firma.de', privacy='Wir nutzen Ihre Angaben nur, um Ihre Anfrage zu beantworten.', privacy_link='Datenschutz',
           need_phone='Bitte geben Sie eine Telefonnummer an, damit wir Sie anrufen können.', need_email='Bitte geben Sie eine E-Mail-Adresse an.', need_name='Bitte geben Sie Ihren Namen an.'),
    ok_t='Vielen Dank.', ok='Ihre Anfrage ist bei uns. Wir melden uns innerhalb eines Werktags.', ok_wa='Lieber WhatsApp? Jetzt schreiben',
    err='Das hat nicht geklappt. Senden Sie dieselbe Anfrage per WhatsApp:', err_wa='Per WhatsApp senden',
    wa_intro='Hallo Nikolay, ich möchte ein Projekt starten.', wa_labels=dict(need='Bedarf', goal='Ziel', start='Start', budget='Budget', way='Nächster Schritt', name='Name', phone='Telefon', email='E-Mail')),
),
}

e = html.escape

# Tax status for the price note (PAngV). Set it when known:
#   'kleinunternehmer' → no VAT is charged (§ 19 UStG)
#   'ust'              → prices plus VAT; then the offer must be stated as business-only
#   None               → no note (NOT ready for launch: tools/dist.py refuses to publish)
TAX = None
TAX_NOTE = {
    'kleinunternehmer': {'en': 'All prices are final prices. No VAT is shown (small business, § 19 UStG).',
                         'de': 'Alle Preise sind Endpreise. Kein Ausweis der Umsatzsteuer gemäß § 19 UStG (Kleinunternehmerregelung).'},
    'ust': {'en': 'Prices plus VAT. Our offer is aimed exclusively at businesses.',
            'de': 'Preise zzgl. gesetzlicher Umsatzsteuer. Unser Angebot richtet sich ausschließlich an Unternehmer.'},
}

# which landscape each part of the page stands in (media/world/*); the hero has its own
SCENE = {'work': 'spires', 'problem': 'clouds', 'system': 'peaks', 'process': 'walls',
         'services': 'dusk', 'why': 'eagle', 'faq': 'clouds', 'contact': 'dawn'}
SYSTEM_STILLS = ['f012', 'f096', 'f132']
INDEX = {'work': 1, 'problem': 2, 'system': 3, 'process': 4, 'services': 5, 'why': 6, 'faq': 7, 'contact': 8}
PATH_STILLS = ['f001', 'f060', 'f108', 'f132']


EXTRA = {
    'en': dict(path=['Offer', 'Proof', 'Price', 'Enquiry'], click='Get a quote', corner=[('Digital experiences', 'built with intention'), ('Potsdam · Berlin', 'Germany')],
               facts=[('1', 'person you talk to: the founder'), ('1 day', 'until you get a reply'), ('DE · EN', 'websites in both languages'), ('100 %', 'of the access is handed to you')],
               vs_up='Upside', vs_down='Downside', vs_badge='Your choice?', word='LET’S TALK', faq_more='Still a question? Write on WhatsApp',
               prices='PRICES', from_='from', ans='answers'),
    'de': dict(path=['Angebot', 'Beweise', 'Preis', 'Anfrage'], click='Angebot anfragen', corner=[('Digitale Erlebnisse,', 'mit Absicht gebaut'), ('Potsdam · Berlin', 'Deutschland')],
               facts=[('1', 'Ansprechpartner: der Gründer'), ('1 Tag', 'bis zur Antwort'), ('DE · EN', 'Websites in beiden Sprachen'), ('100 %', 'der Zugänge gehören Ihnen')],
               vs_up='Vorteil', vs_down='Nachteil', vs_badge='Ihre Wahl?', word='SPRECHEN WIR', faq_more='Noch eine Frage? Schreiben Sie per WhatsApp',
               prices='PREISE', from_='ab', ans='Antworten'),
}

# ------------------------------------------------------------ small drawings for the problem (crisp, made in code)
ILL = {
'slow': '''<svg viewBox="0 0 400 250" class="ill" aria-hidden="true">
  <rect x="20" y="16" width="360" height="218" rx="16" class="ill__frame"/>
  <path d="M20 50h360" class="ill__line"/><circle cx="42" cy="33" r="4.5" class="ill__dot"/><circle cx="58" cy="33" r="4.5" class="ill__dot"/><circle cx="74" cy="33" r="4.5" class="ill__dot"/>
  <rect x="104" y="25" width="190" height="16" rx="8" class="ill__soft"/>
  <rect x="20" y="49" width="104" height="3" class="ill__bar"/>
  <g class="ill__skel"><rect x="44" y="76" width="150" height="16" rx="5"/><rect x="44" y="102" width="110" height="10" rx="5"/><rect x="44" y="128" width="312" height="80" rx="10"/><rect x="230" y="76" width="126" height="36" rx="10"/></g>
  <g transform="translate(200 168)"><g class="ill__spin"><circle r="18" class="ill__ring"/><path d="M0 -18a18 18 0 0 1 18 18" class="ill__arc"/></g></g>
</svg>''',
'phone': '''<svg viewBox="0 0 400 250" class="ill" aria-hidden="true">
  <defs><clipPath id="ill-ph"><rect x="152" y="22" width="96" height="206" rx="16"/></clipPath></defs>
  <g class="ill__ghost"><rect x="40" y="50" width="320" height="150" rx="10"/><path d="M40 72h320"/></g>
  <g clip-path="url(#ill-ph)" class="ill__squeeze">
    <rect x="96" y="40" width="210" height="14" rx="3" class="ill__soft"/>
    <rect x="96" y="62" width="210" height="62" rx="4" class="ill__img"/>
    <g class="ill__skel"><rect x="96" y="132" width="64" height="44" rx="3"/><rect x="168" y="132" width="64" height="44" rx="3"/><rect x="240" y="132" width="64" height="44" rx="3"/>
    <rect x="96" y="184" width="150" height="5" rx="2"/><rect x="96" y="194" width="120" height="5" rx="2"/><rect x="96" y="204" width="170" height="5" rx="2"/></g>
  </g>
  <rect x="152" y="22" width="96" height="206" rx="16" class="ill__frame ill__frame--hi"/>
  <rect x="186" y="30" width="28" height="6" rx="3" class="ill__dot"/>
  <path d="M120 126l-14 0m0 0l6 -6m-6 6l6 6M280 126l14 0m0 0l-6 -6m6 6l-6 6" class="ill__arrows"/>
</svg>''',
'path': '''<svg viewBox="0 0 400 250" class="ill" aria-hidden="true">
  <g class="ill__btns"><rect x="40" y="40" width="92" height="30" rx="15"/><rect x="250" y="34" width="110" height="30" rx="15"/><rect x="60" y="176" width="100" height="30" rx="15"/><rect x="262" y="170" width="92" height="30" rx="15"/><rect x="160" y="104" width="80" height="30" rx="15"/></g>
  <path d="M86 56 C 150 90, 120 150, 108 190 S 230 230, 306 186 S 330 90, 302 50 S 210 70, 200 118" class="ill__wander"/>
  <g class="ill__cursor"><path d="M0 0 L0 22 L6 16 L11 27 L15 25 L10 14 L18 14 Z"/></g>
  <circle cx="200" cy="119" r="22" class="ill__q"/><text x="200" y="127" text-anchor="middle" class="ill__qt">?</text>
</svg>''',
'small': '''<svg viewBox="0 0 400 250" class="ill" aria-hidden="true">
  <path d="M10 232 L118 92 L162 140 L222 40 L300 140 L338 104 L392 232 Z" class="ill__mount"/>
  <path d="M190 74 L222 40 L250 77 L236 72 L222 80 L206 70 Z" class="ill__snow"/>
  <g transform="translate(250 176)"><rect width="74" height="50" rx="7" class="ill__frame ill__frame--hi"/><path d="M0 12h74" class="ill__line"/><circle cx="9" cy="6" r="2" class="ill__dot"/><circle cx="16" cy="6" r="2" class="ill__dot"/><rect x="8" y="20" width="36" height="5" rx="2" class="ill__soft"/><rect x="8" y="30" width="58" height="12" rx="3" class="ill__soft"/></g>
  <g class="ill__lens" transform="translate(306 168)"><circle r="22" class="ill__ring"/><path d="M16 16 L30 30" class="ill__arc"/></g>
</svg>''',
}
PAIN_ILL = ['slow', 'phone', 'path', 'small']
CURSOR = '<svg class="cur" viewBox="0 0 20 30" aria-hidden="true"><path d="M1 1 L1 23 L7 17 L12 28 L16 26 L11 15 L19 15 Z"/></svg>'


def btn(label, href, kind='light', arrow=False, attrs=''):
    return f'<a class="btn btn--{kind}" href="{href}"{attrs}><span>{label}</span>{ARROW if arrow else ""}</a>'


def aik_svg():
    return f'<svg viewBox="{AIK_VIEWBOX}" aria-hidden="true" focusable="false">' + ''.join(f'<path d="{d}"/>' for d in AIK_PATHS) + '</svg>'


def head(c, key, title, side='', ghost=True):
    g = c['ghost'].get(key) if ghost else None
    ghost_html = f'<p class="ghost" aria-hidden="true">{g}</p>' if g else ''
    return (f'{ghost_html}'
            f'<div class="sec__head"><div><p class="label" data-up><b>[ 0{INDEX[key]} ]</b>{c["lbl"][key]}</p>'
            f'<h2 class="h2" id="{key}-title" data-blur>{title}</h2></div>{side}</div>')


def world(c):
    b = c['b']
    imgs = ''.join(f'<img data-scene="{n}" data-src="{b}media/world/{n}-1920.webp" data-srcset="{b}media/world/{n}-1280.webp 1280w, {b}media/world/{n}-1920.webp 1920w" sizes="100vw" alt="">'
                   for n in sorted(set(SCENE.values())))
    return f'<div class="world" aria-hidden="true">{imgs}</div>'


def header(c):
    b = c['b']
    nav = ''.join(f'<li><a href="{h}">{x}</a></li>' for h, x in c['nav'])
    en_cur = ' aria-current="true"' if c['lang'] == 'en' else ''
    de_cur = ' aria-current="true"' if c['lang'] == 'de' else ''
    en_href = './' if c['lang'] == 'en' else '../'
    de_href = './de/' if c['lang'] == 'en' else './'
    return f'''<a class="skip-link" href="#work">{c["skip"]}</a>
<header class="site-header is-cine-hidden">
  <a class="brand" href="{b}" aria-label="AIK Studio"><img src="{b}media/logo/aik-lockup-white.png" width="222" height="120" alt="AIK Studio"></a>
  <nav class="nav" id="site-nav" aria-label="Main">
    <ul class="nav__list">{nav}</ul>
    <div class="nav__more">{btn(c["start"], "#start", "light", True, ' data-start')}<p>{''.join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in SOCIAL)}</p></div>
  </nav>
  <div class="header-tools">
    <div class="lang" aria-label="Language"><a href="{en_href}" hreflang="en" lang="en"{en_cur}>EN</a><a href="{de_href}" hreflang="de" lang="de"{de_cur}>DE</a></div>
    {btn(c["talk"], "#contact", "line", True, ' data-start')}
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav"><span class="menu-toggle__bars" aria-hidden="true"></span><span class="menu-toggle__txt" data-open="{c["menu"]}" data-close="{c["close"]}">{c["menu"]}</span></button>
  </div>
</header>'''


def hero(c):
    b = c['b']; m = b + 'media/hero4/'; h = c['hero']; x = EXTRA[c['lang']]
    plate = e(json.dumps(PLATE, separators=(',', ':')))
    srcset = ', '.join(f'{m}plate-{w}.webp {w}w' for w in PLATE['sizes'])
    lines = ''.join(f'<span class="hx__line"><span style="--d:{220 + 120 * i}">{t}</span></span>' for i, t in enumerate(h['h']))
    (l1, l2), (r1, r2) = x['corner']
    return f'''<section class="hx" id="top" aria-labelledby="hero-title" data-media="{m}" data-plate="{plate}" data-film="{b}media/hero/flight-1920.mp4">
    <div class="hx__stage">
      <div class="hx__scene">
        <picture class="hx__plate">
          <source media="(max-width: 760px) and (orientation: portrait)" srcset="{m}plate-portrait-900.webp 900w, {m}plate-portrait-1400.webp 1400w" sizes="100vw">
          <img src="{m}plate-1920.webp" srcset="{srcset}" sizes="(min-aspect-ratio: 16/9) 100vw, 112vw" alt="{h["alt"]}" width="1920" height="1080" fetchpriority="high" decoding="async">
        </picture>
        <div class="hx__mark" data-word="AIK"><span class="hx__aik" aria-hidden="true">AIK</span></div>
        <div class="hx__shade" aria-hidden="true"></div>
      </div>
      <div class="hx__copy">
        <p class="hx__studio" aria-hidden="true" data-in style="--d:80">Studio</p>
        <h1 class="hx__title" id="hero-title"><span class="visually-hidden">AIK Studio: </span>{lines}</h1>
        <p class="hx__lead" data-in style="--d:520">{h["lead"]}</p>
        <div class="hx__ctas" data-in style="--d:620">
          {btn(h["cta1"], "#contact", "light", True, ' data-start')}
          <a class="round" href="#work"><span class="round__ico" aria-hidden="true">↓</span><span>{h["cta2"]}</span></a>
        </div>
      </div>
      <p class="hx__corner hx__corner--l" data-in style="--d:760">{l1}<br>{l2}</p>
      <p class="hx__corner hx__corner--r" data-in style="--d:820">{r1}<br>{r2}</p>
      <button class="hx__skip" type="button">{h["skip"]}</button>
    </div>
  </section>'''


def work(c):
    b = c['b']; w = c['work']
    def card(case, dup):
        name, meta, kind, txt, im, url = case
        tag = w['concept'] if kind == 'concept' else w['site']
        domain = re.sub(r'^https?://(www\.)?|/$', '', url)
        label = domain if 'netlify' not in domain else w['live']
        pic = (f'<img src="{b}media/work/{im}.webp" alt="{"" if dup else e(name) + ": " + e(txt)}" loading="lazy" decoding="async" width="828" height="1276">'
               if im else f'<span class="case__type" aria-hidden="true">{e(domain)}</span>')
        hide = ' aria-hidden="true"' if dup else ''
        tab = ' tabindex="-1"' if dup else ''
        return f'''<li class="case{' case--text' if not im else ''}"{hide}>
        <a href="{url}" target="_blank" rel="noopener"{tab}>
          <div class="case__frame"><div class="case__pic">{pic}</div><span class="case__tag">{tag}</span><span class="case__go">{label} ↗</span></div>
          <div class="case__info"><h3>{name}</h3><p class="case__meta">{meta}</p><p class="case__txt">{txt}</p></div>
        </a></li>'''
    cards = ''.join(card(cs, False) for cs in w['cases']) + ''.join(card(cs, True) for cs in w['cases'])
    side = f'<p class="sec__side" data-up>{w["note"]}</p>'
    return f'''<section class="sec work" id="work" aria-labelledby="work-title" data-scene="{SCENE["work"]}">
    <div class="slide">
      <div class="slide__in">{head(c, "work", w["title"], side)}</div>
      <div class="reel" data-reel><ol class="reel__track">{cards}</ol></div>
      <div class="slide__in work__foot"><span class="work__hint">{w["drag"]}</span></div>
    </div>
  </section>'''


def problem(c):
    p = c['problem']
    pains = ''.join(f'''<li class="stack__card glass">
        <div class="stack__txt"><p class="stack__n">0{i + 1}</p><h3>{t}</h3><p>{d}</p></div>
        <div class="stack__ill">{ILL[PAIN_ILL[i]]}</div>
      </li>''' for i, (t, d) in enumerate(p['pains']))
    return f'''<section class="sec problem" id="problem" aria-labelledby="problem-title" data-scene="{SCENE["problem"]}">
    <div class="slide slide--photo" style="background-image: url({c['b']}media/world/clouds-1920.webp)"><div class="slide__in">
      {head(c, "problem", p["title"])}
      <ol class="stack">{pains}</ol>
      <div class="stat" data-up>
        <p class="stat__num"><span data-count="{p["stat"]}">{p["stat"]}</span>%</p>
        <p class="stat__txt">{p["stat_txt"]}<small>{p["stat_src"]}</small></p>
      </div>
      <p class="read" data-read>{p["answer"]}</p>
      <p data-up>{btn(p["cta"], "#contact", "light", True, ' data-start')}</p>
    </div></div>
  </section>'''


def system(c):
    s = c['system']; b = c['b']; x = EXTRA[c['lang']]
    ui = [
        '''<div class="ui ui--timer"><svg viewBox="0 0 160 160" aria-hidden="true"><circle cx="80" cy="80" r="66" class="ui__track"/><circle cx="80" cy="80" r="66" class="ui__run" pathLength="1"/></svg><span>3<small>s</small></span></div>''',
        '<div class="ui ui--path">' + ''.join(f'<span style="--i:{i}">{t}</span>' for i, t in enumerate(x['path'])) + '</div>',
        f'''<div class="ui ui--click"><span class="ui__btn">{x["click"]} →</span><i class="ui__ripple"></i>{CURSOR}</div>''',
    ]
    steps = ''.join(f'''<li class="peak" data-up style="--d:{i * 110}">
        <img src="{b}media/stills/{SYSTEM_STILLS[i]}.webp" alt="" loading="lazy" decoding="async" width="540" height="960">
        <span class="peak__i">[ 0{i + 1} ]</span>
        {ui[i]}
        <div class="peak__cap glass"><p class="peak__big">{n}</p><h3>{t}</h3><p>{d}</p></div>
      </li>''' for i, (n, t, d) in enumerate(s['steps']))
    return f'''<section class="sec system" aria-labelledby="system-title" data-scene="{SCENE["system"]}">
    <div class="slide slide--light"><div class="slide__in">
      {head(c, "system", s["title"])}
      <ol class="peaks">{steps}</ol>
      <p class="read read--sm" data-read>{s["foot"]}</p>
    </div></div>
  </section>'''


def process(c):
    p = c['process']; b = c['b']
    st = ''.join(f'''<li class="station{' station--r' if i % 2 else ''}" style="--i:{i}">
        <span class="station__pic"><img src="{b}media/stills/{PATH_STILLS[i]}.webp" alt="" loading="lazy" decoding="async" width="540" height="960"></span>
        <div class="station__txt">
          <p class="station__n">0{i + 1}</p>
          <h3 class="station__name">{t}</h3>
          <p class="station__h">{h}</p>
          <p>{d}</p>
          <p class="station__you">{p["you"]}: <b>{y}</b></p>
        </div>
      </li>''' for i, (t, h, d, y) in enumerate(p['steps']))
    side = f'<p class="sec__side read read--sm" data-read>{p["lead"]}</p>'
    return f'''<section class="sec process" id="process" aria-labelledby="process-title" data-scene="{SCENE["process"]}">
    <div class="slide"><div class="slide__in">
      {head(c, "process", p["title"], side)}
      <div class="path">
        <svg class="path__line" viewBox="0 0 100 1000" preserveAspectRatio="none" aria-hidden="true"><path class="path__base" d="M50 0 C 50 120, 20 140, 22 250 S 80 380, 78 500 S 20 630, 22 750 S 50 900, 50 1000"/><path class="path__draw" pathLength="1" d="M50 0 C 50 120, 20 140, 22 250 S 80 380, 78 500 S 20 630, 22 750 S 50 900, 50 1000"/></svg>
        <ol class="path__stations">{st}</ol>
      </div>
    </div></div>
  </section>'''


def services(c):
    s = c['services']; k = s['calc']; b = c['b']; x = EXTRA[c['lang']]
    def price(pr):
        m = re.match(r'^(from|ab)\s+(.*)$', pr)
        if m: return f'<small>{m.group(1)}</small>{m.group(2)}'
        return pr.replace(' – ', '<i>–</i>')
    packs = []
    for i, (key, name, pr, sub, items, hot) in enumerate(s['packs']):
        li = ''.join(f'<li>{CHECK}{it}</li>' for it in items)
        packs.append(f'''<li class="pack{' pack--hot' if hot else ''}" style="--i:{i}">
        <div class="pack__top"><p class="pack__sub">{sub}</p>{f'<span class="pack__badge">{s["badge"]}</span>' if hot else ''}</div>
        <h3 class="pack__name">{name}</h3>
        <p class="pack__price">{price(pr)}</p>
        <ul class="pack__list">{li}</ul>
        {btn(s["pick"], "#start", "dark" if hot else "light", True, f' data-start data-need="{key}"')}
      </li>''')
    seg = lambda name, opts, on: ''.join(f'<label><input type="radio" name="{name}" value="{v}"{" checked" if v == on else ""}><span>{t}</span></label>' for v, t in opts)
    side = f'<p class="sec__side" data-up>{s["lead"]}</p>'
    return f'''<section class="sec services" id="services" aria-labelledby="services-title" data-scene="{SCENE["services"]}">
    <div class="slide"><div class="slide__in">
      {head(c, "services", s["title"], side, ghost=False)}
      <div class="prices">
        <p class="word word--prices" aria-hidden="true" style="background-image: linear-gradient(180deg, rgb(255 255 255 / .14), rgb(13 17 23 / .35)), url({b}media/world/peaks-1920.webp)">{x["prices"]}</p>
        <ol class="packs" data-up>{''.join(packs)}</ol>
      </div>
      <div class="extras" data-up><span>{s["extras_lbl"]}</span>{''.join(f'<em>{it}</em>' for it in s["extras"])}</div>
      {f'<p class="tax-note" data-up data-tax="{TAX}">{TAX_NOTE[TAX][c["lang"]]}</p>' if TAX else '<p class="tax-note" hidden data-tax="missing"></p>'}
      <form class="calc" data-up data-t='{e(json.dumps(k["t"], ensure_ascii=False))}'>
        <div class="calc__in">
          <h3 class="h3">{k["title"]}</h3>
          <fieldset><legend>{k["type"]}</legend><div class="seg">{seg("type", k["types"], "site")}</div></fieldset>
          <fieldset><legend>{k["pages"]} <output name="pagesOut">5</output></legend><input type="range" name="pages" min="1" max="12" value="5" aria-label="{k["pages"]}"></fieldset>
          <label class="switch"><input type="checkbox" name="cms"><span class="switch__ui" aria-hidden="true"></span><span>{k["cms"]} <small>{k["cms_note"]}</small></span></label>
          <fieldset><legend>{k["care"]}</legend><div class="seg">{seg("care", k["cares"], "0")}</div></fieldset>
        </div>
        <div class="calc__out">
          <svg class="calc__mount" viewBox="0 0 400 160" preserveAspectRatio="none" aria-hidden="true"><path class="calc__far" d="M0 160 L70 110 L120 128 L190 84 L250 120 L320 92 L400 160 Z"/><g class="calc__peak"><path d="M30 160 L120 118 L170 132 L230 40 L290 120 L340 104 L400 160 Z"/><path class="calc__snow" d="M206 72 L230 40 L252 74 L240 70 L230 78 L218 68 Z"/></g></svg>
          <p class="label">{k["out"]}</p>
          <p class="calc__price" aria-live="polite">2 400 – 4 600 €</p>
          <p class="calc__care"></p>
          <p class="calc__note">{k["note"]}</p>
          {btn(k["go"], "#start", "light", True, ' data-start data-from-calc')}
        </div>
      </form>
    </div></div>
  </section>'''


def why(c):
    w = c['why']; b = c['b']; x = EXTRA[c['lang']]
    facts = ''.join(f'<li data-up style="--d:{i * 70}"><b>{v}</b><span>{t}</span></li>' for i, (v, t) in enumerate(x['facts']))
    vs = []
    for i, (name, pr, up, down) in enumerate(w['rows']):
        us = i == len(w['rows']) - 1
        vs.append(f'''<li class="vs__card{' vs__card--us' if us else ''}" data-up style="--d:{i * 80}">
        {f'<span class="vs__badge">AIK</span>' if us else ''}<h3>{name}</h3><p class="vs__price">{pr}</p>
        <p class="vs__row"><i>+</i><span><small>{x["vs_up"]}</small>{up}</span></p>
        <p class="vs__row vs__row--down"><i>–</i><span><small>{x["vs_down"]}</small>{down}</span></p>
      </li>''')
    reasons = ''.join(f'<li class="glass" data-up style="--d:{i * 70}"><p class="reasons__n">0{i + 1}</p><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(w['reasons']))
    social = ''.join(f'<a class="chip" href="{u}" target="_blank" rel="noopener">{n} ↗</a>' for n, u in SOCIAL)
    return f'''<section class="sec why" id="why" aria-labelledby="why-title" data-scene="{SCENE["why"]}">
    <div class="slide"><div class="slide__in">
      {head(c, "why", w["title"])}
      <div class="founder">
        <div class="founder__pic" data-up><img src="{b}media/founder/nikolay-riabov.webp" alt="{w["name"]}, {w["role"]}" loading="lazy" decoding="async" width="600" height="800"><p class="founder__name">{w["name"]}<span>{w["role"]}</span></p></div>
        <div class="founder__txt">
          <p class="founder__q" data-read>“{w["quote"]}”</p>
          <ul class="facts">{facts}</ul>
          <p class="founder__links" data-up>{social}</p>
        </div>
      </div>
      <ol class="vs">{''.join(vs)}</ol>
      <ul class="reasons">{reasons}</ul>
    </div></div>
  </section>'''


def faq(c):
    f = c['faq']; x = EXTRA[c['lang']]
    items = ''.join(f'<li data-up><details><summary><span class="faq__n">{i + 1:02d}</span><span class="faq__q">{q}</span>{PLUS}</summary><div class="faq__a"><p>{a}</p></div></details></li>' for i, (q, a) in enumerate(f['items']))
    side = f'<p class="sec__side faq__count" data-up><b>{len(f["items"]):02d}</b>{x["ans"]}</p>'
    return f'''<section class="sec faq" id="faq" aria-labelledby="faq-title" data-scene="{SCENE["faq"]}">
    <div class="slide"><p class="ghost" aria-hidden="true">{c["ghost"]["faq"]}</p><div class="slide__in">
      {head(c, "faq", f["title"], side, ghost=False)}
      <ul class="faq__list">{items}</ul>
      <p class="faq__more" data-up><a href="https://wa.me/{WA}" target="_blank" rel="noopener">{x["faq_more"]} ↗</a></p>
    </div></div>
  </section>'''


def contact(c):
    k = c['contact']; b = c['b']; x = EXTRA[c['lang']]
    badge = ''.join(f'<span style="--i:{i}">{ch}</span>' for i, ch in enumerate(k['badge']))
    social = ''.join(f'<a href="{u}" target="_blank" rel="noopener">{n} ↗</a>' for n, u in SOCIAL[1:])
    return f'''<section class="sec contact" id="contact" aria-labelledby="contact-title" data-scene="{SCENE["contact"]}">
    <div class="slide slide--photo slide--contact">
    <div class="contact__bg" aria-hidden="true"><img src="{b}media/world/dawn-1920.webp" srcset="{b}media/world/dawn-1280.webp 1280w, {b}media/world/dawn-1920.webp 1920w" sizes="100vw" alt="" loading="lazy" decoding="async"></div>
    <div class="slide__in">
      <p class="label" data-up><b>[ 08 ]</b>{c["lbl"]["contact"]}</p>
      <p class="word word--contact" aria-hidden="true" style="background-image: linear-gradient(180deg, rgb(255 255 255 / .1), rgb(13 17 23 / .2)), url({b}media/hero4/plate-1920.webp)">{x["word"]}</p>
      <h2 class="h2 contact__title" id="contact-title" data-blur>{k["title"]}</h2>
      <p class="sec__lead" data-up>{k["lead"]}</p>
      <div class="go">
        <a class="go__card go__card--light" href="#start" data-start data-up>
          <span class="go__ico">{BUBBLE}</span><span class="go__t">{k["start"]}</span><span class="go__s">{k["start_sub"]}</span>
          <span class="badge" aria-hidden="true"><span class="badge__ring" style="--n:{len(k["badge"])}">{badge}</span><b>→</b></span>
        </a>
        <a class="go__card glass" href="https://wa.me/{WA}" target="_blank" rel="noopener" data-up style="--d:90">
          <span class="go__ico">{PHONE}</span><span class="go__t">{k["wa"]}</span><span class="go__s">{WA_SHOW}</span>
        </a>
      </div>
      <p class="contact__more" data-up>{social}<span>{k["fine"]}</span></p>
    </div></div>
  </section>'''


def footer(c):
    f = c['foot']; b = c['b']
    nav = ''.join(f'<li><a href="{h}">{x}</a></li>' for h, x in c['nav'])
    svc = ''.join(f'<li><a href="#services">{x}</a></li>' for x in f['svc'])
    soc = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u in SOCIAL)
    legal = ''.join(f'<a href="{b}{h}">{x}</a>' for h, x in f['legal'])
    return f'''<footer class="foot">
    <div class="wrap">
      <div class="foot__cols">
        <img class="foot__logo" src="{b}media/logo/aik-lockup-white.png" alt="AIK Studio" width="222" height="120" loading="lazy">
        <div><p>{f["studio"]}</p><ul>{nav}</ul></div>
        <div><p>{f["services"]}</p><ul>{svc}</ul></div>
        <div><p>{f["contact"]}</p><ul>{soc}</ul></div>
      </div>
      <p class="foot__mega" aria-hidden="true">AIK STUDIO</p>
      <div class="foot__base"><span>{f["who"]}</span><span>{f["copy"]}</span>{legal}<button class="pause" type="button" data-pause="{c["pause"]}" data-play="{c["play"]}" aria-pressed="false">{c["pause"]}</button><a href="#top">{f["top"]} ↑</a></div>
    </div>
  </footer>'''


def form(c):
    f = c['form']; b = c['b']; s = f['s']; n = len(s)
    def chips(st):
        typ = 'checkbox' if st['multi'] else 'radio'
        return ''.join(f'<label class="opt"><input type="{typ}" name="{st["name"]}" value="{e(o)}"><span>{o}</span></label>' for o in st['o'])
    steps = []
    for i, st in enumerate(s):
        if st['name'] in ('need', 'goal', 'start'):
            body = f'<div class="opts">{chips(st)}</div>'
        elif st['name'] == 'budget':
            body = f'''<p class="budget"><output name="budgetOut">2 400 €</output><small class="budget__fit"></small></p>
            <input class="range" type="range" name="budget" min="900" max="7000" step="100" value="2400" aria-label="Budget">
            <p class="budget__ends"><span>900 €</span><span>{'7.000' if c['lang'] == 'de' else '7 000'} € +</span></p>'''
        elif st['name'] == 'way':
            body = '<div class="ways">' + ''.join(f'''<label class="way{' way--light' if v == 'call' else ''}"><input type="radio" name="way" value="{v}"><span class="way__ico">{PHONE if v == 'call' else BUBBLE}</span><b>{t}</b><span>{d}</span></label>''' for v, t, d in st['o']) + '</div>'
        else:
            ff = f['f']
            body = f'''<div class="fields">
              <label class="field"><span>{ff["name"]}</span><input name="name" autocomplete="name" maxlength="120" placeholder="{ff["name_ph"]}" data-need="{ff["need_name"]}"></label>
              <label class="field"><span>{ff["phone"]} <small class="opt-note">{ff["phone_opt"]}</small></span><input name="phone" type="tel" autocomplete="tel" maxlength="40" inputmode="tel" placeholder="{ff["phone_ph"]}" data-need="{ff["need_phone"]}"></label>
              <label class="field"><span>{ff["email"]}</span><input name="email" type="email" autocomplete="email" maxlength="254" inputmode="email" placeholder="{ff["email_ph"]}" data-need="{ff["need_email"]}"></label>
              <p class="field__err" role="alert"></p>
              <p class="fields__fine">{ff["privacy"]} <a href="{b}datenschutz.html" target="_blank" rel="noopener">{ff["privacy_link"]}</a></p>
            </div>'''
        auto = st['name'] in ('start', 'way')
        steps.append(f'''<fieldset class="q{' is-on' if i == 0 else ''}" data-step="{i}"{' data-auto' if auto else ''}>
          <legend class="q__t">{st["t"]}</legend>{f'<p class="q__h">{st["h"]}</p>' if st.get("h") else ''}
          {body}
        </fieldset>''')
    fits = e(json.dumps(f['fits'], ensure_ascii=False))
    wa = e(json.dumps(dict(intro=f['wa_intro'], l=f['wa_labels']), ensure_ascii=False))
    return f'''<dialog class="sheet" id="start" aria-labelledby="sheet-title" data-fits="{fits}" data-wa="{wa}" data-num="{WA}">
  <form class="sheet__form" name="project" method="post" action="{b}" data-netlify="true" netlify-honeypot="company" novalidate>
    <input type="hidden" name="form-name" value="project"><input type="hidden" name="lang" value="{c["lang"]}">
    <p hidden><label>Company <input name="company" tabindex="-1" autocomplete="off"></label></p>
    <div class="sheet__top">
      <img src="{b}media/logo/aik-lockup-white.png" alt="AIK Studio" width="222" height="120">
      <p class="sheet__count" id="sheet-title"><span class="visually-hidden">{f["label"]}: </span><b>1</b> / {n}</p>
      <button class="sheet__x" type="button" data-close aria-label="Close">{CLOSE}</button>
      <span class="sheet__bar" aria-hidden="true"><i></i></span>
    </div>
    <div class="sheet__body">
      {''.join(steps)}
      <div class="q q--done" data-step="done" hidden>
        <p class="q__t">{f["ok_t"]}</p><p class="q__h">{f["ok"]}</p>
        <p>{btn(f["ok_wa"], "#", "light", True, ' data-wa-link target="_blank" rel="noopener"')}</p>
      </div>
      <div class="q q--err" data-step="err" hidden>
        <p class="q__h">{f["err"]}</p>
        <p>{btn(f["err_wa"], "#", "light", True, ' data-wa-link target="_blank" rel="noopener"')}</p>
      </div>
    </div>
    <div class="sheet__nav">
      <button class="btn btn--line" type="button" data-back hidden><span>{f["back"]}</span></button>
      <button class="btn btn--light" type="button" data-next disabled><span>{f["next"]}</span></button>
      <button class="btn btn--light" type="submit" data-send hidden data-sending="{f["sending"]}"><span>{f["send"]}</span></button>
      <p class="sheet__fine">{f["fine"]}</p>
    </div>
  </form>
</dialog>'''


def page(c):
    b = c['b']; lang = c['lang']
    alt_en = '../' if lang == 'de' else './'
    alt_de = './' if lang == 'de' else './de/'
    ld = {"@context": "https://schema.org", "@type": "ProfessionalService", "name": "AIK Studio",
          "description": c['desc'], "founder": {"@type": "Person", "name": "Nikolay Riabov"},
          "areaServed": ["Berlin", "Potsdam", "Deutschland"], "address": {"@type": "PostalAddress", "addressLocality": "Potsdam", "addressCountry": "DE"},
          "telephone": "+4915221595565", "priceRange": "900 € – 6 900 €+", "sameAs": [u for n, u in SOCIAL if n in ('Instagram', 'LinkedIn')]}
    loader = LOADER.replace('{b}', b).replace('aria-label="Loading AIK Studio"', f'aria-label="{c["loading"]}"')
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{c["title"]}</title>
<meta name="description" content="{c["desc"]}">
<meta name="theme-color" content="#0d1117">
<link rel="icon" type="image/png" sizes="48x48" href="{b}media/logo/icon-48.png">
<link rel="apple-touch-icon" href="{b}media/logo/icon-180.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{c["title"]}">
<meta property="og:description" content="{c["desc"]}">
<meta property="og:image" content="{b}media/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="de" href="{alt_de}">
<link rel="alternate" hreflang="x-default" href="{alt_en}">
<link rel="preload" href="{b}fonts/bigshoulders-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{b}fonts/jost-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{b}fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" as="image" href="{b}media/loader/aik-lockup.webp" fetchpriority="high">
<link rel="preload" as="image" href="{b}media/hero4/plate-1920.webp" imagesrcset="{', '.join(f'{b}media/hero4/plate-{w}.webp {w}w' for w in PLATE['sizes'])}" imagesizes="(min-aspect-ratio: 16/9) 100vw, 112vw" media="(min-width: 761px), (orientation: landscape)" fetchpriority="high">
<link rel="preload" as="image" href="{b}media/hero4/plate-portrait-900.webp" imagesrcset="{b}media/hero4/plate-portrait-900.webp 900w, {b}media/hero4/plate-portrait-1400.webp 1400w" imagesizes="100vw" media="(max-width: 760px) and (orientation: portrait)" fetchpriority="high">
<link rel="stylesheet" href="{b}css/loader.css">
<link rel="stylesheet" href="{b}css/aik.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{loader}
{world(c)}
{header(c)}

<main id="main">
  {hero(c)}
  {work(c)}
  {problem(c)}
  {system(c)}
  {process(c)}
  {services(c)}
  {why(c)}
  {faq(c)}
  {contact(c)}
  {footer(c)}
</main>

<a class="float" href="#start" data-start><span>{c["start"]}</span><span class="btn__arrow" aria-hidden="true">→</span></a>
{form(c)}

<script src="{b}js/hero4.js" defer></script>
<script src="{b}js/aik.js" defer></script>
</body>
</html>
'''


for lang, path in [('en', 'index.html'), ('de', 'de/index.html')]:
    (ROOT / path).write_text(page(T[lang]))
    print(lang, 'ok', path)
