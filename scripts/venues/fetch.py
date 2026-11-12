"""Download one venue-year into data/raw/venues/.

Usage: python3 scripts/venues/fetch.py <neurips|icml|iclr|acl|emnlp> <year>
*.cc sites: the poster list from /Downloads/<year> (same form post as scripts/fetch.sh) and the orals-posters JSON.
ACL / EMNLP: the collection XML from the ACL Anthology GitHub repository."""
import http.cookiejar
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from venues.parse import parse_anthology, parse_cc  # noqa: E402

CC = {'neurips': 'neurips.cc', 'icml': 'icml.cc', 'iclr': 'iclr.cc'}
ANTHOLOGY = ('acl', 'emnlp')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
TIMEOUT = 600
OUT = pathlib.Path('data/raw/venues')


def _get(opener, url, data=None, referer=None):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': UA, **({'Referer': referer} if referer else {})})
    with opener.open(req, timeout=TIMEOUT) as r:
        return r.read()


def fetch_cc(venue, year):
    host = CC[venue]
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    page = f'https://{host}/Downloads/{year}'
    tok = re.search(rb'csrfmiddlewaretoken" value="([^"]+)', _get(opener, page)).group(1).decode()
    body = urllib.parse.urlencode(dict(csrfmiddlewaretoken=tok, format='5', posters='on', resource='0',
                                       submitaction='Download Data')).encode()
    posters = json.loads(_get(opener, page, data=body, referer=page))
    (OUT / f'{venue}{year}_posters.json').write_text(json.dumps(posters, ensure_ascii=False))
    op = None
    try:
        op = json.loads(_get(opener, f'https://{host}/static/virtual/data/{venue}-{year}-orals-posters.json'))
        (OUT / f'{venue}{year}_op.json').write_text(json.dumps(op, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(f'warning: {venue} {year} orals-posters HTTP {e.code}; track and format will be unknown', file=sys.stderr)
    rows = parse_cc(posters, op or [], venue, year)
    n_op = len(op if isinstance(op, list) else op.get('results', [])) if op else None
    print(f'{venue} {year}: {len(rows)} papers (op: {n_op if op else "missing"}{" entries" if op else ""})')


def fetch_anthology(venue, year):
    raw = _get(urllib.request.build_opener(),
               f'https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/{year}.{venue}.xml')
    text = raw.decode('utf-8')
    ET.fromstring(text)  # raises if not XML
    (OUT / f'{venue}{year}.xml').write_text(text)
    print(f'{venue} {year}: {len(parse_anthology(text, venue, year))} papers')


def main(argv):
    if len(argv) != 3 or argv[1] not in (*CC, *ANTHOLOGY) or not argv[2].isdigit():
        sys.exit(__doc__)
    venue, year = argv[1], int(argv[2])
    OUT.mkdir(parents=True, exist_ok=True)
    (fetch_cc if venue in CC else fetch_anthology)(venue, year)


if __name__ == '__main__':
    main(sys.argv)
