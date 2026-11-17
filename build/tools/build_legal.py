"""Impressum and Datenschutz from one table of facts.

    python3 tools/build_legal.py .

Fill in OWNER below. Anything still None is shown on the page as a marked gap, and
tools/dist.py refuses to publish while a gap is left. Not legal advice: check both texts
with a legal-text generator (e.g. e-recht24, datenschutz-generator.de) or a lawyer.

Researched Nov 2026: § 5 DDG (Impressum; USt-IdNr or Wirtschafts-IdNr if one exists),
EU ODR platform closed on 20 Jul 2025 (no OS link any more), § 36 VSBG (≤ 10 people:
no duty to state willingness, the sentence below is voluntary), § 25 TDDDG (storage on the
device only where the visitor asked for it), supervisory authority for Potsdam: LDA Brandenburg."""
import html, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')

OWNER = dict(
    name='Nikolay Riabov',          # exactly as in the Gewerbeanmeldung / ID
    trade='AIK Studio',
    street=None,                    # street and number: a postal address where letters and court mail can be served (no P.O. box)
    city=None,                      # postcode and town
    email=None,                     # e.g. hallo@<domain>; only with the owner's go-ahead
    phone='+49 1522 1595565',
    vat_id=None,                    # USt-IdNr. if there is one
    w_id=None,                      # Wirtschafts-IdNr. if one has been issued (BZSt, § 139c AO)
    host='Netlify',                 # where the site is hosted
    updated='November 2026',
)
HOSTS = {
    'Netlify': dict(name='Netlify, Inc.', place='USA (San Francisco)',
                    transfer='Netlify verarbeitet Daten auch in den USA. Die Übermittlung stützt sich auf die EU-Standardvertragsklauseln im Auftragsverarbeitungsvertrag von Netlify bzw. auf eine Zertifizierung nach dem EU-US Data Privacy Framework, sofern vorhanden.',
                    check=True),
}

e = html.escape


def v(key, label):
    val = OWNER.get(key)
    return e(val) if val else f'<span class="todo">{label}</span>'


HEAD = '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@T | AIK Studio</title>
<meta name="robots" content="noindex, follow">
<link rel="icon" type="image/png" sizes="48x48" href="./media/logo/icon-48.png">
<link rel="stylesheet" href="./css/aik.css">
<link rel="stylesheet" href="./css/legal.css">
</head>
<body>
<main class="legal"><div class="wrap">
<p><a class="btn btn--line" href="./"><span>← AIK Studio</span></a></p>
<p class="label legal__lbl">AIK Studio · @T</p>
<h1 class="h1">@T</h1>
'''
FOOT = '''<p class="legal__date">Stand: @D</p>
<p class="legal__links"><a href="./impressum.html">Impressum</a><a href="./datenschutz.html">Datenschutz</a><a href="./">Startseite</a></p>
</div></main>
</body>
</html>
'''


def page(title, body):
    return HEAD.replace('@T', title) + body + FOOT.replace('@D', OWNER['updated'])


def impressum():
    o = OWNER
    tax = []
    if o['vat_id']: tax.append(f'Umsatzsteuer-Identifikationsnummer gemäß § 27a UStG: {e(o["vat_id"])}')
    if o['w_id']: tax.append(f'Wirtschafts-Identifikationsnummer gemäß § 139c AO: {e(o["w_id"])}')
    tax_html = ('<h2>Umsatzsteuer / Wirtschafts-ID</h2><p>' + '<br>'.join(tax) + '</p>') if tax else \
        '<h2>Umsatzsteuer / Wirtschafts-ID</h2><p><span class="todo">USt-IdNr. oder Wirtschafts-IdNr. eintragen, falls vorhanden; sonst diesen Abschnitt in tools/build_legal.py entfernen (OWNER: vat_id / w_id)</span></p>'
    body = f'''<h2>Angaben gemäß § 5 DDG</h2>
<p>{e(o["name"])}<br>{e(o["trade"])}<br>{v("street", "Straße und Hausnummer")}<br>{v("city", "PLZ und Ort")}<br>Deutschland</p>
<h2>Kontakt</h2>
<p>Telefon: <a href="tel:{o["phone"].replace(" ", "")}">{e(o["phone"])}</a><br>E-Mail: {f'<a href="mailto:{e(o["email"])}">{e(o["email"])}</a>' if o["email"] else '<span class="todo">E-Mail-Adresse</span>'}</p>
{tax_html}
<h2>Verbraucherstreitbeilegung</h2>
<p>Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
'''
    return page('Impressum', body)


def datenschutz():
    o = OWNER; h = HOSTS[o['host']]
    contact = f'{v("street", "Straße und Hausnummer")}, {v("city", "PLZ und Ort")}<br>Telefon: {e(o["phone"])}<br>E-Mail: {v("email", "E-Mail-Adresse")}'
    body = f'''<p class="legal__lead">Wir verarbeiten personenbezogene Daten nur, soweit es für diese Website und für die Beantwortung Ihrer Anfrage nötig ist. Diese Website setzt keine Cookies, nutzt kein Tracking und keine Analyse-Tools und lädt keine Schriften, Skripte oder Inhalte von fremden Servern.</p>

<h2>1. Verantwortlicher</h2>
<p>{e(o["name"])}, {e(o["trade"])}<br>{contact}</p>

<h2>2. Hosting und Server-Logfiles</h2>
<p>Diese Website wird bei {e(h["name"])}, {e(h["place"])}, gehostet. Beim Aufruf jeder Seite verarbeitet der Hoster technisch notwendige Daten: IP-Adresse, Datum und Uhrzeit, aufgerufene Seite, Browser und Betriebssystem, Referrer. Das ist nötig, um die Website sicher und stabil auszuliefern (Art. 6 Abs. 1 lit. f DSGVO; berechtigtes Interesse an einem sicheren Betrieb). Mit dem Hoster besteht ein Vertrag zur Auftragsverarbeitung (Art. 28 DSGVO).</p>
<p>{e(h["transfer"])}{' <span class="todo">Vor Veröffentlichung prüfen: aktueller DPF-Status von Netlify (dataprivacyframework.gov) und abgeschlossener AV-Vertrag</span>' if h["check"] else ''}</p>

<h2>3. Anfrageformular „Projekt starten“</h2>
<p>Wenn Sie das Formular nutzen, verarbeiten wir Ihre Angaben: Name, Telefonnummer und/oder E-Mail-Adresse sowie Ihre Antworten zu Bedarf, Ziel, Startzeitpunkt, Budget und gewünschtem nächsten Schritt. Wir nutzen sie ausschließlich, um Ihre Anfrage zu beantworten und gegebenenfalls ein Angebot zu erstellen (Art. 6 Abs. 1 lit. b DSGVO, vorvertragliche Maßnahmen). Die Übermittlung erfolgt über den Formulardienst des Hosters ({e(h["name"])}, siehe Abschnitt 2).</p>
<p>Wir löschen die Daten, wenn sie für diesen Zweck nicht mehr nötig sind. Kommt ein Auftrag zustande, bewahren wir sie auf, solange gesetzliche Aufbewahrungsfristen (insbesondere handels- und steuerrechtliche) es verlangen.</p>
<p>Schlägt der Versand fehl, bietet die Website an, dieselbe Anfrage als vorbereitete WhatsApp-Nachricht zu senden. Diese wird erst gesendet, wenn Sie das selbst in WhatsApp tun (siehe Abschnitt 4).</p>

<h2>4. Kontakt per Telefon, WhatsApp, Telegram oder E-Mail</h2>
<p>Wenn Sie uns direkt kontaktieren, verarbeiten wir die mitgeteilten Daten zur Bearbeitung Ihres Anliegens (Art. 6 Abs. 1 lit. b DSGVO, sonst lit. f). Bei WhatsApp (Meta Platforms Ireland Ltd.) und Telegram verarbeiten zusätzlich diese Anbieter Daten nach ihren eigenen Datenschutzbestimmungen, gegebenenfalls auch außerhalb der EU. Wenn Sie das nicht möchten, erreichen Sie uns per Telefon oder E-Mail.</p>

<h2>5. Links zu sozialen Netzwerken und externen Websites</h2>
<p>Die Website enthält einfache Links zu Instagram, LinkedIn, Telegram und WhatsApp sowie zu Projekten im Portfolio. Es sind keine Plugins eingebunden; beim Aufruf unserer Seite werden keine Daten an diese Anbieter übertragen. Erst wenn Sie einen Link anklicken, gelten die Datenschutzbestimmungen der jeweiligen Website.</p>

<h2>6. Speicherung im Browser</h2>
<p>Die Website setzt keine Cookies. Nur wenn Sie „Bewegung anhalten“ wählen, speichert Ihr Browser diese Einstellung lokal (localStorage, Schlüssel „aik-still“), damit Animationen auch beim nächsten Besuch angehalten bleiben. Das dient allein der von Ihnen gewünschten Funktion (§ 25 Abs. 2 Nr. 2 TDDDG). Wählen Sie „Bewegung fortsetzen“, wird der Eintrag gelöscht; Sie können ihn auch über die Einstellungen Ihres Browsers löschen.</p>

<h2>7. Schriften, Bilder und Videos</h2>
<p>Alle Schriften, Bilder und Videos werden von unserem eigenen Server geladen. Es findet keine Verbindung zu Google Fonts oder anderen Drittanbietern statt.</p>

<h2>8. Verschlüsselung</h2>
<p>Die Website wird ausschließlich über eine verschlüsselte Verbindung (HTTPS/TLS) ausgeliefert.</p>

<h2>9. Ihre Rechte</h2>
<p>Sie haben das Recht auf Auskunft (Art. 15 DSGVO), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18), Datenübertragbarkeit (Art. 20) und Widerspruch gegen Verarbeitungen auf Grundlage berechtigter Interessen (Art. 21). Eine erteilte Einwilligung können Sie jederzeit für die Zukunft widerrufen. Wenden Sie sich dazu an die oben genannten Kontaktdaten.</p>

<h2>10. Beschwerderecht</h2>
<p>Sie können sich bei einer Datenschutz-Aufsichtsbehörde beschweren. Zuständig für uns ist: Die Landesbeauftragte für den Datenschutz und für das Recht auf Akteneinsicht Brandenburg, Stahnsdorfer Damm 77, 14532 Kleinmachnow, <a href="https://www.lda.brandenburg.de" target="_blank" rel="noopener">www.lda.brandenburg.de</a>.</p>

<h2>11. Keine automatisierte Entscheidung</h2>
<p>Wir treffen keine automatisierten Entscheidungen und erstellen keine Profile.</p>
'''
    return page('Datenschutz', body)


(ROOT / 'impressum.html').write_text(impressum())
(ROOT / 'datenschutz.html').write_text(datenschutz())
gaps = sum(p.read_text().count('class="todo"') for p in (ROOT / 'impressum.html', ROOT / 'datenschutz.html'))
print('legal pages written;', gaps, 'gap(s) left' if gaps else 'complete')
