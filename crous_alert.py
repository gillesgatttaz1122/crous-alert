#!/usr/bin/env python3
"""Alerte ntfy quand un nouveau logement apparaît sur trouverunlogement.lescrous.fr.

Variables d'environnement :
  NTFY_TOPIC  (obligatoire) sujet ntfy.sh auquel tu es abonné sur ton téléphone
  CROUS_URL   URL de recherche (défaut : https://trouverunlogement.lescrous.fr/tools/47/search)
  STATE_FILE  fichier des annonces déjà vues (défaut : crous_seen.json)
  MAX_PAGES   nombre maximum de pages parcourues (défaut : 20)
"""
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request

BASE = "https://trouverunlogement.lescrous.fr"
URL = os.environ.get("CROUS_URL") or f"{BASE}/tools/47/search"
TOPIC = os.environ.get("NTFY_TOPIC", "")
STATE_FILE = os.environ.get("STATE_FILE", "crous_seen.json")
MAX_PAGES = int(os.environ.get("MAX_PAGES", "20"))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"

# Chaque annonce pointe vers /tools/<id>/accommodations/<id>.
LINK_RE = re.compile(
    r'<a[^>]*href="((?:https://trouverunlogement\.lescrous\.fr)?/tools/\d+/accommodations/(\d+))[^"]*"[^>]*>(.*?)</a>',
    re.S,
)
TAG_RE = re.compile(r"<[^>]+>")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "fr-FR,fr;q=0.9"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def page_url(n):
    if n == 1:
        return URL
    parts = urllib.parse.urlsplit(URL)
    q = dict(urllib.parse.parse_qsl(parts.query))
    q["page"] = str(n)
    return urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(q)))


def scrape():
    found = {}
    for n in range(1, MAX_PAGES + 1):
        body = fetch(page_url(n))
        new_on_page = 0
        for href, acc_id, inner in LINK_RE.findall(body):
            title = html.unescape(TAG_RE.sub(" ", inner))
            title = " ".join(title.split())
            if acc_id not in found:
                new_on_page += 1
                found[acc_id] = {"url": urllib.parse.urljoin(BASE, href), "title": title}
            elif title and not found[acc_id]["title"]:
                found[acc_id]["title"] = title
        print(f"page {n}: {new_on_page} annonce(s)")
        # Page vide ou identique à la précédente : fin de la pagination.
        if new_on_page == 0:
            break
    return found


def notify(title, message, click=None):
    headers = {"Title": title.encode("utf-8"), "Tags": "house", "Priority": "high"}
    if click:
        headers["Click"] = click
    req = urllib.request.Request(f"https://ntfy.sh/{TOPIC}", data=message.encode("utf-8"), headers=headers)
    urllib.request.urlopen(req, timeout=30).read()


def main():
    if not TOPIC:
        sys.exit("NTFY_TOPIC manquant")

    try:
        with open(STATE_FILE) as f:
            seen = set(json.load(f))
        first_run = False
    except FileNotFoundError:
        seen = set()
        first_run = True

    current = scrape()
    new_ids = [i for i in current if i not in seen]
    print(f"{len(current)} annonce(s) en ligne, {len(new_ids)} nouvelle(s)")

    if first_run:
        notify("Alerte CROUS active", f"Surveillance démarrée : {len(current)} logement(s) actuellement en ligne.", URL)
    elif new_ids:
        lines = [f"• {current[i]['title'] or 'Logement ' + i}\n  {current[i]['url']}" for i in new_ids[:10]]
        if len(new_ids) > 10:
            lines.append(f"… et {len(new_ids) - 10} autre(s)")
        click = current[new_ids[0]]["url"] if len(new_ids) == 1 else URL
        notify(f"{len(new_ids)} nouveau(x) logement(s) CROUS", "\n".join(lines), click)

    with open(STATE_FILE, "w") as f:
        json.dump(sorted(seen | set(current)), f)


if __name__ == "__main__":
    main()
